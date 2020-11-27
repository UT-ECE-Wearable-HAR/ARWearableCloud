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
    c.recv(1024)
    t = c.recv(1024)
    size = 0
    for b in t:
        size = size * 256 + int(b)
    logger.info(str(size))
    res = bytearray()
    while(1):
        t = c.recv(1024)
        if not t:
            break
        res += t
    logger.info("Image received")
    userprofile = UserProfile.objects.get(pk=user)
    img = ImgCapture(user=userprofile, img = res)
    img.save()
    logger.info("Image saved")
    c.close()