'''
	db.py
	
	This will handle the database interactions for the affinity application
'''

import pymssql, informixdb, odbc, pyodbc, adodbapi    
	
class BaseDB():
	'''
		base db class - perhaps more of an interface that has methods to be implemented by the specific classes
	'''
	def get_row(self, query, params=None):
		#fetch one row - along the lines of 
		self.cur.execute(query, params)
		row = self.cur.fetchone()
		return row	
	def get_all(self, query, params=None):
		self.cur.execute(query, params)
		rows = self.cur.fetchall()	
		return rows	
	def get_many(self, query, params=None):
		self.cur.executemany(query, params)
		result = self.cur.fetchall()
		return result
	def get_value(self, query, params=None):
		self.cur.execute(query, params)
		result = self.cur.fetchone()
		return result[0]		
	def set_value(self, query, params=None):
		self.cur.execute(query, params)
		self.conn.commit()

class pyOdbcClient(BaseDB):
	def __init__(self):
		print 'instantiated pyOdbcClient'
		self.conn = pyodbc.connect("Driver={IBM INFORMIX ODBC DRIVER};Host=hewey;Server=hewey;Service=istarcarsi;Protocol=olsoctcp;Database=train;Uid=sethw;Pwd=missy79;")
		self.cur = self.conn.cursor()

class OdbcClient():
	def __init__(self):
		print 'instantiated OdbcClient'
		self.conn = odbc.odbc("Driver={IBM INFORMIX ODBC DRIVER};Host=hewey;Server=hewey;Service=istarcarsi;Protocol=olsoctcp;Database=train;Uid=sethw;Pwd=missy79;")
		#self.conn = odbc.odbc("DSN=test")
		self.cur = self.conn.cursor()	
		
	def get_value(self, query, params = None):
		self.cur.execute(query,params)
		data = self.cur.fetchone()		
		return data[0]
		
	def get_row(self, query, params = None):		
		self.cur.execute(query, params)
		query_result = [ dict(line) for line in [ zip([ column[0] for column in self.cur.description ], row) for row in self.cur.fetchall() ] ]
		#print self.cur.fetchone()		
		return query_result[0]

	
class IfxClient(BaseDB):
	'''
		Handle all Informix DB interaction
	'''
	def __init__(self):
		print 'instantiated new Informix client'
		self.conn = informixdb.connect('cars@hewey',user='sethw',password='missy79')
		self.cur = self.conn.cursor(rowformat = informixdb.ROW_AS_DICT)	

class SqlClient(BaseDB):
	'''
		Handle all SqlServer DB interaction
	'''
	def __init__(self):
		print 'instantiated new Sql client'
		self.conn = pymssql.connect(host='sqldev', user='sa', password='D3n$3m!T', database='students', as_dict=True)
		self.cur = self.conn.cursor()	
