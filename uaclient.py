#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from threading import Thread
import hashlib
import time


################INICIO#################
NONCE = ''

def Listen(ip,port):
    """Escuchar."""
    os.system('cvlc --play and exit rtp://@{}:{} 2> /dev/null'.format(ip,port))

def Send_music(ip,port,path):
    """Mandar."""
    os.system('./mp32rtp -i {} -p {} < {}'.format(ip, port, path))

class Log():
    """Class para loggear todo."""
    def __init__(self, log_path):
        """Init."""
        self.log_path = log_path
        self.f = open (self.log_path, 'a')
        text = time.strftime('%Y%m%d%H%M%S', time.gmtime(int(time.time()+7200)))
        text += ' Starting...\r\n'
        self.f.write(text)
    def Send(self, ip, port, sip_text):
        self.f = open (self.log_path, 'a')
        text = time.strftime('%Y%m%d%H%M%S', time.gmtime(int(time.time()+7200)))
        text += ' Sent to {}:{}: {}\r\n'.format(ip,port,sip_text)
        self.f.write(text)
    def Recv(self, ip, port, sip_text):
        self.f = open (self.log_path, 'a')
        text = time.strftime('%Y%m%d%H%M%S', time.gmtime(int(time.time()+7200)))
        text += ' Received from {}:{}: {}\r\n'.format(ip,port,sip_text)
        self.f.write(text)

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
        """Devuelve la lista."""
        return self.list


class Configurator(CONFIGHandler):
    """Configurator."""

    def __init__(self, metodo, option):
        """initialize selfs."""
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
        self.otherrtpport = ''
        self.check_method(metodo, option)

    def check_method(self, method, option):
        """Que metodo usa?."""
        methods = ['REGISTER','INVITE', 'ACK', 'BYE', 'REGISTERLOG']
        PROTOCOL = 'SIP/2.0\r\n'
        # Hilo_listen = Thread(target = Listen, args = (self.ip, self.rtpport))
        # Hilo_Send = Thread(target = Send_music, args = (self.ip,
        #                                                option,
        #                                                self.audio_path))

        if method in methods:
            if method == 'REGISTER':
                PROTOCOL = 'SIP/2.0\r\n'
                self.DATA = '{} sip:{}:{} {}'.format(method, self.login,
                            self.port, PROTOCOL)
                self.DATA = self.DATA + 'Expires: ' + option + '\r\n\r\n'
            elif method == 'REGISTERLOG':
                print(NONCE)
                PROTOCOL = 'SIP/2.0\r\n'
                self.DATA = '{} sip:{}:{} {}'.format('REGISTER', self.login,
                            self.port, PROTOCOL)
                self.DATA = self.DATA + 'Expires: ' + option + '\r\n'
                self.DATA += 'Authorization: Digest response =' + NONCE + '\r\n\r\n'
            elif method == 'INVITE':
                PROTOCOL = 'SIP/2.0\r\n'
                self.DATA = ' '.join([method, "sip:" + option, PROTOCOL])
                self.DATA += 'Content-Type: application/sdp\r\n\r\n'
                self.DATA += 'v=0\r\n'
                self.DATA += 'o={} {}\r\n'.format(self.login, self.ip)
                self.DATA += 's=misesion\r\n'
                self.DATA += 't=0\r\n'
                self.DATA += 'm=audio {} RTP\r\n\r\n'.format(self.rtpport)
            elif method == 'BYE':
                self.DATA = ' '.join([method, "sip:" + option, PROTOCOL])
            elif method == 'ACK':
                PROTOCOL = 'SIP/2.0\r\n\r\n'
                self.DATA = ' '.join(["ACK", "sip:" + self.login, PROTOCOL])
                print('senack')
                # Hilo_Send.start()
                # Hilo_listen.start()


def checking_nonce(nonce, user):
    """result of hash function with password and nonce."""
    function_check = hashlib.md5()
    function_check.update(bytes(str(nonce), "utf-8"))
    function_check.update(bytes(user, "utf-8"))
    function_check.digest()
    return function_check.hexdigest()

def Meth_Handler(method, option):
    """Funcion para manejar cada metodo."""
    config = Configurator(method, option)
    log = Log(config.log_path)
    if method == 'REGISTER':
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((config.PX_SERVER, config.PX_PORT))
            # print(config.DATA)
            my_socket.send(bytes(config.DATA, 'utf-8'))
            log.Send(config.PX_SERVER, config.PX_PORT, config.DATA)
            data = my_socket.recv(1024)
            data = data.decode('utf-8')
            log.Recv(config.PX_SERVER, config.PX_PORT, config.DATA)
            cod_answer = data.split(' ')[1]
            if cod_answer == '401':
                nonce = data.split('"')[1]
                global NONCE
                NONCE = checking_nonce(nonce, config.password)
                config.check_method('REGISTERLOG',option)
                my_socket.send(bytes(config.DATA, 'utf-8'))
                log.Send(config.PX_SERVER, config.PX_PORT, config.DATA)
                data = my_socket.recv(1024)
                data = data.decode('utf-8')
                log.Recv(config.PX_SERVER, config.PX_PORT, config.DATA)
    elif method == 'INVITE':
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((config.PX_SERVER, config.PX_PORT))
            # print(config.DATA)
            my_socket.send(bytes(config.DATA, 'utf-8'))
            log.Send(config.PX_SERVER, config.PX_PORT, config.DATA)


    elif method == 'BYE':
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((config.PX_SERVER, config.PX_PORT))
            my_socket.send(bytes(config.DATA, 'utf-8'))
            log.Send(config.PX_SERVER, config.PX_PORT, config.DATA)
            data = my_socket.recv(1024)
            data = data.decode('utf-8')
            log.Recv(config.PX_SERVER, config.PX_PORT, config.DATA)

#######################MAIN#######################

if __name__ == '__main__':

    try:
        _, CONFIG, METODO, OPTION = sys.argv
        METODO = METODO.upper()

    except ValueError:
        sys.exit('Usage: python3 uaclient.py config method option')

    config = Configurator(METODO, OPTION)

    Meth_Handler(METODO, OPTION)
        #
        # if (cod_answer == '200') and (METODO != 'BYE'):
        #     config.check_method('ACK',5)
        #     my_socket.send(bytes(config.DATA, 'utf-8'))
