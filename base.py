import time
import sqlite3
from random import randint as rd
from os.path import exists


class Base:
	def __init__(self, path):
		if not exists(path):
			with open(path, 'w'):
				print(f'Файл базы данных создан!')
		self.con = sqlite3.connect(path)
		self.cur = self.con.cursor()
		self.init_tables()

	def init_tables(self):
		tables = [
			'users(id integer primary key, user_id integer, last_roll text, dist text)'
		]
		for table in tables:
			self.cur.execute(f'create table if not exists {table};')
			print(f'CHECK TABLE <{table.split("(")[0]}>')
		self.con.commit()

	def get_user(self, user_id):
		user_data = [x for x in self.cur.execute(f'select * from users where user_id={user_id}')]
		if len(user_data) > 0:
			return user_data[0]
		self.cur.execute(f'insert into users(user_id, last_roll, dist) values({user_id}, 0, 0)')
		self.con.commit()
		return [x for x in self.cur.execute(f'select * from users where user_id={user_id}')][0]

	def run(self, user_id):
		dist = rd(0, 500)
		if dist:
			self.cur.execute(f'update users set dist=dist+{dist} where user_id={user_id};')
			self.con.commit()
			return dist
		return 0

	def get_dist(self, user_id):
		return [x for x in self.cur.execute(f'select dist from users where user_id={user_id}')][0][0]

	def get_top(self):
		data = [x for x in self.cur.execute(f'select user_id, dist from users order by dist;')]
		data = sorted(data, key=lambda x: int(x[1].split('.')[0]))[::-1][0:20]
		return data

	def get_last_try(self, user_id):
		last = int([x for x in self.cur.execute(f'select last_roll from users where user_id={user_id}')][0][0].split('.')[0])
		if (time.time() - last) > 24*60*60:
			return True
		return False

	def set_last(self, user_id):
		self.cur.execute(f'update users set last_roll="{time.time()}" where user_id={user_id}')
		self.con.commit()
