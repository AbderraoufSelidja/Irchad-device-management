from fastapi.testclient import TestClient
from main import app
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from db.db_setup import get_db, Base
from db.models.devices import Device, Position, Alert, Component, DeviceTypeEnum, ComponentStatusEnum, InitialStateEnum, OperationalStatusEnum, DeviceStatusEnum, SoftwareVersionEnum, AlertTypeEnum
from datetime import datetime, date

# In-memory SQLite database (disappears after the test)
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create tables for testing
def setup() -> None:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Insert a test device
    db_device = Device(
        serial_number=123,
        type=DeviceTypeEnum.CEINTURE_INTELLIGENTE,
        software_version=SoftwareVersionEnum.V1_0,
        image="https://example.com/image.jpg",
        initial_state=InitialStateEnum.NEUF,
        mac_address="00:1B:44:11:5A:B9",
        operational_status=OperationalStatusEnum.EN_SERVICE,
        status=DeviceStatusEnum.ACTIVE,
        battery_level=95,
        creation_date=date(2025, 3, 14),
        user_id=None
    )
    session.add(db_device)
    session.commit()
    
    # Insert components linked to the device
    db_component1 = Component(device_serial_number=123, type="camera", status=ComponentStatusEnum.OK)
    db_component2 = Component(device_serial_number=123, type="gyroscope", status=ComponentStatusEnum.OK)

    session.add(db_component1)
    session.add(db_component2)
    session.commit()
    
    # Add a position for the device
    db_position = Position(
        device_serial_number=123,
        latitude=36.7528,  
        longitude=3.0422,  
        altitude=50.5,  
        position_name="Bureau 101",
        occupation_timestamp=datetime.utcnow()
    )
    session.add(db_position)
    session.commit()
    
    # Add an alert for the device
    db_alert = Alert(
        device_serial_number=123,
        message="Attention: Device 123 lost connection",
        type=AlertTypeEnum.CONNECTION_LOST,
        date=datetime.utcnow()
    )
    session.add(db_alert)
    session.commit()

# Initialize the test database
setup()

# Override DB dependency for tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Creating the test client
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Server is running"

# Mock d'un device valide
device_data = {
    "serial_number": 456,
    "type": "ceinture intelligente",  
    "software_version": "1.0",
    "image": "https://example.com/image.jpg",
    "initial_state": "neuf",  
    "mac_address": "00:1B:44:11:4A:B9",
    "operational_status": "en service",
    "status": "active",  
    "battery_level": 95,
    "creation_date": "2025-03-14",
    "malvoyant_id": None,
    "components": [
        {"type": "camera", "status": "ok"},
        {"type": "gyroscope", "status": "ok"}
    ]
}

# Test device creation
def test_create_device():
    response = client.post("/devices", json=device_data)
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["message"] == "Device created successfully"
    assert response_json["serial_number"] == device_data["serial_number"]

# Test recovery of all devices
def test_get_all_devices():
    response = client.get("/devices")
    assert response.status_code == 200
    devices = response.json()
    
    # Check that the answer is indeed a list
    assert isinstance(devices, list) 

    # Find the device with serial number 123 (the one inserted in `setup`)
    test_device = next((d for d in devices if d["serial_number"] == 123), None)
    assert test_device is not None

    # Check the values of the inserted device
    assert test_device["serial_number"] == 123
    assert test_device["type"] == "ceinture intelligente"
    assert test_device["software_version"] == "1.0"
    assert test_device["initial_state"] == "neuf"
    assert test_device["image"] == "https://example.com/image.jpg"
    assert test_device["mac_address"] == "00:1B:44:11:5A:B9"
    assert test_device["operational_status"] == "en service"
    assert test_device["status"] == "active"
    assert test_device["battery_level"] == 95
    assert test_device["creation_date"] == "2025-03-14"
    assert test_device["user_id"] is None

# Test recovery of devices with a device type filter
def test_get_devices_by_type():
    # Test with a device type filter (e.g., "ceinture intelligente")
    response = client.get("/devices?device_type=ceinture intelligente")
    assert response.status_code == 200
    devices = response.json()
    assert isinstance(devices, list)  
    # Check the values of the filtered devices
    if devices:
        for device in devices:
            assert device["type"] == "ceinture intelligente"

# Test get details of a specific device
def test_get_device_details():
    response = client.get("/devices/123")  # We recover the device with serial number = 123 (inserted in setup)
    assert response.status_code == 200
    device = response.json()

    assert device["serial_number"] == 123
    assert device["type"] == "ceinture intelligente"
    assert device["software_version"] == "1.0"
    assert device["initial_state"] == "neuf"
    assert device["image"] == "https://example.com/image.jpg"
    assert device["mac_address"] == "00:1B:44:11:5A:B9"
    assert device["operational_status"] == "en service"
    assert device["status"] == "active"
    assert device["battery_level"] == 95
    assert device["creation_date"] == "2025-03-14"
    assert device["user_id"] is None

