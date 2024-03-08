from typing import Optional, List as tList, Any
from dataclasses import dataclass


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
        return cls(**json_data)


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


@dataclass(frozen=True)
class Space:
    id: int
    name: str
    private: bool
    avatar: Optional[str]

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "Space":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            private=json_data["private"],
            avatar=json_data["avatar"]
        )


@dataclass(frozen=True)
class Folder:
    id: int
    name: str

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "Folder":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
        )


@dataclass(frozen=True)
class List:
    id: int
    name: str
    content: str
    task_count: Optional[int]

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "List":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            content=json_data.get("content", ""),
            task_count=json_data["task_count"]
        )


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


@dataclass(frozen=True)
class Task:
    id: str
    name: str
    date_created: Optional[int]
    date_updated: Optional[int]
    due_date: Optional[int]
    start_date: Optional[int]
    custom_fields: tList[CustomField]
    markdown_description: Optional[str]

    def __str__(self):
        return f"{self.__class__.__name__}-{self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_data: dict) -> "Task":
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            date_created=_to_int(json_data["date_created"]),
            date_updated=_to_int(json_data["date_updated"]),
            due_date=_to_int(json_data["due_date"]),
            start_date=_to_int(json_data["start_date"]),
            custom_fields=[CustomField.from_json(x) for x in json_data["custom_fields"]],
            markdown_description=json_data["markdown_description"],
        )
