"""Read the layers of a .jGIS file."""

from __future__ import annotations

import json
import pathlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


def _flatten(tree: list) -> Iterator[str]:
    for item in tree:
        if isinstance(item, str):
            yield item
        elif isinstance(item, dict):
            yield from _flatten(item.get("layers", []))


def read_layers(path: str | pathlib.Path) -> list[dict]:
    """Return every layer in the file, bottom to top, with its source info.

    Keys: name, type, visible, source_type, path, url, data, has_filters.
    Local paths go in path, resolved against the .jGIS file's directory (as a
    Path); remote sources go in url (as a str). Missing values are None.
    """
    path = pathlib.Path(path)
    doc = json.loads(path.read_text())
    layers = doc.get("layers", {})
    sources = doc.get("sources", {})
    order = list(_flatten(doc["layerTree"])) if doc.get("layerTree") else list(layers)

    result = []
    for layer_id in order:
        layer = layers.get(layer_id)
        if layer is None:
            continue
        source = sources.get((layer.get("parameters") or {}).get("source")) or {}
        source_params = source.get("parameters") or {}
        source_path = source_params.get("path")
        url = None
        if source_path and "://" in source_path:
            url, source_path = source_path, None
        elif source_path:
            source_path = path.parent / source_path
        result.append(
            {
                "name": layer.get("name", layer_id),
                "type": layer.get("type"),
                "visible": layer.get("visible", True),
                "source_type": source.get("type"),
                "path": source_path,
                "url": url,
                "data": source_params.get("data"),
                "has_filters": bool((layer.get("filters") or {}).get("appliedFilters")),
            }
        )
    return result
