#!/usr/bin/env python
# A simple Python IRC bot for monitoring github webhooks
# Forked from hardmath123.github.io/socket-science-2.html

import json
import socket
import select
import random
import ssl
import sys
import time

if len(sys.argv) != 6:
  if len(sys.argv) != 5:
    print "Usage: python %s <host> <channel (no #)> [--ssl|--plain] <nick> <hookport>" % sys.argv[0]
    exit(0)


HOST = sys.argv[1]
CHANNEL = "#"+sys.argv[2]
SSL = sys.argv[3].lower() == '--ssl'
PORT = 6697 if SSL else 6667
#HKPT = 4444 if not sys.argv[5] else sys.argv[5] # the port the bot will listen on for hook events. not supported yet

NICK = sys.argv[4]

plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = ssl.wrap_socket(plain) if SSL else plain

connected = False

def got_message(message):
  print message
  global connected # yes, bad Python style. but it works to explain the concept, right?
  words = message.split(' ')
  if 'PING' in message:
    s.sendall(bytes(message.replace('PING', 'PONG')) + '\r\n') # it never hurts to do this :)
  if words[1] == '001' and not connected:
    # As per section 5.1 of the RFC, 001 is the numeric response for
    # a successful connection/welcome message.
    connected = True
    s.sendall("JOIN %s\r\n"%(CHANNEL))
    print "Joining..."
    s.sendall("MODE %s +B\r\n" % NICK) # marks this as a bot
  elif words[1] == 'PRIVMSG' and words[2] == CHANNEL and connected:
    # Might add some commands here later :3
    pass

def read_loop(callback):
  data = ""
  CRLF = '\r\n'
  while True:
    time.sleep(1)
    try:
      readables, writables, exceptionals = select.select([s],[s],[s])
      if s in readables:
        data += s.recv(512)
        while CRLF in data:
          message = data[:data.index(CRLF)]
          data = data[data.index(CRLF)+2:]
          callback(message)
    except KeyboardInterrupt:
      print "Leaving..."
      s.sendall("QUIT %s :Bye\r\n"%(CHANNEL))
      s.close()
      exit(0)


# The main part of the program starts here

print "Connecting..."

s.connect((HOST, PORT))

print "Registering..."

s.sendall("NICK %s\r\n"%(NICK))
s.sendall("USER %s * * :A git repo hook bot\r\n"% NICK)

read_loop(got_message)
