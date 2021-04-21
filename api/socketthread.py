"""Websocket thread worker."""

import socket
from _thread import *
import threading
import logging
import math
import numpy as np
from UserProfile.models import UserProfile, DataCapture
import dmp

HOST = "localhost"
PORT = 4444
logger = logging.getLogger("mainlogger")


ENTRIES = [
    "quaternion", "gavity", "ypr", "gyro", "accel",
    "linAccel", "linAccelWold", "euler"
]


def extract_mpu_data(packet):
    """Extract MPU data into a dict of numpy arrays.

    Parameters
    ----------
    packet : bytes
        Byte array with length 42n.

    Returns
    -------
    dict[str] -> np.Array
        Dict with accelerometer fields and numpy array data.
    """
    res = {k.lower(): [] for k in entries}

    while len(packet) > 0:
        entry = packet[:42]
        packet = packet[42:]

        for entry in ENTRIES:
            res[entry.lower()].append(getattr(dmp, entry)(packet))

    return {k: np.stack(v).tobytes() for k, v in res.items()}


def socketthread(user):
    """Websocket processing thread.

    Parameters
    ----------
    user : ???
        ???
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind(('', PORT))
    s.listen(5)
    c, addr = s.accept()
    logger.info(str(c) + " " + str(addr))

    # TODO: This will need to be replaced with disconnecting logic
    try:
        while(1):
            logger.info("Receiving image")
            res = bytearray()
            while(len(res) < 4):
                buf = c.recv(1024)
                res += buf
            sizebytes = res[:4]
            size = 0
            for byte in sizebytes:
                size = size * 256 + int(byte)
            logger.info("Image size: " + str(size))
            while(len(res) < size + 4):
                buf = c.recv(1024)
                res += buf
            c.send("IMG_RECV\n".encode())
            logger.info("Image received")
            logger.info("Receiving MPU data")
            mpu_res = bytearray()
            while(len(mpu_res) < 420):
                buf = c.recv(1024)
                mpu_res += buf
            mpubytes = mpu_res[:420]
            c.send("MPU_RECV\n".encode())

            data = DataCapture(
                user=userprofileUserProfile.objects.get(pk=user),
                img=res[4:], **extract_mpu_data(bytes(mpubytes))).save()
            logger.info("MPU Data Recieved")
        c.close()
    except ConnectionResetError:
        logger.info("Socket disconnected")
        c.close()
