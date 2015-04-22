# -*- coding: utf-8 -*-
import logging
import re, urllib2
from datetime import datetime, timedelta
from time import mktime,sleep
from BeautifulSoup import BeautifulSoup, NavigableString
from TimerModel import TimerModel
from daemonize import Daemonize

logger = logging.getLogger('appserver')

fh = logging.FileHandler("timer.log", "w")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger('jobs')
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

def Timer():
	lastDate = "2015-01-01"
	while(True):
		logger.debug("LOOP STARTED AT "+datetime.now().strftime("%T"))
		try:
			curDate = datetime.now()
			nextDate = curDate+timedelta(1)
			curStamp = mktime(curDate.timetuple())
			nextDateString = nextDate.strftime("%Y-%m-%d")
			curDateString = curDate.strftime("%Y-%m-%d")
			(year, month, day) = curDateString.split("-")
			if curDateString != lastDate:
				lastDate = curDateString
				queryLiveList(nextDateString)
			else:
				TimerModel().clear_day_item(curDate)
				queryLiveList(curDateString)
				TimerModel().new_info_item(datetime(year=int(year), month=int(month), day=int(day), hour=0, minute=0,second=1), "GameLive", "Game", "http://v.pptv.com/show/QxRz8VmicL23QTrY.html")
		except Exception, e:
			logger.error(e)
			break
		logger.debug("LOOP FINISHED AT "+datetime.now().strftime("%T"))
		sleep(20)
	logger.error("TIMER CEASED")

def queryLiveList(date):
	req = urllib2.Request("http://live.pptv.com/api/subject_list?cb=load.cbs.cbcb_4&date="+date+"&type=35&tid=&cid=&offset=0", headers={
		"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
		})
	try:
		webpage = urllib2.urlopen(req)
	except Exception, e:
		logger.error(e)
		logger.error("601 request fail in html page request")
		return []

	pageContent = webpage.read()
	pattern = re.compile(r"\"html\":\"(.*)\"")
	matcher = pattern.search(pageContent)
	if matcher:
		content = matcher.group(1)
		content = content.replace("\/", "/").replace("\\\"", "\"").replace("\\n", "")
		preContent = "<!DOCTYPE html><html><head><title>本日直播列表</title></head><body>"
		postContent = "</body></html>"
		finalContent = preContent + content + postContent
	else:
		logger.debug("NOT MATCHED")
	soup = BeautifulSoup(finalContent)
	htmlList =  soup.table.contents
	(year, month, day) = date.split("-")
	for tr in htmlList:
		trHtml = tr.prettify()
		pattern = re.compile(r"http[s]?\:\/\/[a-zA-Z0-9]*\.pptv\.com\/[a-zA-Z0-9\/]*\.html")
		matcher = pattern.search(trHtml)
		if matcher:
			itemUrl = matcher.group()
		else:
			itemUrl = None
		timeHtml = tr.contents[0].text
		(hour, minute) = timeHtml.split(":") 
		startTime = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second = 0)
		name = tr.contents[1].contents[1].text
		temp = tr.contents[2].div.contents[0]
		title = ""
		if isinstance(temp, NavigableString):
			title = temp
		else:
			temp = temp.contents[0]
			if isinstance(temp, NavigableString):
				title = temp
			else:
				title = ""
		logger.debug(("#LIVE#", startTime, name, title))
		if itemUrl:
			TimerModel().new_info_item(startTime, title, name, itemUrl)
		else:
			TimerModel().new_info_item(startTime, title, name, None)

if __name__=='__main__':
	pid="timer.pid"
	keep_fds = [fh.stream.fileno()]
	daemon = Daemonize(app="jobs", pid=pid, action=Timer, keep_fds=keep_fds)
	daemon.start()
