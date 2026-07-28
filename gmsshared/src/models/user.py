from base64 import b32encode
from datetime import datetime, timedelta, timezone
from typing import Optional, Self, NoReturn, Tuple, Any

import jwt
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import (
    Boolean, DateTime, Column, Integer, String, ForeignKey, text, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gmsshared.src.util.enums import RoleEnum
from gmsshared.src.util.result import Result
from gmsshared.src.config import get_config
from gmsshared import db, bcrypt
from gmsshared.src.models._ref_role_type import _RefRoleType
from gmsshared.src.models.user_profile import UserProfile
#from gmsshared.src.models.location import Location

# A user can belong to one or more locations
user_location = db.Table("user_location",
                         Column("user_id", BigInteger, ForeignKey("user.id"), primary_key=True),
                         Column("location_id", BigInteger, ForeignKey("location.id"), primary_key=True))


class User(db.Model):
    id = Column(BigInteger, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    active = Column(Boolean(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    verified = Column(Boolean(), nullable=False, default=False)
    verified_on = Column(type_=DateTime, nullable=True)
    deactivated_on = Column(type_=DateTime, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    # A user can have one role
    role_type_id = Column(Integer, ForeignKey('_ref_role_type.id'), nullable=False)
    role = relationship("_RefRoleType")

    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    locations = relationship("Location", secondary=user_location, backref="users")

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    @property
    def password(self) -> NoReturn:
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password: str) -> None:
        log_rounds = get_config().BCRYPT_LOG_ROUNDS
        hash_bytes = bcrypt.generate_password_hash(password, log_rounds)
        self.password_hash = hash_bytes.decode("utf-8")

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Self]:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_email2(cls, email: str) -> Optional[Self]:
        sql = f"""select u.id from user u  
                       where lower(rtrim(ltrim(u.email))) = '{email.lower().strip()}'"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().first()
        return results_as_dict

    @classmethod
    def find_by_first_and_last(cls, first: str, last: str) -> Optional[Self]:
        sql = f"""select u.id from user u left join user_profile up on u.id = up.user_id 
                  where lower(rtrim(ltrim(up.first_name))) = '{first.lower().strip()}' 
                       and lower(rtrim(ltrim(up.last_name))) = '{last.lower().strip()}'"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().first()
        return results_as_dict

    @classmethod
    def find_by_id(cls, _id: int) -> Optional[Self]:
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_location_and_user(cls, user_id: int, location_id: int) -> Optional[Self]:
        return cls.query.filter(cls.id == user_id, cls.locations.any(id=location_id)).first()

    @classmethod
    def find_by_location(cls, location_id: int, active_only: bool = True) -> Optional[Self]:
        active_query = ""
        if active_only:
            active_query = "and u.deactivated_on IS NULL"
        sql = f"""select u.id as user_id, 
                    p.first_name,
                    p.last_name, 
                    rt.name as staff_member_role, 
                    u.verified_on,
                    p.phone_number, 
                    u.email,
                    u.active,
                    u.create_datetime,
                    p.start_date
                 from user_location ul
                    left join user u on u.id = ul.user_id
                    left join user_profile p on u.id = p.user_id
                    left join _ref_role_type rt on rt.id = u.role_type_id 
                 where ul.location_id = {location_id} 
                 and u.role_type_id <> {RoleEnum.MEMBER.value} and u.role_type_id <> {RoleEnum.KIOSK.value}
                 {active_query}
                 """
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def find_by_location_and_role(cls, location_id: int, roles: Tuple[int]) -> Optional[Self]:
        sql = f"""select u.id as user_id, 
                    p.first_name,
                    p.last_name, 
                    rt.name as staff_member_role, 
                    u.verified_on,
                    p.phone_number, 
                    u.email,
                    u.active,
                    u.create_datetime,
                    p.start_date,
                    p.photo_url
                 from user_location ul
                    left join user u on u.id = ul.user_id
                    left join user_profile p on u.id = p.user_id
                    left join _ref_role_type rt on rt.id = u.role_type_id
                 where ul.location_id = {location_id} and u.role_type_id in {roles}"""
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().all()
        return results_as_dict

    @classmethod
    def get_staff_profile_info_by_id(cls, user_id: int, location_id) -> Optional[Self]:
        sql = f"""select u.id as user_id, 
                    ul.location_id as location_id, 
                    p.first_name as first_name, 
                    p.last_name as last_name,
                    u.email,
                    p.phone_number, 
                    p.birth_date as birth_date, 
                    u.verified_on as verified_on,
                    u.active,
                    p.start_date,
                    p.photo_url
                from user_location ul
                    left join user u  on u.id = ul.user_id
                    left join user_profile p on u.id = p.user_id
                where u.id = {user_id} 
                    and ul.location_id = {location_id}"""
        result = db.session.execute(text(sql))
        result_mapping = result.mappings().first()
        if result_mapping:
            results_as_dict = {}
            for key, value in result_mapping.items():
                results_as_dict[key] = value
            return results_as_dict

    @classmethod
    def find_all_coaches(cls) -> Optional[Self]:
        return cls.query.filter_by(role_id=RoleEnum.COACH.value).all()

    @classmethod
    def find_owner_by_gym(cls, gym_id: int) -> Optional[Self]:
        user_id = db.session.execute(text(f"select u.id from user u \
                                                left join user_location ul on u.id = ul.user_id \
                                                   and u.role_type_id = {RoleEnum.OWNER.value} \
                                                left join location l on l.id = ul.location_id \
                                            where l.gym_id = {gym_id}")).first()[0]
        return cls.query.filter_by(id=user_id).first()

    @staticmethod
    def generate_access_token(user: "User", impersonator_id: Optional[int] = None) -> str:
        now = datetime.now(timezone.utc)
        token_age_h = user.role.access_token_timeout_hrs
        #token_age_h = get_config().JWT_TOKEN_EXPIRE_HOURS
        access_expire = now + timedelta(minutes=token_age_h*60)
        payload = dict(exp=access_expire, iat=now, sub=user.id, impersonator=impersonator_id, type="access_token")
        key = get_config().SECRET_KEY
        return jwt.encode(payload, key, algorithm="HS256")

    @staticmethod
    def generate_refresh_token(user: "User") -> str:
        now = datetime.now(timezone.utc)
        token_age_d = user.role.refresh_token_timeout_days
        # token_age_d = get_config().REFRESH_TOKEN_EXPIRE_DAYS
        refresh_expire = now + timedelta(minutes=token_age_d*24*60)
        payload = dict(exp=refresh_expire, iat=now, sub=user.id, impersonator=None, type="refresh_token")
        key = get_config().SECRET_KEY
        return jwt.encode(payload, key, algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> Any:
        if isinstance(token, bytes):
            token = token.decode("ascii")
        if token.startswith("Bearer "):
            split = token.split("Bearer")
            token = split[1].strip()
        try:
            key = get_config().SECRET_KEY
            payload = jwt.decode(token, key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            error = "Access token expired. Please log in again."
            return Result.Fail(error), None
        except jwt.InvalidTokenError:
            error = "Invalid token. Please log in again."
            return Result.Fail(error), None
        token_type = payload["type"] if "type" in payload else None
        user_dict = dict(user_id=payload["sub"], token=token, expires_at=payload["exp"],
                         impersonator_id=payload["impersonator"], type=token_type)
        return Result.Ok(user_dict), user_dict

    @staticmethod
    def generate_verification_code(email: str) -> str:
        from pyotp import TOTP
        salted_secret = get_config().SECRET_KEY + email
        otp_secret = b32encode(bytearray(salted_secret, 'ascii')).decode('utf-8')
        # interval will verify any code generated in the previous 900 s = 15 min
        timed_otp = TOTP(otp_secret, interval=1800, digits=4, name=email, issuer="gymowners.com")
        return timed_otp.now()

    @staticmethod
    def validate_verification_code(code: str, email: str) -> bool:
        from pyotp import TOTP
        salted_secret = get_config().SECRET_KEY + email
        otp_secret = b32encode(bytearray(salted_secret, 'ascii')).decode('utf-8')
        # interval will verify any code generated in the previous 900 s = 15 min
        timed_otp = TOTP(otp_secret, interval=1800, digits=4, name=email, issuer="gymowners.com")
        return timed_otp.verify(code)

    @staticmethod
    def generate_verification_token(email: str) -> str:
        serializer = URLSafeTimedSerializer(get_config().SECRET_KEY)
        return serializer.dumps(email, salt=get_config().CONFIRM_TOKEN_SALT)

    @staticmethod
    def validate_verification_token(token: str, is_profile_setup=False) -> str:
        if is_profile_setup:
            max_age = get_config().PROFILE_SETUP_TOKEN_EXPIRE_SECS
        else:
            max_age = get_config().CONFIRM_TOKEN_EXPIRE_SECS
        serializer = URLSafeTimedSerializer(get_config().SECRET_KEY)
        email = serializer.loads(token, salt=get_config().CONFIRM_TOKEN_SALT,
                                 max_age=max_age)
        return email

    def check_password(self, password: str):
        return bcrypt.check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
