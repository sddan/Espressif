# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 21:20:10 2018

@author: Samuel
"""

import socket, machine, time
from ubinascii import hexlify
from dht import DHT22

device = "ESP8266"

name_rev = str(hexlify(machine.unique_id()).decode("utf-8"))
name = ''
for i in range(len(name_rev), 0, -2):
    name = name + name_rev[i - 2 : i]
name = name[2:len(name)]

class PIR:
    rowdata = """<b>Object Name:</b> %s<br><b>Pin:</b> %s<br><b>Status:</b> %s"""
    
    def __init__(self, name_, pin_):
        self.name = name_
        self.pin = machine.Pin(pin_, machine.Pin.IN, machine.Pin.PULL_DOWN)
    
    def occupancy(self):
        val = self.pin.value()
        if val == 1: status = True
        else: status = False
        return status
    
# =============================================================================
#     def http_row(self):
#         obj_type = 'PIR'
#         
#         data = PIR.rowdata % (self.name, str(self.pin), self.status())
#         return (httpsrv.tablerow %(obj_type, data))
# =============================================================================

class LED:
    rowdata = """<b>Object Name:</b> %s<br><b>Pin:</b> %s<br><b>Status:</b> %s<br><b>Operation:</b> %s"""
    
    def __init__(self, name_, pin_, activestate_ = True):
        self.name = name_
        print('Set up LED with name', name_)
        self.pin = machine.Pin(pin_, machine.Pin.OUT)
        print('Set up LED', name_,  'on GPIO pin', pin_)
        self.activestate = activestate_
        print('LED', name_, 'active state is', activestate_)
        self.status = False
    
    def on(self, timer = 0):
        self.pin.value(1 & self.activestate)
        self.status = True
    
    def off(self, timer = 0):
        self.pin.value(1 ^ self.activestate)
        self.status = False
    
# =============================================================================
#     def http_row(self):
#         obj_type = 'LED'
#         
#         if self.activestate == 1: op = "Active High"
#         else: op = "Active Low"
#         
#         data = LED.rowdata % (self.name, str(self.pin), self.status(), op)
#         return (httpsrv.tablerow %(obj_type, data))        
# =============================================================================
    
class dht22:
    rowdata = """<b>Object Name:</b> %s<br><b>Pin:</b> %s<br><b>Temp:</b> %f C<br><b>Humidity:</b> %f \%"""
    
    def __init__(self, name_, pin_):
        self.name = name_
        print('Set up DHT22 sensor with name', name_)
        self.pin = machine.Pin(pin_, machine.Pin.IN, machine.Pin.PULL_UP)
        self.object = DHT22(self.pin)
        print('Set up DHT22 sensor', name_,  'on GPIO pin', pin_)
        self.temperature = -1
        self.humidity = -1
        self.retry = 0
    
    def measure(self, timer = 0):
        try:
            time.sleep(2.2)
            self.object.measure()
            print('Single DHT22 measurement')
            self.temperature = self.object.temperature()
            self.humidity = self.object.humidity()
        
        except (KeyboardInterrupt, SystemExit):
            raise

    
# =============================================================================
#     def http_row(self):
#         obj_type = 'dht22'
#         data = dht22.rowdata % (self.name, str(self.pin), self.temperature, 1, self.humidity, 2)
#         return (httpsrv.tablerow %(obj_type, data))
# =============================================================================
        
# =============================================================================
# class httpsrv:
#     response = "<!DOCTYPE html><html>%s</html>"
#     header = "<head><title>ESP8266</title></head>"
#     body = """
#     <body>
#         <table border = "1">
#             <thead>Device Data<thead>
#             <tbody>
#             %s
#             </tbody>
#         </table>        
#     </body>
#     """
#     tablerow = "<tr><td>%s</td><td>%s</td></tr>"
# 
#     def __init__(self, addr_, port_):
#         self.addr = addr_
#         self.port = port_
#         
#         #Create socket object
#         self.s = socket.socket()
#         
#         #Allow the socket to be reused after a client connection is served
#         self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         
#         #Registering a callback function to be called upon a client connection
#         self.s.setsockopt(socket.SOL_SOCKET, 20, self.cb)
#     
#     def start(self):
#         self.listen_addr = socket.getaddrinfo(str(self.addr), int(self.port))[0][-1]
#         
#         #Bind the created socket to the given address range
#         self.s.bind(self.listen_addr)
#         
#         self.s.listen(1)
#         
#     def stop(self):
#         self.s.close()
#     
#     def cb(self, socket_):
#         cl_s, client_addr = socket_.accept()
#         print('Client connected from:', client_addr)
#         cl_s_file = cl_s.makefile('rwb', 0)
#         while True:
#             line = cl_s_file.readline()
#             #print('makefile from client connection:', line)
#             if not line or line == b'\r\n':
#                 break
#         cl_s.send(self.resp())
#     
#     def resp(self):
#         resprows = []
#         resprows.append(httpsrv.tablerow % ('ESP8266', '<b>Unique ID:</b> ' + self.parent_obj.name))
#         for obj in self.parent_obj.IO:
#             if obj is not None:
#                 resprows.append(obj.http_row())
#             else: pass
#             
#         resprows.append(self.http_row())
#         respbody = httpsrv.body % '\n'.join(resprows)
#         resp = httpsrv.response % respbody
#         return resp
#     
#     def http_row(self):
#         rowdata = """<b>Listen address range: </b>%s<br><b>Port: </b>%d"""
#         rowdata = rowdata % (self.addr, self.port)
#         return(httpsrv.tablerow % ('HTTP Server', rowdata))
# =============================================================================
