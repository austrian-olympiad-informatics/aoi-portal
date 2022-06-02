from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from flask import current_app


@dataclass
class Contest:
    id: int
    name: str
    description: str
    allow_sso_authentication: bool
    sso_secret_key: str
    sso_redirect_url: str
    allow_frontendv2: bool
    # start_time: datetime.datetime
    # end_time: datetime.datetime
    # analysis_enabled: bool
    # analysis_start_time: datetime.datetime
    # analysis_end_time: datetime.datetime


@dataclass
class ContestUpdateParams:
    name: str
    description: str
    allow_sso_authentication: bool
    sso_secret_key: str
    sso_redirect_url: str


@dataclass
class RankingUser:
    user_id: int
    task_scores: Dict[str, float]
    total_score: float


@dataclass
class RankingResult:
    tasks: List[str]
    ranking: List[RankingUser]


@dataclass
class CreateUserResult:
    cms_id: int
    cms_username: str


class CMSBridge(ABC):
    @abstractmethod
    def list_contests(self) -> List[Contest]:
        ...

    @abstractmethod
    def get_contest_ranking(self, *, contest_id: int) -> RankingResult:
        ...

    @abstractmethod
    def get_contest(self, *, contest_id: int) -> Contest:
        ...

    @abstractmethod
    def update_contest(self, *, contest_id: int, params: ContestUpdateParams) -> None:
        ...

    @abstractmethod
    def create_user(
        self, *, email: str, first_name: str, last_name: str
    ) -> CreateUserResult:
        ...

    @abstractmethod
    def create_participation(
        self, *, user_id: int, contest_id: int, manual_password: Optional[str] = None
    ) -> int:
        ...

    @abstractmethod
    def set_participation_password(
        self, *, contest_id: int, participation_id: int, manual_password: Optional[str]
    ) -> None:
        ...


class FakeCMSBridge(CMSBridge):
    def list_contests(self) -> List[Contest]:
        print("LIST CONTESTS")
        return [
            Contest(
                id=1,
                name="1-Qualifikation",
                description="1. Qualifikation 2022",
                allow_sso_authentication=True,
                sso_secret_key="xzt43HsCkhXBC+nRW7J3sRj9vNpa7Q7pu2VEBLey9Uw=",
                sso_redirect_url="http://localhost:8888/sso/authorized",
                allow_frontendv2=True,
            )
        ]

    def get_contest(self, *, contest_id: int) -> Contest:
        print(f"GET CONTEST {contest_id=}")
        return Contest(
            id=1,
            name="1-Qualifikation",
            description="1. Qualifikation 2022",
            allow_sso_authentication=True,
            sso_secret_key="xzt43HsCkhXBC+nRW7J3sRj9vNpa7Q7pu2VEBLey9Uw=",
            sso_redirect_url="http://localhost:8888/sso/authorized",
            allow_frontendv2=True,
        )

    def update_contest(self, *, contest_id: int, params: ContestUpdateParams) -> None:
        print(f"UPDATE CONTEST {contest_id=} {params=}")

    def create_user(
        self, *, email: str, first_name: str, last_name: str
    ) -> CreateUserResult:
        print(f"CREATE USER {email=} {first_name=} {last_name=}")
        username = f"{first_name} {last_name}".lower().replace(" ", "-")
        return CreateUserResult(1, username)

    def create_participation(
        self, *, user_id: int, contest_id: int, manual_password: Optional[str] = None
    ) -> int:
        print(f"CREATE PARTICIPATION {user_id=} {contest_id=} {manual_password=}")
        return 1

    def set_participation_password(
        self, *, contest_id: int, participation_id: int, manual_password: Optional[str]
    ) -> None:
        print(
            f"SET PARTICIPATION PASSWORD {contest_id=} {participation_id=} {manual_password=}"
        )

    def get_contest_ranking(self, *, contest_id: int) -> RankingResult:
        print(f"GET CONTEST RANKING {contest_id=}")
        return RankingResult(
            tasks=["ZEN", "CACHES", "RUNDREISE"],
            ranking=[
                RankingUser(
                    user_id=1,
                    task_scores={"ZEN": 0, "CACHES": 10, "RUNDREISE": 20},
                    total_score=30,
                )
            ],
        )


class RealCMSBridge(CMSBridge):
    def get_base_url(self) -> str:
        return current_app.config["CMSBRIDGE_BASE_URL"]

    def list_contests(self) -> List[Contest]:
        resp = requests.get(f"{self.get_base_url()}/list-contests")
        resp.raise_for_status()
        return [
            Contest(
                id=v["id"],
                name=v["name"],
                description=v["description"],
                allow_sso_authentication=v["allow_sso_authentication"],
                sso_secret_key=v["sso_secret_key"],
                sso_redirect_url=v["sso_redirect_url"],
                allow_frontendv2=v["allow_frontendv2"],
            )
            for v in resp.json()
        ]

    def get_contest(self, *, contest_id: int) -> Contest:
        resp = requests.get(f"{self.get_base_url()}/contests/{contest_id}")
        resp.raise_for_status()
        v = resp.json()
        return Contest(
            id=v["id"],
            name=v["name"],
            description=v["description"],
            allow_sso_authentication=v["allow_sso_authentication"],
            sso_secret_key=v["sso_secret_key"],
            sso_redirect_url=v["sso_redirect_url"],
            allow_frontendv2=v["allow_frontendv2"],
        )

    def update_contest(self, *, contest_id: int, params: ContestUpdateParams) -> None:
        resp = requests.post(
            f"{self.get_base_url()}/update-contest",
            json={
                "contest_id": contest_id,
                "name": params.name,
                "description": params.description,
                "allow_sso_authentication": params.allow_sso_authentication,
                "sso_secret_key": params.sso_secret_key,
                "sso_redirect_url": params.sso_redirect_url,
            },
        )
        resp.raise_for_status()

    def create_user(
        self, *, email: str, first_name: str, last_name: str
    ) -> CreateUserResult:
        resp = requests.post(
            f"{self.get_base_url()}/create-user",
            json={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        resp.raise_for_status()
        js = resp.json()
        return CreateUserResult(
            cms_id=js["user_id"],
            cms_username=js["username"],
        )

    def create_participation(
        self, *, user_id: int, contest_id: int, manual_password: Optional[str] = None
    ) -> int:
        resp = requests.post(
            f"{self.get_base_url()}/create-participation",
            json={
                "user_id": user_id,
                "contest_id": contest_id,
                "manual_password": manual_password,
            },
        )
        resp.raise_for_status()
        return resp.json()["participation_id"]

    def set_participation_password(
        self, *, contest_id: int, participation_id: int, manual_password: Optional[str]
    ) -> None:
        resp = requests.post(
            f"{self.get_base_url()}/set-participation-password",
            json={
                "participation_id": participation_id,
                "contest_id": contest_id,
                "manual_password": manual_password,
            },
        )
        resp.raise_for_status()

    def get_contest_ranking(self, *, contest_id: int) -> RankingResult:
        resp = requests.get(f"{self.get_base_url()}/get-contest-ranking/{contest_id}")
        resp.raise_for_status()
        js = resp.json()
        return RankingResult(
            tasks=js["tasks"],
            ranking=[
                RankingUser(
                    user_id=r["user_id"],
                    task_scores=r["task_scores"],
                    total_score=r["total_score"],
                )
                for r in js["ranking"]
            ],
        )


cms = RealCMSBridge()
