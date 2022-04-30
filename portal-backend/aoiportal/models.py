from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Boolean, ForeignKey, UniqueConstraint, Date, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
import bcrypt

Base = declarative_base()
db = SQLAlchemy(model_class=Base)

GroupsUsers = Table(
    "groups_users", Base.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("group_id", ForeignKey("group.id")),
    UniqueConstraint("user_id", "group_id")
)


class User(UserMixin, Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    is_admin = Column(Boolean, nullable=False, default=False)
    email_confirmed = Column(Boolean, nullable=False, default=False)
    last_email_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    last_password_change_at = Column(DateTime(timezone=True), nullable=True)

    birthday = Column(Date)
    phone_nr = Column(String)
    address_street = Column(String)
    address_zip = Column(String)
    address_town = Column(String)
    school_name = Column(String)
    school_address = Column(String)

    cms_id = Column(Integer, nullable=True)
    cms_username = Column(String, nullable=True)

    email_verification_codes = relationship("UserEmailVerificationCode", back_populates="user")
    password_reset_codes = relationship("UserPasswordResetCode", back_populates="user")
    participations = relationship("Participation", back_populates="user")
    groups = relationship("Group", secondary=GroupsUsers, back_populates="users")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode(), 
            bcrypt.gensalt()
        )
    
    def clear_password(self) -> None:
        self.password_hash = None

    @property
    def has_password(self) -> bool:
        return self.password_hash is None

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode(),
            self.password_hash
        )

    @property
    def is_active(self) -> bool:
        # Overrides is_active from UserMixin for Flask-Login
        return self.email_confirmed


class UserEmailVerificationCode(Base):
    __tablename__ = "user_email_verification_code"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    email = Column(String, nullable=False)
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="email_verification_codes")


class UserPasswordResetCode(Base):
    __tablename__ = "user_password_reset_code"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="password_reset_codes")


class OAuth(OAuthConsumerMixin, Base):
    __tablename__ = "oauth"
    __table_args__ = (UniqueConstraint("provider", "provider_user_id"),)
    provider_user_id = Column(String(256), nullable=False)
    provider_user_login = Column(String(256), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    user = relationship(
        User,
        # This `backref` thing sets up an `oauth` property on the User model,
        # which is a dictionary of OAuth models associated with that user,
        # where the dictionary key is the OAuth provider name.
        backref=backref(
            "oauth",
            collection_class=attribute_mapped_collection("provider"),
            cascade="all, delete-orphan",
        ),
    )


class Contest(Base):
    __tablename__ = "contest"
    id = Column(Integer, primary_key=True)
    cms_id = Column(Integer, nullable=False)
    cms_name = Column(String, nullable=False)
    cms_description = Column(String, nullable=False)
    # cms_start_time = Column(DateTime(timezone=True), nullable=False)
    # cms_end_time = Column(DateTime(timezone=True), nullable=False)
    # cms_analysis_enabled = Column(Boolean, nullable=False)
    # cms_analysis_start_time = Column(DateTime(timezone=True), nullable=False)
    # cms_analysis_end_time = Column(DateTime(timezone=True), nullable=False)

    public = Column(Boolean, default=False, nullable=False)
    auto_add_to_group_id = Column(Integer, ForeignKey("group.id"), nullable=True)

    participations = relationship("Participation", back_populates="contest")
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
