"""
remote_io_server.py - Server component for remote file I/O experiment on Raspberry Pi
"""

import os
import socketio
import eventlet

from config.settings import SERVER_HOST, SERVER_PORT

# Initialize Socket.IO server
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid, environ):
    print(f"Connection established: {sid}")


@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
def read_file_request(sid, data):
    """
    Handle file read request from client
    """
    filepath = data.get("filepath")
    print(f"Received request to read file: {filepath}")

    if not os.path.exists(filepath):
        sio.emit("read_file_response", {"error": f"File {filepath} not found"}, to=sid)
        return

    try:
        with open(filepath, "rb") as f:
            file_data = f.read()

        # Convert bytes to base64 string for transmission
        import base64

        encoded_data = base64.b64encode(file_data).decode("utf-8")

        sio.emit(
            "read_file_response",
            {"filepath": filepath, "data": encoded_data, "file_size": len(file_data)},
            to=sid,
        )
        print(f"File {filepath} sent successfully ({len(file_data)} bytes)")

    except Exception as e:
        sio.emit("read_file_response", {"error": str(e)}, to=sid)
        print(f"Error reading file: {e}")


if __name__ == "__main__":
    print(f"Starting server on {SERVER_HOST}:{SERVER_PORT}...")
    eventlet.wsgi.server(eventlet.listen((SERVER_HOST, SERVER_PORT)), app)
