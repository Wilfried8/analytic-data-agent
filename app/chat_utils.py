import contextlib
import http.server
import io
import json
import socketserver
import sys
import threading
from typing import List, Optional, Sequence, Union

import altair as alt
import pandas as pd
import proto
from google.cloud import geminidataanalytics

_server_thread: Optional[threading.Thread] = None
_httpd: Optional[socketserver.TCPServer] = None


class _TeeCapture(io.StringIO):
    """Mirror stdout to an in-memory buffer while still printing to console."""

    def __init__(self, *targets):
        super().__init__()
        self._targets = targets

    def write(self, s):
        for target in self._targets:
            target.write(s)
        return super().write(s)

    def flush(self):
        for target in self._targets:
            target.flush()
        super().flush()


def display_section_title(text: str) -> None:
    print(f"\n--- {text.upper()} ---")


def display_schema(datasource_schema) -> None:
    fields = getattr(datasource_schema, "fields")
    df = pd.DataFrame(
        {
            "Column": [f.name for f in fields],
            "Type": [f.type for f in fields],
            "Description": [getattr(f, "description", "-") for f in fields],
            "Mode": [f.mode for f in fields],
        }
    )
    print(df)


def display_datasource(datasource) -> None:
    table_ref = datasource.bigquery_table_reference
    source_name = f"{table_ref.project_id}.{table_ref.dataset_id}.{table_ref.table_id}"
    print(source_name)
    display_schema(datasource.schema)


def handle_data_response(resp) -> None:
    if "query" in resp:
        query = resp.query
        display_section_title("Retrieval query")
        print(f"Query name: {query.name}")
        print(f"Question: {query.question}")
        print("Data sources:")
        for datasource in query.datasources:
            display_datasource(datasource)
    elif "generated_sql" in resp:
        display_section_title("SQL generated")
        print(resp.generated_sql)
    elif "result" in resp:
        display_section_title("Data retrieved")
        fields = [field.name for field in resp.result.schema.fields]
        dataset = {field: [] for field in fields}
        for row in resp.result.data:
            for field in fields:
                dataset[field].append(row[field])
        print(pd.DataFrame(dataset))


def preview_in_browser(port: int = 8080) -> None:
    """Start a simple HTTP server to preview generated charts."""
    global _server_thread, _httpd
    if _server_thread and _server_thread.is_alive():
        print(
            f"\n--> A new chart was generated. Refresh your browser at http://localhost:{port}"
        )
        return
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    try:
        _httpd = socketserver.TCPServer(("", port), Handler)
    except OSError as exc:
        print(f"❌ Could not start server on port {port}: {exc}")
        return
    _server_thread = threading.Thread(target=_httpd.serve_forever)
    _server_thread.daemon = False
    _server_thread.start()
    print("\n" + "=" * 60)
    print(" 📈 CHART READY - PREVIEW IN BROWSER ".center(60))
    print("=" * 60)
    print(f"1. In the Cloud Shell toolbar, click 'Web Preview' and select port {port}.")
    print(f"2. Or, open your local browser to http://localhost:{port}")
    print("=" * 60)
    try:
        try:
            input(
                "\n--> Press Enter here after viewing all charts to shut down the server...\n\n"
            )
        except EOFError:
            print("No stdin available; stopping preview server automatically.")
    finally:
        print("Shutting down server...")
        _httpd.shutdown()
        _server_thread.join()
        _httpd, _server_thread = None, None
        print("Server stopped.")


def handle_chart_response(resp, chart_generated_flag: List[bool]) -> None:
    def _value_to_dict(value):
        if isinstance(value, proto.marshal.collections.maps.MapComposite):
            return {k: _value_to_dict(value[k]) for k in value}
        if isinstance(value, proto.marshal.collections.RepeatedComposite):
            return [_value_to_dict(element) for element in value]
        return value

    if "query" in resp:
        print(resp.query.instructions)
    elif "result" in resp:
        vega_config_dict = _value_to_dict(resp.result.vega_config)
        chart = alt.Chart.from_dict(vega_config_dict)
        chart_filename = "index.html"
        chart.save(chart_filename)
        if chart_generated_flag:
            chart_generated_flag[0] = True


