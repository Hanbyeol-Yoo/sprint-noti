import config
from notion_client import Client

client = Client(auth=config.NOTION_TOKEN)


def print_db_schema(db_id: str, label: str):
    db = client.databases.retrieve(database_id=db_id)
    print(f"\n=== {label} ===")
    for name, prop in db["properties"].items():
        print(f"  [{prop['type']:20s}] {name}")


def print_sprint_page_sample():
    res = client.databases.query(
        database_id=config.SPRINT_DB_ID,
        filter={"property": "스프린트 상태", "status": {"equals": "현재"}},
    )
    pages = res.get("results", [])
    if not pages:
        print("\n현재 Sprint 없음")
        return
    page = pages[0]
    print(f"\n=== Sprint 페이지 샘플 (page url) ===")
    print(f"  page['url'] = {page['url']}")
    print(f"  page['id']  = {page['id']}")
    print("\n  속성 값:")
    for name, prop in page["properties"].items():
        print(f"  [{prop['type']:20s}] {name}")


print_db_schema(config.SPRINT_DB_ID, "Sprint DB 속성")
print_db_schema(config.PROJECT_DB_ID, "Project Management DB 속성")
print_sprint_page_sample()
