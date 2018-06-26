#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor en UDP simple."""

import socketserver
import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import json
import time
import random
import hashlib

ATTR_TIME = '%Y-%m-%d %H:%M:%S +0000'
NONCE = random.randint(0,99999)
Users = {}

try:
    _, CONFIG = sys.argv

except ValueError:
    sys.exit('Usage: python3 proxy_registrar.py config')

################INICIO#################

def register2json():
    """metodo para registrar usuarios en json."""
    with open('registered.json', 'w') as outfile:
        json.dump(Users, outfile, indent=3)

def json2registered():
    """metodo para leer json externo."""
    try:
        with open('registered.json', 'r') as infile:
            Users = json.loads(infile)
    except:
        pass

def Retransmitir(address, data):
    """Retransmisiones, address es una tupla (ip,port)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.connect((address[0], int(address[1])))
        print('retasmita a: ',address)
        # print(data)
        my_socket.send(bytes(data, 'utf-8'))
        data = my_socket.recv(1024)
        cod_answer = data.decode('utf-8')
        print(cod_answer)


###############CLASES###################

class CONFIGHandler(ContentHandler):
    """Clase para manejar CONFIG."""
    def __init__(self):
        """Constructor. Inicializamos las variables."""
        self.list = []
        self.attributs = {}
        self.tags = {
            'server': ['name', 'ip', 'puerto'],
            'database': ['path', 'passwdpath'],
            'log': ['path']}

    def startElement(self, name, attrs):
        """Método que se llama cuando se abre una etiqueta."""

        if name in self.tags:
            dicc = {}
            for attri in self.tags[name]:
                dicc[attri] = attrs.get(attri, "")
            self.list.append({name: dicc})
            self.attributs[name] = dicc

    def get_tags(self):

        return self.list


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    Users = {}


    def check_method(self, method, protocol, sip, data):
        """function for check the method."""
        methods = ['REGISTER','INVITE', 'ACK', 'BYE']
        data_send = ""
        manager = Meth_Manag()
        if method in methods:
            if 1 == 1:
            # if (protocol == 'SIP/2.0') and (sip[0:4] == 'sip:'):
                if method == 'REGISTER':
                    manager.Register(data, self.client_address)
                    data_send = "SIP/2.0 401 Unauthorized\r\n\r\n"
                else:
                    data_send = manager.Invite(data, self.client_address)
            else:
                data_send = "SIP/2.0 400 Bad Request\r\n\r\n"
        else:
            data_send = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
        self.wfile.write(bytes(data_send, 'utf-8'))

    def handle(self):
        """handler server."""
        if not Users:
            json2registered()
        all_data = self.rfile.read().decode('utf-8')
        print('por aki ha pasao: ', all_data)
        data = all_data.split('\r\n')
        data = data[0].split(' ')
        # print(data)
        self.check_method(data[0], data[2], data[1], all_data)

class Meth_Manag(EchoHandler):
    """Manage methods."""
    def __init__(self):
        self.data_send = ""


    def check_exp(self, act_time):
        """Checkear expiracion del user."""
        list_del = []
        for address in Users:
            if Users[address]['expire'] <= act_time:
                list_del.append(address)
        for address in list_del:
            del Users[address]

    def checking_nonce(self, nonce, user):
        """
        method to get the number result of hash function
        with password and nonce
        """
        function_check = hashlib.md5()
        function_check.update(bytes(str(nonce), "utf-8"))
        function_check.update(bytes(user, "utf-8"))
        function_check.digest()
        return function_check.hexdigest()


    def Register(self, data, client_address):
        """handle register."""

        data = data.split('\r\n')
        _, address, protocol = data[0].split(' ')
        _, address, port = address.split(':')
        _, expire = data[1].split(' ')
        actual_time = time.time()
        exp_time = actual_time + int(expire)
        exp_time = time.strftime(ATTR_TIME, time.gmtime(exp_time))
        Users[address] = {'address': client_address[0],'port': port,
                            'expire': exp_time,}
        register2json()
        self.check_exp(time.strftime(ATTR_TIME, time.gmtime(actual_time)))

    def Invite(self, all_data, client_address):
        """handle register."""

        data = all_data.split('\r\n')
        _, address, _ = data[0].split(' ')
        _, name = address.split(':')
        # print(Users)
        address = (Users[name]['address'], Users[name]['port'])
        # print(address)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((address[0], int(address[1])))
            print('retasmita a: ',address)
            # print(data)
            my_socket.send(bytes(all_data, 'utf-8'))
            data = my_socket.recv(1024)
            cod_answer = data.decode('utf-8')
            print(cod_answer)
            return cod_answer

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    parser = make_parser()
    cHandler = CONFIGHandler()
    parser.setContentHandler(cHandler)
    parser.parse('pr.xml')

    print(time.time())
    IP = cHandler.attributs['server']['ip']
    PORT = int(cHandler.attributs['server']['puerto'])
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("\r\nFinalizado servidor")
"""

    CANCION = (sys.argv[3])

"""
