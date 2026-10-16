from datetime import date, timedelta

from notion_client import Client
import config

_client = Client(auth=config.NOTION_TOKEN)


def _get_text(prop: dict, key: str = "rich_text") -> str:
    items = prop.get(key, [])
    return items[0]["plain_text"] if items else ""


def _get_select(prop: dict) -> str:
    for field in ("select", "status"):
        s = prop.get(field)
        if s:
            return s.get("name", "")
    items = prop.get("multi_select", [])
    if items:
        return ", ".join(i["name"] for i in items)
    return ""


def _get_date_range(prop: dict) -> str:
    d = prop.get("date")
    if not d:
        return ""
    start = d.get("start", "")
    end = d.get("end", "")
    return f"{start} ~ {end}" if end else start


def _sprint_period(prop: dict) -> str:
    # ponytail: Notion 자동 생성 스프린트는 주 단위라 일요일에 끝남. 알림에서는 토·일 종료일만 직전 금요일로 표시
    d = prop.get("date") or {}
    start, end = d.get("start", ""), d.get("end", "")
    if end:
        e = date.fromisoformat(end[:10])
        if e.weekday() >= 5:
            end = (e - timedelta(days=e.weekday() - 4)).isoformat()
    return f"{start} ~ {end}" if end else start


def _get_people(prop: dict) -> str:
    people = prop.get("people", [])
    return ", ".join(p.get("name", "") for p in people if p.get("name"))


def get_sprint(status: str) -> dict | None:
    res = _client.databases.query(
        database_id=config.SPRINT_DB_ID,
        filter={"property": "스프린트 상태", "status": {"equals": status}},
    )
    pages = res.get("results", [])
    if not pages:
        return None
    p = pages[0]
    props = p["properties"]
    task_ids = [r["id"] for r in props.get("스프린트 작업", {}).get("relation", [])]
    return {
        "id": p["id"],
        "name": _get_text(props.get("이름", {}), "title"),
        "period": _sprint_period(props.get("기간", {})),
        "sprint_question": _get_text(props.get("Sprint Question", {})),
        "url": p["url"],
        "task_ids": task_ids,
    }


def _fetch_page_title(page_id: str) -> str:
    try:
        page = _client.pages.retrieve(page_id=page_id)
        for prop in page["properties"].values():
            if prop.get("type") == "title":
                items = prop.get("title", [])
                return items[0]["plain_text"] if items else ""
    except Exception:
        pass
    return ""


def _fetch_task(page_id: str) -> dict:
    page = _client.pages.retrieve(page_id=page_id)
    props = page["properties"]

    proj_rel = (props.get("프로젝트") or {}).get("relation", [])
    project = _fetch_page_title(proj_rel[0]["id"]) if proj_rel else ""

    return {
        "name": _get_text(props.get("작업 이름", {}), "title"),
        "status": _get_select(props.get("상태") or {}),
        "project": project,
        "assignee": _get_people(props.get("담당자") or {}),
        "period": _get_date_range(props.get("작업 기간") or {}),
    }


def get_tasks(sprint: dict) -> list[dict]:
    return [_fetch_task(tid) for tid in sprint.get("task_ids", [])]
