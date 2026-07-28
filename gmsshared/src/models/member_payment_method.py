from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (
    DateTime, Column, ForeignKey, BigInteger, Boolean, text, Integer, String, desc
)
from sqlalchemy.sql import func

from gmsshared import db
from gmsshared.src.util.enums import PayrixOnboardStatusEnum
from gmsshared.src.models.member_profile import MemberProfile


class MemberPaymentMethod(db.Model):
    id = Column(BigInteger, nullable=False, primary_key=True)
    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("member_profile.user_id"), nullable=False)
    name = Column(String(50), nullable=True)
    method = Column(Integer, nullable=True)
    last_4_digits_card = Column(String(5), nullable = True)
    last_4_digits_account = Column(String(5), nullable=True)
    last_4_digits_routing = Column(String(5), nullable=True)
    expiration = Column(String(8), nullable=True)
    token = Column(String(50), nullable=True)
    inactive = Column(Boolean, nullable=True, default=True)
    default_method = Column(Boolean, nullable=True, default=False)
    payrix_token_id = Column(String(50), nullable=True)
    payrix_onboarding_status = Column(Integer, nullable=True, server_default='1')
    payrix_onboarding_error = Column(String(100), nullable=True)
    zipcode = Column(String(10), nullable=True)
    payrix_zipcode_onboarding_status = Column(Integer, nullable=True)

    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    member = db.relationship(MemberProfile, backref="payment_methods")

    def __init__(self, location_id: int, member_id: int):
        self.location_id = location_id
        self.user_id = member_id

    @classmethod
    def find_by_member_id2(cls, location_id: int, member_id: int, default_method: bool = False) -> Optional[Self]:
        if default_method:
            return cls.query.filter(MemberPaymentMethod.location_id==location_id,
                                    MemberPaymentMethod.user_id==member_id,
                                    MemberPaymentMethod.default_method==True,
                                    MemberPaymentMethod.inactive==False,
                                    MemberPaymentMethod.token!=None).first()
        else:
            return cls.query.filter_by(location_id=location_id, user_id=member_id).all()

    @classmethod
    def find_by_member_id(cls, location_id: int, member_id: int, default_method: bool = False) -> Optional[Self]:
        where_clause = f"where mpm.location_id = {location_id} and mpm.user_id = {member_id} and mpm.token is not null \
                            and mpm.payrix_onboarding_error is null and mpm.inactive = false"
        sql = (f"select mpm.id, mpm.expiration, mpm.token, mpm.inactive, mpm.default_method, \
                 mpm.last_4_digits_account, mpm.last_4_digits_routing, mpm.last_4_digits_card, location_id, user_id, \
                 mpm.method, mpm.payrix_token_id, mpm.payrix_onboarding_status, mpm.payrix_onboarding_error \
             from member_payment_method mpm {where_clause}")
        result = db.session.execute(text(sql))
        return result.mappings().all()

    @classmethod
    def find_by_id(cls, location_id: int, user_id: int, pm_id: int) -> Optional[Self]:
        return cls.query.filter_by(location_id=location_id, user_id=user_id, id=pm_id).first()

    def save_as_default(self):
        try:
            stmt1 = (f"update member_payment_method set default_method=false \
                    where location_id={self.location_id} and user_id={self.user_id};")
            db.session.execute(text(stmt1))
            stmt2 = (f"update member_payment_method set default_method=true \
                    where location_id={self.location_id} and user_id={self.user_id} and id={self.id};")
            db.session.execute(text(stmt2))
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
