#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
    #def get_host_port(self,url):

    def connect(self, host, port):
        
        # Try to connect to the giving host and port
        try:
            self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.socket.connect( ( host, port ) )
            
        # If the connection is failed, tell to stdout and exit the process
        except:
            print( f"Failed to connect the host: {host} - port: {port}" )
            sys.exit( 1 )

        print( f"Connected to the host: {host} - port: {port}" )
        
        return host, port

    def get_code(self, data):
        return int( data.split()[ 1 ] )

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split( "\r\n\r\n" )[ 1 ]
    
    def sendall(self, data):
        
        # Try to send
        try:
            self.socket.sendall( data.encode( 'utf-8' ) )
            
        # If the send is failed, tell the stdout and close the connection, then exit the process
        except:
            print( "Failed to send" )
            self.close()
            sys.exit( 1 )
        
    def close(self):
        
        # Try to close
        try:
            self.socket.close()
            
        # If close is failed, exit the process, maybe the parent process doing recycle will auto close the connection? 
        except:
            print( "Failed to close" )
            sys.exit( 1 )

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            
            # Try to recv
            try:
                part = sock.recv( 1024 )
                if ( part ): buffer.extend( part )
                else: done = not part
                    
            # If the recv is failed, tell the stdout and close the connection, then exit the process
            except:
                print( "Failed to recv" )
                self.close()
                sys.exit( 1 )
                
        return buffer.decode( 'utf-8' )

    def GET(self, url, args=None):
        code = 500
        body = ""

        path = ""
        port = None
        host = None

        # Get the host and port from giving url
        # Source: https://docs.python.org/3/library/urllib.parse.html
        o = urllib.parse.urlparse( url )
        
        host = o.hostname
        port = o.port
        path = o.path

        # Check the port and host is valid
        # Source: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1821150
        if ( port is None ): port = 80
        if ( o is None ) or ( host is None ) or ( host == "" ):
            print( f"Failed to get the information from URL: {url}" )
            sys.exit( 1 )

        # Check the path is invaild or empty, giving the root path
        if ( path is None ) or ( path == "" ): path = "/"

        # Connect to the host and port
        host, port = self.connect( host, port )
        
        # Create a POST request of URL format
        # Source 1: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers
        # Source 2: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1818167
        # Source 3: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Connection
        get_request = f"GET {path} HTTP/1.1\r\n" + \
                      f"Host: {host}\r\n" + \
                      f"Accept: */*\r\n" + \
                      f"Accept-Charset: utf-8\r\n" + \
                      f"Connection: close\r\n\r\n"

        print( "\n-------- GET Request --------" )
        print( get_request )

        # Send a GET request
        self.sendall( get_request )

        # Get the response of that request
        get_response = self.recvall( self.socket )
        
        print( "-------- GET Response --------" )
        print( get_response )

        # Close the connection
        self.close()
        
        return HTTPResponse( self.get_code( get_response ), self.get_body( get_response ) )

    def POST(self, url, args=None):
        code = 500
        body = ""

        # Get the host and port from giving url
        # Source: https://docs.python.org/3/library/urllib.parse.html
        o = urllib.parse.urlparse( url )

        host = o.hostname
        port = o.port
        path = o.path
        url_args = ""

        # Check the port and host is valid
        # Source: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1821150
        if ( port is None ): port = 80
        if ( o is None ) or ( host is None ) or ( host == "" ):
            print( f"Failed to get the information from URL: {url}" )
            sys.exit( 1 )

        # Check the path is invaild or empty, giving the root path
        if ( path is None ) or ( path == "" ): path = "/"

        # Check the args is giving or not, if giving, transfer from dictionary to URL parameters (From freetest.py we saw the POST(args={dictionary}))
        # Source: https://stackoverflow.com/questions/1233539/python-dictionary-to-url-parameters
        if ( args is None ): url_args = ""
        else: url_args = urllib.parse.urlencode( args )

        # Connect to the host and port
        host, port = self.connect( o.hostname, o.port )

        # Create a POST request of URL format
        # Source 1: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers
        # Source 2: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1818167
        # Source 3: https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Connection
        post_request = f"POST {path} HTTP/1.1\r\n" + \
                       f"Host: {host}\r\n" + \
                       f"Accept: */*\r\n" + \
                       f"Accept-Charset: utf-8\r\n" + \
                       f"Content-Length: {len( url_args )}\r\n" + \
                       f"Content-Type: application/x-www-form-urlencoded\r\n" + \
                       f"Connection: close\r\n\r\n" + \
                       f"{url_args}"

        print( "\n-------- POST Request --------" )
        print( post_request )

        # Send a POST request
        self.sendall( post_request )

        # Get the response of that request
        post_response = self.recvall( self.socket )
        
        print( "-------- POST Response --------" )
        print( post_response )

        # Close the connection
        self.close()
        
        return HTTPResponse( self.get_code( post_response ), self.get_body( post_response ) )

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
