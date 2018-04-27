#!/usr/bin/python
#
# Title: create_webpage_report.py
# Description: This script is used to create a
#              a webpage for weblogic validations
# Author: Insight Global
# Date: 04-11-2018
#
import os, sys, re
#DEBUG = True
DEBUG = False

def replace_all(text, dict):
    for i, j in dict.iteritems():
        text = text.replace(i, j)
    return text

def page_head ():

  print "<!DOCTYPE html>"
  print "<html>"
  print "<head>"
  print "<style>"
  print "table {"
  print "  font-family: Verdana, sans-serif;"
  print "  border-collapse: collapse;"
  print "  width: 100%;"
  print "}"
  print ""
  print "td, th {"
  print "  border: 1px solid #dddddd;"
  print "  text-align: left;"
  print "  padding: 8px;"
  print "}"
  print ""
  print "tr:nth-child(even) {"
  print "  background-color: #dddddd;"
  print "}"
  print "</style>"
  print "</head>"
  print "<body>"
  print ""
  print "<h1>Middleware Weblogic Patch Validations Report</h1>"
  print "<p><font size=\"3\" color=\"blue\">Key: nc = no change</font></p>"
  print ""
  print "<table>"

def page_tail ():

  print "</table>"
  print ""
  print "</body>"
  print "</html>"

def domain_row (domain):

  print " <tr>"
  print "  <th>Domain:</th>"
  print "  <th>" + domain + "</th>"
  print "  <th></th>"
  print "  <th></th>"
  print "  <th></th>"
  print "  <th></th>"
  print " </tr>"

def header_row () :

  print " <tr>"
  print "  <th>Hostname</th>"
  print "  <th>Common Patch Applied</th>"
  print "  <th>Patch Applied</th>"
  print "  <th>OPatch Version</th>"
  print "  <th>WebLogic Version</th>"
  print "  <th>Mount Point</th>"
  print " </tr>"

def data_row (*args):

  print " <tr>"

  for arg in args:
    for entry in arg:
      print "  <th>" + str(entry) + "</th>"

  print " </tr>"

def get_diff_lines (host,*args):

  found_it   = 0
  pre_count  = 0
  post_count = 0
  diff_array = []

  for diff in args:
    for line in diff:
      h = re.search("(^host:)", str(line))
      if h:
        m = re.search(host, str(line))
        if m:
          if not found_it:
            found_it += 1
        else:
          found_it = 0
        
      if found_it:
        m = re.search("(^<|^>)", str(line))
        if m:
          m = re.search("host:", str(line))
          if not m:
            m = re.search("(^<)", str(line))
            if m:
              pre_count += 1
            m = re.search("(^>)", str(line))
            if m:
              post_count += 1
            # search and replace <>
            rep = {"< ": "was: ", "> ": "now: "}
            line = replace_all(line,rep)
            line = line.rstrip() + "<br>"
            if DEBUG:
              print "line: " + line

            diff_array.append(line)

  #if pre_count == post_count:
  #  return diff_array
  #else:
  #  diff_array = []
  return diff_array

def get_host_list (*args):

  row = []
  host_list = []
 
  for diff in args:
    for line in diff:
      m = re.search("(^host)", str(line))
      if m:
        row = line.split(":")
        host_list.append(row[1].rstrip()) 

  host_list = sorted(set(host_list))
  return host_list
   
def read_diff_file (domain,diff):

  diff_array = []
  filename = domain + "_" + diff + ".diff.log"

    # try:

  if os.path.exists(filename):
    file = open(filename, 'r')
    try:
        lines = file.readlines()
        if lines:
          for line in lines:
            diff_array.append(line.rstrip())
    finally: 
      file.close()

  else:
    print ("Exception while reading diff file: %s" % filename)

  return diff_array

def get_domain_list ():

  name = []
  domains = []
  domain_and_diff = []
  file_list = []

  # list the log files in the diff directory
  try: 

    Cmd = "ls *pre_*.fnl.log |sort -u"
    p = os.popen(Cmd, "r")
    while True:
      line = p.readline()
      if not line: break
      m = re.search("(post)", str(line))
      if not m:
        file_list.append(line.rstrip())
	
    p.close()

  except:
    print ("Exception while reading diff directory.")

  # loop the files and split file name on underscore <domain>_<diff>.log
  # get a list of domains 
  for diff_file in file_list:

    try:

      name = diff_file.split('.')
      domain_and_diff = name[0].split('pre_')
      m = re.search("(pre)", domain_and_diff[0].rstrip())
      if not m:
        domains.append(domain_and_diff[0].rstrip())
      
    except:
      print ("Exception while parsing file name info.")

  domains = sorted(set(domains))

  return domains


if __name__ == "__main__":

  hosts     = []
  host_list = []

  compatchapplied = []
  patchapplied    = []
  opatchversion   = []
  weblogicversion = []
  mountpoint      = []

  domains = get_domain_list ()

  if not DEBUG:
    page_head()

  for domain in domains:

    if DEBUG:
      print "line: " + domain

    if not DEBUG:
      # print the domain row
      domain_row(domain)
      header_row()

    # read the diff file for this domain
    compatchapplied = read_diff_file(domain,'compatchapplied')
    patchapplied    = read_diff_file(domain,'patchapplied')
    opatchversion   = read_diff_file(domain,'opatchversion')
    weblogicversion = read_diff_file(domain,'weblogicversion')
    mountpoint      = read_diff_file(domain,'mountpoint')

    # get a list of hosts for this domain
    hosts = get_host_list (compatchapplied)
    host_list = sorted(set(hosts))

    # for each host in the domain assemble the diff line
    for host in host_list:
 
      if DEBUG:
        print "line: " + host

      strings   = []
      diff_line = []
      diff_line.append(host.rstrip())

      # common patch applied
      strings = get_diff_lines(host,compatchapplied)
      s = ""
      if strings:
        for string in strings:
          s += str(string)
      else:
        s = " nc"
      s = "<font size=\"1\" color=\"blue\">" + s.rstrip() + "</font>"
      diff_line.append(s)

      # patch applied
      strings = get_diff_lines(host,patchapplied)
      s = ""
      if strings:
        for string in strings:
          s += str(string)
      else:
        s = " nc"
      s = "<font size=\"1\" color=\"blue\">" + s.rstrip() + "</font>"
      diff_line.append(s)

      # opatch version
      strings = get_diff_lines(host,opatchversion)
      s = ""
      if strings:
        for string in strings:
          s += str(string)
      else:
        s = " nc"
      s = "<font size=\"1\" color=\"blue\">" + s.rstrip() + "</font>"
      diff_line.append(s)

      # weblogic version
      strings = get_diff_lines(host,weblogicversion)
      s = ""
      if strings:
        for string in strings:
          s += str(string)
      else:
        s = " nc"
      s = "<font size=\"1\" color=\"blue\">" + s.rstrip() + "</font>"
      diff_line.append(s)

      # mount point
      strings = get_diff_lines(host,mountpoint)
      s = ""
      if strings:
        for string in strings:
          s += str(string)
      else:
        s = " nc"
      s = "<font size=\"1\" color=\"blue\">" + s.rstrip() + "</font>"
      diff_line.append(s)
    
      if not DEBUG:
        data_row(diff_line)

  if not DEBUG:
    page_tail()

  exit
