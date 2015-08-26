#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, json
import sys
import sqlite3 as lite
from datetime import datetime
import configparser

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import os

def initDB():
	try:
		con = lite.connect('logs.db')
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS ip_log(id INTEGER PRIMARY KEY ASC AUTOINCREMENT, hostname TEXT, ip_address TEXT, location TEXT, isp TEXT, when_was_inserted DATE)")
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

def insertIP(hostname, ip_address, location, isp, when_was_inserted):
	try:
		con = lite.connect('logs.db')
		cur = con.cursor()
		cur.execute("INSERT INTO ip_log(hostname, ip_address, location, isp, when_was_inserted) VALUES (?, ?, ?, ?, ?)", (hostname, ip_address, location, isp, when_was_inserted))
		con.commit()
	except lite.Error as e:
		if con:
			con.rollback()
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.close()

def getLastIP():
	try:
		con = lite.connect('logs.db')
		cur = con.cursor()
		cur.execute("SELECT * FROM ip_log ORDER BY id DESC LIMIT 1")
		rows = cur.fetchall()
	except lite.Error as e:
		if con:
			con.rollback()
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.close()
		return rows

def mail(to, subject, server_name, hostname, ip_address, location, isp, when_was_inserted):
	msg = MIMEMultipart('alternative')

	msg['From'] = server_name
	msg['To'] = to
	msg['Subject'] = subject

	head = open ("head.html", "r")
	html = head.read()
	body = open ("email.html", "r")
	html += body.read().format(hostname=hostname, ip_address=ip_address, location=location, isp=isp, when_was_inserted=when_was_inserted)

	msg.attach(MIMEText(html, 'html'))

	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(GMAIL_USER, GMAIL_PASSWORD)
	mailServer.sendmail(GMAIL_USER, to, msg.as_string())
	mailServer.close()

############################################################
############################################################
############################################################


configParser = configparser.RawConfigParser()   
configFilePath = r'email.cfg'
configParser.read(configFilePath)

IP_URL = configParser.get('URLS', 'IP_URL')
PING_URL = configParser.get('URLS', 'PING_URL')
response = requests.get(IP_URL)
if response.status_code != 200:
	testResponse = requests.get(PING_URL)
	if testResponse.status_code != 200:
		sys.exit("NO INTERNET CONNECTION")
	sys.exit("404 - NOT FOUND")

jsonResponse = response.json()

initDB()
lastIP = getLastIP()
if lastIP == []:
	print("Inserting first IP address "+jsonResponse['YourFuckingIPAddress'])
	insertIP(jsonResponse['YourFuckingHostname'], jsonResponse['YourFuckingIPAddress'],
			 jsonResponse['YourFuckingLocation'], jsonResponse['YourFuckingISP'], datetime.now())
	newIP = getLastIP()

	GMAIL_USER = configParser.get('EMAIL', 'GMAIL_USER')
	GMAIL_PASSWORD = configParser.get('EMAIL', 'GMAIL_PASSWORD')
	SERVER_NAME = configParser.get('SERVER', 'SERVER_NAME')

	mail(configParser.get('EMAIL', 'TO_EMAIL'),
	   	 configParser.get('EMAIL', 'SUBJECT_EMAIL'),
	   	 SERVER_NAME,
	   	 newIP[0][1],
	   	 newIP[0][2],
	   	 newIP[0][3],
	   	 newIP[0][4],
	   	 newIP[0][5])
elif lastIP[0][2] != jsonResponse['YourFuckingIPAddress']:
	print("Inserting new IP address "+jsonResponse['YourFuckingIPAddress'])
	insertIP(jsonResponse['YourFuckingHostname'], jsonResponse['YourFuckingIPAddress'],
			 jsonResponse['YourFuckingLocation'], jsonResponse['YourFuckingISP'], datetime.now())
	newIP = getLastIP()

	GMAIL_USER = configParser.get('EMAIL', 'GMAIL_USER')
	GMAIL_PASSWORD = configParser.get('EMAIL', 'GMAIL_PASSWORD')
	SERVER_NAME = configParser.get('SERVER', 'SERVER_NAME')

	mail(configParser.get('EMAIL', 'TO_EMAIL'),
	   	 configParser.get('EMAIL', 'SUBJECT_EMAIL'),
	   	 SERVER_NAME,
	   	 newIP[0][1],
	   	 newIP[0][2],
	   	 newIP[0][3],
	   	 newIP[0][4],
	   	 newIP[0][5])
else:
	print("No IP changes")