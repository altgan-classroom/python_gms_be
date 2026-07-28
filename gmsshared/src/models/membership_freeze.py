from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (
    DateTime, Column, Integer, Boolean, ForeignKey, Float, BigInteger, text, Date, func
)

from gmsshared import db
from gmsshared.src.models.user import User
from gmsshared.src.models.location import Location
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.plan import Plan
from gmsshared.src.util.enums import RoleEnum
from gmsshared.src.models._ref_freeze_reason_type import _RefFreezeReasonType


class MembershipFreeze(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    membership_id = Column(BigInteger, ForeignKey("membership.id"), nullable=False)
    freeze_from = Column(Date, nullable=True)
    freeze_to = Column(Date, nullable=True)
    freeze_date = Column(Date, nullable=True)
    freeze_reason_type_id = Column(Integer, ForeignKey(_RefFreezeReasonType.id), nullable=True)
    freeze_by = Column(BigInteger, nullable=True)
    unfreeze_date = Column(Date, nullable=True)
    unfreeze_by = Column(BigInteger, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, location_id:int, user_id: int, membership_id: int):
        self.location_id = location_id
        self.user_id = user_id
        self.membership_id = membership_id

    @classmethod
    def find_by_id(cls, location_id: int, member_id: int, membership_id: int, id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id, membership_id=membership_id, id=id).first()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
