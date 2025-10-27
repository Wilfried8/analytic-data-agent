from __future__ import annotations

import json
from typing import Iterable, List, Optional

from google.api_core import exceptions
from google.cloud import geminidataanalytics

from .chat_utils import run_chat_session, stream_chat_response
from .config import Settings


def ensure_conversation(
    settings: Settings,
    conversation_id: str,
    *,
    create_if_missing: bool = True,
) -> geminidataanalytics.Conversation:
    client = geminidataanalytics.DataChatServiceClient()
    conversation_name = client.conversation_path(
        settings.project_id, settings.location, conversation_id
    )
    try:
        return client.get_conversation(request={"name": conversation_name})
    except exceptions.NotFound:
        if not create_if_missing:
            raise
        conversation = geminidataanalytics.Conversation(
            agents=[
                client.data_agent_path(
                    settings.project_id, settings.location, settings.data_agent_id
                )
            ],
        )
        return client.create_conversation(
            request=geminidataanalytics.CreateConversationRequest(
                parent=client.common_location_path(settings.project_id, settings.location),
                conversation_id=conversation_id,
                conversation=conversation,
            )
        )


def interactive_chat(
    settings: Settings,
    conversation_id: str,
    *,
    exit_keyword: str = "exit",
    enable_preview: bool = False,
    transcript_path: Optional[str] = None,
) -> None:
    exit_keyword = exit_keyword.strip().lower()
    if not exit_keyword:
        raise ValueError("exit_keyword must not be empty.")

    ensure_conversation(settings, conversation_id)
    print("Interactive chat started. Type your messages; enter"
          f" '{exit_keyword}' to exit.")
    transcript: List[dict] = []

    try:
        while True:
            try:
                question = input("> ").strip()
            except EOFError:
                print("\nEOF received. Ending session.")
                break
            if not question:
                continue
            if question.lower() == exit_keyword:
                print("Ending interactive session.")
                break
            stream_chat_response(
                question,
                project_id=settings.project_id,
                location=settings.location,
                data_agent_id=settings.data_agent_id,
                conversation_id=conversation_id,
                transcript_log=transcript,
                enable_preview=enable_preview,
            )
    finally:
        if transcript_path and transcript:
            with open(transcript_path, "w", encoding="utf-8") as handle:
                json.dump(transcript, handle, indent=2)
            print(f"Transcript saved to {transcript_path}")


def scripted_chat(
    settings: Settings,
    conversation_id: str,
    questions: Iterable[str],
    *,
    enable_preview: bool = False,
    transcript_path: Optional[str] = None,
) -> List[dict]:
    ensure_conversation(settings, conversation_id)
    return run_chat_session(
        questions,
        project_id=settings.project_id,
        location=settings.location,
        data_agent_id=settings.data_agent_id,
        conversation_id=conversation_id,
        enable_preview=enable_preview,
        transcript_path=transcript_path,
    )
