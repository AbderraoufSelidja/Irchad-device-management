from pydantic import BaseModel
from datetime import date as Date
from typing import Optional, List
from db.models.devices import DeviceTypeEnum, ComponentStatusEnum, InitialStateEnum, OperationalStatusEnum, DeviceStatusEnum, SoftwareVersionEnum
from db.models.maintainers import (
    InterventionType,
    InterventionStatus,
    FailureStatus,
)

class ComponentCreate(BaseModel):
    type: str
    status: ComponentStatusEnum 

class DeviceCreateBase(BaseModel):
    serial_number: int
    type: DeviceTypeEnum
    software_version: SoftwareVersionEnum
    image: str
    initial_state: InitialStateEnum
    mac_address: str
    operational_status: OperationalStatusEnum
    status: DeviceStatusEnum
    battery_level: int
    creation_date: Date
    malvoyant_id: Optional[int] = None
    components: Optional[List[ComponentCreate]] = []


class DeviceUpdateBase(BaseModel):
    type: DeviceTypeEnum
    software_version: str
    image: str
    initial_state: InitialStateEnum
    mac_address: str
    operational_status: OperationalStatusEnum
    status: DeviceStatusEnum
    battery_level: int
    malvoyant_id: Optional[int] = None
    components: Optional[List[ComponentCreate]] = []

class ComponentStatus(BaseModel):
    type: str
    status: ComponentStatusEnum

class DeviceStatusUpdate(BaseModel):
    serial_number: int
    operational_status: OperationalStatusEnum
    status: DeviceStatusEnum
    battery_level: int
    components: List[ComponentStatus]
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    temperature: float = 25.0


class FailureBase(BaseModel):
    failure_type: str
    status: FailureStatus


class FailureCreate(FailureBase):
    intervention_id: int  # Needed when creating separately


class FailureUpdate(FailureBase):
    pass


class Failure(FailureBase):
    id: int
    intervention_id: int

    class Config:
        from_attributes = True


class InterventionBase(BaseModel):
    device_serial_number: int
    type: InterventionType
    date: Optional[Date] = None
    note: Optional[str] = None
    status: InterventionStatus
    estimated_duration: Optional[str] = None


class InterventionCreate(InterventionBase):
    failures: Optional[List[FailureCreate]] = []


class Intervention(InterventionBase):
    id: int
    failures: List[Failure] = []

    class Config:
        from_attributes = True
