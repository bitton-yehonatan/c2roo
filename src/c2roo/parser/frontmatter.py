import yaml


def parse_frontmatter(content: str) -> tuple[dict[str, object], str]:
    """Extract YAML frontmatter and body from a markdown string.

    Returns (metadata_dict, body_string). If no frontmatter is found,
    returns ({}, full_content).
    """
    if not content.startswith("---"):
        return {}, content.strip()

    # Find the closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content.strip()

    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3 :].strip()

    if not yaml_str:
        return {}, body

    meta = yaml.safe_load(yaml_str)
    if not isinstance(meta, dict):
        return {}, body

    return meta, body
