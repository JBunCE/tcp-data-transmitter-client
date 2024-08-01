import base64
import json
from io import BytesIO

import customtkinter as ctk
import threading as th

from mss import mss
import socket

from PIL import Image, ImageTk

import api_calls


class ErrorAlert(ctk.CTk):
    def __init__(self, message):
        ctk.CTk.__init__(self)

        self.title('Invalid credentials')
        self.geometry('350x200')
        self.resizable(False, False)

        self.message_label = ctk.CTkLabel(self, text=message)
        self.message_label.pack(side='top', pady=10, padx=10)

        self.ok_button = ctk.CTkButton(self, text='Ok', command=self.destroy)
        self.ok_button.pack(side='top', pady=10, padx=10)


class Login(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)

        self.title('Desktop Cast')
        self.geometry('300x300')
        self.resizable(False, False)

        self.username_label = ctk.CTkLabel(self, text='Phone number')
        self.username_label.pack(side='top', pady=10, padx=10)

        self.username_input = ctk.CTkEntry(self)
        self.username_input.pack(side='top', pady=10, padx=10)

        self.password_label = ctk.CTkLabel(self, text='Password')
        self.password_label.pack(side='top', pady=10, padx=10)

        self.password_input = ctk.CTkEntry(self, show='*')
        self.password_input.pack(side='top', pady=10, padx=10)

        self.login_button = ctk.CTkButton(self, text='Login', command=self.login)
        self.login_button.pack(side='top', pady=10, padx=10)

    def login(self):
        response = api_calls.login(self.username_input.get(), self.password_input.get())

        if response['status'] == 'success':
            self.destroy()
            app = DesktopCastClient(response['data']['data']['userId'])
            app.mainloop()
        else:
            error_alert = ErrorAlert("Unauthorized")
            error_alert.mainloop()


class DesktopCastClient(ctk.CTk):
    def __init__(self, userId):
        ctk.CTk.__init__(self)

        self.user_id = userId

        self.image_on_canvas = None
        self.title('Desktop Cast Client')
        self.geometry('1366x768')
        self.resizable(False, False)

        self.stream_thread = th.Thread(target=self.start_stream)

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(side='left', fill='y', padx=10, pady=10)

        self.stream_frame = ctk.CTkFrame(self)
        self.stream_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        self.title_stream_label = ctk.CTkLabel(self.options_frame, text='Stream title')
        self.title_stream_label.pack(side='top', pady=10, padx=10)

        self.title_stream_input = ctk.CTkEntry(self.options_frame)
        self.title_stream_input.pack(side='top', pady=10, padx=10)

        self.stream_description_label = ctk.CTkLabel(self.options_frame, text='Stream description')
        self.stream_description_label.pack(side='top', pady=10, padx=10)

        self.stream_description_input = ctk.CTkEntry(self.options_frame)
        self.stream_description_input.pack(side='top', pady=10, padx=10)

        self.stream_button = ctk.CTkButton(self.options_frame, text='Stream', command=self.stream_thread.start)
        self.stream_button.pack(side='top', pady=10, padx=10)

        self.stream_canvas = ctk.CTkCanvas(self.stream_frame, bg='black')
        self.stream_canvas.pack(side='left', fill='both', expand=True)

    def start_stream(self):
        sct = mss()
        monitor = sct.monitors[0]  # Use the first monitor

        stream = api_calls.create_stream(
            self.title_stream_input.get(),
            self.stream_description_input.get(),
            self.user_id
        )

        # Make connection
        message = {
            "type": "Connect",
            "data": {
                "is_streamer": 1,
                "stream_id": stream['data']['id']
            }
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 1935)
        print('connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)

        message_bytes = json.dumps(message).encode()
        sock.sendall(message_bytes)

        while True:
            frame = sct.grab(monitor)
            img_pil = Image.frombytes('RGB', frame.size, frame.rgb)

            max_width = 800
            width, height = img_pil.size
            aspect_ratio = width / height
            new_height = max_width / aspect_ratio

            img_pil = img_pil.resize((max_width, round(new_height)))

            buf = BytesIO()
            img_pil.save(buf, format='JPEG')
            image_base64 = base64.b64encode(buf.getvalue()).decode('ascii')

            message = {
                "type": "Frame",
                "data": {
                    "bytes": image_base64 + "$"
                }
            }

            message_bytes = json.dumps(message).encode()
            sock.sendall(message_bytes)

            img_tk = ImageTk.PhotoImage(image=img_pil)
            self.stream_canvas.create_image(0, 0, image=img_tk, anchor='nw')
            self.image_on_canvas = img_tk


if __name__ == '__main__':
    app = Login()
    app.mainloop()
