#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys

try:
    _, METODO, SIP_ADDRESS = sys.argv

except IndexError:
    sys.exit('Usage: python3 client.py method receiver@IP:SIPport')

SERVER, PORT = SIP_ADDRESS.split(':')
login, SERVER = SERVER.split('@')
PORT = int(PORT)
METODO = METODO.upper()
PROTOCOL = 'SIP/2.0\r\n\r\n'
DATA = ' '.join([METODO.upper(), "sip:" + SIP_ADDRESS, PROTOCOL])

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((SERVER, PORT))
    my_socket.send(bytes(DATA, 'utf-8'))
    data = my_socket.recv(1024)
    cod_answer = data.decode('utf-8').split(' ')[-2]
    if (cod_answer == '200') and (METODO != 'BYE'):
        DATA = ' '.join(["ACK", "sip:" + SIP_ADDRESS, PROTOCOL])
        my_socket.send(bytes(DATA, 'utf-8'))
