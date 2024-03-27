from dataclasses import dataclass, field
from datetime import timedelta
from typing import List

import pytz

from clickup_to_ical.ical.event import Event


def _time_to_duration(td: timedelta) -> str:
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    h = f"{f'{hours:02d}H' if hours > 0 else ''}"
    m = f"{f'{minutes:02d}M' if minutes > 0 else ''}"
    s = f"{f'{seconds:02d}S' if seconds > 0 else ''}"

    return f"P{days if days > 0 else ''}T{h}{m}{s}"


@dataclass(frozen=True)
class Calendar:
    version: str
    prodid: str
    method: str = None
    calscale: str = None
    calendar_name: str = None
    calendar_description: str = None
    calendar_timezone = None
    calendar_ttl: timedelta = None
    events: List[Event] = field(default_factory=list)

    def __str__(self):
        ret = [
            f"VERSION:{self.version}",
            f"PRODID:{self.prodid}",
        ]
        if self.method is not None:
            ret.append(f"METHOD:{self.method}")
        if self.calscale is not None:
            ret.append(f"CALSCALE:{self.calscale}")
            ret.append(f"X-MICROSOFT-CALSCALE:{self.calscale}")
        if self.calendar_name is not None:
            ret.append(f"X-WR-CALNAME:{self.calendar_name}")
        if self.calendar_description is not None:
            ret.append(f"X-WR-CALDESC:{self.calendar_description}")
        if self.calendar_timezone is not None and self.calendar_timezone != pytz.UTC:
            ret.append(f"X-WR-TIMEZONE:{str(self.calendar_timezone)}")
        if self.calendar_ttl is not None:
            ret.append(f"X-PUBLISHED-TTL:{_time_to_duration(self.calendar_ttl)}")

        ret.extend(str(event) for event in self.events)

        return "BEGIN:VCALENDAR\n{}\nEND:VCALENDAR".format('\n'.join(ret))
