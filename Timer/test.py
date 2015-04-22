import re

htmlString = "dskjfgjhksdhttp://v.pptv.com/show/MVV9ibmLIOHbZV78.htmlskdhksdjafh"

pattern = re.compile(r"http[s]?\:\/\/[a-zA-Z0-9]*\.pptv\.com\/[a-zA-Z0-9\/]*\.html")

matcher = pattern.search(htmlString)
if matcher:
	print matcher.group()
else:
	print "Not catched"