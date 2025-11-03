from __future__ import annotations

"""Helpers to interact with Gemini Data Analytics chat streams."""

import json
from typing import List, Optional, Sequence, Union

from google.cloud import geminidataanalytics


def _capture_text(resp) -> str:
    """Join text parts from the streaming response and print them."""
    text = "".join(resp.parts)
    print(text)
    return text


def stream_chat_response(
    question: str,
    *,
    project_id: str,
    location: str,
    data_agent_id: str,
    conversation_id: str,
    transcript_log: Optional[List[dict]] = None,
    enable_preview: bool = False,  # kept for compatibility; no-op now
    preview_port: int = 8080,  # unused, maintained for signature stability
    data_chat_client: Optional[geminidataanalytics.DataChatServiceClient] = None,
):
    """
    Send a chat request and capture only the generated SQL (and final answer text).
    """
    data_chat_client = data_chat_client or geminidataanalytics.DataChatServiceClient()
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

    print(question)
    generated_sql: Optional[str] = None
    final_answer: Optional[str] = None

    stream = data_chat_client.chat(request=request)
    for response in stream:
        system_msg = response.system_message
        if "text" in system_msg:
            final_answer = _capture_text(getattr(system_msg, "text"))
        elif "data" in system_msg and "generated_sql" in system_msg.data:
            generated_sql = system_msg.data.generated_sql
            print("\n--- SQL GENERATED ---\n")
            print(generated_sql)
        print("\n")

    turn = {
        "question": question,
        "answer": (final_answer or "").strip(),
        "generated_sql": generated_sql,
    }
    if transcript_log is not None:
        transcript_log.append(turn)
    return turn


def run_chat_session(
    questions: Union[str, Sequence[str]],
    *,
    project_id: str,
    location: str,
    data_agent_id: str,
    conversation_id: str,
    transcript_path: Optional[str] = None,
    enable_preview: bool = False,
    preview_port: int = 8080,
    data_chat_client: Optional[geminidataanalytics.DataChatServiceClient] = None,
) -> List[dict]:
    """Run questions sequentially within the same conversation and capture SQL."""
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
