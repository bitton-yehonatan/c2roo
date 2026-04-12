from pathlib import Path

from c2roo.models import (
    Agent,
    Command,
    Hook,
    McpServer,
    Plugin,
    PluginMetadata,
    Skill,
)


def test_plugin_metadata_required_fields():
    meta = PluginMetadata(
        name="test", version=None, description="A test", author=None, homepage=None, license=None
    )
    assert meta.name == "test"
    assert meta.version is None


def test_skill_with_all_fields():
    skill = Skill(
        name="pdf-processing",
        description="Process PDFs",
        body="# Instructions\nDo stuff.",
        license="MIT",
        compatibility=None,
        metadata={"author": "test"},
        allowed_tools="Read Bash",
        resources=[Path("scripts/extract.py")],
        disable_model_invocation=True,
        user_invocable=None,
        context="fork",
        agent="Explore",
    )
    assert skill.name == "pdf-processing"
    assert skill.disable_model_invocation is True
    assert len(skill.resources) == 1


def test_command_minimal():
    cmd = Command(
        name="commit",
        description="Create a commit",
        argument_hint=None,
        allowed_tools=None,
        body="Do a commit.",
    )
    assert cmd.name == "commit"
    assert cmd.allowed_tools is None


def test_agent_tools_list():
    agent = Agent(
        name="code-reviewer",
        description="Reviews code",
        model="sonnet",
        tools=["Read", "Grep", "Glob", "Bash"],
        color="yellow",
        body="You are a code reviewer.",
    )
    assert "Bash" in agent.tools
    assert agent.model == "sonnet"


def test_hook_fields():
    hook = Hook(event="PreToolUse", matcher="Edit|Write", command="python3 lint.py", timeout=10)
    assert hook.event == "PreToolUse"
    assert hook.matcher == "Edit|Write"


def test_mcp_server_stdio():
    server = McpServer(
        name="my-server",
        command="npx",
        args=["-y", "@org/server"],
        env={"KEY": "val"},
        url=None,
        headers={},
        disabled=False,
        always_allow=["tool1"],
        timeout=60,
    )
    assert server.command == "npx"
    assert server.url is None


def test_mcp_server_sse():
    server = McpServer(
        name="remote",
        command=None,
        args=[],
        env={},
        url="http://localhost:3000/sse",
        headers={"Authorization": "Bearer tok"},
        disabled=False,
        always_allow=[],
        timeout=None,
    )
    assert server.url == "http://localhost:3000/sse"
    assert server.command is None


def test_plugin_assembles_all_entities():
    plugin = Plugin(
        metadata=PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test",
            author=None,
            homepage=None,
            license=None,
        ),
        skills=[],
        commands=[],
        agents=[],
        hooks=[],
        mcp_servers={},
        source_path=Path("/tmp/test"),
    )
    assert plugin.metadata.name == "test-plugin"
    assert plugin.skills == []
