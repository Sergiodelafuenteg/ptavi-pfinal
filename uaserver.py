#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor en UDP simple."""

import socketserver
import sys
import os
from uaclient import CONFIGHandler

try:
    _, CONFIG = sys.argv

except ValueError:
    sys.exit('Usage: python3 uaserver.py config')

########################INICIO#################

class Configurator(CONFIGHandler):

    """Configurator."""
    def __init__(self, metodo, option):
        """initialize selfs"""
        parser = make_parser()
        self.cHandler = CONFIGHandler()
        parser.setContentHandler(self.cHandler)
        parser.parse(CONFIG)

        self.login = self.cHandler.attributs['account']['username']
        self.password = self.cHandler.attributs['account']['passwd']
        self.ip = self.cHandler.attributs['uaserver']['ip']
        self.port = self.cHandler.attributs['uaserver']['puerto']
        self.rtpport = self.cHandler.attributs['rtpaudio']['puerto']
        self.PX_SERVER = self.cHandler.attributs['regproxy']['ip']
        self.PX_PORT = int(self.cHandler.attributs['regproxy']['puerto'])
        self.log_path = self.cHandler.attributs['log']['path']
        self.audio_path = self.cHandler.attributs['audio']['path']


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def check_method(self, method, protocol, sip):
        """function for check the method."""
        methods = ['INVITE', 'ACK', 'BYE']
        data_send = ""
        if method in methods:
            if (protocol == 'SIP/2.0\r\n\r\n') and (sip[0:4] == 'sip:'):
                if method == 'INVITE':
                    data_send = ("SIP/2.0 100 Trying\r\n\r\n" +
                                 "SIP/2.0 180 Ringing\r\n\r\n" +
                                 "SIP/2.0 200 OK\r\n\r\n")
                elif method == 'BYE':
                    data_send = "SIP/2.0 200 OK\r\n\r\n"
                elif method == 'ACK':
                    os.system('mp32rtp -i 127.0.0.1 -p 23032 < ' +
                              CANCION)
            else:
                data_send = "SIP/2.0 400 Bad Request\r\n\r\n"
        else:
            data_send = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
        self.wfile.write(bytes(data_send, 'utf-8'))

    def handle(self):
        """handler server."""
        data = self.rfile.read().decode('utf-8')
        metodo, sip_address, protocol = data.split(' ')
        self.check_method(metodo, protocol, sip_address)

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos

    serv = socketserver.UDPServer((IP, PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()
