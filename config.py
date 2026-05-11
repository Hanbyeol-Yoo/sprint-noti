import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN: str = os.environ["NOTION_TOKEN"]
SPRINT_DB_ID: str = os.environ["SPRINT_DB_ID"]
PROJECT_DB_ID: str = os.environ["PROJECT_DB_ID"]
SLACK_WEBHOOK_URL: str = os.environ["SLACK_WEBHOOK_URL"]
