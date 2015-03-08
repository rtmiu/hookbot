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

from server import HookServer

if len(sys.argv) != 6:
  print "Usage: python %s <host> <channel (no #)> [--ssl|--plain] <nick> <hookport>" % sys.argv[0]
  exit(0)


HOST = sys.argv[1]
CHANNEL = "#"+sys.argv[2]
SSL = sys.argv[3].lower() == '--ssl'
PORT = 6697 if SSL else 6667
HKPT =  int(sys.argv[5]) # the port the bot will listen on for hook events.

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
  h = HookServer(('', HKPT))
  while True:
    time.sleep(1)
    try:
      readables, writables, exceptionals = select.select([s, h.socket],[s, h.socket],[s, h.socket])
      if s in readables:
        data += s.recv(512)
        while CRLF in data:
          message = data[:data.index(CRLF)]
          data = data[data.index(CRLF)+2:]
          callback(message)
      if h.socket in readables:
        h.handle_request()
        hook = json.loads(h.hook)
        try:
          # this only works for push hooks currently
          s.sendall('NOTICE {0} :{1[pusher][name]} pushed {2} commit(s) to {1[repository][name]} | "{1[head_commit][message]}" | {1[compare]}\r\n'.format(CHANNEL, hook, len(hook['commits'])))
        except e:
          print e
          pass
    except KeyboardInterrupt:
      print "Leaving..."
      s.sendall("QUIT Bye\r\n")
      s.close()
      exit(0)


# The main part of the program starts here

print "Connecting..."

s.connect((HOST, PORT))

print "Registering..."

s.sendall("NICK %s\r\n"%(NICK))
s.sendall("USER %s * * :A git repo hook bot\r\n"% NICK)

read_loop(got_message)
