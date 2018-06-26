#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler



################INICIO#################


class CONFIGHandler(ContentHandler):
    """Clase para manejar CONFIG."""
    def __init__(self):
        """Constructor. Inicializamos las variables."""
        self.list = []
        self.attributs = {}
        self.tags = {
            'account': ['username', 'passwd'],
            'uaserver': ['ip', 'puerto'],
            'rtpaudio': ['puerto'],
            'regproxy': ['ip', 'puerto'],
            'log': ['path'],
            'audio': ['path']}

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
        self.port = int(self.cHandler.attributs['uaserver']['puerto'])
        self.rtpport = self.cHandler.attributs['rtpaudio']['puerto']
        self.PX_SERVER = self.cHandler.attributs['regproxy']['ip']
        self.PX_PORT = int(self.cHandler.attributs['regproxy']['puerto'])
        self.log_path = self.cHandler.attributs['log']['path']
        self.audio_path = self.cHandler.attributs['audio']['path']

        metodo = metodo.upper()
        self.check_method(metodo, option)

    def check_method(self, method, option):
        methods = ['REGISTER','INVITE', 'ACK', 'BYE']
        if method in methods:
            if method == 'REGISTER':
                PROTOCOL = 'SIP/2.0\r\n'
                self.DATA = ' '.join([method, "sip:" + self.login, PROTOCOL])
                self.DATA = '{} sip:{}:{} {}'.format(method, self.login,
                            self.port, PROTOCOL)
                self.DATA = self.DATA + 'Expires: ' + option + '\r\n\r\n'
            elif method == 'INVITE':
                PROTOCOL = 'SIP/2.0\r\n'
                self.DATA = ' '.join([method, "sip:" + option, PROTOCOL])
                self.DATA += 'Content-Type: application/sdp\r\n\r\n'
                self.DATA += 'v=0\r\n'
                self.DATA += 'o={} {}\r\n'.format(self.login, self.ip)
                self.DATA += 's=misesion\r\n'
                self.DATA += 't=0\r\n'
                self.DATA += 'm=audio {} RTP\r\n\r\n'.format(self.rtpport)
            elif method == 'ACK':
                PROTOCOL = 'SIP/2.0\r\n\r\n'
                self.DATA = ' '.join(["ACK", "sip:" + self.login, PROTOCOL])
                print('senack')

def Code_Manager(cod_answer):
    codes = ['200','400', '401', '404', '405']
    if method in methods:
        if cod_answer == '200':
            pass
        elif cod_answer == '400':
            pass
        elif cod_answer == '401':
            pass
        elif cod_answer == '404':
            pass
        elif cod_answer == '405':
            pass

#######################MAIN#######################

if __name__ == '__main__':

    try:
        _, CONFIG, METODO, OPTION = sys.argv

    except ValueError:
        sys.exit('Usage: python3 uaclient.py config method option')

    config = Configurator(METODO, OPTION)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.connect((config.PX_SERVER, config.PX_PORT))
        # print(config.DATA)
        my_socket.send(bytes(config.DATA, 'utf-8'))
        data = my_socket.recv(1024)
        cod_answer = data.decode('utf-8')
        print(cod_answer)

        if (cod_answer == '200') and (METODO != 'BYE'):
            config.check_method('ACK',5)
            my_socket.send(bytes(config.DATA, 'utf-8'))
