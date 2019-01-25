#!/usr/bin/env python3

from pikama import Pikama

import threading
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import asyncio
import json
import time
import sys

class RootHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        cam.need_snapshot = True
        self.render("webcontrol.html", rnd=time.time())
        # self.write("kaixo, pikama naiz<br/><img src='static/snapshot.jpg?{0}' />".format(str(time.time())))
        # self.finish()
    
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

class CommandsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, cmd):
        print(cmd)
        
        if cmd=="reset":
            cam.firstFrame = None
            self.write("ok")
        elif cmd=="mirror_horizontal":
            cam.mirror_horizontal = not cam.mirror_horizontal
            self.write("ok")
        elif cmd=="mirror_vertical":
            cam.mirror_vertical = not cam.mirror_vertical
            self.write("ok")
        elif cmd=="max_area":
            cam.max_area += 500
            self.write("ok")
        elif cmd=="min_area":
            cam.min_area += 100
            self.write("ok")
        elif cmd=="threshold":
            cam.thval += 10
            self.write("ok")
        elif cmd=="view":
            cam.displayImageIndex += 1
            if cam.displayImageIndex>2:
                cam.displayImageIndex=0
            self.write("ok")

        self.redirect('/')
        # self.finish()

class WebServer(threading.Thread):
    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        application = tornado.web.Application([
            (r"/", RootHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
            (r"/do/(.*)", CommandsHandler),
            (r'/blobs', WSHandler)])
        application.listen(12345)
        print ('/////starting the server on http://localhost:12345')
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        tornado.ioloop.IOLoop.current().stop()

    def broadcast(self, txt):
        WSHandler.broadcast(txt)

class WSHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def open(self):
        self.waiters.add(self)
        print ('-----websocket connection opened. now:'+str(len(self.waiters)))
        # self.write_message("connection opened")
        cam.firstFrame = None

    def on_message(self, message):
        print ('----websocket receive: ' + message)
        # self.write_message("receive: "+message)

    @classmethod
    def broadcast(self, message):
        for waiter in self.waiters:
            waiter.write_message(message)

    def on_close(self):
        self.waiters.remove(self)
        print ('-----websocket connection closed. now:'+str(len(self.waiters)))
# 

last_blobs = list()
try:
    cam = Pikama()
    WebServer().start()
    while cam.is_active:
        blobs = cam.search_blobs()
        # if blobs is not None:
        if last_blobs != blobs:
            last_blobs == blobs
            WebServer().broadcast(json.dumps(blobs))
    cam.stop()
    WebServer().stop()
    sys.exit()

except (KeyboardInterrupt, SystemExit):
#     cam.stop()
#     tornado.ioloop.IOLoop.current().stop()
#     sys.exit()
    raise SystemExit()

finally:
    raise

