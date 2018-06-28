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


try:
    _, CONFIG = sys.argv

except ValueError:
    sys.exit('Usage: python3 proxy_registrar.py config')

################INICIO#################

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
    Passwords = {'a':'po'}


    def register2json(self):
        """metodo para registrar usuarios en json."""
        with open('registered.json', 'w') as outfile:
            json.dump(self.Users, outfile, indent=3)

    def json2registered(self):
        """metodo para leer json externo."""
        try:
            with open('registered.json', 'r') as infile:
                self.Users = json.load(infile)
        except:
            print('bjbj')

    def json2paswords(self):
        """metodo para leer passwords externos."""
        try:
            with open('passwords.json', 'r') as infile:
                self.Passwords = json.load(infile)
                print(self.Passwords)
        except:
            print('koko')

    def check_method(self, method, protocol, sip, data):
        """function for check the method."""
        methods = ['REGISTER','INVITE', 'ACK', 'BYE']
        data_send = ""
        if method in methods:
            # if 1 == 1:

            if (protocol == 'SIP/2.0') and (sip[0:4] == 'sip:'):
                if method == 'REGISTER':
                    print(len(data.split('\r\n')))
                    if len(data.split('\r\n')) == 5:
                        self.Register(data, self.client_address)
                        data_send = "SIP/2.0 200 OK\r\n\r\n"
                    else:
                        data_send = "SIP/2.0 401 Unauthorized\r\n"
                        data_send += 'WWW Authenticate: Digest nonce="{}"\r\n\r\n'
                        data_send = data_send.format(NONCE)
                elif method == 'INVITE':
                    self.Invite(data, self.client_address)
                elif method == 'ACK':
                    self.ACK(data, self.client_address)
            else:
                data_send = "SIP/2.0 400 Bad Request\r\n\r\n"
        else:
            data_send = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
        self.wfile.write(bytes(data_send, 'utf-8'))

    def handle(self):
        """handler server."""
        if not self.Users:
            print('nousers')
            self.json2registered()
        self.json2paswords()
        all_data = self.rfile.read().decode('utf-8')
        # print('por aki ha pasao: ', all_data)
        data = all_data.split('\r\n')
        data = data[0].split(' ')
        # print(data)
        self.check_method(data[0], data[2], data[1], all_data)

    def check_exp(self, act_time):
        """Checkear expiracion del user."""
        list_del = []
        for address in self.Users:
            if self.Users[address]['expire'] <= act_time:
                list_del.append(address)
        for address in list_del:
            del self.Users[address]
        self.register2json()

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
        # if len(data) != 5:
        #     pass
        print(len(data), data)
        _, address, protocol = data[0].split(' ')
        _, address, port = address.split(':')
        _, expire = data[1].split(' ')
        actual_time = time.time()
        exp_time = actual_time + int(expire)
        exp_time = time.strftime(ATTR_TIME, time.gmtime(exp_time))
        self.Users[address] = {'address': client_address[0],'port': port,
                            'expire': exp_time,}
        self.register2json()
        self.check_exp(time.strftime(ATTR_TIME, time.gmtime(actual_time)))
        print(self.checking_nonce(NONCE,'pepe'))

    def Auth_Register(arg):
        pass

    def Invite(self, all_data, client_address):
        """handle register."""

        origen = all_data.split('o=')[1]
        origen = origen.split(' ')[0]
        address_origen = (self.Users[origen]['address'], self.Users[origen]['port'])
        print(address_origen)
        data = all_data.split('\r\n')
        _, address, _ = data[0].split(' ')
        _, name = address.split(':')
        # print(self.Users)
        address = (self.Users[name]['address'], self.Users[name]['port'])
        # print(address)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((address[0], int(address[1])))
            print('retasmita a: ',address)
            # print(data)
            my_socket.send(bytes(all_data, 'utf-8'))
            data2 = my_socket.recv(1024)
            my_socket.connect((address_origen[0], int(address_origen[1])))
            my_socket.send(data2)

        def ACK(self, all_data, client_address):
            data = all_data.split('\r\n')
            _, address, _ = data[0].split(' ')
            _, name = address.split(':')
            # print(self.Users)
            address = (self.Users[name]['address'], self.Users[name]['port'])
            # print(address)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.connect((address[0], int(address[1])))
                print('retasmita a: ',address)
                # print(data)
                my_socket.send(bytes(all_data, 'utf-8'))


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
