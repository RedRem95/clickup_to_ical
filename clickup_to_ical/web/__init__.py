import os
from datetime import timedelta
from logging import getLogger
import threading

from flask import Flask, request, Response
from clickup_to_ical import __version__
from clickup_to_ical.web.utils import ThreadingDict
from clickup_to_ical.host import TRUE_VALUES
from clickup_to_ical.web.stores import tasks, auth, default_event_length

_LOGGER = getLogger("clickup_to_ical")
app = Flask("clickup_to_ical")


@app.route("/api/1.0/calendar", methods=["GET"])
def get_calendar():
    import uuid
    from ical.calendar import Calendar
    from ical.event import Event
    from ical.types import CalAddress
    from ical.calendar_stream import IcsCalendarStream
    from datetime import datetime
    auth_key = request.headers.get("Authorization", request.args.get("token", None))
    if not auth_key:
        _LOGGER.info("Authorization token \"token\" missing from query arguments")
        _LOGGER.info("Authorization header \"Authorization\" missing from header")
        return "Unauthorized: No auth key provided in header", 401
    clickup_user_id = auth.get(auth_key, None)
    if clickup_user_id is None:
        _LOGGER.info("Authorization in header not set in auth file")
        return "Unauthorized: Key not recognized", 401
    _LOGGER.info(f"requested calendar: {request.args} for user: {clickup_user_id}")

    date_types = request.args.get("date_types", None)
    if date_types is None:
        def date_type_filter(_dt_name) -> bool:
            return True
    else:
        allowed_date_types = [x.strip().lower() for x in date_types.split(",")]

        def date_type_filter(_dt_name) -> bool:
            return _dt_name.lower() in allowed_date_types

    if request.args.get("only_assigned", "true").lower() in TRUE_VALUES:
        assigned_tasks = tasks[clickup_user_id]
    else:
        assigned_tasks = tasks[None]

    calendar = Calendar()
    calendar.prodid = f'-//CLICKUP-TO-ICAL-CONVERTER//github.com/RedRem95/clickup_to_ical//{__version__}//'
    calendar.version = '2.0'

    for task in assigned_tasks:
        members = {x.id: x for x in task.get_members()}
        for dt_name, dt in ((x, y) for x, y in task.get_all_dates().items() if date_type_filter(_dt_name=x)):
            real_name = dt_name[2 if dt_name.startswith('__') else 0:]
            event = Event(
                uid=str(uuid.uuid3(uuid.NAMESPACE_X500, f"{task.id}-{dt_name}")),
                dtstamp=datetime.utcfromtimestamp(float(task.date_created) / 1000),
                url=task.url,
                summary=f"{task.name} - {real_name}",
                dtstart=dt,
                dtend=dt + timedelta(seconds=default_event_length.get(real_name, 0)),
            )
            if task.priority is not None:
                event.priority = task.priority
            if task.markdown_description is not None and len(task.markdown_description) > 0:
                from markdown import markdown
                from bs4 import BeautifulSoup
                desc = BeautifulSoup(markdown(task.markdown_description), features='html.parser').get_text()
                event.description = desc

            if task.creator in members and members[task.creator].email:
                event.organizer = CalAddress(
                    uri=f"mailto:{members[task.creator].email}",
                    common_name=members[task.creator].username
                )

            for assignee in task.get_assignees():
                event.attendees.append(CalAddress(
                    uri=f"mailto:{assignee.email}",
                    common_name=assignee.username
                ))

            calendar.events.append(event)

    return Response(IcsCalendarStream.calendar_to_ics(calendar), mimetype="text/calendar", status=200)
