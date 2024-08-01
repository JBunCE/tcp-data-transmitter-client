import cv2
import json
import socket
import base64
import zlib

import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 1935)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:
    # Send data
    message = {
        "type": "Connect",
        "data": {
            "is_streamer": 0,
            "stream_id": 27
        }
    }
    message_bytes = json.dumps(message).encode()
    sock.sendall(message_bytes)

finally:
    while True:
        data = sock.recv(1000000)
        if data:
            print(data)
            frame_data = base64.b64decode(data)
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
