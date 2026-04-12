from c2roo.models.hook import Hook
from c2roo.converter.hook_converter import convert_hooks


def test_convert_hooks_to_guidance():
    hooks = [
        Hook(event="PreToolUse", matcher="Edit|Write", command="python3 hooks/lint.py", timeout=10),
        Hook(event="SessionStart", matcher=None, command="echo starting", timeout=None),
    ]
    result = convert_hooks(hooks)
    assert "## PreToolUse" in result
    assert "Edit|Write" in result
    assert "python3 hooks/lint.py" in result
    assert "## SessionStart" in result
    assert "echo starting" in result
    assert "Converted from Claude Code hooks" in result


def test_convert_empty_hooks():
    result = convert_hooks([])
    assert result == ""
