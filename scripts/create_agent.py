"""CLI to create or fetch the Gemini Data Analytics agent."""

import argparse
import logging

from app.agent_service import create_or_update_agent
from app.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or fetch the data agent context."
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Fail if the agent already exists instead of fetching it.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    settings = load_settings()
    agent = create_or_update_agent(settings, allow_update=not args.no_update)
    print(agent)


if __name__ == "__main__":
    main()
