#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import socket
import struct
import hashlib
import threading
import subprocess
from TestEngines.config import *


SIZE = 1024
HEAD_STRUCT = '128sIq32s'
info_size = struct.calcsize(HEAD_STRUCT)


def calc_md5(file_path):
    with open(file_path, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5


def unpack_file_info(file_info):
    file_name, file_name_len, file_size, md5 = struct.unpack(
        HEAD_STRUCT, file_info)
    file_name = file_name[:file_name_len]
    return file_name, file_size, md5


def tcp_link(sock, address):
    print('Accept new connection from %s:%s...' % address)
    # receive cases
    while True:
        file_info = sock.recv(info_size)
        if file_info == b'Finished':
            break
        else:
            file_name, file_size, md5_recv = unpack_file_info(file_info)
            file_name = file_name.decode('utf-8')
            md5_recv = md5_recv.decode('utf-8')
            recved_size = 0
            file = os.path.join(CASE_DIR, file_name)
            print('\nReceiving case files:' + file)
            with open(file, 'wb') as fw:
                while recved_size < file_size:
                    remained_size = file_size - recved_size
                    recv_size = SIZE if remained_size > SIZE else remained_size
                    recv_file = sock.recv(recv_size)
                    recved_size += len(recv_file)
                    fw.write(recv_file)
            md5 = calc_md5(file)
            if md5 != md5_recv:
                print('MD5 comparison fail!')
            else:
                print('Successfully received.')

    # run cases
    subprocess.run([sys.executable, 'run.py'], stdout=subprocess.PIPE)

    # latest report
    report_file = sorted(
        [(x, x.stat().st_mtime) for x in os.scandir(REPORT_DIR)
         if x.is_file() and x.name.endswith(".html")],
        key=lambda i: i[1])[-1][0]

    file_name, file_path = report_file.name, report_file.path
    file_name_len = len(file_name)
    file_size = os.path.getsize(file_path)
    file_md5 = calc_md5(file_path)

    # send report
    print("\nSending report...")
    file_head = struct.pack(HEAD_STRUCT,
                            file_name.encode('utf-8'),
                            file_name_len,
                            file_size,
                            file_md5.encode('utf-8'))
    sock.send(file_head)
    with open(file_path, 'rb') as fr:
            for msg in fr:
                sock.send(msg)
    print("Report sent.")
    sock.close()
    print('\nConnection from %s:%s closed.' % address)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', int(CONFIG.get('RECEIVER_MODE', 'PORT'))))
s.listen(1)
print('Waiting for connection...')
try:
    while True:
        c_sock, c_address = s.accept()
        t = threading.Thread(target=tcp_link, args=(c_sock, c_address))
        t.start()
except KeyboardInterrupt:
    pass
