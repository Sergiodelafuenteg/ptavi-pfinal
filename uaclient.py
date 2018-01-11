#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


try:
    _, CONFIG, METODO, OPTION = sys.argv

except ValueError:
    sys.exit('Usage: python3 uaclient.py config method option')

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

        self.PX_SERVER = self.cHandler.attributs['regproxy']['ip']
        self.PX_PORT = int(self.cHandler.attributs['regproxy']['puerto'])
        self.login = self.cHandler.attributs['account']['username']
        self.password = self.cHandler.attributs['account']['passwd']
        metodo = metodo.upper()
        self.check_method(metodo, option)

    def check_method(self, method, option):
        methods = ['REGISTER','INVITE', 'ACK', 'BYE']
        if method in methods:
            if method == 'REGISTER':
                PROTOCOL = 'SIP/2.0\r\n'
                self.DATA = ' '.join([method, "sip:" + self.login, PROTOCOL])
                self.DATA = self.DATA + 'Expires: ' + option + '\r\n\r\n'
            elif method == 'INVITE':
                PROTOCOL = 'SIP/2.0\r\n\r\n'
                self.DATA = ' '.join([method, "sip:" + self.login, PROTOCOL])

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

    config = Configurator(METODO, OPTION)


    print("jajaj")




with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((config.PX_SERVER, config.PX_PORT))
    my_socket.send(bytes(config.DATA, 'utf-8'))
    data = my_socket.recv(1024)
    print(data)
    cod_answer = data.decode('utf-8').split(' ')[-2]
    if (cod_answer == '200') and (METODO != 'BYE'):
        DATA = ' '.join(["ACK", "sip:" + SIP_ADDRESS, PROTOCOL])
        my_socket.send(bytes(DATA, 'utf-8'))
