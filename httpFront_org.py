#!/usr/bin/env python
#coding=utf-8



__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "bones7456"
__home_page__ = ""

#import malboxDaemon
import os, sys, platform
import posixpath
import BaseHTTPServer
from SocketServer import ThreadingMixIn
import threading
import urllib
import cgi
import shutil
import mimetypes
import re
import time
import urlparse


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
import socket
import json
import struct


port = 8080
serveraddr = ('', port)

class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "SimpleHTTPWithUpload" 

    def retResult(self, stat, result, onlyHeader=False):
        self.send_response(stat)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()
        self.wfile.write(result)
        print result

    def do_GET(self):
        """Serve a GET request."""
        path = urlparse.urlparse(self.path)
        if path.path!='/':
            self.retResult(404, "Not Found")
            return
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        pass

    def do_POST(self):
        """Serve a POST request."""
        r, info, sessionID = self.deal_post_data()
        print r, info, "by: ", self.client_address
        if r:
            resStr = json.dumps({'status':True, 'sessionID': sessionID})
        else:
            resStr = json.dumps({'status':False})
        self.retResult(200, resStr)

    def deal_post_data(self):
        boundary = self.headers.plisttext.split("=")[1]
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary", None)
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
        if not fn:
            return (False, "Can't find out file name...", None)
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = fn[0]
        from MalboxListener import UPLOAD_PATH
        try:
            out = open(UPLOAD_PATH+fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?", None)
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                #sessionID = malboxDaemon.addFile(fn)
                return (True, "File '%s' upload success!" % fn, None)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.", None)

    def send_head(self):
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n" )
        f.write("<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write("<input name=\"file\" type=\"file\"/>")
        f.write("<input type=\"submit\" value=\"upload\"/>")
        f.write("</form>\n")
        f.write("</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

class ThreadingServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass
   
if __name__ == '__main__':
    srvr = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)
    
    srvr.serve_forever()
