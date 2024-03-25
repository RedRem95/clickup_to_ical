import os
import logging
from typing import List as tList, Union

from requests import Response
from requests_ratelimiter import LimiterSession

from .data import Member, Team, Space, List, Folder, Task

_SESSION = LimiterSession(per_minute=int(os.environ.get("CLICKUP_RATE_LIMIT", 50)))

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


def get_spaces(team: Team) -> tList[Space]:
    response = _get_url(f"https://api.clickup.com/api/v2/team/{team.id}/space", params={"archived": "false"})
    return [Space.from_json(x, team=team) for x in response.json()["spaces"]]


def get_folders(space: Space) -> tList[Folder]:
    response = _get_url(f"https://api.clickup.com/api/v2/space/{space.id}/folder", params={"archived": "false"})
    return [Folder.from_json(x, space=space) for x in response.json()["folders"]]


def get_lists(origin: Union[Folder, Space]) -> tList[List]:
    if isinstance(origin, Folder):
        response = _get_url(f"https://api.clickup.com/api/v2/folder/{origin.id}/list", params={"archived": "false"})
    elif isinstance(origin, Space):
        response = _get_url(f"https://api.clickup.com/api/v2/space/{origin.id}/list", params={"archived": "false"})
    else:
        raise TypeError(f"Unsupported origin type {type(origin)}")
    return [List.from_json(x, origin=origin) for x in response.json()["lists"]]


def get_tasks(lst: List, with_subtasks: bool = False, with_closed: bool = False) -> tList[Task]:
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
        response = _get_url(f"https://api.clickup.com/api/v2/list/{lst.id}/task", params=params)
        d = response.json()
        tasks.extend([Task.from_json(x, lst=lst) for x in d["tasks"]])
        if d["last_page"]:
            break
        page += 1
    return tasks


def get_tasks_all(with_subtasks: bool = False, with_closed: bool = False) -> tList[Task]:
    from itertools import chain
    teams = get_teams()
    spaces = list(chain(*[get_spaces(team=x) for x in teams]))
    folders = list(chain(*[get_folders(space=x) for x in spaces]))
    lists = list(chain(*[get_lists(origin=x) for x in spaces + folders]))
    return list(chain(*[get_tasks(lst=x, with_subtasks=with_subtasks, with_closed=with_closed) for x in lists]))


__all__ = [
    "get_teams", "get_spaces", "get_folders", "get_lists", "get_lists", "get_tasks", "get_tasks_all",
    "Member", "Team", "Space", "List", "Folder", "Task"
]
