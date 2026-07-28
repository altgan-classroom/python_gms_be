from datetime import datetime
from typing import Optional, Self

from sqlalchemy import (
    DateTime, Date, Column, Integer, String, ForeignKey, BigInteger, Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from gmsshared import db
from gmsshared.src.models._ref_gender_type import _RefGenderType
from gmsshared.src.models._ref_relationship_type import _RefRelationshipType
from gmsshared.src.models._ref_relationship_status_type import _RefRelationshipStatusType
from gmsshared.src.models._ref_shirt_size_type import _RefShirtSizeType
from gmsshared.src.models._ref_shirt_fit_type import _RefShirtFitType


class UserProfile(db.Model):
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    middle_name = Column(String(50), nullable=True)
    preferred_name = Column(String(50), nullable=True)
    photo_url = Column(String(255), nullable=True)
    birth_date = Column(Date, nullable=True)
    address_street = Column(String(255), nullable=True)
    address_street_2 = Column(String(100), nullable=True)
    address_city = Column(String(255), nullable=True)
    address_state = Column(String(20), nullable=True)
    address_zip = Column(String(10), nullable=True)
    address_country = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)
    emergency_first_name = Column(String(50), nullable=True)
    emergency_last_name = Column(String(50), nullable=True)
    emergency_phone_number = Column(String(50), nullable=True)
    guardian_first_name = Column(String(50), nullable=True)
    guardian_last_name = Column(String(50), nullable=True)
    guardian_phone_number = Column(String(50), nullable=True)
    gender_type_id = Column(Integer, nullable=True)
    emergency_relationship_type_id = Column(Integer, nullable=True)
    relationship_status_type_id = Column(Integer, ForeignKey('_ref_relationship_status_type.id'), nullable=True)
    have_children = Column(Boolean, nullable=True)
    shirt_size_type_id = Column(Integer, ForeignKey('_ref_shirt_size_type.id'), nullable=True)
    shirt_fit_type_id = Column(Integer, ForeignKey('_ref_shirt_fit_type.id'), nullable=True)
    about = Column(String(280), nullable=True)
    start_date = Column(DateTime, nullable=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)
    accepted_terms_conditions_datetime = Column(type_=DateTime, nullable=True)
    accepted_privacy_policy_datetime = Column(type_=DateTime, nullable=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), primary_key=True, nullable=False)
    user = relationship("User", back_populates="user_profile")

    @classmethod
    def find_by_user_id(cls, user_id: int) -> Optional[Self]:
        return cls.query.filter_by(user_id=user_id).first()

    def __init__(self, first_name: str, last_name: str,
                 accepted_terms_conditions_privacy_policy_datetime: datetime | None = None):
        self.first_name = first_name
        self.last_name = last_name
        self.accepted_terms_conditions_datetime = accepted_terms_conditions_privacy_policy_datetime
        self.accepted_privacy_policy_datetime = accepted_terms_conditions_privacy_policy_datetime

    def save(self):
        db.session.add(self)

    def save_and_commit(self):
        self.save()
        db.session.commit()
