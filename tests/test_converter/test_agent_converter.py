from c2roo.converter.agent_converter import convert_agent
from c2roo.models.agent import Agent


def test_convert_agent_to_mode_and_rules():
    agent = Agent(
        name="code-reviewer",
        description="Reviews code for bugs and quality issues",
        body=(
            "You are an expert code reviewer. Analyze code for bugs, security issues, "
            "and quality problems.\n\nFocus on:\n- Logic errors\n- Security vulnerabilities"
            "\n- Performance issues"
        ),
        model="sonnet",
        tools=["Read", "Grep", "Glob", "Bash"],
        color="yellow",
    )
    result = convert_agent(agent)
    mode = result.mode
    assert mode["slug"] == "code-reviewer"
    assert mode["name"] == "Code Reviewer"
    assert "expert code reviewer" in mode["roleDefinition"]
    assert "read" in mode["groups"]
    assert "command" in mode["groups"]
    assert "edit" not in mode["groups"]
    assert "expert code reviewer" in result.rules_content
    assert "Originally configured for model: sonnet" in result.rules_content
    assert "Converted from Claude Code agent" in result.rules_content
    assert result.slug == "code-reviewer"


def test_convert_agent_tool_mapping():
    agent = Agent(
        name="full-agent",
        description="Has all tools",
        body="Instructions.",
        tools=[
            "Read",
            "Grep",
            "Glob",
            "LS",
            "Write",
            "Edit",
            "MultiEdit",
            "Bash",
            "BashOutput",
            "KillShell",
            "WebFetch",
        ],
    )
    result = convert_agent(agent)
    groups = result.mode["groups"]
    assert "read" in groups
    assert "edit" in groups
    assert "command" in groups


def test_convert_agent_humanizes_name():
    agent = Agent(name="my-cool-agent", description="Does cool stuff", body="You are cool.")
    result = convert_agent(agent)
    assert result.mode["name"] == "My Cool Agent"


def test_convert_agent_no_model():
    agent = Agent(name="basic", description="Basic agent", body="Do things.")
    result = convert_agent(agent)
    assert "Originally configured for model" not in result.rules_content
