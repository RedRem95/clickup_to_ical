from datetime import timedelta
from logging import getLogger

import pytz
from flask import Flask, request, Response

from clickup_to_ical import __version__
from clickup_to_ical.host import TRUE_VALUES
from clickup_to_ical.web.stores import tasks, auth, default_event_length
from clickup_to_ical.web.utils import ThreadingDict

_LOGGER = getLogger("clickup_to_ical")
app = Flask(f"clickup_to_ical-{__version__}")
_LOGGER.info(f"Creating flask app for clickup_to_ical-{__version__}")


@app.route("/api/1.0/calendar", methods=["GET"])
def get_calendar():
    import uuid
    from clickup_to_ical.ical import Calendar, Event, User
    from datetime import datetime
    request_from = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    auth_key = request.headers.get("Authorization", request.args.get("token", None))
    if not auth_key:
        _LOGGER.info("Authorization token \"token\" missing from query arguments")
        _LOGGER.info("Authorization header \"Authorization\" missing from header")
        return "Unauthorized: No auth key provided in header", 401
    clickup_user_id = auth.get(auth_key, None)
    if clickup_user_id is None:
        _LOGGER.info("Authorization in header not set in auth file")
        return "Unauthorized: Key not recognized", 401

    log = {"user id": clickup_user_id}

    date_types = request.args.get("date_types", None)
    if date_types is None:
        log["event types"] = "all"

        def date_type_filter(_dt_name) -> bool:
            return True
    else:
        allowed_date_types = [x.strip().lower() for x in date_types.split(",")]
        log["event types"] = "[" + ", ".join(f"\"{x}\"" for x in allowed_date_types) + "]"

        def date_type_filter(_dt_name) -> bool:
            return _dt_name.lower() in allowed_date_types

    if request.args.get("only_assigned", "true").lower() in TRUE_VALUES:
        log["assignees"] = clickup_user_id
        assigned_tasks = tasks.get(clickup_user_id, [])
    else:
        log["assignees"] = "all"
        assigned_tasks = tasks.get(None, [])

    include_closed = request.args.get("include_closed", "false") in TRUE_VALUES
    log["closed included"] = include_closed

    _LOGGER.info(f"Request from {request_from}: <{'; '.join(f'{x}: {y}' for x, y in log.items())}>")
    calendar = Calendar(
        version='2.0',
        prodid=f'-//CLICKUP-TO-ICAL-CONVERTER//github.com/RedRem95/clickup_to_ical//{__version__}//',
        calendar_name="ClickupToIcal Calendar",
        calendar_description="ClickupToIcal Calendar\n{}".format("\n".join(f"{x}: {y}" for x, y in log.items())),
    )

    for task in (x for x in assigned_tasks if (include_closed or x.is_open())):
        members = {x.id: x for x in task.get_members()}
        if task.markdown_description is not None and len(task.markdown_description) > 0:
            from markdown import markdown
            from bs4 import BeautifulSoup
            desc = BeautifulSoup(markdown(task.markdown_description), features='html.parser').get_text()
            task_description = desc
        else:
            task_description = None

        if task.creator in members and members[task.creator].email:
            task_organizer = User(
                uri=f"mailto:{members[task.creator].email}",
                name=members[task.creator].username
            )
        else:
            task_organizer = None

        task_attendees = []
        for assignee in task.get_assignees():
            task_attendees.append(User(
                uri=f"mailto:{assignee.email}",
                name=assignee.username
            ))

        for dt_name, dt in ((x, y) for x, y in task.get_all_dates().items() if date_type_filter(_dt_name=x)):
            real_name = dt_name[2 if dt_name.startswith('__') else 0:]
            event = Event(
                uid=str(uuid.uuid3(uuid.NAMESPACE_X500, f"{task.id}-{dt_name}")),
                dtstamp=datetime.fromtimestamp(float(task.date_created) / 1000, tz=pytz.UTC),
                url=task.url,
                summary=f"{task.get_name()} - {real_name}",
                dtstart=dt,
                dtend=dt + timedelta(seconds=default_event_length.get(real_name, 0)),
                priority=task.priority,
                organizer=task_organizer,
                attendees=task_attendees,
                description=task_description,
            )
            calendar.events.append(event)

    return Response(str(calendar), mimetype="text/calendar", status=200)
