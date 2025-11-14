"""Inspect data agents in the configured project/location."""

import argparse
import json
from google.cloud import geminidataanalytics

from app.agent_service import get_agent, list_agents
from app.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect Gemini Data Analytics agents."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="List all agents in the location instead of only the configured one.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Return data as JSON instead of the default text summary.",
    )
    args = parser.parse_args()

    settings = load_settings()

    if args.all:
        agents = list_agents(settings)
        if args.json:
            print(
                json.dumps(
                    [agent_to_dict(agent) for agent in agents], indent=2, default=str
                )
            )
        else:
            for agent in agents:
                print_summary(agent)
                print("-" * 40)
    else:
        agent = get_agent(settings)
        if agent is None:
            print(
                f"Agent '{settings.data_agent_id}' not found in "
                f"{settings.project_id}/{settings.location}."
            )
            return
        if args.json:
            print(json.dumps(agent_to_dict(agent), indent=2, default=str))
        else:
            print_summary(agent)


def agent_to_dict(agent) -> dict:
    return geminidataanalytics.DataAgent.to_dict(agent)


def print_summary(agent) -> None:
    print(f"Name      : {agent.name}")
    print(f"Created   : {agent.create_time}")
    if agent.update_time:
        print(f"Updated   : {agent.update_time}")
    context = agent.data_analytics_agent.published_context
    print("Instruction snippet:")
    print((context.system_instruction or "").splitlines()[0:5])


if __name__ == "__main__":
    main()
