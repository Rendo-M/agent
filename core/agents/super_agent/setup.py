from registry import registry

from agents.low_agents.search_agent import SearchAgent


def setup_agents() -> None:
    registry.register(SearchAgent())