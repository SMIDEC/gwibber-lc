#!/usr/bin/env python

import urllib, pycurl, json, StringIO
import traceback
from util import log
from util import exceptions
from util.const import proxy_factory

class CurlDownloader:
  def __init__(self, url, params=None, post=False, username=None, password=None, header=None, body=None):
    self.curl = pycurl.Curl()

    if header:
      self.curl.setopt(pycurl.HTTPHEADER, header)

    if body:
      self.curl.setopt(pycurl.POST, 1)
      self.curl.setopt(pycurl.POSTFIELDS, body)
  
    if params:
      if post:
        self.curl.setopt(pycurl.HTTPPOST, [(x, str(y)) for x,y in params.items()])
      else:
        url = "?".join((url, urllib.urlencode(params)))
    
    self.curl.setopt(pycurl.URL, str(url))
    #log.logger.debug("URL: %s", str(url))
    
    if username and password:
      self.curl.setopt(pycurl.USERPWD, "%s:%s" % (str(username), str(password)))

    self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
    self.curl.setopt(pycurl.MAXREDIRS, 5)
    self.curl.setopt(pycurl.TIMEOUT, 150)
    self.curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0)

    self.content = StringIO.StringIO()
    self.curl.setopt(pycurl.WRITEFUNCTION, self.content.write)
    
    if proxy_factory:
      log.logger.debug("libproxy: getting proxies")
      proxylist = proxy_factory.getProxies(str(url))

      if proxylist:
        proxy = proxylist[0]
        if (proxy.find("@") != -1):
            self.curl.setopt(pycurl.PROXYAUTH, ["CURLAUTH_ANY"])
        if (proxy.find("direct://") != 0):
            log.logger.debug("using proxy %s", proxy)
            self.curl.setopt(pycurl.PROXY, proxy)

    try:
      self.curl.perform()
    except:
      traceback.print_exc()
      log.logger.error("Failed to communicate with %s", str(url))
  
  def get_json(self):
    try:
      return json.loads(self.get_string())
    except ValueError as e:
      log.logger.error("Failed to parse the response, error was: %s", str(e))
      return str(e)

  def get_string(self):
    return self.content.getvalue()

Download = CurlDownloader


