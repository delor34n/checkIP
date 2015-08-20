#!/usr/bin/pythona
# -*- coding: utf-8 -*-

import requests, json

ip_url = 'https://wtfismyip.com/json'

response = requests.get(ip_url)
print(response.json())