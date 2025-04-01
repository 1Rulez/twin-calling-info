from sqlalchemy import String, Boolean, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CalNumbers(Base):
    __tablename__ = "call_numbers"

    id: Mapped[str] = mapped_column(Integer, autoincrement=True, primary_key=True)
    phone: Mapped[str] = mapped_column(String(30), unique=True)
    time_start: Mapped[Time] = mapped_column(Time)
    time_end: Mapped[Time] = mapped_column(Time)
    is_active: Mapped[bool] = mapped_column(Boolean)
