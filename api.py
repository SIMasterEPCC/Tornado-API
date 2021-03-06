from pymongo import MongoClient

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
import ast
from datetime import datetime

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
        self.write("{\"medidas\":[")
        for document in medidas[:len(medidas)-1]:
            self.write(document)
            self.write(",")
        self.write(medidas[-1])
        self.write("]}")
            
    def post(self):
        db = self.application.database
        data = self.request.body.decode('utf-8')
        values = data.split("&")
        temperature = values[0].split("=")[1]
        humidity = values[1].split("=")[1]
        data = "{\"Temperatura\":" + str(temperature) + ", \"Fecha\":\"" + str(datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + "\", \"Dispositivo\":1, \"Humedad\":\"" + str(humidity) + "\"}"
        jsonValue = json.loads(data)
        d = ast.literal_eval(str(jsonValue))
        db.medidas.insert(d)
        print(json)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
