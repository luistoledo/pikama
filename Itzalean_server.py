from threading import Thread

from pikama import Pikama
from server import Server
# import wsserver
import argparse

if __name__ == '__main__':
  camera = Pikama()
  server = Server()

  try:
    print("to start")
    # t = Thread(target = server.start())
    server.start()
    # t.start()
    print("started")

    while camera.is_active:
      blobs = camera.search_blobs()
      if blobs != None:
        if len(blobs)>1 :
          server.broadcast(blobs)
      
        # print(len(blobs))
          # print(blobs)

  
  except KeyboardInterrupt:
    server.stop()
    sys.exit()

  except:
    raise
# 