# ESRI_Administration for ESRI ArcGIS Server and ESRI Portal
Scripting for Portal Administration

#Purpose: ESRI Portal and ESRI ArcGIS Server Maintenance Tasks

#Dependant modules required
 - ntlm
 - arcpy

Both scripts are build on the REST API for
ESRI Portal 10.3
ESRI ArcGIS Server 10.3

#RetrieveArcGISContent.py
- generateTokenPortal
- setSecurity (NTLM)
- mapPortalUsers - creates a visual graphic of relationship between Portal Users and Portal Groups
- generateUsers - current users from ESRI Portal
- generateContent - audits all the user Portal content
- generateAllGroupUsers - generate all users for all Portal Groups
- generateGroups - audits all the Portal Groups
- getPortalConfig - fecth current Portal configuration
- deletePortalContent - remove Portal Content

#useArcGISAdminServer.py - generates all ArcGIS Server Content

Susan Jones
Auckland
sjones@spatiallogic.co.nz

24 August 2016
