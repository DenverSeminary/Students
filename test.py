#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


import db, os, functools

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/another", NotherHandler),
        ]
        settings = dict(
            cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",            
            #xsrf_cookies=True,                                   
        )
        tornado.web.Application.__init__(self, handlers, **settings)     
        self.sqlclient = db.SqlClient()
        self.ifxclient = db.IfxClient()


def registered(method):
    """Decorate with this method to restrict to site admins."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.sqlclient.get_row("select count(*) from users where auth_acct = %s and auth_svc = %s", ('swasheck', 'fb'))[0] == 0:
            print 'redirect to registration'
            return
            raise web.HTTPError(403)        
        else:
            return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(tornado.web.RequestHandler):	
	@property
	def sqlclient(self):
		return self.application.sqlclient
	@property
	def ifxclient(self):
		return self.application.ifxclient
	def get(self):		
		print 'instantiated'		

class MainHandler(BaseHandler):	
	@registered
	def get(self):		
		self.write("Hello, world")		
		
class NotherHandler(BaseHandler):
	def get(self):		
		self.write("Another page")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
