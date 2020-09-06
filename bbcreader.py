#!/usr/bin/python
## pwfr library bbcreader.py
# vim: ft=python ts=4 sw=4 et:

#*   Open Source software - copyright and GPLv2 apply. Briefly:       *
#*    - No warranty/guarantee of fitness, use is at own risk          *
#*    - No restrictions on strictly-private use/copying/modification  *
#*    - No re-licensing this work under more restrictive terms        *
#*    - Redistributing? Include/offer to deliver original source      *
#*   Philosophy/full details at http://www.gnu.org/copyleft/gpl.html  *

from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
import urllib3

default_location= "ls13"


class WeatherData(object):
    # proxy for dict type so we can have a fixed, predefined,
    # set of keys mapping to an intended default value
    def __init__(self):
        self._data= {
                'title': None,
                'description': None,
                'pubDate': None
                }

    def __getitem__(self, name):
        if name in self._data:
            return self._data[name]
        else:
            raise KeyError(name)    # can't retrieve from nonexistent key

    def __setitem__(self, name, value):
        if name in self._data:
            self._data[name]= value
        else:
            raise KeyError(name)    # can only replace where key exists



class ForecastReader(object):
    def __init__(self):
        self._cache_file= None;
        self._rss_data= None;
        self._rss_url= None;
        self.status= 'Summary unavailable'

    def getStatus(self):
        return "STATUS: %s\n" %(self.status)

    def getSummary(self):
        return self.getStatus()

    def readCache(self):
        with open(self._cache_file) as file:
            self._rss_data= file.read()

    def setCacheFile(self, name):
        self._cache_file= name

    def writeCache(self):
        if hasattr(self, '_rss_data'):
            with open(self._cache_file, 'w') as file:
                file.write(self._rss_data)

    def readRSS(self):
        http= urllib3.PoolManager()
        req= http.request('GET', self._rss_url)
        self._rss_data= req.data
        self.status= 'RSS data not processed'
        return self._rss_data

    def setURL(self, ref):
        ## TODO: deny change following data retrieval (or
        ## invalidate cache, requiring a refetch)?
        self._rss_url= ref


## BBCReader
##
## For parsing the BBC Weather RSS feeds, which provide:
## "title" field, with:
##      name (at start of title)
##      brief text summary
##      temperatures
## "description" field, containing:
##      max/min temperatures
##      wind direction and speed ("<n>mph")
##      visibility (word)
##      pressure ("<n>mb")
##      humidity
##      UV risk (number on a scale)
##      pollution (eg. "low")
##      sunrise/sunset times ("HH:MM <TZ>")
## "pubDate" field, with human readable timestamp/timezone

class BBCReader(ForecastReader):
    def __init__(self, location):
        super(BBCReader, self).__init__()
        self._location= location
        #self.setURL("https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/%s" %(self._location))
        #self.setCacheFile("bbcreader-forecast-%s.dat" %(location))
        self.setURL("https://weather-broker-cdn.api.bbci.co.uk/en/observation/rss/%s" %(self._location))
        self.setCacheFile("bbcreader-current-%s.dat" %(location))
        self.forecast= []

    def getSummary(self):
        report= ["BBC Weather for location '%s':\n" %(self._location)]
        report.append("[URL: %s]\n" %(self._rss_url))
        report.extend(self.process())
        return ''.join(report)

    def process(self):
        if self._rss_data is None:
            return [self.getStatus()]
        else:
            summary= []
            self.forecast= []
            try:
                dom= parseString(self._rss_data)

                for (num, item) in enumerate(dom.getElementsByTagName('item'), start=1):
                    itemData= WeatherData()
                    for subitem in item.childNodes:
                        if subitem.nodeName == 'title':
                            itemData["title"]= " ".join(t.nodeValue.encode('ascii',errors='ignore') for t in subitem.childNodes if t.nodeType == t.TEXT_NODE)
                        elif subitem.nodeName == 'description':
                            itemData["description"]= " ".join(t.nodeValue.encode('ascii',errors='ignore') for t in subitem.childNodes if t.nodeType == t.TEXT_NODE)
                        elif subitem.nodeName == 'pubDate':
                            itemData["pubDate"]= " ".join(t.nodeValue for t in subitem.childNodes if t.nodeType == t.TEXT_NODE)

                    summary.append("Item %d\n" %(num))
                    summary.append("- title: %s\n" %(itemData["title"]))
                    summary.append("- description: %s\n" %(itemData["description"]))
                    summary.append("- pubDate: %s\n" %(itemData["pubDate"]))
                    self.forecast.append(itemData)

                dom.unlink()
                self.status= 'OK'
            except ExpatError as ee:
                self.status= "Parse error in RSS (invalid location '%s'?)" %(self._location)
                summary.append(self.getStatus())
            return summary

if __name__ == "__main__":
    forecast= BBCReader(default_location)
    forecast.readCache()
    #forecast.readRSS()
    forecast.writeCache()
    #print(forecast.getSummary())
