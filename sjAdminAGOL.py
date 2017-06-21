#sjAccessAGOL.py

#purpose:
#generate content report for arcgis online (AGOL) users

#susan jones
#22 June 2017

#import Modules
import requests, json, urllib, urllib2, getpass, datetime, time, os, io

#set Proxy Server
def setProxyServer(NTUser, NTPass, proxyUrlString):
    proxyString = 'http://' + NTUser + ':' + NTPass + proxyUrlString
    print(proxyString)
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
logFileDir = "\\\\atalgisau01\\admin\\Portal User Content\\AGOL"
base = "https://www.arcgis.com/sharing"
username = "sjonesAT" #raw_input('Administrative AGOL user: ')
password = "cha1tdb123" # getpass.getpass(prompt = 'Enter AGOL password:')


#search parameters
userToSearch = "amitkokje1" #raw_input('AGOL user for content search: ')
num = 10

#log Content
print("\nSet up file for AGOL Content Logging")
fs = open(logFileDir + os.path.sep + "AGOL_" + userToSearch + ".csv", "w")
fs.write("Owner,Folder,ServiceName,ServiceType,NumViews,Created,Modified,Access\n")


#todo collect Content for Selected AGOL users
print("\ngetting Content for " + userToSearch)

#NT Auth Details
print("\nget NT Authentication Details")
domain = 'TRANSPORT\\'
NTUser = domain + getpass.getuser()
NTPass = getpass.getpass(prompt = 'Enter password for TRANSPORT\\' + getpass.getuser() + ':')
proxyUrlString = '@at-proxy.aucklandtransport.govt.nz:8080'

#todo: set Proxy Server
print("\ninstall Proxy Server")
setProxyServer(NTUser, NTPass, proxyUrlString)

#todo: generate Token
print("\ngenerate Token")
token = generateToken(base, username, password)

#todo: fetch Users
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


#get the Users
userList = []
for j in jsonResponse['results']:
    if  j['username'] == userToSearch:
        userList.append(j['username'])
        print(j['username']+"\t"+j['fullName'])
userList.sort()


for user in userList:
    
    print("\ngetting AGOL Content for " + user)
        
    #fetch Content
    print("\nfetch Content for " + userToSearch)
    start = 1
    num = 10
    total = 500
    n = 0

    #loop through content
    while start < total:
        url = base + "/rest/content/users/" + user
        payload = {'f': 'json'
                 ,'username': username
                 ,'password': password
                 ,'num': num
                 ,'start': start        
                 ,'token': token}
        parameters = urllib.urlencode(payload) #remember to generate json content
        response = urllib2.urlopen(url, parameters).read()
        jsp = json.loads(response)
        total = jsp['total']
        if 'items' in jsp.keys():
            for g in jsp['items']: #print("folder = " + str(f['title']))
                n += 1
                created = time.strftime('%d/%m/%Y', time.gmtime(g['created']/1000))
                modified = time.strftime('%d/%m/%Y', time.gmtime(g['modified']/1000))
                url = str(g['url'])
                if url == 'None':
                    url = ""
                title = g['title']
                try:
                    fs.write(userToSearch+",,\""+title.decode().encode('utf-8')+"\","+g['type']+","+str(g['numViews'])+","+str(created)+','+str(modified)+","+g['access']+"\n")
                except:
                    print(g)
            start = start + num


        #content For Folders
        if 'folders' in jsp.keys():
            folders = []
            for f in jsp['folders']:
                folders.append([f['id'],f['title']])
            cnt = n
            ##print("\ngenerate content for Folders")
            for f in folders:
                start = 1
                num = 10
                total = 500
                while start < total:
                    url = base + "/rest/content/users/" + user + "/" + str(f[0])
                    payload = {'f': 'json'
                             ,'username': username
                             ,'password': password
                             ,'num': num
                             ,'start': start        
                             ,'token': token}
                    parameters = urllib.urlencode(payload) #remember to generate json content
                    response = urllib2.urlopen(url, parameters).read()
                    jsp = json.loads(response)
                    total = jsp['total']
                    if 'items' in jsp.keys():
                        for g in jsp['items']: #print("folder = " + str(f['title']))
                            n += 1
                            created = time.strftime('%d/%m/%Y', time.gmtime(g['created']/1000))
                            modified = time.strftime('%d/%m/%Y', time.gmtime(g['modified']/1000))
                            url = str(g['url'])
                            if url == 'None':
                                url = ""
                            title = g['title']
                            try:
                                fs.write(userToSearch+","+f[1]+",\""+title.decode().encode('utf-8')+"\","+g['type']+","+str(g['numViews'])+","+str(created)+','+str(modified)+","+g['access']+"\n")
                            except:
                                print("\nusername:\t"+user)
                                print("\ntitle:\t"+title)
                                print("\ntype:\t"+g['type'])
                                print("created:\t"+str(created))
                                print("modified:\t"+str(modified))
                                print("Folder:\t"+f[1]+"\n")
                                print(g)

                    start = start + num

             #close File
            fs.close()


#end Logging
print("\nContent logged to "+logFileDir)
end = datetime.datetime.now()

#elapsed
print("\nelapsed " + str(end - begin))

#completed
print("\ncompleted")
