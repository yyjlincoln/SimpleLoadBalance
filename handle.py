#Created by Lincoln Yan - https://github.com/yyjlincoln
#Date: 20181103

#imports
from socket import socket, SHUT_RDWR
from threading import Thread
from _thread import start_new,exit_thread
from errors import StatusMonitor
from errors import printlog as print
import hashlib, base64, random
import string
from urllib import parse
import os

LoadBalance={'yyjlincoln.win':('localhost',83),'yyjlincoln.xyz':('localhost',83),'wechat.yyjlincoln.win':('localhost',81),'wechat.yyjlincoln.xyz':('localhost',81),'files.yyjlincoln.xyz':('localhost',82),'files.yyjlincoln.win':('localhost',82)}

@StatusMonitor(allow_error=True)
class Handle(Thread): # Handles requests
    @StatusMonitor(allow_error=True)
    def __init__(self,sx,addr):
        Thread.__init__(self)
        self.sx=sx
        self.addr=addr

    @StatusMonitor(allow_error=True)
    def run(self):
        sx=self.sx
        addr=self.addr
        #处理事件
        ConnectionEstablished(sx,addr)

@StatusMonitor(allow_error=True,print_error=False)
def Forward_Rec(fromsx,tosx):
    continous=0
    while True:
        try:
            data=fromsx.recv(20480)
            if data==b'':
                continous+=1
                if continous>=3:
                    raise Exception('Connection Reset.')
                    return
            else:
                continous=0
                tosx.send(data)
        except:
            tosx.shutdown(SHUT_RDWR)
            tosx.close()
#            fromsx.shutdown(SHUT_RDWR)
#            fromsx.close()
            return

@StatusMonitor(allow_error=True,print_error=False)
def ConnectionEstablished(sx,addr):
    header=sx.recv(20480).decode()
    HostAna=header.split('Host: ')
    if len(HostAna)>1:
        Host=HostAna[1].split('\r\n')[0]
    if Host in LoadBalance:
#        print('Load Balance',level='[Info]')
        So=socket()
        try:
            So.connect(LoadBalance[Host])
            So.send(header.encode())
            start_new(Forward_Rec,(sx,So))
            start_new(Forward_Rec,(So,sx))            
        except:
            So.close()
            sx.close()
            print('Unable to connect',level='[Error]')
    else:
        sx.close()
    
