import enum
from datetime import date
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date
from sqlalchemy.orm import relationship
from ..db_setup import Base
from .devices import Device


class InterventionType(enum.Enum):
    PREVENTIVE = "préventive"
    CURATIVE = "curative"


class InterventionStatus(enum.Enum):
    PENDING = "en attente"
    IN_PROGRESS = "en cours"
    COMPLETED = "terminé"
    POSTPONED = "reporté"
    CANCELED = "annulé"


class FailureStatus(enum.Enum):
    RESOLVED = "résolu"
    UNRESOLVED = "non résolu"


class Intervention(Base):
    __tablename__ = "intervention"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_serial_number = Column(
        Integer, ForeignKey("device.serial_number"), nullable=False
    )
    type = Column(
        Enum(InterventionType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    date = Column(Date, default=date.today, nullable=False)
    note = Column(String, nullable=True)
    status = Column(
        Enum(InterventionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    estimated_duration = Column(String, nullable=True)

    device = relationship(Device, back_populates="interventions")
    failures = relationship(
        "Failure", back_populates="intervention", cascade="all, delete-orphan"
    )


class Failure(Base):
    __tablename__ = "failure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(Integer, ForeignKey("intervention.id"), nullable=False)
    failure_type = Column(String, nullable=False)
    status = Column(
        Enum(FailureStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    intervention = relationship("Intervention", back_populates="failures")
