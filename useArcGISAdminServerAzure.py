#useArcGISAdminServerAzure.py

#TOOL PURPOSE
#Report an Edit the current Services hosted in an ESRI ArcGIS Server environment

#FUNCTIONS IMPLEMENTED
#1. setSecurity
#2. generateToken
#3. editService

#PYTHON FRAMEWORK
#This script is built and supported for Python 2.7

#DEPENDENCY MODULES
#1. ntlm - windows authentication security module. https://github.com/trustrachel/python-ntlm3

#FRAMEWORK:
#Process:
#START HERE
#get ArcGIS Server from User
#get ESRI Portal from User
#user Authenticates to Portal
#specify UAT/PROD directory for writing
#...
#functions are toggled for self service reporting
#NB Need to edit the service paramters in editService module - commented out for now

#AUTHORING
#Susan Jones
#25 August 2016
#sjones.gis@gmail.com


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

#get ArcGIS Service Into
def getArcGISServiceInfo(serviceUrl,folder):
    #serviceUrl =  agsUrl + '/admin/services' + svc['folderName'] + svc['serviceName'] + '.' + svc['type']
    setSecurity (serviceUrl, username, password)
    svcResponse = urllib2.urlopen(serviceUrl,parameters).read()
    svcJsonResponse = json.loads(svcResponse)
    agsServiceInfo = '{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(folder,svcJsonResponse['serviceName'],svcJsonResponse['type'],svcJsonResponse['minInstancesPerNode'],svcJsonResponse['maxInstancesPerNode'],svcJsonResponse['maxWaitTime'],svcJsonResponse['maxUsageTime'],svcJsonResponse['maxIdleTime'])
    return agsServiceInfo

#get Manifest The Service and write to text file
def manifestService(serviceUrl, folder):
    manifestUrl = serviceUrl + '/iteminfo/manifest/manifest.json'
    setSecurity (manifestUrl, username, password)
    manifestResponse = urllib2.urlopen(manifestUrl,parameters).read()
    manifestJsonResponse = json.loads(manifestResponse)
    #fetch The Resource
    mxd = ''
    sp = ''
    try:
        if manifestJsonResponse['resources'] != None: 
            for m in manifestJsonResponse['resources']: 
                mxd = (m['onPremisePath']) 
                client = (m['clientName']) 
                sp = (m['serverPath']) 
        #fetch the datasources
        for d in manifestJsonResponse['databases']:
            ds = d['datasets']
            conn = d['onServerConnectionString']
            for fc in ds:
                sName = str(svc['serviceName'])+'.'+str(svc['type'])
                data = str(fc['onServerName'])
                dsWrite = data+','+folder+','+sName+','+str(mxd)+','+str(client)+','+str(sp)
                fds.write(dsWrite+'\n')
    except: print('cannot Process:\t' + serviceUrl)

