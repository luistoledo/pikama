import argparse
import math
import threading
import cv2
import time

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message
from pythonosc import udp_client


clients = []
# dummy_shapes = [[10,10,100,100],[20,20,20,50],[100,30,100,100]]
dummy_shapes = [10,10,100,100]



# args
parser = argparse.ArgumentParser()
parser.add_argument("--ip",
    default="127.0.0.1", help="The ip to listen on")
parser.add_argument("--port",
    type=int, default=5005, help="The port to listen on")
args = parser.parse_args()




# callbacks
def route_echo(addr, args, data):
  try:
    print("[{0}] ~ {1} - {2}".format(addr, args, data))
    client = udp_client.SimpleUDPClient(addr[0], addr[1])
    client.send_message("/test", data)
  except ValueError: pass



def route_register(addr, args, data):
  if addr not in clients:
    clients.append(addr)
  print (clients)
  # broadcast_msg(dummy_shapes)
  for x in range(0, 10):
    broadcast_msg(dummy_shapes)
    time.sleep(10)






# OSC routes
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/stop", print)
dispatcher.map("/start", print)
dispatcher.map("/echo", route_echo , needs_reply_address=True)
dispatcher.map("/subscribe", route_register , needs_reply_address=True)



# OSC server
server = osc_server.ThreadingOSCUDPServer(
    (args.ip, args.port), dispatcher)
print("Serving on {}".format(server.server_address))
# server.serve_forever()

server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()



def broadcast_msg(msg):
  for client in clients:
    response = udp_client.SimpleUDPClient(client[0], client[1])
    response.send_message("/test", msg)


while True:
  key = cv2.waitKey(1) & 0xFF

  # keyboard controls
  if key == ord("q"):
    break
  if key == ord("l"):
    for x in range(0, 10):
      broadcast_msg(dummy_shapes)
      time.sleep(10)
  if key == ord("t"):
    broadcast_msg(dummy_shapes)



