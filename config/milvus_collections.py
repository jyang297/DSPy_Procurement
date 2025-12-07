import os
from pathlib import Path
from typing import Dict, Optional, Union

import yaml

DEFAULT_COLLECTIONS = {
    "suppliers": "suppliers_demo",
    "contracts": "contracts_demo",
    "audits": "audits_demo",
}


def _ensure_demo_suffix(name: str) -> str:
    return name if name.endswith("_demo") else f"{name}_demo"


def load_collection_names(
    config_path: Optional[Union[str, Path]] = None,
) -> Dict[str, str]:
    """
    Load collection names from YAML, always enforcing a _demo suffix.

    When config_path is not provided, the loader looks for a MILVUS_COLLECTION_CONFIG
    env override, otherwise falls back to config/milvus_collections.yaml next to this file.
    """
    base_path = Path(__file__).resolve().parent
    fallback_path = base_path / "milvus_collections.yaml"
    path = Path(os.environ.get("MILVUS_COLLECTION_CONFIG", fallback_path))

    if config_path:
        path = Path(config_path)

    data = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    configured = data.get("collections", {})

    return {
        key: _ensure_demo_suffix(configured.get(key, default))
        for key, default in DEFAULT_COLLECTIONS.items()
    }
