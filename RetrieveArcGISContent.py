#RetrieveArcGISContent.py

#TOOL PURPOSE
#ESRI Portal Content Reporting and Management

#ABSTRACT
#This script contains a numner of function for reporting the user, group and content of ArcGIS Server 
#when managed using Portal. 

#Specifically, it is desgined to access the Portal using the REST API Web Service called from within 
#the organisations corporate network 

#FUNCTIONS IMPLEMENENTED
#1. generateTokenPortal
#2. setSecurity
#3. mapPortalUsers
#4. generateUsers
#5. generateContent
#6. generateAllGroupUsers
#7. generateGroups
#8. getPortalConfig
#9. deletePortalContent

#PYTHON FRAMEWORK
#This script is built and supported for Python 2.7

#DEPENDENCY MODULES
#1. ntlm - windows authentication security module. https://github.com/trustrachel/python-ntlm3

#FRAMEWORK:
#Process:
#START HERE
#get Portal Server from User
#user Authenticates to Portal
#specify UAT/PROD directory for writing
#...
#functions are toggled for self service reporting

#AUTHORING
#Susan Jones
#25 August 2016
#sjones.gis@gmail.com


#Todo: import Modules
import arcpy, json, string, datetime, sys
from urlparse import urlparse, urlunparse
from ntlm import HTTPNtlmAuthHandler
import urllib, urllib2, sys, os, time, unicodedata, codecs, getpass
from operator import itemgetter


