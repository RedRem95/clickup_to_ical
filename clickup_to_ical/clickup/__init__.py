import os
import logging
from typing import List as tList

from requests import Response
from requests_ratelimiter import LimiterSession

from .data import Member, Team, Space, List, Folder, Task

_SESSION = LimiterSession(per_minute=int(os.environ.get("CLICKUP_RATE", 100)))

try:
    os.environ["CLICKUP_API_KEY"]
except KeyError:
    logging.exception("CLICKUP_API_KEY not set. Please set CLICKUP_API_KEY in environment variables.")
    exit(1)


def _get_url(url: str, params=None) -> Response:
    return _SESSION.get(url, headers={"Authorization": os.environ["CLICKUP_API_KEY"]}, params=params)


def get_teams() -> tList[Team]:
    response = _get_url("https://api.clickup.com/api/v2/team")
    return [Team.from_json(x) for x in response.json()["teams"]]


def get_spaces(team: int) -> tList[Space]:
    response = _get_url(f"https://api.clickup.com/api/v2/team/{team}/space", params={"archived": "false"})
    return [Space.from_json(x) for x in response.json()["spaces"]]


def get_folders(space: int) -> tList[Folder]:
    response = _get_url(f"https://api.clickup.com/api/v2/space/{space}/folder", params={"archived": "false"})
    return [Folder.from_json(x) for x in response.json()["folders"]]


def get_lists_folder(folder: int) -> tList[List]:
    response = _get_url(f"https://api.clickup.com/api/v2/folder/{folder}/list", params={"archived": "false"})
    return [List.from_json(x) for x in response.json()["lists"]]


def get_lists_space(space: int) -> tList[List]:
    response = _get_url(f"https://api.clickup.com/api/v2/space/{space}/list", params={"archived": "false"})
    return [List.from_json(x) for x in response.json()["lists"]]


def get_tasks(lst: int, with_subtasks: bool = False, with_closed: bool = False) -> tList[Task]:
    tasks: tList[Task] = []
    page: int = 0
    while True:
        params = {
            "archived": "false",
            "include_markdown_description": "true",
            "page": page,
        }
        if with_subtasks:
            params["subtasks"] = "true"
        if with_closed:
            params["include_closed"] = "true"
        response = _get_url(f"https://api.clickup.com/api/v2/list/{lst}/task", params=params)
        d = response.json()
        tasks.extend([Task.from_json(x) for x in d["tasks"]])
        if d["last_page"]:
            break
        page += 1
    return tasks


__all__ = [
    "get_teams", "get_spaces", "get_folders", "get_lists_folder", "get_lists_space",
    "Member", "Team", "Space", "List", "Folder", "Task"
]
