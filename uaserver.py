#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor en UDP simple."""

import socketserver
import sys
import os
from xml.sax import make_parser
from threading import Thread
from uaclient import CONFIGHandler#, Configurator

CONFIG = ""
########################INICIO#################

def Listen(ip,port):
    os.system('cvlc rtp://@{}:{} 2> /dev/null'.format(ip,port))

def Send_music(ip,port,path):
    os.system('mp32rtp -i {} -p {} < {}'.format(ip, port, path))

class Configurator(CONFIGHandler):

    """Configurator."""
    def __init__(self):
        """initialize selfs"""
        parser = make_parser()
        self.cHandler = CONFIGHandler()
        parser.setContentHandler(self.cHandler)
        parser.parse(CONFIG)

        self.login = self.cHandler.attributs['account']['username']
        self.password = self.cHandler.attributs['account']['passwd']
        self.ip = self.cHandler.attributs['uaserver']['ip']
        self.port = int(self.cHandler.attributs['uaserver']['puerto'])
        self.rtpport = self.cHandler.attributs['rtpaudio']['puerto']
        self.PX_SERVER = self.cHandler.attributs['regproxy']['ip']
        self.PX_PORT = int(self.cHandler.attributs['regproxy']['puerto'])
        self.log_path = self.cHandler.attributs['log']['path']
        self.audio_path = self.cHandler.attributs['audio']['path']

class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""
    print('popop')

    def check_method(self, method, protocol, sip):
        """function for check the method."""
        config = Configurator()
        Hilo_listen = Thread(target = Listen, args = (config.ip, config.rtpport))
        Hilo_Send = Thread(target = Send_music, args = (config.ip,
                                                       config.rtpport,
                                                       config.audio_path))

        methods = ['INVITE', 'ACK', 'BYE']
        data_send = ""
        if method in methods:
            if (protocol == 'SIP/2.0') and (sip[0:4] == 'sip:'):
                if method == 'INVITE':
                    busy = False
                    if not busy:
                        print('nobusy')
                    print('loase')
                    data_send = ("SIP/2.0 100 Trying\r\n\r\n" +
                                 "SIP/2.0 180 Ringing\r\n\r\n" +
                                 "SIP/2.0 200 OK\r\n\r\n")
                    data_send+= ('Content-Type: application/sdp\r\n\r\n' +
                                'v=0\r\n' +
                                'o={} {}\r\n'.format(config.login, config.ip) +
                                's=misesion\r\n' +
                                't=0\r\n' +
                                'm=audio {} RTP\r\n\r\n'.format(config.rtpport))
                elif method == 'BYE':
                    data_send = "SIP/2.0 200 OK\r\n\r\n"
                    os.system("killall Hilo_listen")
                    os.system("killall Hilo_Send")
                elif method == 'ACK':
                    Hilo_listen.start()
                    Hilo_Send.start()
            else:
                data_send = "SIP/2.0 400 Bad Request\r\n\r\n"
        else:
            data_send = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
        self.wfile.write(bytes(data_send, 'utf-8'))
        print(data_send)

    def handle(self):
        """handler server."""
        data = self.rfile.read().decode('utf-8')
        print(data)
        data = data.split('\r\n')
        metodo, sip_address, protocol = data[0].split(' ')
        print(metodo + ' || ' + sip_address + ' || ' + protocol)
        self.check_method(metodo, protocol, sip_address)

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    try:
        CONFIG = sys.argv[1]

    except ValueError:
        sys.exit('Usage: python3 uaserver.py config')

    config = Configurator()

    serv = socketserver.UDPServer((config.ip, config.port), EchoHandler)
    print("Listening...")
    print(config.ip,config.port)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("\r\nFinalizado servidor")
