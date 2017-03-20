from pymongo import MongoClient

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
import ast

from tornado.options import define, options

define("port", default=1521, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/medidas", TemperatureHandler)
        ]

        settings = dict(
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.con = MongoClient()
        self.database = self.con["medidas"]


class TemperatureHandler(tornado.web.RequestHandler):
    def get(self):
        db = self.application.database
        medidasdb = db.medidas
        cursor = medidasdb.find({},{"_id":0})
        medidas = list(cursor)
        self.write("{\"temperature\":[")
        for document in medidas[:len(medidas)-1]:
            self.write(document)
            self.write(",")
        self.write(medidas[-1])
        self.write("]}")
        	
    def post(self):
        db = self.application.database
        data = json.loads(self.request.body.decode('utf-8'))
	d = ast.literal_eval(str(data))
        db.temperature.insert(d)
	print type(d)
        print('JSON data:', d)
        self.write("200")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
