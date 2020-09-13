#!/usr/bin/python
## pwfr library bbcreader.py
# vim: ft=python ts=4 sw=4 et:

#*   Open Source software - copyright and GPLv2 apply. Briefly:       *
#*    - No warranty/guarantee of fitness, use is at own risk          *
#*    - No restrictions on strictly-private use/copying/modification  *
#*    - No re-licensing this work under more restrictive terms        *
#*    - Redistributing? Include/offer to deliver original source      *
#*   Philosophy/full details at http://www.gnu.org/copyleft/gpl.html  *

default_location= "ls13"

class ForecastReader(object):
    def __init__(self):
        self.status= 'Summary unavailable'

    def getStatus(self):
        return "STATUS: %s\n" %(self.status)

    def getSummary(self):
        return self.getStatus()

## BBCReader
##
## For parsing the BBC Weather RSS feeds

class BBCReader(ForecastReader):
    def __init__(self, location):
        super(BBCReader, self).__init__()
        self._location= location

    def getSummary(self):
        report= ["BBC Weather for location '%s':\n" %(self._location)]
        report.extend(self.getStatus())
        return ''.join(report)

if __name__ == "__main__":
    forecast= BBCReader(default_location)
    print(forecast.getSummary())
