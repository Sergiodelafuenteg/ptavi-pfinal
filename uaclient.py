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

    def Const_Constructor(self, arg):

        METODO = METODO.upper()
        SERVER, PORT = SIP_ADDRESS.split(':')
        login, SERVER = SERVER.split('@')
        PORT = int(PORT)
        METODO = METODO.upper()
        PROTOCOL = 'SIP/2.0\r\n\r\n'
        DATA = ' '.join([METODO.upper(), "sip:" + SIP_ADDRESS, PROTOCOL])


class Configurator(object):
    """Configurator."""
    def __init__(self, arg):
        self.arg = arg



#######################MAIN#######################

if __name__ == '__main__':

    parser = make_parser()
    cHandler = CONFIGHandler()
    parser.setContentHandler(cHandler)
    parser.parse(CONFIG)
    print(cHandler.get_tags())


    print("jajaj")



"""
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((SERVER, PORT))
    my_socket.send(bytes(DATA, 'utf-8'))
    data = my_socket.recv(1024)
    cod_answer = data.decode('utf-8').split(' ')[-2]
    if (cod_answer == '200') and (METODO != 'BYE'):
        DATA = ' '.join(["ACK", "sip:" + SIP_ADDRESS, PROTOCOL])
        my_socket.send(bytes(DATA, 'utf-8'))
"""
