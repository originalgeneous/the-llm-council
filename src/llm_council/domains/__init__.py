"""Domain-specific prompt addenda.

Domains layer a subject-matter prompt addendum onto whatever mode is active for
a subagent. This keeps the lens axis (mode) orthogonal to the subject-matter
axis (domain) so that adding e.g. legal or academic support is one YAML file
rather than a new mode plus schema.

See `medical.yaml` for the reference implementation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

DOMAINS_DIR = Path(__file__).parent

_VALID_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _validate_domain_name(name: str) -> None:
    if not name:
        raise ValueError("Domain name cannot be empty")
    if not _VALID_NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid domain name '{name}': must match pattern "
            f"'^[a-z0-9][a-z0-9_-]*$' (lowercase alphanumeric, hyphens, underscores)"
        )


def _ensure_path_containment(path: Path, base_dir: Path) -> None:
    resolved = path.resolve()
    base_resolved = base_dir.resolve()
    try:
        resolved.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Domain path escapes allowed directory: {path}")


def load_domain(name: str) -> dict[str, Any]:
    """Load a domain configuration by name.

    Raises:
        ValueError: name fails validation or path escapes the domains directory.
        FileNotFoundError: config file does not exist.
    """
    _validate_domain_name(name)
    config_path = DOMAINS_DIR / f"{name}.yaml"
    _ensure_path_containment(config_path, DOMAINS_DIR)

    if not config_path.exists():
        raise FileNotFoundError(f"Domain not found: {name}")
    with open(config_path) as f:
        loaded = yaml.safe_load(f)
    if not isinstance(loaded, dict):
        raise ValueError(f"Domain config for '{name}' must be a YAML dictionary")
    return loaded


def list_domains() -> list[str]:
    return [p.stem for p in DOMAINS_DIR.glob("*.yaml")]


def get_domain_addendum(name: str | None) -> str:
    """Return the prompt_addendum for a domain, or an empty string for a no-op.

    `None` and `"general"` always return `""` so callers can unconditionally
    concatenate the result without a defensive branch.
    """
    if name is None or name == "general":
        return ""
    config = load_domain(name)
    addendum = config.get("prompt_addendum", "")
    if not isinstance(addendum, str):
        raise ValueError(f"Domain '{name}' prompt_addendum must be a string")
    return addendum.strip()


__all__ = [
    "DOMAINS_DIR",
    "load_domain",
    "list_domains",
    "get_domain_addendum",
]
