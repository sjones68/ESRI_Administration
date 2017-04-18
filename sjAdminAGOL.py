#sjAccessAGOL.py

#import Modules
import requests, json, urllib, urllib2, getpass, datetime, time, os

#set Proxy Server
def setProxyServer(NTUser, NTPass, proxyUrlString):
    proxyString = 'http://' + NTUser + ':' + NTPass + proxyUrlString
    proxy_handler = urllib2.ProxyHandler({'http': proxyString, 'https': proxyString})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)


#generate Token
def generateToken(base, username, password):
    url = base + "/generateToken?"
    payload  = {'username' : username
                 ,'password' : password
                 ,'referer' : base
                 ,'f' : 'json' }
    parameters = urllib.urlencode(payload) #remember to generate json content
    response = urllib2.urlopen(url, parameters).read()
    jsonResponse = json.loads (response)
    token = jsonResponse['token']
    return token



##START HERE
print("***\nAccess REST Admin AGOL\n***")  

#begin Logging
begin = datetime.datetime.now()

#collect Parameters
print("\ncollect Parameters")
base = "https://www.arcgis.com/sharing"

username = "ATeamGIS"
password = "ATeamGIS1"

#search parameters
userToSearch = raw_input('AGOL user for content search: ')
num = 10

#log Content
print("\nSet up file for AGOL Content Logging")
logFileDir = "d:\\tmp\\"
fs = open(logFileDir + os.path.sep + "AGOL_" + userToSearch + ".csv", "w")
fs.write("Owner,Folder,ServiceName,ServiceType,NumViews,Created,Modified,Access\n")


#todo Puprose is to collect content
print("\ngetting Content for " + userToSearch)

#NT Auth Details
print("\nget NT Authentication Details")
domain = 'TRANSPORT\\'
NTUser = domain + getpass.getuser()
NTPass = getpass.getpass(prompt = 'Enter password for ' + getpass.getuser() + ':')
proxyUrlString = '@at-proxy.aucklandtransport.govt.nz:8080'

#Proxy Server
print("\ninstall Proxy Server")
setProxyServer(NTUser, NTPass, proxyUrlString)

#Generate Token
print("\ngenerate Token")
token = generateToken(base, username, password)

#fetch Users
print("\nfetch Users")
url = base + "/rest/community/users?"
payload = {'f': 'json'
         ,'username': username
         ,'password': password
         ,'q': userToSearch
         ,'num': num
         ,'token': token}
parameters = urllib.urlencode(payload) #remember to generate json content
response = urllib2.urlopen(url, parameters).read()
jsonResponse = json.loads(response)
total = jsonResponse['total']
if total == 1:
    for j in jsonResponse['results']:
        userName = j['username']
        fullName = j['fullName']
        print("\ngetting AGOL Content for " + userName)


#fetch Content
print("\nfetch Content for " + userToSearch)
start = 1
num = 10
total = 500
n = 0
while start < total:
    url = base + "/rest/content/users/" + userToSearch
    payload = {'f': 'json'
             ,'username': username
             ,'password': password
             ,'num': num
             ,'start': start        
             ,'token': token}
    parameters = urllib.urlencode(payload) #remember to generate json content
    response = urllib2.urlopen(url, parameters).read()
    jsonResponse = json.loads(response)
    total = jsonResponse['total']
    for g in jsonResponse['items']: #print("folder = " + str(f['title']))
        n += 1
        created = time.strftime('%d/%m/%Y', time.gmtime(g['created']/1000))
        modified = time.strftime('%d/%m/%Y', time.gmtime(g['modified']/1000))
        url = str(g['url'])
        if url == 'None': url = ""
        fs.write(userToSearch+",,\""+g['title']+"\","+g['type']+","+str(g['numViews'])+","+str(created)+','+str(modified)+","+g['access']+"\n") 
    start = start + num



#content For Folders
folders = []
for f in jsonResponse['folders']:
    folders.append([f['id'],f['title']])
cnt = n
##print("\ngenerate content for Folders")
for f in folders:
    start = 1
    num = 10
    total = 500
    while start < total:
        url = base + "/rest/content/users/" + userToSearch + "/" + str(f[0])
        payload = {'f': 'json'
                 ,'username': username
                 ,'password': password
                 ,'num': num
                 ,'start': start        
                 ,'token': token}
        parameters = urllib.urlencode(payload) #remember to generate json content
        response = urllib2.urlopen(url, parameters).read()
        jsonResponse = json.loads(response)
        total = jsonResponse['total']
        for g in jsonResponse['items']: #print("folder = " + str(f['title']))
            n += 1
            created = time.strftime('%d/%m/%Y', time.gmtime(g['created']/1000))
            modified = time.strftime('%d/%m/%Y', time.gmtime(g['modified']/1000))
            url = str(g['url'])
            if url == 'None': url = ""
            fs.write(userToSearch+","+f[1]+",\""+g['title']+"\","+g['type']+","+str(g['numViews'])+","+str(created)+','+str(modified)+","+g['access']+"\n")
        start = start + num

 #close File
fs.close()

#end Logging
end = datetime.datetime.now()

#elapsed
print("\nelapsed " + str(end - begin))

#completed
print("\ncompleted")