#todo: generate portal token
def generateTokenPortal(username, password, portalUrl, callEnd):
    url = portalUrl + callEnd
    parameters = urllib.urlencode({'username' : username,
                                   'password' : password,
                                   'client' : 'referer',
                                   'referer': portalUrl,
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
        arcpy

#todo: set Security
def setSecurity (url, username, password):    
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)
    auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
    opener = urllib2.build_opener(auth_NTLM)
    urllib2.install_opener(opener)


#todo: map Group Accees for all portal users
def mapPortalUsers(allUserList):

    #todo: admin user list
    adminUserList = ['AmitKokj1@TRANSPORT', 'ChristoP1@TRANSPORT', 'SusanJon1@TRANSPORT', 'ChrisWhe1@TRANSPORT', 'adm_AmitKokj1@TRANSPORT']

    #todo: prepare PortalGroupAccess.csv for Writing
    print 'todo: prepare PortalGroupAccess.csv for Writing'
    fs = open(folder + os.path.sep + "PortalGroupAccess.csv", "w+")

    #todo: get All Portal Groups
    header = 'UserName'
    users = []
    groups=[]
    for rec in sorted(allUserList, key = itemgetter(1)):
        if not rec[1] in groups:
            groups.append(rec[1])
    groups.sort()

    #sort user for users
    for rec in sorted(allUserList, key = itemgetter(0)):
        if not rec[0] in users:
            users.append(rec[0])
    users.sort()

    #todo: get Columns Names for the Header
    header = 'UserName'
    f = 1
    for grp in groups:
        col = "col" + str(f)
        header = header + ',\"' + grp + '\"' ##grp.strip()
        f += 1 
    fs.write(header+'\n')

    #todo: get User Access
    #cycle through the users  
    cnt = 0                              
    for user in users:

        #cycle through the groups
        belongList = []
        for rec in sorted(allUserList, key = itemgetter(0)):
            if rec[0] == user:
                if rec[1] in groups:
                    belongList.append(groups.index(rec[1]))


        #get all group membership for user (and write to the file)
        f = 0
        t = 0
        row = user
        while f < len(groups):
            if f in belongList:
                row = row + ',X'
                t += 1
            else:
                row = row + ','
            f += 1
        fs.write(row+'\n')

        #todo: remove User
        if t == 1:
            #check if user
            cnt += 1
            if not user in adminUserList:
                deleteUserURL = portalUrl + 'sharing/rest/community/users/' + user  + '/delete'     
                #setSecurity (deleteUserURL, username, password)
                #parameter = urllib.urlencode({'f' : 'json'})
                #deleteUserResponse = urllib2.urlopen(deleteUserURL, parameter).read()
                #deleteUserJson = json.loads(deleteUserResponse)
                #print deleteUserJson

    #close the File
    fs.close()


#todo: generate Users
def generateUsers(folder):
    start = 1
    f = 1
    num = 100
    query = "a*"
    url = portalUrl + 'sharing/rest/community/users?'
    setSecurity (url, username, password)

    #todo: get Total Content
    parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
    response = urllib2.urlopen(url, parameters ).read()
    jsonResponse = json.loads(response)
    total = jsonResponse['total']
    #print str(total) + ' users'
    allPortalUsers = []

    #todo: prepare file for writing
    fs = open(folder + os.path.sep + "PortalUsers.csv", "w+")
    fs.write("Username,Full Name,Created,Modified,LastLogin\n")
    #cycle through the users
    while f < total + 1:
        parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
        response = urllib2.urlopen(url, parameters ).read()
        jsonResponse = json.loads(response)
        #loop 
        for i in jsonResponse['results']:
            created = time.strftime('%d/%m/%Y', time.gmtime(i['created']/1000))
            modified = time.strftime('%d/%m/%Y', time.gmtime(i['modified']/1000))

            #todo: get lastlogin
            try:

                #todo: allPortalUsers list
                #if not i['username'] in allPortalUsers:
                allPortalUsers.append([i['username'], 'No Group', 'U'])

                #collect user details
                userUrl = portalUrl + 'sharing/rest/community/users/' + i['username']       
                parameter = urllib.urlencode({'f' : 'json'})
                userResponse = urllib2.urlopen(userUrl, parameter).read()
                userJson = json.loads(userResponse)
                lastlogin = time.strftime('%d/%m/%Y', time.gmtime(userJson['lastLogin']/1000))
            except:
                print 'cannot process\t' + i['username']  
                lastlogin = ''

            fs.write(i['username'] + ',' + i['fullName'] + ',' + created + ',' + modified + ',' + lastlogin + '\n') #username,fullName,created          
            f+=1
        start += 100
    fs.close()

    #return Parameters
    return allPortalUsers


#todo: generate Content
def generateContent(folder):
    #todo: output List
    start = 1
    f = 1
    num = 100
    query = "a*"
    url = portalUrl + 'sharing/rest/search?'
    setSecurity (url, username, password)

    #todo: get Total Content
    parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
    response = urllib2.urlopen(url, parameters ).read()
    jsonResponse = json.loads(response)
    total = jsonResponse['total']
    #print str(total) + ' content'

    #todo: prepare file for writing
    fs = open(folder + os.path.sep + "PortalContent.csv", mode = "w+")
    fs.write("Owner,Title,Created,Modified,URL,NumViews,Type\n")
    fsH = open(folder + os.path.sep + "PortalContentHosted.csv", mode = "w+")
    fsH.write("Owner,Title,Created,Modified,URL,NumViews,Type\n")
    fsNH = open(folder + os.path.sep + "PortalContentNonHosted.csv", mode = "w+")
    fsNH.write("Owner,Title,Created,Modified,URL,NumViews,Type\n")
    while f < total + 1: 
        parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
        response = urllib2.urlopen(url, parameters ).read()
        jsonResponse = json.loads(response)     
        #loop through the Results
        for i in jsonResponse['results']:
            created = time.strftime('%d/%m/%Y', time.gmtime(i['created']/1000))
            modified = time.strftime('%d/%m/%Y', time.gmtime(i['modified']/1000))
            ##print to file
            if string.find(i['owner'], 'esri') == -1:
                serviceInfo = (i['owner'] + ',\"' + i['title'] + '\",' + created + ',' + modified + ',' + str(i['url']) + ',' + str(i['numViews']) + ',' + i['type'] + '\n' )
                fs.write(serviceInfo)
            if string.find(i['owner'], 'esri') == -1 and str(i['url']) == 'None':
                serviceInfo = (i['owner'] + ',\"' + i['title'] + '\",' + created + ',' + modified + ',' + str(i['url']) + ',' + str(i['numViews']) + ',' + i['type'] + '\n' )
                fsNH.write(serviceInfo)
            if string.find(i['owner'], 'esri') == -1 and str(i['url']) <> 'None':
                serviceInfo = (i['owner'] + ',\"' + i['title'] + '\",' + created + ',' + modified + ',' + str(i['url']) + ',' + str(i['numViews']) + ',' + i['type'] + '\n' )
                fsH.write(serviceInfo)
            f+=1
        start += 100
    fs.close()
    fsH.close()
    fsNH.close()


#todo: Get All Group Users
def generateAllGroupUsers(portalUrl):

    #todo: start Empty
    allUserList = []

    start = 1
    f = 1
    num = 100
    query = "a*"
    url = portalUrl + 'sharing/rest/community/groups?'
    setSecurity (url, username, password)

    #todo: get Total Content
    parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
    response = urllib2.urlopen(url, parameters ).read()
    jsonResponse = json.loads(response)
    total = jsonResponse['total']
    #print str(total) + ' content'

    #cycle All the groups
    while f < total + 1: 
        parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
        response = urllib2.urlopen(url, parameters ).read()
        jsonResponse = json.loads(response)     
        #loop through the Results
        for i in jsonResponse['results']:

            #todo: process each Group
            if string.find(i['owner'], 'esri') == -1:

                allUserList.append([i['owner'], 'No Group', 'U'])

                groupUrl = portalUrl + 'sharing/rest/community/groups/' + i['id'] + '/users?'       
                #todo: drill through the Users
                parameter = urllib.urlencode({'f' : 'json'})
                grpResponse = urllib2.urlopen(groupUrl, parameter).read()
                grpJsonResponse = json.loads(grpResponse)

                ##admin
                for admin in  grpJsonResponse['admins']:
                    allUserList.append([admin, i['title'], 'A'])

                #users
                for user in  grpJsonResponse['users']:
                    allUserList.append([user, i['title'], 'U'])

            f+=1
        start += 100

    #todo: Sort
    allUserList.sort()

    #return allUserList
    return allUserList


#todo: generate Groups
def generateGroups(folder, allPortalUsers):
    #todo: initialise
    uniqueGroups = []
    allUserList = []
    start = 1
    f = 1
    num = 100
    query = "a*"
    url = portalUrl + 'sharing/rest/community/groups?'
    setSecurity (url, username, password)

    ##todo: prepare file for writing
    fs = open(folder + os.path.sep + "PortalGroup.txt", "w")
    fs.write("Portal Group Documentation for " + portalUrl + "\n")

    #todo: loop Users and Group Ownership
    tempUser = []
    for rec in allPortalUsers:
        tempUser.append(rec[0])
    tempUser.sort()

    #todo: Process Users
    for user in tempUser:

        #user
        print "Processing:\t" + user + " Content"

        #todo: get Owner Groups
        grpUrl = portalUrl + 'sharing/rest/community/groups?'  
        setSecurity (grpUrl, username, password)
        grpParams = urllib.urlencode({'f' : 'json', 'q' : user, 'start' : start, 'num' : num}) #remember to generate json content
        grpResponse = urllib2.urlopen(grpUrl, grpParams).read()
        grpjsonResponse = json.loads(grpResponse)

        #get the Group Properties
        for grp in grpjsonResponse['results']:

            #check for reprocessing of Groups
            if not grp['title'] in uniqueGroups:
                uniqueGroups.append(grp['title'])

                ##todo: check User in Groups
                getUserUrl = portalUrl + 'sharing/rest/community/groups/' + grp['id']

                #todo: test the user url
                setSecurity (getUserUrl, username, password)
                getUserParams = urllib.urlencode({'f' : 'json'}) #remember to generate json content
                getUserResponse = urllib2.urlopen(getUserUrl, getUserParams).read()
                getUserJsonResponse = json.loads(getUserResponse)
                #todo: make usergroup List1
                created = time.strftime('%d/%m/%Y', time.gmtime(getUserJsonResponse['created']/1000))
                modified = time.strftime('%d/%m/%Y', time.gmtime(getUserJsonResponse['modified']/1000))
                #todo: process each Group
                groupUserUrl = portalUrl + 'sharing/rest/community/groups/' + str(grp['id']) + '/users?'      
                #todo: drill through the Users
                groupUserParameter = urllib.urlencode({'f' : 'json'})
                setSecurity (groupUserUrl, username, password)
                groupUserResponse = urllib2.urlopen(groupUserUrl, groupUserParameter).read()
                groupUserJsonResponse = json.loads(groupUserResponse)
                #print grpJsonResponse
                fs.write('\n--------------------\nGroup:\t' +  str(grp['title']) + '\n')
                fs.write('Created:\t' + created)
                fs.write('\nModified:\t' + modified)
                fs.write('\nAdmins:')
                #admins
                for admins in  groupUserJsonResponse['admins']:
                    fs.write('\n\t' + admins)

                    #check if admins in allUserList
                    allUserList.append([admins, str(grp['title']), 'A'])
                #users
                fs.write('\nUsers:')
                for users in  groupUserJsonResponse['users']:
                    fs.write('\n\t' + users)

                    #check if admins in allUserList
                    allUserList.append([users, str(grp['title']), 'U'])

    #close the file
    fs.close() 

    #return
    allUserList.sort()
    return allUserList


#todo: get Portal Content
def getPortalConfig(portalUrl):  #get the portal arcgis base

    print '\nPortal Configuration\t' + portalUrl + '\n'

    contentPortal = portalUrl + 'sharing/rest/portals/self'
    setSecurity (contentPortal, username, password)
    params = urllib.urlencode({'f' : 'json'})
    contentResponse = urllib2.urlopen(contentPortal, params ).read()
    jsonContentResponse = json.loads(contentResponse)

    #list of items Not to incluse
    contentLst = ['user', 'defaultBasemap', 'defaultExtent','rotatorPanels', 'helperServices', 'layerTemplatesGroupQuery', 'helpMap']

    for content in jsonContentResponse:
        #if not in list
        if content not in contentLst:
            print content + '\n' + str(jsonContentResponse[content]) 

    if content == 'user':
        print '\n' + content[user]


#todo: delete Portal Content
def deletePortalContent(folder):
    start = 1
    f = 1
    num = 100
    query = "a*"
    url = portalUrl + 'sharing/rest/search?'
    setSecurity (url, username, password)

    #todo: admin user list
    adminUserList = ['AmitKokj1@TRANSPORT', 'ChristoP1@TRANSPORT', 'SusanJon1@TRANSPORT', 'ChrisWhe1@TRANSPORT', 'adm_AmitKokj1@TRANSPORT']

    #todo: get Total Content
    parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
    response = urllib2.urlopen(url, parameters ).read()
    jsonResponse = json.loads(response)
    total = jsonResponse['total']
    print str(total) + ' content'

    #todo: 
    fs = open(folder + os.path.sep + "ContentToDelete.csv", "w+")
    fs.write("Title,Owner,Created,Modified\n")

    #todo: prepare To Delete Content
    deleteUrl = portalUrl + 'sharing/rest/content/users/'
    while f < total + 1: 
        parameters = urllib.urlencode({ 'q' : query, 'f' : 'json', 'start' : start, 'num' : num}) #remember to generate json content
        setSecurity (url, username, password)
        response = urllib2.urlopen(url, parameters ).read()
        jsonResponse = json.loads(response)     
        #loop through the Results
        for i in jsonResponse['results']:
            created = time.strftime('%d/%m/%Y', time.gmtime(i['created']/1000))
            modified = time.strftime('%d/%m/%Y', time.gmtime(i['modified']/1000))
            ##print to file
            if i['numViews'] == 0 and string.find(i['owner'], "esri") == -1 and not i['owner'] in adminUserList:
                ##serviceInfo = (i['owner'] + ',\"' + i['title'] + '\",' + created + ',' + modified + ',' + str(i['url']) + ',' + str(i['numViews']) + ',' + i['type'] + '\n' )
                fs.write(i['title'] + "," + i['owner'] + "," + created + "," + modified + "\n") 
                deleteItemUrl = deleteUrl + i['owner'] + "/items/" + i['id'] + "/delete"
                #deleteParameters = urllib.urlencode({ 'f' : 'json'})
                #setSecurity (deleteItemUrl, username, password)
                #deleteResponse = urllib2.urlopen(deleteItemUrl, deleteParameters).read()
                #print json.loads(deleteResponse)
                print deleteItemUrl


            f+=1
        start += 100
    fs.close()




#todo: START HERE
#place a banner in the code
print '***\nESRI Portal Content Reporting and Management\nSusan Jones\n***\n'

#todo: set The Portal Connections
server = raw_input('get the portal server name:')
portalUrl = 'https://' + server +'.aucklandtransport.govt.nz/arcgis/'
ending='sharing/rest/generateToken?'


#todo: show The server
print 'Portal\t' + portalUrl + '\n'


#user credentials
domain = 'TRANSPORT\\'
username = domain + getpass.getuser()
password = getpass.getpass(prompt = 'Enter password for ' + username + ':')


#output Folder
envLst = ['UAT','PROD']
envn = raw_input(" or ".join(envLst) + '\n')
folder = '\\\\atalgisaU01\\ADMIN\\Portal User Content\\' + envn


#todo: generate Token
print 'generate Token...'
setSecurity (portalUrl + 'sharing/rest/generateToken?', username, password)
token = generateTokenPortal(username, password, portalUrl, 'sharing/rest/generateToken?')


#todo: generate Content
print "\ntodo: generate Content"
generateContent(folder)


#todo: generate Users
print "\ntodo: generate Users"
allPortalUsers = generateUsers(folder)
print 'user Group List ' + str(len(allPortalUsers))


#todo: better User and Group Management
print '\ntodo: better User and Group Management'


#todo: generate Groups
print "\ntodo: generate Groups"
groupUserList = generateGroups(folder, allPortalUsers)
print 'user Group List ' + str(len(groupUserList))


#todo: generate All Group Users
print "\ntodo: generate All Group Users"
allUsers = generateAllGroupUsers(portalUrl)  #get users in groups
print 'all Group List ' + str(len(allUsers))


#allUserList = allUsers
allUserList = groupUserList + allPortalUsers


#todo: map Users To Groups
print "\ntodo: map Users To Groups"
mapPortalUsers(allUserList)


#todo: delete Portal Content
#print "\ntodo: delete Portal Content"
#deletePortalContent(folder)


#todo: get Portal Configuration
#print 'get Portal Configuration'
#getPortalConfig(portalUrl)


#completion message
print "\ncompleted"
