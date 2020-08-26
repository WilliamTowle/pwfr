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

class ForecastReader(object):
    def __init__(self):
        self.cache_file= None;
        self.rss_data= None;
        self.rss_url= None;

    def process(self):
        return ["[Summary not available]\n"]

    def readCache(self):
        with open(self.cache_file) as file:
            self.rss_data= file.read()

    def setCacheFile(self, name):
        self.cache_file= name

    def writeCache(self):
        if hasattr(self, 'rss_data'):
            with open(self.cache_file, 'w') as file:
                file.write(self.rss_data)

    def readRSS(self):
        http= urllib3.PoolManager()
        req= http.request('GET', self.rss_url)
        self.rss_data= req.data
        return self.rss_data

    def setURL(self, ref):
        self.rss_url= ref


## BBCReader
##
## For parsing the BBC Weather RSS feeds

class BBCReader(ForecastReader):
    def __init__(self, location):
        super(BBCReader, self).__init__()
        self.location= location
        #self.setURL("https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/%s" %(self.location))
        #self.setCacheFile("bbcreader-forecast-%s.dat" %(location))
        self.setURL("https://weather-broker-cdn.api.bbci.co.uk/en/observation/rss/%s" %(self.location))
        self.setCacheFile("bbcreader-current-%s.dat" %(location))

    def getReport(self):
        report= ["BBC Weather for location '%s':\n" %(self.location)]
        report.append("[URL: %s]\n" %(self.rss_url))
        report.extend(self.process())
        return ''.join(report)

    def process(self):
        if self.rss_data is None:
            return ["[Summary not available]\n"]
        else:
            summary= []
            try:
                dom= parseString(self.rss_data)

                if dom.childNodes[0].nodeName == 'rss':
                    summary.append("RSS parse completed, got DOM with %d node[s] ('rss' first) OK\n" %(dom.childNodes.length))

                dom.unlink()
            except ExpatError as ee:
                summary.append("Parse error in RSS (invalid location '%s'?)" %(self.location))

            return summary

if __name__ == "__main__":
    forecast= BBCReader(default_location)
    forecast.readCache()
    #forecast.readRSS()
    print(forecast.getReport())
