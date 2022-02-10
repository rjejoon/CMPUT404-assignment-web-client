#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Jejoon Ryu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self, url):
        o = urllib.parse.urlparse(url)
        host = o.hostname
        port = o.port if o.port else 80
        return host, port

    def get_path(self, url):
        o = urllib.parse.urlparse(url)
        return o.path if o.path else '/'

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        l = data.split('\r\n')
        status = l[0]
        return int(status.split(' ')[1])

    def get_headers(self, data):
        l = data.split('\r\n')
        i = l.index('')
        return l[:i]

    def get_body(self, data):
        l = data.split('\r\n')
        i = l.index('')
        return l[i+1]
    
    def sendall(self, data):
        try:
            self.socket.sendall(data.encode('utf-8'))
        except socket.error:
            print("Error: GET send failed")
            sys.exit(1)

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        try:
            ret = buffer.decode('utf-8')
        except UnicodeDecodeError:
            ret = buffer.decode('ISO-8859-1')
        return ret

    def GET(self, url, args=None):
        headers = []
        host, port = self.get_host_port(url)
        ip = socket.gethostbyname(host)
        self.connect(ip, port)

        headers.append(f'GET {self.get_path(url)} HTTP/1.0')
        headers.append(f'Host: {host}')
        headers.append('\r\n')     # finish header

        self.sendall('\r\n'.join(headers))
        reply = self.recvall(self.socket)
        self.close()

        code = self.get_code(reply)
        headers = self.get_headers(reply)
        body = self.get_body(reply)
        print(code)
        print(headers)
        print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
