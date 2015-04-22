# -*- coding: utf-8 -*-
import MySQLdb
from time import mktime
from datetime import datetime
from ast import literal_eval
import logging
from utils import SQLINFO

logger = logging.getLogger('appserver')

class TimerModel(object):

	def __init__(self):
		super(TimerModel, self).__init__()  
		conn=MySQLdb.connect(host=SQLINFO["HOST"],user="root",passwd=SQLINFO["PASSWORD"],db=SQLINFO["DB"], charset="utf8")  
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
				ind = 23 + ALPHABET.index(char)
				hash_ += ind
		hash_ += (time % 100000) * 10000
		return hash_

	def new_info_item(self, dtime, title, name, url):
		timeCode = mktime(dtime.timetuple())
		hashValue = self.hashName(name+title, timeCode)
		name = literal_eval("u'%s'" % name)
		title = literal_eval("u'%s'" % title)
		timeValue = dtime.strftime("%T")
		dateValue = dtime.strftime("%Y-%m-%d")
		if name in [u'解放者杯', u'亚冠', u'中超', u'大足赛', u'澳超', u'中超', u'德甲', u'葡超', u'西甲', u'英超', u'意甲', u'英冠', u'欧联杯', u'足总杯']: 
			picture = "football"
		elif name==u'游戏':
			picture = "game"
		else:
			picture = "default"
		if not url:
			exe_string = "INSERT INTO live_daylist(name, title, ctime, dtime, datetime, hash, pic) Values(%s, %s, %s, %s, %s, %s, %s)"
			self.cursor.execute(exe_string, (name, title, timeCode, timeValue, dateValue, hashValue, picture))
		else:
			search_string = "SELECT vid FROM m3u8live WHERE date = %s and hashval = %s"
			self.cursor.execute(search_string, (dateValue, hashValue))
			info = self.cursor.fetchone()
			if not info:				
				exe_string = "INSERT INTO m3u8live(name, date, category, url, starttime, title, lid, hashval) Values(%s, %s, %s, %s, %s, %s, %s, %s)"
				self.cursor.execute(exe_string, (name, dateValue, "default", url, timeCode, title, 1, hashValue))
				exe_string = "SELECT max(vid) FROM m3u8live"
				self.cursor.execute(exe_string)
				one = self.cursor.fetchone()
				if one:
					vid = one[0]
					exe_string = "INSERT INTO live_daylist(name, title, ctime, dtime, datetime, hash, vid, pic) Values(%s, %s, %s, %s, %s, %s, %s, %s)"
					self.cursor.execute(exe_string, (name, title, timeCode, timeValue, dateValue, hashValue, vid, picture))
			else:
				vid = info[0]
				exe_string = "INSERT INTO live_daylist(name, title, ctime, dtime, datetime, hash, vid, pic) Values(%s, %s, %s, %s, %s, %s, %s, %s)"
				self.cursor.execute(exe_string, (name, title, timeCode, timeValue, dateValue, hashValue, vid, picture))
	
	def clear_day_item(self, date):
		ddate = date.strftime("%Y-%m-%d")
		exe_string = "DELETE FROM live_daylist WHERE datetime = %s"
		self.cursor.execute(exe_string, (ddate, ))
