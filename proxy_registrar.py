#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor en UDP simple."""

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


try:
    _, CONFIG = sys.argv

except ValueError:
    sys.exit('Usage: python3 proxy_registrar.py config')

################INICIO#################

def checking_nonce(self, nonce, user):
    """
    method to get the number result of hash function
    with password and nonce
    """
    function_check = hashlib.md5()
    function_check.update(bytes(str(nonce), "utf-8"))
    function_check.update(bytes(self.devolver_pass(user), "utf-8"))
    function_check.digest()
    return function_check.hexdigest()


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

    def check_method(self, method, protocol, sip):
        """function for check the method."""
        methods = ['REGISTER','INVITE', 'ACK', 'BYE']
        data_send = ""
        if method in methods:
            if (protocol == 'SIP/2.0\r\n') and (sip[0:4] == 'sip:'):
                if method == 'INVITE':
                    data_send = ("SIP/2.0 100 Trying\r\n\r\n" +
                                 "SIP/2.0 180 Ringing\r\n\r\n" +
                                 "SIP/2.0 200 OK\r\n\r\n")
                elif method == 'BYE':
                    data_send = "SIP/2.0 200 OK\r\n\r\n"
                elif method == 'ACK':
                    os.system('mp32rtp -i 127.0.0.1 -p 23032 < ' +
                              CANCION)
                elif method == 'REGISTER':
                    data_send = "SIP/2.0 401 Unauthorized\r\n\r\n"
            else:
                data_send = "SIP/2.0 400 Bad Request\r\n\r\n"
        else:
            data_send = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
        self.wfile.write(bytes(data_send, 'utf-8'))

    def handle(self):
        """handler server."""
        data = self.rfile.read().decode('utf-8')
        data = data.split(' ')
        print(data)
        self.check_method(data[0], data[2][0:9], data[1])

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    parser = make_parser()
    cHandler = CONFIGHandler()
    parser.setContentHandler(cHandler)
    parser.parse('pr.xml')

    IP = cHandler.attributs['server']['ip']
    PORT = int(cHandler.attributs['server']['puerto'])
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()
"""

    CANCION = (sys.argv[3])

"""
