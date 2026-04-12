import pytest

from c2roo.parser.frontmatter import parse_frontmatter


def test_basic_frontmatter():
    content = """---
name: test-skill
description: A test skill
---

# Body content

Some instructions here.
"""
    meta, body = parse_frontmatter(content)
    assert meta["name"] == "test-skill"
    assert meta["description"] == "A test skill"
    assert "# Body content" in body
    assert "Some instructions here." in body


def test_no_frontmatter():
    content = "# Just a markdown file\n\nNo frontmatter here."
    meta, body = parse_frontmatter(content)
    assert meta == {}
    assert "# Just a markdown file" in body


def test_empty_frontmatter():
    content = "---\n---\n\nBody only."
    meta, body = parse_frontmatter(content)
    assert meta == {}
    assert "Body only." in body


def test_frontmatter_with_list_values():
    content = """---
name: agent
tools:
  - Read
  - Grep
  - Bash
---

Body."""
    meta, body = parse_frontmatter(content)
    assert meta["tools"] == ["Read", "Grep", "Bash"]
    assert "Body." in body


def test_frontmatter_with_boolean():
    content = """---
name: skill
disable-model-invocation: true
user-invocable: false
---

Content."""
    meta, body = parse_frontmatter(content)
    assert meta["disable-model-invocation"] is True
    assert meta["user-invocable"] is False


def test_body_stripped_of_leading_whitespace():
    content = """---
name: test
---



Body starts here."""
    meta, body = parse_frontmatter(content)
    assert body == "Body starts here."
