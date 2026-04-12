from pathlib import Path

from c2roo.parser.agent_parser import parse_agent

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_agent():
    agent_path = FIXTURES / "agents" / "code-reviewer.md"
    agent = parse_agent(agent_path)

    assert agent.name == "code-reviewer"
    assert agent.description == "Reviews code for bugs and quality issues"
    assert agent.model == "sonnet"
    assert agent.tools == ["Read", "Grep", "Glob", "Bash"]
    assert agent.color == "yellow"
    assert "expert code reviewer" in agent.body
    assert "Security vulnerabilities" in agent.body
