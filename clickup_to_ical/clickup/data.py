import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List as tList, Any, Union, Dict


def _to_int(value: str) -> Optional[int]:
    if value is None:
        return None
    return int(value)


@dataclass(frozen=True)
class Member:
    id: int
    username: str
    email: str
    color: str
    profilePicture: Optional[str]
    initials: str
    role: int
    custom_role: Optional[str]
    last_active: str
    date_joined: str
    date_invited: str

    def __str__(self):
        return f"{self.__class__.__name__}-{self.username} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "Member":
        return cls(
            id=_to_int(json_data.get("id")),
            username=json_data.get("username"),
            email=json_data.get("email"),
            color=json_data.get("color"),
            profilePicture=json_data.get("profilePicture"),
            initials=json_data.get("initials"),
            role=_to_int(json_data.get("role")),
            custom_role=json_data.get("custom_role"),
            last_active=json_data.get("last_active"),
            date_joined=json_data.get("date_joined"),
            date_invited=json_data.get("date_invited"),
        )


@dataclass(frozen=True)
class Team:
    id: int
    name: str
    color: str
    avatar: Optional[str]
    members: tList[Member]

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "Team":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            color=json_data["color"],
            avatar=json_data["avatar"],
            members=[Member.from_json(x["user"]) for x in json_data["members"]]
        )

    def get_members(self) -> tList[Member]:
        return self.members


@dataclass(frozen=True)
class Space:
    id: int
    name: str
    private: bool
    avatar: Optional[str]
    team: Team

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict, team: Team) -> "Space":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            private=json_data["private"],
            avatar=json_data["avatar"],
            team=team
        )

    def get_members(self) -> tList[Member]:
        return self.team.get_members()


@dataclass(frozen=True)
class Folder:
    id: int
    name: str
    space: Space

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict, space: Space) -> "Folder":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            space=space,
        )

    def get_members(self) -> tList[Member]:
        return self.space.get_members()


@dataclass(frozen=True)
class List:
    id: int
    name: str
    content: str
    task_count: Optional[int]
    origin: Union[Folder, Space]

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict, origin: Union[Folder, Space]) -> "List":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            content=json_data.get("content", ""),
            task_count=json_data["task_count"],
            origin=origin,
        )

    def get_members(self) -> tList[Member]:
        return self.origin.get_members()


@dataclass(frozen=True)
class CustomField:
    id: str
    name: str
    type: str
    type_config: dict
    value: Optional[Any]

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "CustomField":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            type=json_data["type"],
            type_config=json_data["type_config"],
            value=json_data.get("value", None)
        )


# @dataclass(frozen=True) # TODO: Find better way to have frozen dataclass and be able to have parents as Task type
@dataclass
class Task:
    id: str
    name: str
    date_created: Optional[int]
    date_updated: Optional[int]
    due_date: Optional[int]
    start_date: Optional[int]
    custom_fields: tList[CustomField]
    markdown_description: Optional[str]
    lst: List
    assignees: tList[int]
    creator: Optional[int]
    priority: int
    url: str
    parent: Union[None, str, "Task"]
    status: dict

    def get_assignees(self) -> tList[Member]:
        return [x for x in self.get_members() if x.id in self.assignees]

    def get_all_dates(self) -> Dict[str, datetime]:
        ret = {}
        if self.due_date is not None:
            ret["Due Date"] = datetime.fromtimestamp(float(self.due_date) / 1000, tz=timezone.utc)
        if self.start_date is not None:
            ret["Start Date"] = datetime.fromtimestamp(float(self.start_date) / 1000, tz=timezone.utc)
        for custom_field in self.custom_fields:
            if custom_field.type == "date" and custom_field.value is not None:
                ret[f"__{custom_field.name}"] = datetime.fromtimestamp(float(custom_field.value) / 1000,
                                                                       tz=timezone.utc)
        return ret

    def get_members(self) -> tList[Member]:
        return self.lst.get_members()

    def __str__(self):
        return f"{self.__class__.__name__}-{self.get_name()} ({self.id})"

    def get_name(self) -> str:
        if self.parent is None:
            return self.name
        return (f"{self.parent.get_name() if isinstance(self.parent, Task) else self.parent} "
                f"{os.environ.get('SUBTASK_CONNECTION_SYMBOL', '📥')} "
                f"{self.name}")

    def update(self, other_tasks: tList["Task"]):
        if isinstance(self.parent, str):
            for t in other_tasks:
                if t.id == self.parent:
                    self.parent = t

    def is_open(self) -> bool:
        return not self.status.get("type", "open").lower() == "closed"

    @classmethod
    def from_json(cls, json_data: dict, lst: List) -> "Task":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            date_created=_to_int(json_data["date_created"]),
            date_updated=_to_int(json_data["date_updated"]),
            due_date=_to_int(json_data["due_date"]),
            start_date=_to_int(json_data["start_date"]),
            custom_fields=[CustomField.from_json(x) for x in json_data["custom_fields"]],
            markdown_description=json_data["markdown_description"],
            lst=lst,
            assignees=[int(x["id"]) for x in json_data["assignees"]],
            creator=json_data.get("creator", {}).get("id", None),
            priority=json_data["priority"].get("id", None) if json_data["priority"] is not None else None,
            url=json_data["url"],
            parent=json_data.get("parent", None),
            status=json_data.get("status", {})
        )
