import fastapi
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from db.db_setup import get_db
from db.models.devices import Device, Position, Alert, Component
from schemas import DeviceCreateBase, DeviceUpdateBase, DeviceStatusUpdate
from datetime import datetime
from fastapi import Query
from db.models.devices import ComponentStatusEnum, AlertTypeEnum
from api.sockets import WebSocketManager


router = fastapi.APIRouter()

manager = WebSocketManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  
    except WebSocketDisconnect:
        manager.disconnect(websocket)


################################################################
@router.get("/devices")   
def get_all_devices(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    device_type: str = Query(None)
):
    query = db.query(Device)
    if device_type:
        query = query.filter(Device.type == device_type)
    
    devices = query.offset(offset).limit(limit).all()

    return [
        {
            "serial_number": device.serial_number,
            "type": device.type,
            "software_version": device.software_version,
            "initial_state": device.initial_state,
            "image": device.image,
            "mac_address": device.mac_address,
            "operational_status": device.operational_status,
            "status": device.status,
            "battery_level": device.battery_level,
            "creation_date": device.creation_date,
            "user_id": device.user_id
        }
        for device in devices
    ]
################################################################
@router.post("/devices")
def create_device(payload: DeviceCreateBase, db: Session = Depends(get_db)):
    # Check if device with serial number or MAC already exists
    existing_device = db.query(Device).filter(
        (Device.serial_number == payload.serial_number) |
        (Device.mac_address == payload.mac_address)
    ).first()

    if existing_device:
        raise HTTPException(status_code=400, detail="Device with given serial number or MAC address already exists")

    new_device = Device(
        serial_number=payload.serial_number,
        type=payload.type,
        software_version=payload.software_version,
        image=payload.image,
        initial_state=payload.initial_state,
        mac_address=payload.mac_address,
        operational_status=payload.operational_status,
        status=payload.status,
        battery_level=payload.battery_level,
        creation_date=payload.creation_date,
        user_id=payload.malvoyant_id  # 👈 maps to user_id in DB
    )

    db.add(new_device)

    for comp in payload.components:
        new_component = Component(
            device_serial_number=payload.serial_number,
            type=comp.type,
            status=comp.status or ComponentStatusEnum.OK  # optional fallback
        )
        db.add(new_component)

    db.commit()
    db.refresh(new_device)

    return {
        "message": "Device created successfully",
        "serial_number": new_device.serial_number
    }
################################################################

@router.get("/devices/{serial_number}")
def get_device(serial_number: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.serial_number == serial_number).first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "serial_number": device.serial_number,
        "type": device.type,
        "software_version": device.software_version,
        "initial_state": device.initial_state,
        "image": device.image,
        "mac_address": device.mac_address,
        "operational_status": device.operational_status,
        "status": device.status,
        "battery_level": device.battery_level,
        "creation_date": device.creation_date,
        "user_id": device.user_id
    }

