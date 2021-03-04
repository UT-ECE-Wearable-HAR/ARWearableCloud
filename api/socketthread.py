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
    result = {point: np.array([]) for point in ["qw","qx","qy","qz","gravx","gravy","gravz","y","p","r","ax","ay","az",
        "gyrx","gyry","gyrz","linaccelx","linaccely","linaccelz","lawx","lawy","lawz","ex","ey","ez"]}

    for idx in range(10):
        entry = packet[:42]
        packet = packet[42:]

        q = dmp.Quaternion()
        dmp.dmpGetQuaternion(q, entry)
        result['qw'] = np.append(result['qw'], q.w)
        result['qx'] = np.append(result['qx'], q.x)
        result['qy'] = np.append(result['qy'], q.y)
        result['qz'] = np.append(result['qz'], q.z)
        #logger.info(result['qw'])
        #logger.info(result['qx'])
        #logger.info(result['qy'])
        #logger.info(result['qz'])
        #logger.info(f"quaternion: w: {q.w}, x: {q.x}, y: {q.y}, z: {q.z}")

        gravity = dmp.VectorFloat()
        dmp.dmpGetGravity(gravity, q)
        result['gravx'] = np.append(result['gravx'], gravity.x)
        result['gravy'] = np.append(result['gravy'], gravity.y)
        result['gravz'] = np.append(result['gravz'], gravity.z)
        #logger.info(f"gravity: x: {gravity.x}, y: {gravity.y}, z: {gravity.z}")

        ypr = dmp.VectorFloat()
        dmp.dmpGetYawPitchRoll(ypr, q, gravity)
        result['y'] = np.append(result['y'], ypr.z)
        result['p'] = np.append(result['p'], ypr.y)
        result['r'] = np.append(result['r'], ypr.x)
        # ypr is radians, converted here to degrees for display
        #logger.info("YAW: %3.1f" % (ypr.z * 180 / math.pi))
        #logger.info("PITCH: %3.1f" % (ypr.y * 180 / math.pi))
        #logger.info("ROLL: %3.1f" % (ypr.x * 180 / math.pi))

        
        vec = dmp.VectorInt16()
        dmp.dmpGetGyro(vec, entry)
        result['gyrx'] = np.append(result['gyrx'], vec.x)
        result['gyry'] = np.append(result['gyry'], vec.y)
        result['gyrz'] = np.append(result['gyrz'], vec.z)
        #logger.info(f"Gyro: x: {vec.x}, y: {vec.y}, z: {vec.z}")


        accel = dmp.VectorInt16()
        dmp.dmpGetAccel(accel, entry)
        result['ax'] = np.append(result['ax'], accel.x)
        result['ay'] = np.append(result['ay'], accel.y)
        result['az'] = np.append(result['az'], accel.z)
        #logger.info(f"Accel: x: {accel.x}, y: {accel.y}, z: {accel.z}")

        # remmoves gravity component from accel
        accelReal = dmp.VectorInt16()
        dmp.dmpGetLinearAccel(accelReal, accel, gravity)
        result['linaccelx'] = np.append(result['linaccelx'], accelReal.x)
        result['linaccely'] = np.append(result['linaccely'], accelReal.y)
        result['linaccelz'] = np.append(result['linaccelz'], accelReal.z)
        #logger.info(f"LinearAccel: x: {accelReal.x}, y: {accelReal.y}, z: {accelReal.z}")

        # rotate measured 3D acceleration vector into original state
        # frame of reference based on orientation quaternion
        vec = dmp.VectorInt16()
        dmp.dmpGetLinearAccelInWorld(vec, accelReal, q)
        result['lawx'] = np.append(result['lawx'], vec.x)
        result['lawy'] = np.append(result['lawy'], vec.y)
        result['lawz'] = np.append(result['lawz'], vec.z)
        #logger.info(f"LinearAccelInWorld: x: {vec.x}, y: {vec.y}, z: {vec.z}")

        euler = dmp.VectorFloat()
        dmp.dmpGetEuler(euler, q)
        result['ex'] = np.append(result['ex'], euler.x)
        result['ey'] = np.append(result['ey'], euler.y)
        result['ez'] = np.append(result['ez'], euler.z)
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
