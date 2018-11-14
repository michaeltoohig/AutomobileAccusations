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


class Vehicle(Base):
    # Own properties
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow(), index=True)
    plate = Column(String, nullable=False, unique=True)
