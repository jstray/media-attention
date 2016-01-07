# Use the MediaCloud API to create a CSV showing nunmber of sentences mentioning each candidate
# from June to December 2015

import requests
from dateutil import parser
from datetime import date
from datetime import timedelta
import csv

# generate a MediaCloud query URL for specified search and tine range
# searches in US mainstream media collection
def MCQueryURL(query,start,end):
	key=''
	url = ('https://api.mediacloud.org/api/v2/sentences/count?key=' + 
	        key + 
	        '&q=sentence:' +
	        query + 
	        '+AND+tags%5C_id%5C_media:8875027&split=1&split_start_date=' + 
	        start +
	        '&split_end_date=' +
	        end )
	return url


# filters out all keys that do not correspond to valid dates ("gap" etc returned by MediaCloud)
def FilterDates(keys):
	out = []
	for k in keys:
	    try:
	        parser.parse(k)
	        out.append(k)
	    except ValueError:
	    	k=k # do nothing
	return out

# Query for a single candidate over specified range
# Returns dict of date / count pairs.
def MCQuery(query,start,end):
	response = requests.get(MCQueryURL(query,start,end))
	data = response.json()
	out = {}
	for d in FilterDates(data['split'].keys()):
		out[d[0:10]] = data['split'][d]				# d[0:10] because we want YYYY-MM-DD strings
	return out

# Return time series for candidate. 
def MCGetCandidateSeries(candidate):
	# Break the date range into <90 day intervals so we get day-level data (limitation of MC API)
	out = MCQuery(candidate, "2015-01-01","2015-03-01")
	out.update(MCQuery(candidate, "2015-03-01","2015-05-01"))
	out.update(MCQuery(candidate, "2015-05-01","2015-07-01"))
	out.update(MCQuery(candidate, "2015-07-01","2015-09-01"))
	out.update(MCQuery(candidate, "2015-09-01","2015-11-01"))
	out.update(MCQuery(candidate, "2015-11-01","2016-01-01"))
	return out


# Get time series for each candidate
# (O'Malley does not need escaped apostrophe, I tested :)
candidates = [	"Hillary+AND+Clinton", "Bernie+AND+Sanders", "Martin+AND+O'Malley", "Carly+AND+Fiorina",
				"Donald+AND+Trump", "Ben+AND+Carson", "Ted+AND+Cruz", "Marco+AND+Rubio", "Jeb+AND+Bush"]
startDate = date(2015,1,1)
endDate = date(2016,1,1)

counts = {}
for c in candidates:
	counts[c] = MCGetCandidateSeries(c)


# Write to CSV, one row per day
with open("MediaCloudCounts.csv", "w", newline='') as csv_file:
	writer = csv.writer(csv_file, delimiter=',')

	writer.writerow(['date'] + candidates) # header

	day = startDate
	while day != endDate:
		dateStr = day.strftime("%Y-%m-%d")
		countRow = list(map(lambda c: counts[c][dateStr], candidates)) # get counts for each on this day
		writer.writerow([dateStr] + countRow)
		day = day + timedelta(1)