#update ArcGIS Service Parameters
def updateArcGISServiceParameters(serviceUrl, env):
    print("updating "+serviceUrl)
    setSecurity (serviceUrl, username, password)
    svcResponse = urllib2.urlopen(serviceUrl,parameters).read()
    svcJsonResponse = json.loads(svcResponse)
    #fetch service
    fs.write('{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(folder,svcJsonResponse['serviceName'],svcJsonResponse['type'],svcJsonResponse['minInstancesPerNode'],svcJsonResponse['maxInstancesPerNode'],svcJsonResponse['maxWaitTime'],svcJsonResponse['maxUsageTime'],svcJsonResponse['maxIdleTime']))
    #todo:update the service
    editJson = json.dumps(svcJsonResponse)
    editServiceUrl = serviceUrl + '/edit'
    editParameters = urllib.urlencode({'f' : 'json', 'token': token, 'service': editJson})
    setSecurity (editServiceUrl, username, password)
    editResponse = urllib2.urlopen(editServiceUrl, editParameters).read()
    #todo: Update gretaer thann maxIdleTime
    #preproduction
    if env in ["uat", "pp"]:
        maxUsageTime = 60
        maxIdleTime = 180
        maxWaitTime = 60
        minInstancesPerNode = 0
        maxInstancesPerNode = 1
    #production
    if env == "prod":
        maxUsageTime = 300
        maxIdleTime = 180
        maxWaitTime = 60
        minInstancesPerNode = 1
        #maxInstancesPerNode = 3
    #todo: Standardise settings
    if svcJsonResponse['maxIdleTime'] <> maxIdleTime or svcJsonResponse['maxUsageTime'] <> maxUsageTime or svcJsonResponse['maxWaitTime'] <> maxWaitTime or svcJsonResponse['maxInstancesPerNode'] <> maxInstancesPerNode  or svcJsonResponse['minInstancesPerNode'] <> minInstancesPerNode:
        #todo: update the service parameters
        svcJsonResponse['minInstancesPerNode'] = minInstancesPerNode  #minInstancesPerNode
        svcJsonResponse['maxInstancesPerNode'] = maxInstancesPerNode  #maxInstancesPerNode
        svcJsonResponse['maxUsageTime'] = maxUsageTime  #600 prod 
        svcJsonResponse['maxIdleTime'] = maxIdleTime  #180 prod 
        svcJsonResponse['maxWaitTime'] = maxWaitTime  #60 prod 
        #todo:update the service
        editJson = json.dumps(svcJsonResponse)
        editParameters = urllib.urlencode({'f' : 'json', 'token': token, 'service': editJson})
        setSecurity (editServiceUrl, username, password)
        editResponse = urllib2.urlopen(editServiceUrl, editParameters).read()
        print(str(editResponse)+':\t'+svcJsonResponse['serviceName'])


##todo: START HERE - it all starts here
#place a banner in the code
print '***\nManage ArcGIS Admin Server Content in Azure\nSusan Jones\nAuckland Transport\n***\n'

#get the server
env = raw_input("get the GIS Environment: e.g. PROD/PP/TEST\n")
u = "Susan.Jones"
p = "Cha1tdb123"
if string.lower(env) == 'prod':
    server = 'maps'
elif string.lower(env) == 'pp': 
    server = 'ppmaps'
elif string.lower(env) == 'test': 
    env = "uat"
    server = 'atwebtst01'
    u = "SusanJones"
    p = "Cha1tdb123"
else: 
    server = 'maps'
agsUrl = "https://"+server+".at.govt.nz/arcgis"

#todo: get portal and environments
portalUrl = "https://" + server + ".at.govt.nz/arcgis"

#get the windows domain credentials
domain = 'TRANSPORT\\'
username = domain + getpass.getuser()
password = getpass.getpass(prompt = 'Enter password for ' + username + ':')

#todo: generate ArcGIS admin Token
url = portalUrl + '/sharing/rest/generateToken?'
setSecurity (url, username, password)
token = generateToken(u, p, url)

#todo: get The Services at the root level
n = 0

#generate Logging
print('ArcGIS Server\t'+agsUrl+'\n')

#write arcgis service info to a file
folder = r"C:\Users\Susanjon1\OneDrive - Auckland Transport\GIS Azure"
fileAGSToWrite = folder+os.path.sep+env+os.path.sep+'ArcGISContent.csv'
print(fileAGSToWrite)
fs = open(fileAGSToWrite, 'w+')
fs.write('Folder,serviceName,type,minInstancesPerNode,maxInstancesPerNode,maxWaitTime,maxUsageTime,maxIdleTime\n')

#wrte data sources to a file
fileDSSToWrite = folder+os.path.sep+env+os.path.sep+'ArcGISDatasets.csv'
fds = open(fileDSSToWrite, 'w+')
fds.write('Dataset,Folder,Service,onPremisePath,clientName,ServerPath\n')

#todo: get and process Arcgis Services
setSecurity (agsUrl + '/admin/services', u, p)
parameters = urllib.urlencode({'f' : 'json', 'token': token})
rootUrl = agsUrl + '/admin/services'
response = urllib2.urlopen(rootUrl,parameters).read()
jsonResponse = json.loads(response)

#todo: loop services
f = ''
print("Root Folder")
for svc in jsonResponse['services']:
    serviceUrl =  agsUrl + '/admin/services' + svc['folderName'] + svc['serviceName'] + '.' + svc['type']
    #todo: get The Service Definition Parameters
    try:
        agsInfo = getArcGISServiceInfo(serviceUrl, '')
        fs.write(agsInfo)
    except: print('cannot Get Datasource:\t' + serviceUrl)
    #todo: manifest The Service
    try:    
        manifestService(serviceUrl, '') 
    except: print("error:\t"+serviceUrl)
    ##todo: update The service definition
    #try:    
    #    updateArcGISServiceParameters(serviceUrl, string.lower(env))
    #except: print("cannot Update:\t"+serviceUrl)

#todo: get The Folders
folders = []
for f in jsonResponse['folders']: 
    if f not in ['Hosted', 'System', 'Utilities']: folders.append(f)

#todo: loop Though the Folders and Map Services
for f in folders:
    print(f)
    #todo: change indent here
    #for folder in folders:
    folderUrl =  agsUrl + '/admin/services' + '/' + f   ## + '/' + svc['serviceName'] + '.' + svc['type']
    setSecurity (folderUrl, username, password)
    fldResponse = urllib2.urlopen(folderUrl,parameters).read()
    fldJsonResponse = json.loads(fldResponse)
    for svc in fldJsonResponse['services']:
        serviceUrl = agsUrl + '/admin/services' + '/' + f + '/' + svc['serviceName'] + '.' + svc['type']
        #todo: get The Service Definition Parameters
        try:
            agsInfo = getArcGISServiceInfo(serviceUrl, f)
            fs.write(agsInfo)
        except: print('cannot Get Datasource:\t' + serviceUrl)
        #todo: manifest The Service
        try:    
            manifestService(serviceUrl, f) 
        except:             print("error:\t"+serviceUrl)
        #todo: update The service definition
        #try:    
        #    updateArcGISServiceParameters(serviceUrl, string.lower(env))
        #except: print("cannot Update:\t"+serviceUrl)

##todo: close the file
fs.close()
fds.close()

#notify Completion
print '\ncompleted'
