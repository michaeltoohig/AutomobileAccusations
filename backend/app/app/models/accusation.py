# -*- coding: utf-8 -*-

# Import standard library packages
from datetime import datetime

# Import installed packages
from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

# Import app code
from app.db.base_class import Base

# Typings, for autocompletion (VS Code with Python plug-in)
from typing import List  # noqa


class Accusation(Base):
    """ Accusation Model for storing accusation details """
    # Own properties
    id = Column(Integer, primary_key=True, autoincrement=True)
    public_id = Column(String(100), unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    comment = Column(String(160))
    occured_at = Column(DateTime, nullable=False)
    # Relationships
    vehicle_id = Column(Integer, ForeignKey('vehicle.id'), nullable=False)
    vehicle = relationship('Vehicle', backref='accusations')
    acc_type_id = Column(Integer, ForeignKey('accusationtype.id'), nullable=False)
    acc_type = relationship('AccusationType', back_populates='accusations')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='accusations')

    def __repr__(self):
        return "<Accusation '{}'>".format(self.id)


class AccusationType(Base):
    """ AccusationType Model for storing types of accusations details """
    # Own properties
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    desc = Column(String(120), nullable=False, index=True)
    # Relationships
    accusations = relationship('Accusation', back_populates='acc_type')

    def __repr__(self):
        return "<AccusationType '{}'>".format(self.name)