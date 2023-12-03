import socket

import os
import errno


class Supervisor(object):
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket()
        self.socket.connect((ip, port))

    def send(self, message: str):
        self.socket.sendall(message.encode())

    @classmethod
    def create(cls, ip: str, port: int):
        try:
            return Supervisor(ip, port)
        except OSError as err:
            if err.errno == errno.ECONNRESET:
                return None
            raise err
