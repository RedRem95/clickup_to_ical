from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

import pytz


def _datetime_to_str(dt_name: str, dt: datetime) -> str:
    base = f"{dt.year:04d}{dt.month:02d}{dt.day:02d}T{dt.hour:02d}{dt.minute:02d}{dt.second:02d}"
    if dt.tzinfo is None:
        return f"{dt_name}:{base}"
    elif dt.tzinfo in (pytz.UTC, timezone.utc, pytz.timezone("UTC")):
        return f"{dt_name}:{base}Z"
    else:
        return f"{dt_name};TZID={dt.tzinfo};VALUE=DATE:{base}"


@dataclass(frozen=True)
class User:
    uri: str
    name: str = None

    def __str__(self, user_type: str = "ATTENDEE"):
        return f"{user_type}{'' if self.name is None else f';CN={self.name}'}:{self.uri}"


@dataclass(frozen=True)
class Event:
    uid: str
    dtstamp: datetime
    dtstart: datetime
    dtend: datetime = None
    created: datetime = None
    last_modified: datetime = None
    url: str = None
    location: str = None
    summary: str = None
    description: str = None
    sequence: int = None
    transp: str = None
    status: str = None
    priority: int = None
    organizer: User = None
    attendees: List[User] = field(default_factory=list)

    def __str__(self):
        ret = [
            f"UID:{self.uid}",
            _datetime_to_str("DTSTAMP", self.dtstamp),
            _datetime_to_str("DTSTART", self.dtstart)
        ]

        if self.dtend is not None:
            ret.append(_datetime_to_str("DTEND", self.dtend))
        if self.created is not None:
            ret.append(_datetime_to_str("CREATED", self.created))
        if self.last_modified is not None:
            ret.append(_datetime_to_str("LAST-MODIFIED", self.created))
        if self.url is not None:
            ret.append(f"URL:{self.url}")
        if self.location is not None:
            ret.append(f"LOCATION:{self.location}")
        if self.summary is not None:
            ret.append(f"SUMMARY:{self.summary}")
        if self.description is not None:
            ret.append(f"DESCRIPTION:{self.description}")
        if self.sequence is not None:
            ret.append(f"SEQUENCE:{self.sequence}")
        if self.transp is not None:
            ret.append(f"TRANSP:{self.transp}")
        if self.status is not None:
            ret.append(f"STATUS:{self.status}")
        if self.priority is not None:
            ret.append(f"PRIORITY:{self.priority}")
        if self.organizer is not None:
            ret.append(self.organizer.__str__(user_type="ORGANIZER"))
        ret.extend(x.__str__(user_type="ATTENDEE") for x in self.attendees)

        return "BEGIN:VEVENT\n{}\nEND:VEVENT".format("\n".join(ret))
