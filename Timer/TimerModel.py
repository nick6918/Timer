# -*- coding: utf-8 -*-
import MySQLdb
from time import mktime
from datetime import datetime
import logging

logger = logging.getLogger('appserver')

class TimerModel(object):

	def __init__(self):
		super(TimerModel, self).__init__()  
		conn=MySQLdb.connect(host="127.0.0.1",user="root",passwd="",db="yqc", charset="utf8")  
		self.cursor = conn.cursor() 

	def encodeString(self, pd_name):
		#pd_name = pd_name.decode('utf-8')	
		nname = ""
		for c in pd_name:
			c = "%%u%04X" % ord(c);
			nname += c
		return nname 

	def hashName(self, name, time):
		temp = self.encodeString(name)
		ALPHABET = "abcdefghijklmnopqrstvwxyz123456789"
		hash_ = 0
		for char in temp:
			if char in ALPHABET:
				ind = 23+ALPHABET.index(char)
				hash_ += ind
		hash_ += (time % 100000) * 10000
		return hash_

	def new_info_item(self, dtime, title, name, url):
		timeCode = mktime(dtime.timetuple())
		hashValue = self.hashName(name+title, timeCode)
		timeValue = dtime.strftime("%T")
		dateValue = dtime.strftime("%Y-%m-%d")
		if not url:
			exe_string = "INSERT INTO live_daylist(name, title, ctime, dtime, datetime, hash) Values(%s, %s, %s, %s, %s, %s)"
			self.cursor.execute(exe_string, (name.encode('utf-8'), title.encode('gbk'), timeCode, timeValue, dateValue, hashValue))
		else:
			search_string = "SELECT vid FROM m3u8live WHERE date = %s and hashval = %s"
			self.cursor.execute(search_string, (dateValue, hashValue))
			info = self.cursor.fetchone()
			if not info:				
				exe_string = "INSERT INTO m3u8live(name, date, category, url, starttime, title, lid, hashval) Values(%s, %s, %s, %s, %s, %s, %s, %s)"
				self.cursor.execute(exe_string, (name, dateValue, "game", url, timeCode, title, 1, hashValue))
				exe_string = "SELECT max(vid) FROM m3u8live"
				self.cursor.execute(exe_string)
				one = self.cursor.fetchone()
				if one:
					vid = one[0]
					exe_string = "INSERT INTO live_daylist(name, title, ctime, dtime, datetime, hash, vid) Values(%s, %s, %s, %s, %s, %s, %s)"
					self.cursor.execute(exe_string, (name.encode('utf-8'), title.encode('gbk'), timeCode, timeValue, dateValue, hashValue, vid))
			else:
				vid = info[0]
				exe_string = "INSERT INTO live_daylist(name, title, ctime, dtime, datetime, hash, vid) Values(%s, %s, %s, %s, %s, %s, %s)"
				self.cursor.execute(exe_string, (name.encode('utf-8'), title.encode('gbk'), timeCode, timeValue, dateValue, hashValue, vid))
	
	def clear_day_item(self, date):
		ddate = date.strftime("%Y-%m-%d")
		exe_string = "DELETE FROM live_daylist WHERE datetime = %s"
		self.cursor.execute(exe_string, (ddate, ))
