from pikama import Pikama

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

    cam = Pikama()
    while cam.is_active:
        blobs = cam.search_blobs()
        # if blobs is not None:
        if last_blobs != blobs:
            last_blobs == blobs
    cam.stop()
