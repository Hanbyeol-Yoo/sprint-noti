import config

MAX_TASKS = 10

_EMPTY_TEXT = "미작성"
_NO_TASKS = "없습니다."


def _t(value: str) -> str:
    return value if value else _EMPTY_TEXT


def _format_task(task: dict) -> str:
    name = task["name"] or _EMPTY_TEXT
    project = task["project"] or "프로젝트 미지정"
    assignee = task["assignee"] or "담당자 미지정"
    period = task["period"] or "기간 미설정"
    status = task["status"] or "상태 미지정"
    return f"- {name} | {project} | {assignee} | {period} | {status}"


def _format_task_list(tasks: list[dict]) -> str:
    if not tasks:
        return f"- {_NO_TASKS}"
    lines = [_format_task(t) for t in tasks[:MAX_TASKS]]
    remaining = len(tasks) - MAX_TASKS
    if remaining > 0:
        lines.append(f"- 외 {remaining}건은 Sprint 페이지에서 확인해 주세요.")
    return "\n".join(lines)


def _build_warnings(
    current_sprint: dict,
    current_tasks: list[dict],
    last_sprint: dict | None,
    last_tasks: list[dict],
) -> list[str]:
    warnings = []
    if not current_sprint.get("sprint_question"):
        warnings.append("이번 Sprint 계획(Sprint Question)이 비어 있습니다.")
    if not current_tasks:
        warnings.append("이번 Sprint에 연결된 작업이 없습니다. 작업을 추가해 주세요.")
    if any(not t["period"] for t in current_tasks):
        warnings.append("이번 Sprint 작업 중 작업 기간이 비어 있는 항목이 있습니다.")
    if last_sprint and any(t["status"] in ("시작 전", "진행 중") for t in last_tasks):
        warnings.append("지난 Sprint에서 이어지는 작업의 상태를 확인해 주세요.")
    if last_sprint and last_tasks and not any(t["status"] == "완료" for t in last_tasks):
        warnings.append("지난 Sprint 완료 작업이 없습니다. 상태 업데이트가 누락되었는지 확인해 주세요.")
    return warnings


def build_message(
    current_sprint: dict,
    last_sprint: dict | None,
    current_tasks: list[dict],
    last_tasks: list[dict],
) -> str:
    lines = []

    sprint_name = current_sprint["name"] or "Sprint"
    lines += [
        f"🚀 {sprint_name}이 시작되었습니다.",
        f"기간: {_t(current_sprint['period'])}",
        "",
        "🧭 이번 Sprint 계획",
        _t(current_sprint.get("sprint_question", "")),
        "",
        "🗂 이번 Sprint 작업",
        _format_task_list(current_tasks),
        "",
    ]

    if last_sprint:
        last_name = last_sprint["name"] or "지난 Sprint"
        completed = [t for t in last_tasks if t["status"] == "완료"]
        in_progress = [t for t in last_tasks if t["status"] == "진행 중"]
        not_started = [t for t in last_tasks if t["status"] == "시작 전"]
        carryover = in_progress + not_started

        lines += [
            f"📊 지난 {last_name} 결과",
            f"- 완료: {len(completed)}건",
            f"- 진행 중: {len(in_progress)}건",
            f"- 시작 전: {len(not_started)}건",
            "",
            "📌 지난 Sprint에서 이어지는 작업",
            _format_task_list(carryover),
            "",
            "✅ 지난 Sprint 완료 작업",
            _format_task_list(completed),
            "",
        ]
    else:
        lines += [
            "📊 지난 Sprint 결과",
            "- 지난 Sprint를 찾을 수 없습니다.",
            "",
        ]

    warnings = _build_warnings(current_sprint, current_tasks, last_sprint, last_tasks)
    lines.append("⚠️ 확인 필요")
    lines += [f"- {w}" for w in warnings] if warnings else ["- 없습니다."]
    lines += ["", "🔗 Sprint 페이지", config.SPRINT_PAGE_URL]

    return "\n".join(lines)


def build_error_message() -> str:
    return (
        "⚠️ Sprint 시작 알림을 생성하지 못했습니다.\n"
        "사유: 현재 Sprint를 찾을 수 없습니다.\n\n"
        "확인 필요:\n"
        "- Sprint DB에 `스프린트 상태 = 현재`인 페이지가 있는지 확인해 주세요.\n"
        "- 또는 이번 주 기간이 설정되어 있는지 확인해 주세요."
    )
