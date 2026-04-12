from pathlib import Path

from c2roo.parser.skill_parser import parse_skill

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sample-plugin"


def test_parse_skill():
    skill_dir = FIXTURES / "skills" / "pdf-processing"
    skill = parse_skill(skill_dir)

    assert skill.name == "pdf-processing"
    assert skill.description == "Extract text and tables from PDF files using Python libraries"
    assert skill.license == "MIT"
    assert skill.allowed_tools == "Read Bash"
    assert skill.disable_model_invocation is True
    assert skill.context == "fork"
    assert skill.user_invocable is None
    assert skill.agent is None
    assert "# PDF Processing" in skill.body
    assert "PyPDF2" in skill.body
    assert any(p.name == "extract.py" for p in skill.resources)


def test_parse_skill_missing_skill_md():
    empty_dir = FIXTURES / "skills"
    try:
        parse_skill(empty_dir)
        assert False, "Should have raised"
    except FileNotFoundError:
        pass
