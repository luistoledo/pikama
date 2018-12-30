import argparse
import math
import threading
import time
import sys

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message
from pythonosc import udp_client



# args
parser = argparse.ArgumentParser()
parser.add_argument("--ip",
    default="127.0.0.1", help="The ip to listen on")
parser.add_argument("--port",
    type=int, default=5005, help="The port to listen on")
args = parser.parse_args()


class OSCServer:
  router = None
  clients = []
  # dummy_data = [[10,10,100,100],[20,20,20,50],[100,30,100,100]]
  dummy_data = [10,10,100,100]


    # callbacks
  def route_echo(self, addr, args, data):
    try:
      print("[{0}] ~ {1} - {2}".format(addr, args, data))
      client = udp_client.SimpleUDPClient(addr[0], addr[1])
      client.send_message("/test", data)
    except ValueError: pass

  def route_register(self, addr, args, data):
    if addr not in self.clients:
      self.clients.append(addr)
      print ("registering :{0}".format(self.clients))

    # broadcast 10 messages to all clients
    for x in range(0, 10):
      self.broadcast_msg(self.dummy_data)
      time.sleep(3)

  def broadcast_msg(self, msg):
    for client in self.clients:
      response = udp_client.SimpleUDPClient(client[0], client[1])
      response.send_message("/test", msg)

  def __init__(self):
    # OSC routes
    self.router = dispatcher.Dispatcher()
    self.router.map("/stop", print)
    self.router.map("/start", print)
    self.router.map("/echo", self.route_echo , needs_reply_address=True)
    self.router.map("/subscribe", self.route_register , needs_reply_address=True)

  # uses args.ip & args.port
  def start(self, args):
    # OSC server
    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), self.router)

    print("Serving on {}".format(server.server_address))
    # server.serve_forever()

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    # threading.daemon=True
    server_thread.start()

  def stop(self):
    server_thread.stop();

if __name__ == '__main__':
  try:
    server = OSCServer()
    server.start(args)

  except (KeyboardInterrupt, SystemExit):
    server.stop()
    sys.exit()

  except:
    raise

sys.exit()




# while True:
#   key = cv2.waitKey(1) & 0xFF

#   # keyboard controls
#   if key == ord("q"):
#     break
#   if key == ord("l"):
#     for x in range(0, 10):
#       broadcast_msg(dummy_shapes)
#       time.sleep(10)
#   if key == ord("t"):
#     broadcast_msg(dummy_shapes)



