from c2roo.report import ConversionReport


def test_report_tracks_entities():
    report = ConversionReport(plugin_name="superpowers")
    report.add_skill("pdf-processing", dropped=["context", "agent"])
    report.add_skill("frontend-design", dropped=[])
    report.add_command("commit", dropped=["allowed-tools"])
    report.add_agent("code-reviewer")
    report.add_hooks(count=2)

    assert report.skill_count == 2
    assert report.command_count == 1
    assert report.agent_count == 1
    assert report.hook_count == 2
    assert report.mcp_count == 0

    assert ("pdf-processing", ["context", "agent"]) in report.skill_drops
    assert ("commit", ["allowed-tools"]) in report.command_drops


def test_report_render_returns_string():
    report = ConversionReport(plugin_name="test")
    report.add_skill("s1", dropped=[])
    output_path = "/home/user/.roo"
    text = report.render(output_path)

    assert "Skills" in text
    assert "1 converted" in text
    assert output_path in text
