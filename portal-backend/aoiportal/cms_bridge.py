from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
import datetime
from flask import current_app
import requests


@dataclass
class BridgeContest:
    id: int
    name: str
    description: str
    # start_time: datetime.datetime
    # end_time: datetime.datetime
    # analysis_enabled: bool
    # analysis_start_time: datetime.datetime
    # analysis_end_time: datetime.datetime

"""
@dataclass
class BridgeUser:
    id: int
    username: str
    email: str


@dataclass
class BridgeParticipation:
    id: int
    user_id: int
    contest_id: int
    # hidden: bool
"""

@dataclass
class CreateUserResult:
    cms_id: int
    cms_username: str


class CMSBridge(ABC):
    @abstractmethod
    def list_contests(self) -> List[BridgeContest]:
        ...

    @abstractmethod
    def create_user(self, *, email: str, first_name: str, last_name: str) -> CreateUserResult:
        ...

    @abstractmethod
    def create_participation(self, *, user_id: int, contest_id: int, manual_password: Optional[str] = None) -> int:
        ...

    @abstractmethod
    def set_participation_password(self, *, contest_id: int, participation_id: int, manual_password: Optional[str]) -> None:
        ...


class FakeCMSBridge(CMSBridge):
    def list_contests(self) -> List[BridgeContest]:
        print("LIST CONTESTS")
        return [BridgeContest(
            id=1,
            name="1-Qualifikation",
            description="1. Qualifikation 2022",
        )]
    
    def create_user(self, *, email: str, first_name: str, last_name: str) -> CreateUserResult:
        print(f"CREATE USER {email=} {first_name=} {last_name=}")
        username = f"{first_name} {last_name}".lower().replace(" ", "-")
        return CreateUserResult(
            1, username
        )

    def create_participation(self, *, user_id: int, contest_id: int, manual_password: Optional[str] = None) -> int:
        print(f"CREATE PARTICIPATION {user_id=} {contest_id=} {manual_password=}")
        return 1

    def set_participation_password(self, *, contest_id: int, participation_id: int, manual_password: Optional[str]) -> None:
        print(f"SET PARTICIPATION PASSWORD {contest_id=} {participation_id=} {manual_password=}")


class RealCMSBridge(CMSBridge):
    def get_base_url(self) -> str:
        return current_app.config["CMSBRIDGE_BASE_URL"]

    def list_contests(self) -> List[BridgeContest]:
        resp = requests.get(f"{self.get_base_url()}/list-contests")
        resp.raise_for_status()
        return [
            BridgeContest(
                id=v["id"],
                name=v["name"],
                description=v["description"],
            )
            for v in resp.json()
        ]
    
    def create_user(self, *, email: str, first_name: str, last_name: str) -> CreateUserResult:
        resp = requests.post(f"{self.get_base_url()}/create-user", json={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        })
        resp.raise_for_status()
        js = resp.json()
        return CreateUserResult(
            cms_id=js["user_id"],
            cms_username=js["username"],
        )

    def create_participation(self, *, user_id: int, contest_id: int, manual_password: Optional[str] = None) -> int:
        resp = requests.post(f"{self.get_base_url()}/create-participation", json={
            "user_id": user_id,
            "contest_id": contest_id,
            "manual_password": manual_password,
        })
        resp.raise_for_status()
        return resp.json()["participation_id"]

    def set_participation_password(self, *, contest_id: int, participation_id: int, manual_password: Optional[str]) -> None:
        resp = requests.post(f"{self.get_base_url()}/set-participation-password", json={
            "participation_id": participation_id,
            "contest_id": contest_id,
            "manual_password": manual_password,
        })
        resp.raise_for_status()


cms = FakeCMSBridge()
