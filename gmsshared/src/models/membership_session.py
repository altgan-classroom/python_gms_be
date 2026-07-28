from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (
    DateTime, Column, Integer, String, Boolean, ForeignKey, Float, BigInteger, text, Date
)

from gmsshared import db
from gmsshared.src.models.user import User
from gmsshared.src.models.location import Location
from gmsshared.src.models.member_profile import MemberProfile
from gmsshared.src.models.plan import Plan
from gmsshared.src.util.enums import RoleEnum
from gmsshared.src.models.membership import Membership


class MembershipSession(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    membership_id = Column(BigInteger, ForeignKey("membership.id"), nullable=False)
    sessions_count = Column(Integer, nullable=True)
    price_per_session = Column(Float, nullable=True)
    sessions_purchase_date = Column(Date, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    notes = Column(String(250), nullable=True)
    total_amount = Column(Float, nullable=True)

    membership = db.relationship(Membership, backref="sessions")

    def __init__(self, location_id:int, user_id: int, membership_id: int, ):
        self.location_id = location_id
        self.user_id = user_id
        self.membership_id = membership_id

    @classmethod
    def find_by_id(cls, location_id: int, member_id: int, membership_id: int, id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=member_id, membership_id=membership_id, id=id).first()

    @classmethod
    def get_sessions_detail_by_id(cls, location_id: int, member_id: int, membership_id: int) -> Optional[Self]:
        sql = (f"""
            select {location_id} as location_id, {member_id} as user_id, {membership_id} as membership_id, 
                ifnull(sum(sessions_count), 0) as sessions_bought, 
                (select ifnull(sessions_count, 0) from membership mp where mp.location_id = {location_id} 
                             and mp.user_id = {member_id} and mp.id = {membership_id}) 
                as sessions_remaining 
            from membership_session mps 
            where mps.location_id = {location_id} and mps.user_id = {member_id} 
               and mps.membership_id = {membership_id}
        """)
        result = db.session.execute(text(sql))
        results_as_dict = result.mappings().first()
        return results_as_dict


    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
