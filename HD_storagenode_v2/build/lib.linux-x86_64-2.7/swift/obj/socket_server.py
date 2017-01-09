import socket
import time
import os

sde1 = "df /dev/sde1"

sds = [sde1]

def disk_info():
    Size = 0
    Used = 0
    for sd in sds:
        disks = os.popen(sd)
        i = 0
        for disk in disks:
            if i==0:
                i = 1
                continue
            Size += float(disk.split()[1])
            Used += float(disk.split()[2])
    return str(Size) + " " + str(Used)

def Server():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('192.168.1.222',8080))
    sock.listen(1)
    while True:
        connection,address = sock.accept()
        try:
            connection.settimeout(10)
            buf = connection.recv(1024)
            if buf == "get disk info":
                connection.send(disk_info())
            else:
                connection.send("Unknow message!")
        except socket.timeout:
            print 'socket timeout!'
        connection.close()

if __name__ == '__main__':
    Server()
