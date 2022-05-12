# type: ignore
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()
db = SQLAlchemy(model_class=Base)

GroupsUsers = Table(
    "groups_users",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("group_id", ForeignKey("group.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    is_admin = Column(Boolean, nullable=False, default=False)

    birthday = Column(Date)
    phone_nr = Column(String)
    address_street = Column(String)
    address_zip = Column(String)
    address_town = Column(String)
    school_name = Column(String)
    school_address = Column(String)

    cms_id = Column(Integer, nullable=True)
    cms_username = Column(String, nullable=True)

    participations = relationship(
        "Participation", back_populates="user", cascade="all, delete"
    )
    groups = relationship("Group", secondary=GroupsUsers, back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete")
    email_change_requests = relationship(
        "UserEmailChangeRequest", back_populates="user", cascade="all, delete"
    )
    password_reset_requests = relationship(
        "UserPasswordResetRequest", back_populates="user", cascade="all, delete"
    )
    github_oauths = relationship(
        "UserGitHubOAuth", back_populates="user", cascade="all, delete"
    )
    google_oauths = relationship(
        "UserGoogleOAuth", back_populates="user", cascade="all, delete"
    )


class UserSession(Base):
    __tablename__ = "user_session"

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship(User, back_populates="sessions")


class UserRegisterRequest(Base):
    __tablename__ = "user_register_request"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
    verification_code = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False)
    valid = Column(Boolean, nullable=False)


class UserEmailChangeRequest(Base):
    __tablename__ = "user_email_change_request"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, back_populates="email_change_requests")
    new_email = Column(String, nullable=False)
    verification_code = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False)
    valid = Column(Boolean, nullable=False)


class UserPasswordResetRequest(Base):
    __tablename__ = "user_password_reset_request"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, back_populates="password_reset_requests")
    verification_code = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False)
    valid = Column(Boolean, nullable=False)


class UserGitHubOAuth(Base):
    __tablename__ = "user_github_oauth"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    access_token = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, back_populates="github_oauths")
    extra_data = Column(String, nullable=False)


class UserGoogleOAuth(Base):
    __tablename__ = "user_google_oauth"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    access_token = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, back_populates="google_oauths")
    extra_data = Column(String, nullable=False)


class Contest(Base):
    __tablename__ = "contest"
    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, unique=True, index=True)

    cms_id = Column(Integer, nullable=False)
    cms_name = Column(String, nullable=False)
    cms_description = Column(String, nullable=False)
    cms_allow_sso_authentication = Column(Boolean, nullable=False, default=False)
    cms_sso_secret_key = Column(String, nullable=False, default="")
    cms_sso_redirect_url = Column(String, nullable=False, default="")

    url = Column(String, nullable=False, default="")

    # cms_start_time = Column(DateTime, nullable=False)
    # cms_end_time = Column(DateTime, nullable=False)
    # cms_analysis_enabled = Column(Boolean, nullable=False)
    # cms_analysis_start_time = Column(DateTime, nullable=False)
    # cms_analysis_end_time = Column(DateTime, nullable=False)

    order_priority = Column(Float, nullable=False, default=0)
    open_signup = Column(Boolean, default=False, nullable=False)
    quali_round = Column(Boolean, default=False, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    auto_add_to_group_id = Column(Integer, ForeignKey("group.id"), nullable=True)
    deleted = Column(Boolean, default=False, nullable=False)

    name = Column(String, nullable=False)
    teaser = Column(String, nullable=False)
    description = Column(String, nullable=False)

    participations = relationship(
        "Participation", back_populates="contest", cascade="all, delete"
    )
    auto_add_to_group = relationship("Group")


class Participation(Base):
    __tablename__ = "participation"
    id = Column(Integer, primary_key=True)
    cms_id = Column(Integer, nullable=False)
    contest_id = Column(Integer, ForeignKey("contest.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    manual_password = Column(String, nullable=True)

    user = relationship("User", back_populates="participations")
    contest = relationship("Contest", back_populates="participations")


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)

    users = relationship("User", secondary=GroupsUsers, back_populates="groups")
