from sqlalchemy import Column, ForeignKey, Integer, Boolean, String, Float, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from ..db_setup import Base
from datetime import datetime, date
from enum import Enum as PyEnum  

class SoftwareVersionEnum(str, PyEnum):
    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"
    V2_0 = "2.0"


class DeviceTypeEnum(str, PyEnum):
    CEINTURE_INTELLIGENTE = "ceinture intelligente"
    CEINTURE_VIBRANTE = "ceinture vibrante"
    CEINTURE_NORMAL = "ceinture normal"
    BRACELET_INTELLIGENT = "bracelet intelligent"
    BRACELET_VIBRANT = "bracelet vibrant"
    BRACELET_NORMAL = "bracelet normal"
    LUNETTES_INTELLIGENTES = "lunettes intelligentes"
    LUNETTES_LIDAR = "lunettes lidar"
    LUNETTES_NORMAL = "lunettes normal"
    CASQUE_AUDIO_INTELLIGENT = "casque audio intelligent"
    CASQUE_AUDIO_NORMAL = "casque normal"


class InitialStateEnum(str, PyEnum):
    NEUF = "neuf"
    RECONDITIONNE = "reconditionné"
    DEFECTUEUX = "défectueux"

class OperationalStatusEnum(str, PyEnum):
    EN_SERVICE = "en service"
    EN_VEILLE = "en veille"
    EN_MAINTENANCE = "en maintenance"


class UserStatusEnum(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class DeviceStatusEnum(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AlertTypeEnum(str, PyEnum):
    BATTERY_LOW = "battery low"
    CONNECTION_LOST = "connection lost"
    COMPONENT_ERROR = "component error"
    COMPONENT_OUT_OF_ORDER  = "component out of order"
    EN_MAINTENANCE = "en maintenance"
    SYSTEM_OVERLOAD = "system overload"
    MEMORY_OVERLOAD = "memory overload"
    HIGH_TEMPERATURE = "high temperature"

# Device Model
class Device(Base):
    __tablename__ = "device"
    serial_number = Column(Integer, primary_key=True)
    type = Column(Enum(DeviceTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    software_version = Column(Enum(SoftwareVersionEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    image = Column(String, nullable=False) 
    initial_state = Column(Enum(InitialStateEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    mac_address = Column(String, unique=True, nullable=False)
    operational_status = Column(Enum(OperationalStatusEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(Enum(DeviceStatusEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    battery_level = Column(Integer, nullable=False)
    creation_date = Column(Date, nullable=False)
    user_id= Column(Integer,nullable=True)
    # Relationships

    positions = relationship("Position", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    components = relationship("Component", back_populates="device", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="device", cascade="all, delete-orphan")





# Position Model
class Position(Base):
    __tablename__ = "position"
    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(Integer, ForeignKey("device.serial_number"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    occupation_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    position_name = Column(String, nullable=True)
    device = relationship("Device", back_populates="positions")
    
# Alert Model
class Alert(Base):
    __tablename__ = "alert"
    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(Integer, ForeignKey("device.serial_number"), nullable=False)
    message = Column(String, nullable=False)
    type = Column(Enum(AlertTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    device = relationship("Device", back_populates="alerts")

class ComponentStatusEnum(str, PyEnum):
    OK = "ok"
    EN_PANNE = "en panne"
    ERREUR = "erreur"

# Component Model
class Component(Base):
    __tablename__ = "component"
    
    id = Column(Integer, primary_key=True, index=True)
    device_serial_number = Column(Integer, ForeignKey("device.serial_number"), nullable=False)
    type = Column(String, nullable=False) 
    status = Column(Enum(ComponentStatusEnum, values_callable=lambda x: [e.value for e in x]), nullable=False, default=ComponentStatusEnum.OK.value)

    device = relationship("Device", back_populates="components")
