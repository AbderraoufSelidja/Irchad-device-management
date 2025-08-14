# IRCHAD Project - Device Management Module  

## Device Management Module  

IRCHAD is an innovative system designed to assist visually impaired individuals in navigating indoor environments autonomously and safely.  
Developed as part of a final-year project in the 2CS (Cycle Supérieur) SIL specialization (2024/2025) at the Higher National School of Computer Science (ESI, ex INI).

My contribution focused on the **Device Management** module. This module is responsible for managing devices assigned to users. Administrators can allocate, track in real-time, update, and maintain devices linked to each user, ensuring seamless integration with the overall navigation system. This module is built with a FastAPI backend, facilitating efficient and robust device administration. 

## Features  
- **Full Device CRUD**: Create, Read, Update, and Delete devices.  
- **User-Device Assignment**: Assign or unassign devices to registered users.  
- **Component Management**: Track the status of individual device components (e.g., GPS, camera).
- **API Integration**: The backend provides RESTful APIs for easy communication with other components of the system.  
- **Device History Tracking**: Keep a history of past device assignments and usage logs for analysis.
- **Real-Time Status Tracking**: Update and broadcast device status (battery, CPU/memory usage, temperature) in real-time via WebSockets.
- **Automated Alert System**: Generate and log alerts for critical conditions(Low Battery, Connection Lost, Component Error or Failure, System Overload (CPU, Memory), High Temperature)

## Backend -------------------------------

## Technologies Used
- **Backend**: FastAPI (Python)  
- **Database**: PostgreSQL  

## Installation  

### Prerequisites  
- Python 3.8+  
- PostgreSQL  
### Backend Setup  
1. Clone the repository:  
   - git clone git@github.com:AbderraoufSelidja/irchad-device-management-fastapi.git
   - move to /Bacjebd folder by running th comand: cd irchad-device-management/Backend
2. Create a virtual environment and activate it and install dependencies:
   - python -m venv venv.
   - .\venv\Scripts\activate
   - pip install -r requirements.txt
3. Run the backend server
  - python -m uvicorn main:app --reload
4. Test the API
  - Open your browser and go to: http://127.0.0.1:8000/docs
5. Test the WebSocket
  - You can run the file named service_ws_client.py to connect to the WebSocket server and listen for real-time messages.
  - Run the client: python test_websocket.py
  - You should see a confirmation message like "Connected to WebSocket server...". This terminal is now your real-time message log.
  - While the client is running, use another method (e.g., the API docs at http://127.0.0.1:8000/docs, Postman, or curl) to send a POST request to the /devices/status endpoint.
  - Provide a valid JSON body to simulate a device sending a status update.
  - Immediately check the terminal where your WebSocket client is running. You will see the JSON data from your POST request appear as a broadcasted message, confirming that the real-time system is working.
6. Running Unit Tests
  - From the Backend directory (the same directory containing main.py), run the following command: pytest
  - This command will automatically discover and run all tests in the project. You should see an output indicating the number of tests that passed.



