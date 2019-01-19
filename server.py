#!/usr/bin/env python3

from pikama import Pikama

import threading
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import asyncio
import json
import sys

class RequestHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self, path):
        self.write("Test")
        self.finish()

class WebServer(threading.Thread):
    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        application = tornado.web.Application([
            # (r"/(.*)", RequestHandler),
            (r'/blobs', WSHandler)])
        application.listen(12345)
        tornado.ioloop.IOLoop.instance().start()
        print ('/////starting the server on http://localhost:9090')


    def broadcast(self, txt):
        WSHandler.broadcast(txt)

class WSHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def open(self):
        self.waiters.add(self)
        print ('-----websocket connection opened')
        self.write_message("connection opened")

    def on_message(self, message):
        print ('----websocket receive: ' + message)
        # self.write_message("receive: "+message)

    @classmethod
    def broadcast(self, message):
        for waiter in self.waiters:
            waiter.write_message(message)

    def on_close(self):
        self.waiters.remove(self)
        print ('-----websocket connection closed')


try:
    cam = Pikama()
    WebServer().start()
    while cam.is_active:
        blobs = cam.search_blobs()
        if blobs is not None:
            if len(blobs) > 0:
                blobs = json.dumps(blobs)
                WebServer().broadcast(blobs)
                # print(blobs)
                # break

except KeyboardInterrupt:
    tornado.ioloop.IOLoop.instance().stop()
    sys.exit()

except:
    raise
