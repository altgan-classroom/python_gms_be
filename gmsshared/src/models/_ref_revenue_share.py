from typing import Optional, List, Self
from datetime import datetime

from sqlalchemy import (
    DateTime, Column, Integer, String, Float, Boolean, SmallInteger, JSON
)
from sqlalchemy.sql import func

from gmsshared import db


class _RefRevenueShare(db.Model):
    __tablename__ = "_ref_revenue_share"
    id = Column(Integer, primary_key=True)
    model_id = Column(SmallInteger, nullable=False)
    name = Column(String(60), nullable=False)
    lower = Column(Float, nullable=True)
    upper = Column(Float, nullable=True)
    environment = Column(String(5), nullable=False)
    payrix_group_id = Column(String(50), nullable=False)
    payrix_fee_ids = Column(JSON, nullable=True)
    revenue_share_fee = Column(Float, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Self]:
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, id: int) -> Optional[Self]:
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_bounds(cls, lower: float, upper: float, environment: str) -> Optional[Self]:
        return cls.query.filter_by(_RefRevenueShare.lower >= lower, _RefRevenueShare.upper <= upper,
                    _RefRevenueShare.environment.lower() == environment.lower(), _RefRevenueShare.active == True).first()

    @classmethod
    def find_by_model(cls, model_id: int, environment: str) -> Optional[Self]:
        return cls.query.filter_by(model_id=model_id, environment=environment)

    @classmethod
    def get_all(cls, env: str) -> Optional[List[Self]]:
        return cls.query.filter(_RefRevenueShare.environment == env, _RefRevenueShare.active == True).order_by(_RefRevenueShare.lower.desc()).all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
