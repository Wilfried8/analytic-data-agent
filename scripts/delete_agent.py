"""CLI to delete the configured data agent."""

import argparse
import logging

from app.agent_service import delete_agent
from app.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete the configured data agent.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore soft-delete failures (best-effort deletion).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    settings = load_settings()
    delete_agent(settings, force=args.force)


if __name__ == "__main__":
    main()
