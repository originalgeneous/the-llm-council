"""Tests for the domain addendum layer."""

from __future__ import annotations

import pytest

from llm_council.domains import (
    get_domain_addendum,
    list_domains,
    load_domain,
)
from llm_council.subagents import get_effective_system_prompt, load_subagent


def test_list_domains_contains_general_and_medical() -> None:
    names = list_domains()
    assert "general" in names
    assert "medical" in names


def test_load_general_has_empty_addendum() -> None:
    config = load_domain("general")
    assert config["name"] == "general"
    assert config["prompt_addendum"] == ""


def test_load_medical_mentions_all_seven_sections() -> None:
    config = load_domain("medical")
    addendum = config["prompt_addendum"]
    for marker in (
        "Source-authority",
        "Hallucination risk",
        "Clinical-safety",
        "Trial-specific",
        "Cross-source consistency",
        "Evidence-quality",
        "Differential",
    ):
        assert marker in addendum, f"medical addendum missing section marker {marker!r}"


def test_get_domain_addendum_none_returns_empty() -> None:
    assert get_domain_addendum(None) == ""


def test_get_domain_addendum_general_returns_empty() -> None:
    assert get_domain_addendum("general") == ""


def test_get_domain_addendum_medical_is_nonempty() -> None:
    addendum = get_domain_addendum("medical")
    assert addendum.strip()
    assert "Source-authority grounding" in addendum


def test_load_nonexistent_domain_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_domain("does-not-exist")


@pytest.mark.parametrize(
    "bad_name",
    [
        "../etc/passwd",
        "Medical",
        "-leading-dash",
        "",
        "med/ical",
    ],
)
def test_invalid_domain_name_rejected(bad_name: str) -> None:
    with pytest.raises((ValueError, FileNotFoundError)):
        load_domain(bad_name)


def test_get_effective_system_prompt_appends_medical_addendum() -> None:
    config = load_subagent("critic")
    baseline = get_effective_system_prompt(config, mode="review")
    with_medical = get_effective_system_prompt(config, mode="review", domain="medical")
    assert "Source-authority grounding" not in baseline
    assert "Source-authority grounding" in with_medical
    assert with_medical.startswith(baseline)


def test_get_effective_system_prompt_general_domain_matches_baseline() -> None:
    config = load_subagent("critic")
    baseline = get_effective_system_prompt(config, mode="review")
    with_general = get_effective_system_prompt(config, mode="review", domain="general")
    assert with_general == baseline
