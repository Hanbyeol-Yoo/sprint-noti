import requests
import config
import notion_api as nc
import message_builder as mb


def send_slack(text: str) -> None:
    resp = requests.post(config.SLACK_WEBHOOK_URL, json={"text": text}, timeout=10)
    resp.raise_for_status()


def main() -> None:
    current_sprint = nc.get_sprint("현재")
    if not current_sprint:
        send_slack(mb.build_error_message())
        return

    last_sprint = nc.get_sprint("마지막")
    current_tasks = nc.get_tasks(current_sprint["id"])
    last_tasks = nc.get_tasks(last_sprint["id"]) if last_sprint else []

    message = mb.build_message(current_sprint, last_sprint, current_tasks, last_tasks)
    send_slack(message)


if __name__ == "__main__":
    main()