def handle_schema_response(resp) -> None:
    if "query" in resp:
        print(resp.query.question)
    elif "result" in resp:
        display_section_title("Schema resolved")
        print("Data sources:")
        for datasource in resp.result.datasources:
            display_datasource(datasource)


def handle_text_response(resp) -> None:
    parts = resp.parts
    print("".join(parts))


def show_message(msg, chart_generated_flag: List[bool]) -> None:
    system_msg = msg.system_message
    if "text" in system_msg:
        handle_text_response(getattr(system_msg, "text"))
    elif "schema" in system_msg:
        handle_schema_response(getattr(system_msg, "schema"))
    elif "data" in system_msg:
        handle_data_response(getattr(system_msg, "data"))
    elif "chart" in system_msg:
        handle_chart_response(getattr(system_msg, "chart"), chart_generated_flag)
    print("\n")


def stream_chat_response(
    question: str,
    *,
    project_id: str,
    location: str,
    data_agent_id: str,
    conversation_id: str,
    transcript_log: Optional[List[dict]] = None,
    enable_preview: bool = True,
    preview_port: int = 8080,
    data_chat_client: Optional[geminidataanalytics.DataChatServiceClient] = None,
):
    """
    Sends a chat request, processes the streaming response, and optionally
    launches a chart preview server.
    """
    data_chat_client = data_chat_client or geminidataanalytics.DataChatServiceClient()
    chart_generated_flag = [False]
    messages = [
        geminidataanalytics.Message(
            user_message=geminidataanalytics.UserMessage(text=question)
        )
    ]
    conversation_reference = geminidataanalytics.ConversationReference(
        conversation=data_chat_client.conversation_path(
            project_id, location, conversation_id
        ),
        data_agent_context=geminidataanalytics.DataAgentContext(
            data_agent=data_chat_client.data_agent_path(
                project_id, location, data_agent_id
            ),
        ),
    )
    request = geminidataanalytics.ChatRequest(
        parent=f"projects/{project_id}/locations/{location}",
        messages=messages,
        conversation_reference=conversation_reference,
    )
    tee = _TeeCapture(sys.stdout)
    with contextlib.redirect_stdout(tee):
        print(question)
        stream = data_chat_client.chat(request=request)
        for response in stream:
            show_message(response, chart_generated_flag)
        if enable_preview and chart_generated_flag[0]:
            preview_in_browser(port=preview_port)
    output_text = tee.getvalue()
    if transcript_log is not None:
        transcript_log.append({"question": question, "output": output_text})
    return output_text


def run_chat_session(
    questions: Union[str, Sequence[str]],
    *,
    project_id: str,
    location: str,
    data_agent_id: str,
    conversation_id: str,
    transcript_path: Optional[str] = None,
    enable_preview: bool = True,
    preview_port: int = 8080,
    data_chat_client: Optional[geminidataanalytics.DataChatServiceClient] = None,
) -> List[dict]:
    """
    Runs a list of questions sequentially within the same conversation.
    Optionally persists the transcript to disk as JSON.
    """
    if isinstance(questions, str):
        questions = [questions]
    transcript_log: List[dict] = []
    for question in questions:
        stream_chat_response(
            question,
            project_id=project_id,
            location=location,
            data_agent_id=data_agent_id,
            conversation_id=conversation_id,
            transcript_log=transcript_log,
            enable_preview=enable_preview,
            preview_port=preview_port,
            data_chat_client=data_chat_client,
        )
    if transcript_path:
        with open(transcript_path, "w", encoding="utf-8") as handle:
            json.dump(transcript_log, handle, indent=2)
        print(f"Transcript saved to {transcript_path}")
    return transcript_log
