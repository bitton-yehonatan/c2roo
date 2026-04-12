from c2roo.converter.skill_converter import convert_skill
from c2roo.models.skill import Skill


def test_convert_skill_cleans_frontmatter():
    skill = Skill(
        name="pdf-processing",
        description="Extract PDFs",
        body="# Instructions\n\nDo stuff.",
        license="MIT",
        allowed_tools="Read Bash",
        disable_model_invocation=True,
        user_invocable=False,
        context="fork",
        agent="Explore",
        resources=[],
    )
    result = convert_skill(skill)
    assert result.frontmatter["name"] == "pdf-processing"
    assert result.frontmatter["license"] == "MIT"
    assert result.frontmatter["allowed-tools"] == "Read Bash"
    assert "disable-model-invocation" not in result.frontmatter
    assert "context" not in result.frontmatter
    assert result.dropped_fields == [
        "agent",
        "context",
        "disable-model-invocation",
        "user-invocable",
    ]
    assert result.body == "# Instructions\n\nDo stuff."


def test_convert_skill_no_optional_fields():
    skill = Skill(name="simple", description="Simple skill", body="Do things.", resources=[])
    result = convert_skill(skill)
    assert result.frontmatter["name"] == "simple"
    assert "license" not in result.frontmatter
    assert result.dropped_fields == []
