from peewee import MySQLDatabase

db = MySQLDatabase('database', user='user', password='password', host='host')
table_name = 'items'
