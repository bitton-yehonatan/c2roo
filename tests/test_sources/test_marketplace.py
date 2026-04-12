import yaml

from c2roo.sources.marketplace import DEFAULT_MARKETPLACES, MarketplaceRegistry


def test_default_marketplaces():
    assert len(DEFAULT_MARKETPLACES) >= 2
    names = [m["name"] for m in DEFAULT_MARKETPLACES]
    assert "official" in names
    assert "community" in names


def test_registry_init_creates_config(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    assert config_path.exists()
    data = yaml.safe_load(config_path.read_text())
    assert len(data["marketplaces"]) >= 2


def test_registry_list(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    sources = registry.list_sources()
    assert len(sources) >= 2
    assert sources[0]["name"] == "official"


def test_registry_add(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    registry.add_source("custom", "my-org/my-marketplace", "Custom plugins")

    sources = registry.list_sources()
    names = [s["name"] for s in sources]
    assert "custom" in names


def test_registry_add_duplicate_raises(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    try:
        registry.add_source("official", "other/repo", "Duplicate")
        assert False, "Should have raised"
    except ValueError as e:
        assert "already exists" in str(e)


def test_registry_remove(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()
    registry.add_source("custom", "my-org/repo", "Temp")

    registry.remove_source("custom")

    names = [s["name"] for s in registry.list_sources()]
    assert "custom" not in names


def test_registry_remove_nonexistent_raises(tmp_path):
    config_path = tmp_path / "marketplaces.yaml"
    registry = MarketplaceRegistry(config_path=config_path)
    registry.ensure_config()

    try:
        registry.remove_source("nonexistent")
        assert False, "Should have raised"
    except ValueError as e:
        assert "not found" in str(e)
