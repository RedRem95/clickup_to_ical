import os
from logging import getLogger

from clickup_to_ical.host import TRUE_VALUES
from clickup_to_ical.web.utils import ThreadingDict


_LOGGER = getLogger("clickup_to_ical")


def _update_auth():
    import json
    if "AUTH_FILE" in os.environ:
        with open(os.environ["AUTH_FILE"], "r") as f_in:
            _LOGGER.info("Read new auth file")
            return json.load(f_in)
    return None


auth = ThreadingDict(auto_update=(_update_auth, 60 * 5))


def _update_default_length():
    import json
    if "DEFAULT_LENGTH" in os.environ:
        with open(os.environ["DEFAULT_LENGTH"], "r") as f_in:
            _LOGGER.info("Read new default length for events file")
            return json.load(f_in)
    else:
        return {}


default_event_length = ThreadingDict(auto_update=(_update_default_length, 60 * 5))


def _update_tasks():
    from clickup_to_ical.clickup import get_tasks_all
    from collections import defaultdict
    _LOGGER.info("Updating tasks")
    _tasks = get_tasks_all(
        with_closed=os.environ.get("TASKS_CLOSED", "") in TRUE_VALUES,
        with_subtasks=os.environ.get("TASKS_SUBTASKS", "") in TRUE_VALUES,
    )
    _LOGGER.info(f"Found {len(_tasks)} tasks")
    d = defaultdict(list)
    for _task in _tasks:
        d[None].append(_task)
        for _assignee in _task.assignees:
            d[_assignee].append(_task)
    return {k: tuple(v) for k, v in d.items()}


tasks = ThreadingDict(auto_update=(_update_tasks, int(os.environ.get("CLICKUP_CALL_RATE", 60 * 15))))
