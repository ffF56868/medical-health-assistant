from datetime import UTC, datetime, timedelta


SOURCE_TIER_LABELS = {
    "authority": "权威机构",
    "professional": "专业机构",
    "general": "一般资料",
    "unverified": "待核实",
}
SOURCE_TIERS = frozenset(SOURCE_TIER_LABELS)
REVIEW_AFTER_DAYS = 365


def get_source_tier_label(source_tier: str | None) -> str:
    return SOURCE_TIER_LABELS.get(source_tier or "unverified", "待核实")


def needs_source_review(
    source_tier: str | None,
    updated_at: datetime | None,
) -> bool:
    if source_tier not in SOURCE_TIERS or source_tier == "unverified":
        return True
    if updated_at is None:
        return True
    return updated_at < datetime.now(UTC) - timedelta(days=REVIEW_AFTER_DAYS)
