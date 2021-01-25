import socket
from _thread import *
import threading
import logging
from UserProfile.models import UserProfile, ImgCapture 

HOST = "localhost"
PORT = 4444

def socketthread(user):
    logger = logging.getLogger("mainlogger") 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind(('', PORT)) 
    s.listen(5) 
    c, addr = s.accept()
    logger.info(str(c) + " " + str(addr))
    
    #TODO: This will need to be replaced with disconnecting logic
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
            while(len(res) < size+4):
                buf = c.recv(1024)
                res += buf
            c.send("IMG_RECV\n".encode())
            logger.info("Image received")
            userprofile = UserProfile.objects.get(pk=user)
            img = ImgCapture(user=userprofile, img = res[4:])
            img.save()
            logger.info("Image saved")
    except ConnectionResetError:
        logger.info("Socket disconnected")
        c.close()