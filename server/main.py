#!/usr/bin/env python3

from gyro_listener import GyroListener

if __name__ == "__main__":
    gl = GyroListener("192.168.0.22", 5678, conn_limit = 1)
    gl.start()
