import logging
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import db, functools, random

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("facebook_api_key", help="your Facebook application API key",
       default="9e2ada1b462142c4dfcc8e894ea1e37c")
define("facebook_secret", help="your Facebook application secret",
       default="32fc6114554e3c53d5952594510021e2")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/login", AuthLoginHandler),
            (r"/admin", AdminHander),
            (r"/logout", AuthLogoutHandler),
            (r"/user/([0-9]+)", UserProfile), 
            (r"/register", RegisterHandler), 
            (r"/finish", FinishRegistration),
            (r"/reg_validate", ValidationHandler),
            (r"/user/edit/([0-9]+)", EditUserProfile), 
        ]
        settings = dict(
            cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #xsrf_cookies=True,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,                        
        )
        tornado.web.Application.__init__(self, handlers, **settings)     
        self.sqlclient = db.SqlClient()
        #self.ifxclient = db.IfxClient()
        self.odbcclient = db.OdbcClient()
        self.pyodbcclient = db.pyOdbcClient()
        
def registered(method):
    """Decorate with this method to restrict to site admins."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
		cx_id = self.get_secure_cookie("cx_id")
		if not cx_id:
			cx_id = self.sqlclient.get_row("select cx_id from users where auth_acct = %s and auth_svc = %s", (self.current_user['id'], 'fb'))
			if not cx_id:
				self.redirect('/register')
				return
				raise web.HTTPError(403)        
			else:
				self.set_secure_cookie('cx_id',str(cx_id[0]))
				return method(self, *args, **kwargs)
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
	@property
	def odbcclient(self):
		return self.application.odbcclient
	@property
	def pyodbcclient(self):
		return self.application.pyodbcclient			
	def get_current_user(self):
		user_json = self.get_secure_cookie("user")
		if not user_json: return None
		return tornado.escape.json_decode(user_json)

class ValidationHandler(BaseHandler):
	@tornado.web.authenticated
	def post(self):
		cx_id = self.get_argument("cx_id")
		valtype = self.get_argument("valtype")
		value = self.get_argument("value")
		if valtype == "major":
			sql = "select count(id) from major_table m join prog_enr_rec p on m.major = p.major1 and p.id = ? and m.txt = ?"
		else:			
			sql = "select count(id) from id_rec where id = ? and %s = ?" % valtype						
		ct = self.pyodbcclient.get_value(sql, [str(cx_id), str(value)])
		print ct
		if ct == 0:			
			self.render("fail.html",cx_id=cx_id)
		else:
			self.write('1')			
			
class FinishRegistration(BaseHandler):
	@tornado.web.authenticated
	def post(self):
		cx_id = self.get_argument("cx_id")
		firstname = self.get_argument("firstname")
		lastname = self.get_argument("lastname")
		email = self.get_argument("email")
		auth_svc = 'fb'
		auth_acct = self.current_user['id']
		self.sqlclient.set_value("insert into users (cx_id, firstname, lastname, email, auth_acct, auth_svc) VALUES (%d,%s,%s,%s,%s,%s)",
			(int(cx_id), firstname, lastname, email, auth_acct, auth_svc))
		self.redirect("/")
				
        
class RegisterHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):		
		if self.sqlclient.get_row("select count(*) from users where auth_acct = %s and auth_svc = %s", (self.current_user['id'], 'fb'))[0] > 0:
			self.redirect("/")
		else:
			self.render("register2.html")
	@tornado.web.authenticated
	def post(self):
		cx_id = self.get_argument("cx_id")
		lastname = self.get_argument("lastname")
		firstname = self.get_argument("firstname")	
		email = self.get_argument("email")	
		ids = []
		nextid = int(cx_id)
		firstid = int(cx_id)
		ids.append(nextid)		
		emails = []
		majors = []
		address = []
		zips = []	
		user_data = self.odbcclient.get_row(
		'''
			select  i.id, addr_line1, substring(zip from 0 for 6) zip, email2, txt
				from id_rec i 
				join prog_enr_rec p on i.id = p.id
					join major_table m on p.major1 = m.major
				where i.id = ?''',[ids[0]])	
		emails.append(user_data['email2'])
		majors.append(user_data['txt'])
		address.append(user_data['addr_line1'])
		zips.append(user_data['zip'])
		sql = '''
			select first 1 i.id, addr_line1, substring(zip from 0 for 6) zip, email2, txt
				from id_rec i 
				join prog_enr_rec p on i.id = p.id
					join major_table m on p.major1 = m.major
				where i.id >= ? and i.id not in (%s)
					and addr_line1 is not null and  addr_line1 not in ('',%s) 
					and zip is not null and substring(zip from 0 for 6) not in ('',%s)
					and email2 is not null and email2 not in ('',%s)
					and txt is not null and txt not in ('',%s) '''
		for x in range(4):	
			stmt = sql  % (','.join('%s' % i for i in ids), ','.join("'%s'" % i for i in address), ','.join("'%s'" % i for i in zips), ','.join("'%s'" % i for i in emails), ','.join("'%s'" % i for i in majors))			
			while nextid in ids:
				nextid = random.randint(firstid-1000, firstid+100)		
			row = self.odbcclient.get_row(stmt, [nextid, user_data['txt']])								
			emails.append(row['email2'])
			majors.append(row['txt'])
			address.append(row['addr_line1'])
			zips.append(row['zip'])
			ids.append(nextid)		
		random.shuffle(emails)
		random.shuffle(address)
		random.shuffle(majors)
		random.shuffle(zips)		
		self.render('validate.html',email=email,firstname=firstname,lastname=lastname,cx_id=cx_id,emails=emails,majors=majors,address=address,zips=zips)	
		
class AdminHander(BaseHandler):
	@tornado.web.authenticated
	@registered	
	def get(self):
		categories = self.sqlclient.get_all("select id,value from categories")
		activities = self.sqlclient.get_all("select id,value from activities")
		self.render("admin.html", categories=categories, activities=activities)
class UserProfile(BaseHandler):
	@tornado.web.authenticated
	def get(self, uid):
		self.write("Future Home of User Profile Information for uid=%s" % uid)

class EditUserProfile(BaseHandler):
	@tornado.web.authenticated
	def get(self, uid):
		if uid.isdigit():
			sql = "select cx_id, firstname, lastname, email, isnull(phone,'Phone Number') phone, isnull(facebook, 'Facebook URL') facebook,	isnull(twitter, 'Twitter URL') twitter,	isnull(blog, 'Blog URL') blog from users where cx_id=%s"
			profile = self.sqlclient.get_row(sql, (uid,))
			self.render("profedit.html", profile=profile)
		else:
			self.redirect("/")
			

class MainHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated    
    #@tornado.web.asynchronous
    @registered
    def get(self):
		sql = '''
			select categoryid, category, a.activityid, activity, userid
				from (	
						select c.id CategoryID, c.value Category, a.id ActivityID, a.value Activity
								from activities a 
									right join categories c 
										on a.categoryid = c.id ) as a
				left join signups s 
					on a.activityid = s.activityid
						and s.userid = 0
		'''		
		
		data = self.sqlclient.get_all(sql)				
		categorynames = list(set([row['category'] for row in data]))		
		signups = {}
		for name in categorynames:
			signups[name] = []
			for row in data:
				if row['category'] == name:
					if row['userid'] is not None:						
						signups[name].append({'activity':row['activity'], 'activityid': row['activityid'], 'checked': True})
					else:
						signups[name].append({'activity':row['activity'], 'activityid': row['activityid'], 'checked': False})
		self.render("main2.html", signups=signups, cx_id=self.get_secure_cookie("cx_id"))

class AuthLoginHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        my_url = (self.request.protocol + "://" + self.request.host +
                  "/login?next=" +
                  tornado.escape.url_escape(self.get_argument("next", "/")))
        if self.get_argument("code", False):
            self.get_authenticated_user(
                redirect_uri=my_url,
                client_id=self.settings["facebook_api_key"],
                client_secret=self.settings["facebook_secret"],
                code=self.get_argument("code"),
                callback=self._on_auth)
            return
        self.authorize_redirect(redirect_uri=my_url,
                                client_id=self.settings["facebook_api_key"],
                                extra_params={"scope": "read_stream"})
    
    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        self.redirect("/")


class AuthLogoutHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("cx_id")
        self.redirect("http://denverseminary.edu")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
