import BaseHTTPServer

class HookHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
  def do_POST(self):
    addr = self.client_address[0]
    if addr.startswith('192.30.25') and int(addr[9]) >= 2: # quick and dirty way to check the IP is from github (192.30.252.0/22)
      print "Hook Received."
      print self.headers
      self.send_response(200)
      self.end_headers()
      print "Processing hook..."
      self.server.hook = self.rfile.read() # copy the hook's (massive) payload to where we can use it. this takes a while
      print "Sent 200 response to ", self.address_string()
    return

class HookServer(BaseHTTPServer.HTTPServer):

  def __init__(self, server_address):
    BaseHTTPServer.HTTPServer.__init__(self, server_address, HookHandler)
    self.hook = ''
