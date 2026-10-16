import os

for k in ("NOTION_TOKEN", "SPRINT_DB_ID", "PROJECT_DB_ID", "SLACK_WEBHOOK_URL"):
    os.environ.setdefault(k, "test")

from notion_api import _get_date_range, _sprint_period  # noqa: E402


def _d(start, end=None):
    return {"date": {"start": start, "end": end}}


# 2026-10-12 월 / 10-16 금 / 10-17 토 / 10-18 일
assert _sprint_period(_d("2026-10-12", "2026-10-18")) == "2026-10-12 ~ 2026-10-16"  # 일 → 금
assert _sprint_period(_d("2026-10-12", "2026-10-17")) == "2026-10-12 ~ 2026-10-16"  # 토 → 금
assert _sprint_period(_d("2026-10-12", "2026-10-16")) == "2026-10-12 ~ 2026-10-16"  # 이미 금
assert _sprint_period(_d("2026-10-05", "2026-10-18")) == "2026-10-05 ~ 2026-10-16"  # 2주 스프린트
assert _sprint_period(_d("2026-10-12")) == "2026-10-12"
assert _sprint_period({}) == ""
# 작업 기간은 그대로
assert _get_date_range(_d("2026-10-12", "2026-10-18")) == "2026-10-12 ~ 2026-10-18"
print("ok")
