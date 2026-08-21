from datetime import UTC, datetime, timedelta


SOURCE_TIER_LABELS = {
    "authority": "权威机构",
    "professional": "专业机构",
    "general": "一般资料",
    "unverified": "待核实",
}
SOURCE_TIERS = frozenset(SOURCE_TIER_LABELS)
REVIEW_AFTER_DAYS = 365
PLACEHOLDER_SOURCES = frozenset({"", "manual", "未标注来源"})


def get_source_tier_label(source_tier: str | None) -> str:
    return SOURCE_TIER_LABELS.get(source_tier or "unverified", "待核实")


def normalize_to_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def get_source_review_reasons(
    source: str | None,
    source_tier: str | None,
    updated_at: datetime | None,
    source_url: str | None = None,
) -> list[str]:
    reasons: list[str] = []
    if (source or "").strip() in PLACEHOLDER_SOURCES:
        reasons.append("未标注具体资料来源")
    if not (source_url or "").strip():
        reasons.append("未提供可访问的来源链接")
    if source_tier not in SOURCE_TIERS or source_tier == "unverified":
        reasons.append("可信度等级为待核实")

    normalized_updated_at = normalize_to_utc(updated_at)
    if normalized_updated_at is None:
        reasons.append("未记录最后更新时间")
    elif normalized_updated_at < datetime.now(UTC) - timedelta(days=REVIEW_AFTER_DAYS):
        reasons.append(f"最后更新距今超过 {REVIEW_AFTER_DAYS} 天")
    return reasons


def needs_source_review(
    source_tier: str | None,
    updated_at: datetime | None,
    source: str | None = None,
    source_url: str | None = None,
) -> bool:
    return bool(
        get_source_review_reasons(source, source_tier, updated_at, source_url)
    )
