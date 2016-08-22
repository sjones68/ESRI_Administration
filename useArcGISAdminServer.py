#useArcGISServer.py

#Todo:
#ESRI ArcGIS Server Loggging

#Functions Implemented
#generateTokenPortal
#setSecurity
#generateUsers
#deleteUsers
#generateContent
#transferOwnership
#transferGroup
#getPortalConfig


#Purpose: Perform ArcGIS Server and ArcGIS Portal Logging

#import Modules
import json, string, os, xml
from urlparse import urlparse, urlunparse
from ntlm import HTTPNtlmAuthHandler

#import Modules
import urllib, urllib2, sys, os, time, unicodedata, codecs, getpass


#set Security
def setSecurity (url, username, password):    
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)
    auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
    opener = urllib2.build_opener(auth_NTLM)
    urllib2.install_opener(opener)


#todo: generate Token
def generateToken(username, password, agsUrl):
    parameters = urllib.urlencode({'username' : username,
                                   'password' : password,
                                   'client' : 'referer',
                                   'referer': agsUrl,
                                   'expiration': 60, #minutes
                                   'f' : 'json'})
    response = urllib2.urlopen(url,parameters).read()
    try:
        jsonResponse = json.loads(response)
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print jsonResponse['error']['message']
            for detail in jsonResponse['error']['details']:
                print detail
    except ValueError, e:
        print 'An unspecified error occurred.'
        print e

#todo: edit Service
def editService(agsUrl):
    print agsUrl



##todo: START HERE - it all starts here

#place a banner in the code
print '***\nManage ArcGIS Admin Server Content\nSusan Jones\nAuckland Transport\n***\n'


#todo: get the server
server = raw_input("get the ArcGIS Server: e.g. ATALGISAU01\n")
if server == '': server = 'ATALGISAP01'
agsUrl = "https://" + server + ".aucklandtransport.govt.nz/arcgis"


#todo: get portal
server = raw_input("get the Portal Server: e.g. ATALGISPSU01\n")
if server == '': server = 'ATALGISAP01'
portalUrl = "https://" + server + ".aucklandtransport.govt.nz/arcgis"


#todo: select The Environment
envList = ['UAT', 'PROD']
selEnv = raw_input(' or '.join(envList) + ' ?\n')


#todo: get The User Credentials
domain = 'TRANSPORT\\'


##username = domain + getpass.getuser()
#username = "agsadmin"
username = domain + getpass.getuser()
password = getpass.getpass(prompt = 'Enter password for ' + username + ':')


#todo: generate ArcGIS admin Token
url = portalUrl + '/sharing/rest/generateToken?'
setSecurity (url, username, password)
token = generateToken(username, password, url)
#print token


#todo: get The Services at the root level
n = 0


#generate Logging
#print 'ArcGIS Server\t' + agsUrl + '\n'

##todo: write to File
folder = '\\\\atalgisau01\\ADMIN\\Portal User Content\\' + selEnv
fs = open(folder + os.path.sep + 'ArcGISContent.csv', 'w+')
fs.write('Folder,serviceName,type,minInstancesPerNode,maxInstancesPerNode,maxWaitTime,maxUsageTime,maxIdleTime\n')


#todo: get and process Arcgis Services
setSecurity (agsUrl + '/admin/services', username, password)
parameters = urllib.urlencode({'f' : 'json', 'token': token})
rootUrl = agsUrl + '/admin/services'
response = urllib2.urlopen(rootUrl,parameters).read()
jsonResponse = json.loads(response)


#todo: loop services
for svc in jsonResponse['services']:
    serviceUrl =  agsUrl + '/admin/services' + svc['folderName'] + svc['serviceName'] + '.' + svc['type']
    setSecurity (serviceUrl, username, password)
    svcResponse = urllib2.urlopen(serviceUrl,parameters).read()
    svcJsonResponse = json.loads(svcResponse)
    #print svcJsonResponse['minInstancesPerNode']
    fs.write('{0},{1},{2},{3},{4},{5},{6},{7}\n'.format('/',svcJsonResponse['serviceName'],svcJsonResponse['type'],svcJsonResponse['minInstancesPerNode'],svcJsonResponse['maxInstancesPerNode'],svcJsonResponse['maxWaitTime'],svcJsonResponse['maxUsageTime'],svcJsonResponse['maxIdleTime']))



#todo: loop folders containing services
for folder in jsonResponse['folders']:
    folderUrl =  agsUrl + '/admin/services' + '/' + folder   ##+ '/' + svc['serviceName'] + '.' + svc['type']
    setSecurity (folderUrl, username, password)
    fldResponse = urllib2.urlopen(folderUrl,parameters).read()
    fldJsonResponse = json.loads(fldResponse)
    for svc in fldJsonResponse['services']:
        serviceUrl = agsUrl + '/admin/services' + '/' + folder + '/' + svc['serviceName'] + '.' + svc['type']
        setSecurity (serviceUrl, username, password)
        svcResponse = urllib2.urlopen(serviceUrl,parameters).read()
        svcJsonResponse = json.loads(svcResponse)
        fs.write('{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(folder,svcJsonResponse['serviceName'],svcJsonResponse['type'],svcJsonResponse['minInstancesPerNode'],svcJsonResponse['maxInstancesPerNode'],svcJsonResponse['maxWaitTime'],svcJsonResponse['maxUsageTime'],svcJsonResponse['maxIdleTime']))

        ##todo: Update gretaer thann maxmaxIdleTime
        #if svcJsonResponse['maxIdleTime'] > 60:

        #    #todo: update the service parameters
        #    svcJsonResponse['minInstancesPerNode'] = 0  #minInstancesPerNode
        #    svcJsonResponse['maxInstancesPerNode'] = 1  #maxInstancesPerNode
        #    svcJsonResponse['maxUsageTime'] = 300  #maxUsageTime
        #    svcJsonResponse['maxIdleTime'] = 60  #maxIdleTime
        #    svcJsonResponse['maxWaitTime'] = 60  #maxWaitTime
        #    svcJsonResponse['recycleInterval'] = 24  #recycleInterval

        #    #todo:update the service
        #    editJson = json.dumps(svcJsonResponse)
        #    editServiceUrl = agsUrl + '/admin/services' + '/' + folder + '/' + svc['serviceName'] + '.' + svc['type'] + '/edit'
        #    editParameters = urllib.urlencode({'f' : 'json', 'token': token, 'service': editJson})
        #    setSecurity (editServiceUrl, username, password)
        #    editResponse = urllib2.urlopen(editServiceUrl, editParameters).read()
        #    print agsUrl + '/admin/services' + '/' + folder + '/' + svc['serviceName'] + '.' + svc['type']
        #    print str(editResponse)


        

##todo: close the file
fs.close()


print '\ncompleted'
