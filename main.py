#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, json
import sys
import sqlite3 as lite

IP_URL = 'https://wtfismyip.com/json'
PING_URL = 'http://www.google.cl'

def initDB():
	try:
		con = lite.connect('logs.db')
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS ip_log(id INTEGER PRIMARY KEY ASC, hostname TEXT, ip_address TEXT, location TEXT, isp TEXT, when_was_inserted DATE)")
		con.commit()
	except lite.Error as e:
		if con:
			con.rollback()
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.close()

def dropDB():
	try:
		con = lite.connect('logs.db')
		cur = con.cursor()
		cur.execute("DROP TABLE IF EXISTS ip_log")
		con.commit()
	except lite.Error as e:
		if con:
			con.rollback()
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.close()

def insertIP(hostname, ip_address, location, when_was_inserted):
	try:
		con = lite.connect('logs.db')
		cur = con.cursor()
		cur.execute("INSERT INTO ip_log(hostname, ip_address, location, isp, when_was_inserted) VALUES (?, ?, ?, ?)", (hostname, ip_address, location, when_was_inserted))
		con.commit()
	except lite.Error as e:
		if con:
			con.rollback()
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.close()

response = requests.get(IP_URL)
if response.status_code != 200:
	testResponse = requests.get(PING_URL)
	if testResponse.status_code != 200:
		sys.exit("NO INTERNET CONNECTION")
	sys.exit("404 - NOT FOUND")

jsonResponse = response.json()
print(jsonResponse['YourFuckingHostname'])
print(jsonResponse['YourFuckingIPAddress'])
print(jsonResponse['YourFuckingLocation'])
print(jsonResponse['YourFuckingISP'])

dropDB()
initDB()
insertIP(jsonResponse['YourFuckingHostname'], jsonResponse['YourFuckingIPAddress'],
		jsonResponse['YourFuckingLocation'], jsonResponse['YourFuckingISP'])