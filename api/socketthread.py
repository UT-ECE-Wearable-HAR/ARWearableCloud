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

def compress_mpudict(dict):
    quart = np.vstack([dict['qw'],dict['qx'],dict['qy'],dict['qz']])
    gravity = np.vstack([dict['gravx'],dict['gravy'],dict['gravz']])
    ypr = np.vstack([dict['y'],dict['p'],dict['r']])
    gyro = np.vstack([dict['gyrx'],dict['gyry'],dict['gyrz']])
    accel = np.vstack([dict['ax'],dict['ay'],dict['az']])
    linaccel = np.vstack([dict['linaccelx'],dict['linaccely'],dict['linaccelz']])
    linaccelinworld = np.vstack([dict['lawx'],dict['lawy'],dict['lawz']])
    euler = np.vstack([dict['ex'],dict['ey'],dict['ez']])
    return {"quart": quart, "gravity": gravity, "ypr":ypr, "gyro":gyro, 
        "accel":accel, "linaccel":linaccel, "linaccelinworld":linaccelinworld, "euler":euler}

def mpu_extract_10(packet):
    result = {point: np.array([], dtype='float32') for point in ["qw","qx","qy","qz","gravx","gravy","gravz",
        "y","p","r","ex","ey","ez"]}
    result.update({point: np.array([], dtype='int16') for point in ["ax","ay","az","gyrx","gyry","gyrz",
        "linaccelx","linaccely","linaccelz","lawx","lawy","lawz"]})
    for idx in range(10):
        entry = packet[:42]
        packet = packet[42:]

        q = dmp.quaternion(packet)
        result['qw'] = np.append(result['qw'], q[0])
        result['qx'] = np.append(result['qx'], q[1])
        result['qy'] = np.append(result['qy'], q[2])
        result['qz'] = np.append(result['qz'], q[3])
        #logger.info(result['qw'])
        #logger.info(result['qx'])
        #logger.info(result['qy'])
        #logger.info(result['qz'])
        #logger.info(f"quaternion: w: {q.w}, x: {q.x}, y: {q.y}, z: {q.z}")

        gravity = dmp.gravity(packet)
        result['gravx'] = np.append(result['gravx'], gravity[0])
        result['gravy'] = np.append(result['gravy'], gravity[1])
        result['gravz'] = np.append(result['gravz'], gravity[2])
        #logger.info(f"gravity: x: {gravity.x}, y: {gravity.y}, z: {gravity.z}")

        ypr = dmp.yawPitchRoll(packet)
        result['y'] = np.append(result['y'], ypr[0])
        result['p'] = np.append(result['p'], ypr[1])
        result['r'] = np.append(result['r'], ypr[2])
        # ypr is radians, converted here to degrees for display
        #logger.info("YAW: %3.1f" % (ypr.z * 180 / math.pi))
        #logger.info("PITCH: %3.1f" % (ypr.y * 180 / math.pi))
        #logger.info("ROLL: %3.1f" % (ypr.x * 180 / math.pi))

        
        gyro = dmp.gyro(packet)
        result['gyrx'] = np.append(result['gyrx'], gyro[0])
        result['gyry'] = np.append(result['gyry'], gyro[1])
        result['gyrz'] = np.append(result['gyrz'], gyro[2])
        #logger.info(f"Gyro: x: {vec.x}, y: {vec.y}, z: {vec.z}")


        accel = dmp.accel(packet)
        result['ax'] = np.append(result['ax'], accel[0])
        result['ay'] = np.append(result['ay'], accel[1])
        result['az'] = np.append(result['az'], accel[2])
        #logger.info(f"Accel: x: {accel.x}, y: {accel.y}, z: {accel.z}")

        # remmoves gravity component from accel
        linAccel = dmp.linAccel(packet)
        result['linaccelx'] = np.append(result['linaccelx'], linAccel[0])
        result['linaccely'] = np.append(result['linaccely'], linAccel[1])
        result['linaccelz'] = np.append(result['linaccelz'], linAccel[2])
        #logger.info(f"LinearAccel: x: {accelReal.x}, y: {accelReal.y}, z: {accelReal.z}")

        # rotate measured 3D acceleration vector into original state
        # frame of reference based on orientation quaternion
        linAccelWorld = dmp.linAccelWorld(packet)
        result['lawx'] = np.append(result['lawx'], linAccelWorld[0])
        result['lawy'] = np.append(result['lawy'], linAccelWorld[1])
        result['lawz'] = np.append(result['lawz'], linAccelWorld[2])
        #logger.info(f"LinearAccelInWorld: x: {vec.x}, y: {vec.y}, z: {vec.z}")

        euler = dmp.euler(packet)
        result['ex'] = np.append(result['ex'], euler[0])
        result['ey'] = np.append(result['ey'], euler[1])
        result['ez'] = np.append(result['ez'], euler[2])
        # euler angles are in radians
        #logger.info(f"euler: psi: {euler.x}, theta: {euler.y}, phi: {euler.z}")
        packet = packet[42:]
    return compress_mpudict(result)

def socketthread(user):
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
            logger.info("Receiving MPU data")
            mpu_res = bytearray()
            while(len(mpu_res) < 420):
                buf = c.recv(1024)
                mpu_res += buf
            mpubytes = mpu_res[:420]
            mpu_results = mpu_extract_10(bytes(mpubytes))
            #logger.info(mpu_results)
            c.send("MPU_RECV\n".encode())
            userprofile = UserProfile.objects.get(pk=user)

            """logger.info("quart" + str(mpu_results['quart'].dtype) + "gravity" + str(mpu_results['gravity'].dtype) + 
                "ypr" + str(mpu_results['ypr'].dtype) + "gyro" + str(mpu_results['gyro'].dtype) + "accel" + str(mpu_results['accel'].dtype) + 
                "linaccel" + str(mpu_results['linaccel'].dtype) + "law" + str(mpu_results['linaccelinworld'].dtype) + "euler" + str(mpu_results['euler'].dtype))"""


            data = DataCapture(user = userprofile, img = res[4:], quarternion = mpu_results['quart'], 
                gravity = mpu_results['gravity'].tobytes(), ypr = mpu_results['ypr'].tobytes(), gyro = mpu_results['gyro'].tobytes(), 
                accel = mpu_results['accel'].tobytes(), linaccel = mpu_results['linaccel'].tobytes(), 
                linaccelinworld = mpu_results['linaccelinworld'].tobytes(), euler = mpu_results['euler'].tobytes())
            data.save()
            logger.info("MPU Data Recieved")
        c.close()
    except ConnectionResetError:
        logger.info("Socket disconnected")
        c.close()
