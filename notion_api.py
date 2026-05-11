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
    return {
        "id": p["id"],
        "name": _get_text(props.get("이름", {}), "title"),
        "period": _get_date_range(props.get("기간", {})),
        "work_area": _get_text(props.get("작업 영역", {})),
        "completion_unit": _get_text(props.get("이번 Sprint 완료 단위", {})),
        "end_check": _get_text(props.get("종료 시 확인 결과", {})),
        "url": props.get("페이지 URL", {}).get("url", ""),
    }


def get_tasks(sprint_id: str) -> list[dict]:
    results = []
    cursor = None
    while True:
        kwargs: dict = {
            "database_id": config.PROJECT_DB_ID,
            "filter": {"property": "Sprint", "relation": {"contains": sprint_id}},
        }
        if cursor:
            kwargs["start_cursor"] = cursor
        res = _client.databases.query(**kwargs)
        results.extend(res.get("results", []))
        if not res.get("has_more"):
            break
        cursor = res["next_cursor"]

    tasks = []
    for page in results:
        props = page["properties"]
        status_prop = props.get("상태 요약") or props.get("상태") or {}
        project_prop = props.get("프로젝트") or props.get("Application") or {}
        tasks.append({
            "name": _get_text(props.get("이름", {}), "title"),
            "status": _get_select(status_prop),
            "project": _get_select(project_prop),
            "days": props.get("예상 일수", {}).get("number"),
        })
    return tasks
