#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import struct
import hashlib
import threading
from TestEngines.config import *


SIZE = 1024
receivers = [(x.name, x.path)
             for x in os.scandir(REMOTE_CASE_DIR) if x.is_dir()]
HEAD_STRUCT = '128sIq32s'
info_size = struct.calcsize(HEAD_STRUCT)


def calc_md5(path_to_calc):
    with open(path_to_calc, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5


def unpack_file_info(file_info):
    file_name, file_name_len, file_size, md5 = struct.unpack(
        HEAD_STRUCT, file_info)
    file_name = file_name[:file_name_len]
    return file_name, file_size, md5


def tcp_link(receiver_name, receiver_path):
    # connect to receiver
    receiver_server = CONFIG.get(
        'SENDER_MODE', receiver_name.upper()).split(':')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # establish connection
    sock.connect((receiver_server[0], int(receiver_server[1])))
    # read cases
    remote_case = [
        (x.name, x.path, len(x.name), os.path.getsize(x.path), calc_md5(x.path))
        for x in os.scandir(receiver_path)
        if x.is_file() and x.name.endswith(".xlsx") and '~$' not in x.name]
    # send cases
    print("\nSending cases...")
    for file_name, file_path, file_name_len, file_size, file_md5 in remote_case:
        file_head = struct.pack(HEAD_STRUCT,
                                file_name.encode('utf-8'),
                                file_name_len,
                                file_size,
                                file_md5.encode('utf-8'))
        sock.send(file_head)
        with open(file_path, 'rb') as fr:
            for msg in fr:
                sock.send(msg)
    sock.send(b'Finished')
    print("Cases sent.")

    # receive report
    file_info = sock.recv(info_size)
    file_name, file_size, md5_recv = unpack_file_info(file_info)
    file_name, md5_recv = file_name.decode('utf-8'), md5_recv.decode('utf-8')
    recved_size = 0
    file = os.path.join(REMOTE_REPORT_DIR, receiver_name + '.' + file_name)
    print('\nReceiving Report File:' + file)
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
    sock.close()


for receiver in receivers:
    t = threading.Thread(target=tcp_link, args=receiver)
    t.start()
