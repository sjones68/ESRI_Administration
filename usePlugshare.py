#sjParseJson.py


#from http://www.plugshare.com/

#import Modules
import json, string, os
from urlparse import urlparse, urlunparse
from ntlm import HTTPNtlmAuthHandler
import urllib2, urllib


#set Security
def setSecurity (url, username, password):    
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)
    auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
    opener = urllib2.build_opener(auth_NTLM)
    urllib2.install_opener(opener)


print "***\nParse Json Data\n***"
latitude = str(-36.848)
delLat = str(1)
longitude = str(174.762)
delLng = str(1)
count = str(100)


username = "transport\SusanJon1"
password = "Cha1tdb1265"
plugShareUrl = "http://www.plugshare.com/api/locations/region?"
parameters = urllib.urlencode({'latitude' : latitude, 'longitude' : longitude, 'spanLat' : delLat, 'spanLng': delLng, 'count': count})

setSecurity (plugShareUrl, username, password)

print "security set"

response = urllib2.urlopen(plugShareUrl, parameters).read()

print response


n= 0
#load
##jsonFile = r'd:\Tmp\all.json'
##csvFile = r'd:\Tmp\all.csv'
##
##fs = open(csvFile,"w")
##
##json_data = open(jsonFile).read()
##responses = json.loads(json_data)
##
##fs.write("stationsId,name,itype,longitude,latitude\n")
##
###loop Response
##for response in responses:
##    stationsId = response['stations'][0]['id']
##    longitude = response['longitude']
##    latitude = response['latitude']
##    name = response['name']
##    itype = response['icon_type']
##    if name == "":
##        name = "n/a"
##    n += 1
##    fs.write(str(n) + "," + name.replace(",", "") + "," + str(stationsId) + "," + itype + "," + str(longitude) + "," + str(latitude) + "\n")
##del responses
##
##fs.close()
##
##print "look at " + csvFile
##print str(n) + " records"

print "\ncompleted"
print "susan is a JSON guru"
