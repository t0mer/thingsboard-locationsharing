import requests
import os
import pickle
import http.client 
import re
import requests
import pprint
from loguru import logger
import logging
http.client._MAXHEADERS = 1000


cookies_file = "./cookies/" + os.getenv("COOKIES_FILE_NAME")



def parseCookieFile(cookiefile):
    """Parse a cookies.txt file and return a dictionary of key value pairs
    compatible with requests."""

    cookies = {}
    with open (cookiefile, 'r') as fp:
        for line in fp:
            if not re.match(r'^\#', line):
                lineFields = line.strip().split('\t')
                if len (lineFields) >= 6:
                    cookies[lineFields[5]] = lineFields[6]
			    
    return cookies



def run():
    cookies = parseCookieFile(cookies_file)
    # pprint.pprint(cookies)
    response = requests.get('https://maps.google.com', cookies=cookies)

    # Get the cookies from the response
    cookies = response.cookies
    logger.info('Cookies reloaded')