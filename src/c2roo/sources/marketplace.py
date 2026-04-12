import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import yaml

DEFAULT_MARKETPLACES = [
    {
        "name": "official",
        "repo": "anthropics/claude-plugins-official",
        "description": "Official Anthropic plugins",
    },
    {
        "name": "community",
        "repo": "anthropics/claude-plugins-community",
        "description": "Community-submitted plugins",
    },
]

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "c2roo" / "marketplaces.yaml"
CACHE_DIR = Path.home() / ".cache" / "c2roo"
CACHE_TTL_SECONDS = 3600  # 1 hour


class MarketplaceRegistry:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self.config_path = config_path

    def ensure_config(self) -> None:
        """Create default config if it doesn't exist."""
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(
                yaml.dump({"marketplaces": DEFAULT_MARKETPLACES}, default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )

    def _load(self) -> dict:
        self.ensure_config()
        return yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {"marketplaces": []}

    def _save(self, data: dict) -> None:
        self.config_path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

    def list_sources(self) -> list[dict]:
        return self._load().get("marketplaces", [])

    def add_source(self, name: str, repo: str, description: str) -> None:
        data = self._load()
        existing_names = {m["name"] for m in data.get("marketplaces", [])}
        if name in existing_names:
            raise ValueError(f"Marketplace '{name}' already exists.")
        data["marketplaces"].append({"name": name, "repo": repo, "description": description})
        self._save(data)

    def remove_source(self, name: str) -> None:
        data = self._load()
        original_len = len(data.get("marketplaces", []))
        data["marketplaces"] = [m for m in data.get("marketplaces", []) if m["name"] != name]
        if len(data["marketplaces"]) == original_len:
            raise ValueError(f"Marketplace '{name}' not found.")
        self._save(data)

    def fetch_marketplace_json(self, source: dict) -> list[dict]:
        """Fetch and parse marketplace.json from a marketplace source."""
        repo = source["repo"]
        name = source["name"]

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{name}.json"
        if cache_file.exists():
            age = time.time() - cache_file.stat().st_mtime
            if age < CACHE_TTL_SECONDS:
                return json.loads(cache_file.read_text(encoding="utf-8"))

        temp_dir = tempfile.mkdtemp(prefix="c2roo-mkt-")
        try:
            url = f"https://github.com/{repo}.git"
            subprocess.run(
                ["git", "clone", "--depth", "1", url, temp_dir],
                check=True,
                capture_output=True,
            )

            manifest_path = Path(temp_dir) / ".claude-plugin" / "marketplace.json"
            if not manifest_path.exists():
                return []

            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            plugins = data.get("plugins", [])

            cache_file.write_text(json.dumps(plugins), encoding="utf-8")

            return plugins
        except subprocess.CalledProcessError:
            return []
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def search_plugin(self, plugin_name: str, source_filter: str | None = None) -> tuple[dict, dict] | None:
        """Search marketplaces for a plugin by name.

        Returns (plugin_entry, marketplace_source) or None.
        """
        sources = self.list_sources()
        if source_filter:
            sources = [s for s in sources if s["name"] == source_filter]

        for source in sources:
            plugins = self.fetch_marketplace_json(source)
            for plugin in plugins:
                if plugin.get("name") == plugin_name:
                    return plugin, source

        return None