# Test a non-existent device
def test_get_nonexistent_device():
    response = client.get("/devices/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

# Mock the new device data for update
update_data = {
    "type": "bracelet vibrant",
    "software_version": "1.2",
    "image": "https://example.com/new_image.jpg",
    "initial_state": "défectueux",
    "mac_address": "00:1B:44:11:5A:C0",
    "operational_status": "en veille",
    "status": "active",
    "battery_level": 50,
    "malvoyant_id": None, 
    "components": [
        {"type": "capteur thermique", "status": "ok"},
        {"type": "accéléromètre", "status": "ok"}
    ]
}

# Test update successful
def test_update_device():
    response = client.put("/devices/123", json=update_data)
    assert response.status_code == 200
    response_json = response.json()

    assert response_json["message"] == "Device updated successfully"
    assert "previous_values" in response_json
    assert "updated_values" in response_json
    assert response_json["updated_values"]["serial_number"] == 123
    assert response_json["updated_values"]["type"] == update_data["type"]
    assert response_json["updated_values"]["software_version"] == update_data["software_version"]

# Test update of a non-existent device
def test_update_nonexistent_device():
    response = client.put("/devices/999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

# Test toggle device status
def test_toggle_device_status():
    # First, get current status
    response = client.get("/devices/123")
    current_status = response.json()["status"]
    
    # Toggle status
    response = client.patch("/devices/123")
    assert response.status_code == 200
    response_json = response.json()
    
    assert "message" in response_json
    assert response_json["serial_number"] == 123
    assert response_json["new_status"] != current_status

# Test recovery of device components
def test_get_device_components():
    response = client.get("/devices/123/components")
    assert response.status_code == 200
    
    components = response.json()
    
    # Check that components exist
    assert len(components) >= 2  # At least the components added in setup and update
    
    # Check component structure
    for component in components:
        assert "id" in component
        assert "device_serial_number" in component
        assert "type" in component
        assert component["device_serial_number"] == 123

def test_get_components_nonexistent_device():
    response = client.get("/devices/9999/components")  # Serial number that does not exist
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

# Test update device status and create alerts
def test_update_device_status_creates_alerts():
    payload = {
        "serial_number": 123,
        "operational_status": "en maintenance",
        "status": "inactive",
        "battery_level": 10,
        "memory_usage": 95.0,
        "cpu_usage": 95.0,
        "temperature": 80.0,
        "components": [
            {
                "type": "capteur thermique",
                "status": "en panne"
            },
            {
                "type": "accéléromètre",
                "status": "ok"
            }
        ]
    }
    # Send POST request to update device status
    response = client.post("/devices/status", json=payload)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["message"] == "Device status updated"
    # Should create multiple alerts based on conditions
    assert json_response["alerts_created"] >= 1

# Test get all alerts
def test_get_all_alerts():
    response = client.get("/alerts")
    assert response.status_code == 200
    alerts = response.json()
    
    # Check that alerts exist
    assert len(alerts) >= 1
    
    for alert in alerts:
        assert "id" in alert
        assert "device_serial_number" in alert
        assert "message" in alert
        assert "type" in alert
        assert "date" in alert

# Test for retrieving alerts with pagination and alert type filter
def test_get_alerts_with_filters_and_pagination():
    # Filter by alert type (e.g., "connection lost")
    response = client.get("/alerts?alert_type=connection lost&limit=5&offset=0")
    assert response.status_code == 200
    alerts = response.json()
    
    # Check that all returned alerts match the filter
    for alert in alerts:
        assert alert["type"] == "connection lost"

# Test get device alerts
def test_get_device_alerts():
    response = client.get("/devices/123/alerts")
    assert response.status_code == 200
    
    alerts = response.json()
    
    # Check that alerts exist for this device
    assert isinstance(alerts, list)
    
    # Check that all alerts belong to the device
    for alert in alerts:
        assert alert["device_serial_number"] == 123

# Test delete an alert by ID
def test_delete_alert():
    # First, get an existing alert
    response = client.get("/alerts")
    alerts = response.json()
    
    if alerts:
        alert_id = alerts[0]["id"]
        
        # Delete the alert
        response = client.delete(f"/alerts/{alert_id}")
        assert response.status_code == 200
        assert f"Alert with ID {alert_id} has been deleted successfully" in response.json()["message"]

        # Verify the alert is deleted
        response_check = client.get("/alerts")
        remaining_alerts = response_check.json()
        assert all(a["id"] != alert_id for a in remaining_alerts)

# Test delete non-existent alert
def test_delete_nonexistent_alert():
    response = client.delete("/alerts/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"

# Test delete non-existent device
def test_delete_nonexistent_device():
    serial_number = 99999  # Serial number that does not exist
    response = client.delete(f"/devices/{serial_number}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"

# Test delete device (should be last test as it removes the device)
def test_delete_device():
    serial_number = 123  
    response = client.delete(f"/devices/{serial_number}")
    assert response.status_code == 200
    assert f"Device with serial number {serial_number} and its related records have been deleted successfully" in response.json()["message"]
    
    # Verify the device is deleted
    response = client.get(f"/devices/{serial_number}")
    assert response.status_code == 404