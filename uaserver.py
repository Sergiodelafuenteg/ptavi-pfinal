#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor en UDP simple."""

import socketserver
import sys
import os
from xml.sax import make_parser
from threading import Thread
from uaclient import CONFIGHandler, Log

CONFIG = ""
########################INICIO#################

def Listen(ip,port):
    os.system('cvlc rtp://@{}:{} 2> /dev/null'.format(ip,port))

def Send_music(ip,port,path):
    os.system('./mp32rtp -i {} -p {} < {}'.format(ip, port, path))

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
        self.otherrtpport =''

class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""
    print('popop')

    def check_method(self, method, protocol, sip, all_data):
        """function for check the method."""
        config = Configurator()
        log = Log(config.log_path)
        Hilo_listen = Thread(target = Listen, args = (config.ip, config.rtpport))
        Hilo_Send = Thread(target = Send_music, args = (config.ip,
                                                       config.otherrtpport,
                                                       config.audio_path))

        methods = ['INVITE', 'ACK', 'BYE', 'SIP/2.0']
        data_send = ""
        busy = False
        if method in methods:
            if (protocol == 'SIP/2.0') and (sip[0:4] == 'sip:'):
                if method == 'INVITE':
                    if not busy:
                        data_send = ("SIP/2.0 100 Trying\r\n\r\n" +
                                     "SIP/2.0 180 Ringing\r\n\r\n" +
                                     "SIP/2.0 200 OK\r\n\r\n")
                        data_send+= ('Content-Type: application/sdp\r\n\r\n' +
                                    'v=0\r\n' +
                                    'o={} {}\r\n'.format(config.login, config.ip) +
                                    's=misesion\r\n' +
                                    't=0\r\n' +
                                    'm=audio {} RTP\r\n\r\n'.format(config.rtpport))
                    else:
                        data_send = "SIP/2.0 480 Temporarily Unavailable\r\n\r\n"
                elif method == 'BYE':
                    data_send = "SIP/2.0 200 OK\r\n\r\n"
                    os.system('pkill -9 vlc')
                    os.system('pkill -9 mp3')
                    busy = False
                elif method == 'ACK':
                    busy = True
                    Hilo_listen.start()
                    Hilo_Send.start()
            elif protocol == 'Trying':
                option = all_data.split('audio ')
                option = option[1].split(' ')[0]
                config.otherrtpport = option
                Hilo_Send = Thread(target = Send_music, args = (config.ip,
                                                               config.otherrtpport,
                                                               config.audio_path))
                origen = all_data.split('o=')[1]
                origen = origen.split(' ')[0]
                Hilo_listen.start()
                Hilo_Send.start()
                data_send = ' '.join(["ACK", "sip:" + origen, 'SIP/2.0\r\n\r\n'])
            else:
                data_send = "SIP/2.0 400 Bad Request\r\n\r\n"
        else:
            data_send = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
        self.wfile.write(bytes(data_send, 'utf-8'))
        log.Send(config.PX_SERVER, config.PX_PORT, data_send)
        print(data_send)

    def handle(self):
        """handler server."""
        log = Log(config.log_path)
        data = self.rfile.read().decode('utf-8')
        log.Recv(config.PX_SERVER, config.PX_PORT, data)
        print(data)
        all_data = data
        data = data.split('\r\n')
        print(data)
        metodo, sip_address, protocol = data[0].split(' ')
        print(metodo + ' || ' + sip_address + ' || ' + protocol)
        self.check_method(metodo, protocol, sip_address, all_data)

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
