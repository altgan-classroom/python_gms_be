from datetime import datetime, date
from typing import Optional, Self, List, Tuple
from sqlalchemy import or_
from sqlalchemy import (
    DateTime, Column, ForeignKey, BigInteger, SmallInteger, Boolean, text, and_, String
)
from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from sqlalchemy import or_, select
from gmsshared import db
from gmsshared.src.models.membership import Membership
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.location import Location
from gmsshared.src.models.session import Class
from gmsshared.src.models.user import User
from gmsshared.src.models.user_profile import UserProfile

class MemberOpenGym(db.Model):
    __tablename__ = "member_opengym"
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    class_id = Column(BigInteger, nullable=True)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    membership_id = Column(BigInteger, ForeignKey("membership.id"), nullable=True)
    class_time = Column(DateTime, nullable=True)
    member_registered_time = Column(DateTime, nullable=False, server_default=func.now())
    member_waitlist = Column(SmallInteger, nullable=True, server_default='0')
    member_cancelled_time = Column(DateTime, nullable=True)
    member_checked_in_time = Column(DateTime, nullable=True)
    cancel_rebook_email_time = Column(DateTime, nullable=True)
    cancel_reason = Column(String(200), nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    member = db.relationship(MemberProfile, backref="open_gym")
    membership = db.relationship(Membership, backref="open_gym")
    location = db.relationship(Location)

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
