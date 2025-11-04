"""CLI entry point for scripted or interactive chat sessions."""

import argparse
import uuid

from app.chat_service import interactive_chat, scripted_chat
from app.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the data agent.")
    parser.add_argument(
        "--conversation-id",
        help="Existing conversation identifier; defaults to a generated ID.",
    )
    parser.add_argument("--preview", action="store_true", help="Enable chart preview server.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode; otherwise runs a default scripted set of questions.",
    )
    parser.add_argument(
        "--exit-command",
        default="exit",
        help="Command to end the interactive chat (default: exit).",
    )
    parser.add_argument(
        "--transcript-path",
        default="chat_transcript.json",
        help="Where to store the transcript. Use '-' to skip saving.",
    )
    parser.add_argument(
        "questions",
        nargs="*",
        help="Optional questions for scripted mode (if empty, defaults are used).",
    )
    args = parser.parse_args()

    settings = load_settings()
    conversation_id = args.conversation_id or f"chat-{uuid.uuid4().hex[:12]}"
    transcript_path = None if args.transcript_path == "-" else args.transcript_path

    if args.interactive:
        interactive_chat(
            settings,
            conversation_id,
            exit_keyword=args.exit_command,
            enable_preview=args.preview,
            transcript_path=transcript_path,
        )
    else:
        questions = args.questions or [
            "Hey what data do you have access to?",
            "what is the number of resident ?",
        ]
        scripted_chat(
            settings,
            conversation_id,
            questions,
            enable_preview=args.preview,
            transcript_path=transcript_path,
        )


if __name__ == "__main__":
    main()