################################################################
@router.put("/devices/{serial_number}")
def update_device(
    serial_number: int, 
    device_data: DeviceUpdateBase, 
    db: Session = Depends(get_db)
):
    # Get the existing device
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Store existing values for reference
    existing_data = {
        "type": device.type,
        "software_version": device.software_version,
        "image": device.image,
        "initial_state": device.initial_state,
        "mac_address": device.mac_address,
        "operational_status": device.operational_status,
        "status": device.status,
        "battery_level": device.battery_level,
        "user_id": device.user_id
    }

    # Update only the fields that were provided in the request
    if device_data.type is not None:
        device.type = device_data.type
    if device_data.software_version is not None:
        device.software_version = device_data.software_version
    if device_data.image is not None:
        device.image = device_data.image
    if device_data.initial_state is not None:
        device.initial_state = device_data.initial_state
    if device_data.mac_address is not None:
        device.mac_address = device_data.mac_address
    if device_data.operational_status is not None:
        device.operational_status = device_data.operational_status
    if device_data.status is not None:
        device.status = device_data.status
    if device_data.battery_level is not None:
        device.battery_level = device_data.battery_level
    if device_data.malvoyant_id is not None:
        # If user is being unassigned (set to None)
        if device_data.malvoyant_id is None:
            device.user_id = None
        else:
            # Verify the user exists
            user = db.query(User).filter(User.id == device_data.malvoyant_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            device.user_id = device_data.malvoyant_id

    # Handle components if provided
    if device_data.components is not None:
        # First delete existing components
        db.query(Component).filter(Component.device_serial_number == serial_number).delete()
        
        # Add new components
        for comp in device_data.components:
            new_component = Component(
                device_serial_number=serial_number,
                type=comp.type,
                status=comp.status or ComponentStatusEnum.OK
            )
            db.add(new_component)

    db.commit()
    db.refresh(device)

    # Prepare response showing both old and new values
    response_data = {
        "message": "Device updated successfully",
        "previous_values": existing_data,
        "updated_values": {
            "serial_number": device.serial_number,
            "type": device.type,
            "software_version": device.software_version,
            "image": device.image,
            "initial_state": device.initial_state,
            "mac_address": device.mac_address,
            "operational_status": device.operational_status,
            "status": device.status,
            "battery_level": device.battery_level,
            "user_id": device.user_id
        }
    }

    return response_data
#####################################################################
@router.delete("/devices/{serial_number}")
def delete_device(serial_number: int, db: Session = Depends(get_db)):
    # Fetch the device
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    db.query(Position).filter(Position.device_serial_number == serial_number).delete()
    db.query(Component).filter(Component.device_serial_number == serial_number).delete()
    db.query(Alert).filter(Alert.device_serial_number == serial_number).delete()

    # Delete the device itself
    db.delete(device)
    db.commit()

    return {"message": f"Device with serial number {serial_number} and its related records have been deleted successfully."}

#####################################################################

@router.get("/devices/{serial_number}/components")
def get_device_components(serial_number: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    components = db.query(Component).filter(Component.device_serial_number == serial_number).all()

    return [{"id": comp.id, "device_serial_number": comp.device_serial_number, "type": comp.type} for comp in components]

###########################################################################
@router.patch("/devices/{serial_number}")
def toggle_device_status(serial_number: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.status == "active":
        device.status = "inactive"
    else:
        device.status = "active"

    db.commit()
    db.refresh(device)

    return {
        "message": f"Device status changed to {device.status.value}",
        "serial_number": device.serial_number,
        "new_status": device.status
    }
###########################################################################

# Update a device's status and generate alerts based on specific conditions (battery level, connection, components)
@router.post("/devices/status")
async def update_device_status(payload: DeviceStatusUpdate, db: Session = Depends(get_db)):
    # Check if the device exists
    device = db.query(Device).filter(Device.serial_number == payload.serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Generate alerts
    alerts = []


       # Component status alerts
    for comp_data in payload.components:
        component = db.query(Component).filter(
            Component.device_serial_number == payload.serial_number,
            Component.type == comp_data.type
        ).first()

        if component:
            # Update status if it has changed
            if component.status != comp_data.status.value:
                component.status = comp_data.status.value
                db.add(component)

                # Create specific alert based on the new status
                if comp_data.status.value.lower() == "erreur":
                    alerts.append(Alert(
                        device_serial_number=payload.serial_number,
                        message=f"Attention: Component '{comp_data.type}' of device {payload.serial_number} encountered an error.",
                        type=AlertTypeEnum.COMPONENT_ERROR,
                        date=datetime.utcnow()
                    ))
                elif comp_data.status.value.lower() == "en panne":
                    alerts.append(Alert(
                        device_serial_number=payload.serial_number,
                        message=f"Attention: Component '{comp_data.type}' of device {payload.serial_number} is out of order.",
                        type=AlertTypeEnum.COMPONENT_OUT_OF_ORDER,
                        date=datetime.utcnow()
                    ))
        else:
            raise HTTPException(status_code=404, detail=f"Component '{comp_data.type}' not found for device {payload.serial_number}")


    # Battery level alert
    if device.battery_level != payload.battery_level:
        if payload.battery_level < 20:
            alerts.append(Alert(
                device_serial_number=payload.serial_number,
                message=f"Attention: Device {payload.serial_number} battery level is below 20%. Current level: {payload.battery_level}%",
                type=AlertTypeEnum.BATTERY_LOW,
                date=datetime.utcnow()
            ))
        device.battery_level = payload.battery_level
        db.commit()
    # Connection status alert
    if device.status != payload.status:
        if payload.status.lower() == "inactive" and device.status.lower() == "active":
            alerts.append(Alert(
                device_serial_number=payload.serial_number,
                message=f"Attention: Device {payload.serial_number} lost connection",
                type=AlertTypeEnum.CONNECTION_LOST,
                date=datetime.utcnow()
            ))
        device.status = payload.status   
        db.commit()
    # Operational status alert
    if device.operational_status != payload.operational_status:
        if payload.operational_status.value.lower() == "en maintenance":
            alerts.append(Alert(
                device_serial_number=payload.serial_number,
                message=f"Device {payload.serial_number} is under maintenance.",
                type=AlertTypeEnum.EN_MAINTENANCE,
                date=datetime.utcnow()
            ))
        device.operational_status = payload.operational_status
        db.commit()

    device.memory_usage = payload.memory_usage
    device.cpu_usage = payload.cpu_usage
    device.temperature = payload.temperature
    
    if payload.cpu_usage > 90:
        alerts.append(Alert(
            device_serial_number=payload.serial_number,
            message=f"Attention: Device {payload.serial_number} CPU usage is critically high at {payload.cpu_usage}%",
            type=AlertTypeEnum.SYSTEM_OVERLOAD,
            date=datetime.utcnow()
        ))
        
    if payload.memory_usage > 90:
        alerts.append(Alert(
            device_serial_number=payload.serial_number,
            message=f"Attention: Device {payload.serial_number} memory usage is critically high at {payload.memory_usage}%",
            type=AlertTypeEnum.MEMORY_OVERLOAD,
            date=datetime.utcnow()
        ))
        
    if payload.temperature > 75:
        alerts.append(Alert(
            device_serial_number=payload.serial_number,
            message=f"Attention: Device {payload.serial_number} temperature is critically high at {payload.temperature}°C",
            type=AlertTypeEnum.HIGH_TEMPERATURE,
            date=datetime.utcnow()
        ))
    db.commit()
    # Insert alerts into the database
    if alerts:
        db.add_all(alerts)
        db.commit()
    try:
        await manager.broadcast_device_status(payload) 
    except Exception as e:
        print(f"Erreur WebSocket : {e}")

    return {"message": "Device status updated", "alerts_created": len(alerts)}

# Get all alerts (admin view) with pagination and filter by alert type
@router.get("/alerts")
def get_all_alerts(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1), 
    offset: int = Query(0, ge=0), 
    alert_type: AlertTypeEnum = Query(None, title="Alert type", description="Optional filter by alert type")
):
    query = db.query(Alert).order_by(Alert.date.desc()) 

    
    if alert_type:
        query = query.filter(Alert.type == alert_type)
    alerts = query.limit(limit).offset(offset).all()
    return [
        {
            "id": alert.id,
            "device_serial_number": alert.device_serial_number,
            "message": alert.message,
            "date": alert.date,
            "type": alert.type 
        }
        for alert in alerts
    ]

# Get all alerts for a specific device
@router.get("/devices/{serial_number}/alerts")
def get_device_alerts(serial_number: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.serial_number == serial_number).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    alerts = db.query(Alert).filter(Alert.device_serial_number == serial_number).order_by(Alert.date.desc()).all()

    return alerts

# Delete an alert by its ID
@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()

    return {"message": f"Alert with ID {alert_id} has been deleted successfully"}

# Health check endpoint
@router.get("/")
def read_root():
    return "Server is running"