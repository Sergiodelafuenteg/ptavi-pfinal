#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor en UDP simple."""

import socketserver
import sys
import os


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
    if len(sys.argv) != 4:
        sys.exit("Usage: python3 server.py IP port audio_file")
    IP = sys.argv[1]
    PORT = int(sys.argv[2])
    CANCION = (sys.argv[3])
    serv = socketserver.UDPServer((IP, PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()
