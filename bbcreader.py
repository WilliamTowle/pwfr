#!/usr/bin/python
## pwfr library bbcreader.py
# vim: ft=python ts=4 sw=4 et:

#*   Open Source software - copyright and GPLv2 apply. Briefly:       *
#*    - No warranty/guarantee of fitness, use is at own risk          *
#*    - No restrictions on strictly-private use/copying/modification  *
#*    - No re-licensing this work under more restrictive terms        *
#*    - Redistributing? Include/offer to deliver original source      *
#*   Philosophy/full details at http://www.gnu.org/copyleft/gpl.html  *

import urllib3

default_location= "ls13"

class ForecastReader(object):
    def __init__(self):
        self._rss_data= None;
        self._rss_url= None;

    def process(self):
        return ["[Summary not available]\n"]

    def readRSS(self):
        http= urllib3.PoolManager()
        req= http.request('GET', self._rss_url)
        self._rss_data= req.data
        return self._rss_data

    def setURL(self, ref):
        self._rss_url= ref


## BBCReader
##
## For parsing the BBC Weather RSS feeds

class BBCReader(ForecastReader):
    def __init__(self, location):
        super(BBCReader, self).__init__()
        self._location= location
        #self.setURL("https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/%s" %(self._location))
        self.setURL("https://weather-broker-cdn.api.bbci.co.uk/en/observation/rss/%s" %(self._location))

    def getReport(self):
        report= ["BBC Weather for location '%s':\n" %(self._location)]
        report.append("[URL: %s]\n" %(self._rss_url))
        report.extend(self.process())
        return ''.join(report)

    def process(self):
        if self._rss_data is not None:
            return ["%s\n" %(self._rss_data)]
        else:
            return ["[Summary not available]\n"]

if __name__ == "__main__":
    forecast= BBCReader(default_location)
    forecast.readRSS()
    print(forecast.getReport())
