#!/usr/bin/python
#
# Title: diff_weblogic_logs.py
# Description: This script is used to get the difference
#              between pre and post patching log files.
# Author: Insight Global
# Date: 04-15-2018
#
#DEBUG = True
import os, sys, re
DEBUG = False

def get_diff_lines (host,*args):

  found_it = 0
  diff_array = []

  for diff in args:
    for line in diff:
      m = re.search(host, str(line))
      if m:
        found_it += 1
      if found_it:
        m = re.search("host:", str(line))
        if not m:
          line = line.rstrip()
          diff_array.append(line)

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
   
def read_pre_tmp_log (domain,diff):

  diff_array = []
  filename = domain + "pre_" + diff + ".fnl.log"

  if os.path.exists(filename):
    file = open(filename, 'r')
    try:
        pre_lines_seen = set()
        lines = file.readlines()
        if lines:
          for line in lines:
            m = re.search("(^host:)", str(line))
            if m:
              host = line
            
            m = re.search("(^Patch)", str(line))
            if m:
              p = line.split(":")
              new_line = host + p[0].rstrip()
              # print "p_zero: " + new_line
              if new_line not in pre_lines_seen:
                diff_array.append(line.rstrip())
                # print "p_add1: " + new_line
                pre_lines_seen.add(new_line)
            else:
              new_line = host + line.rstrip()
              if new_line not in pre_lines_seen:
                diff_array.append(line.rstrip())
                pre_lines_seen.add(new_line)

    finally: 
      file.close()

  #for diff in diff_array:
  #  print "pre_diff: " + diff

  return diff_array

def read_post_tmp_log (domain,diff):

  diff_array = []
  filename = domain + "post_" + diff + ".fnl.log"

  if os.path.exists(filename):
    file = open(filename, 'r')
    try:
        post_lines_seen = set()
        lines = file.readlines()
        if lines:
          for line in lines:
            m = re.search("(^host:)", str(line))
            if m:
              host = line
            
            m = re.search("(^Patch)", str(line))
            if m:
              p = line.split(":")
              new_line = host + p[0].rstrip()
              # print "p_zero: " + new_line
              if new_line not in post_lines_seen:
                diff_array.append(line.rstrip())
                # print "p_add1: " + new_line
                post_lines_seen.add(new_line)
            else:
              new_line = host + line.rstrip()
              if new_line not in post_lines_seen:
                diff_array.append(line.rstrip())
                post_lines_seen.add(new_line)

    finally: 
      file.close()

  #for diff in diff_array:
  #  print "post_diff: " + diff

  return diff_array

def get_domain_list ():

  name = []
  domains = []
  domain_and_diff = []
  file_list = []

  # list the temp log files in the diff directory
  try: 

    Cmd = "ls *pre_*.fnl.log |sort -u"
    p = os.popen(Cmd, "r")
    while True:
      line = p.readline()
      if not line: break
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

def diff_pre_and_post (host,pre,post):

  diff  = []
  match = 0
  found_pre  = 0
  found_post = 0

  if DEBUG:
    print "host: " + host

  for pre_row in pre:
    m = re.search("(^host:)", str(pre_row))
    if m:
      m = re.search(host, str(pre_row))
      if m:
        found_pre = 1
      else:
        found_pre = 0
    if found_pre:
      match = 0
      for post_row in post:
        m = re.search("(^host:)", str(post_row))
        if m:
          m = re.search(host, str(post_row))
          if m:
            found_post = 1
          else:
            found_post = 0
        if found_post:
          # This is kinda a work around for
          # the common patch applied string
          #
          m = re.search("(^Patch)", str(post_row))
          if m:
            p = post_row.split(":")
            if DEBUG:
              print "pst +++++++ " + str(post_row)
              print "pre ======= " + str(pre_row)
            m = re.search(p[0].rstrip(), str(pre_row))
            if m:
              if DEBUG:
                print "dededa we have a match!"
                diff.append("* " + pre_row)
              match = 1
              break
          #
          # end work around    
          else:
            if pre_row.rstrip() == post_row.rstrip():
              if DEBUG:
                diff.append("* " + pre_row)
              match = 1
              break
 
      if match == 0:
        # Lets not append if host is in the row
        m = re.search("(host:)", str(pre_row))
        if not m:
          diff.append("< " + pre_row)
          if DEBUG:
            print "< " + pre_row

  found_pre  = 0
  found_post = 0

  for post_row in post:
    m = re.search("(^host:)", str(post_row))
    if m:
      m = re.search(host, str(post_row))
      if m:
        found_post = 1
      else:
        found_post = 0
    if found_post:
      match = 0
      for pre_row in pre:
        m = re.search("(^host:)", str(pre_row))
        if m:
          m = re.search(host, str(pre_row))
          if m:
            found_pre = 1
          else:
            found_pre = 0
        if found_pre:
          # This is kinda a work around for the
          # common patch applied string
          #
          m = re.search("(^Patch)", str(pre_row))
          if m:
            p = pre_row.split(":")
            if DEBUG:
              print "pre +++++++ " + str(pre_row)
              print "pst ======= " + str(post_row)
            m = re.search(p[0].rstrip(), str(post_row))
            if m:
              if DEBUG:
                print "dededa we have a match!"
                diff.append("* " + post_row)
              match = 1
              break
          #
          # end work around    
          else:
            if post_row.rstrip() == pre_row.rstrip():
              if DEBUG:
                diff.append("* " + post_row)
              match = 1
              break
 
      if match == 0:
        # Lets not append if host is in the row
        m = re.search("(host:)", str(pre_row))
        if not m:
          diff.append("> " + post_row)
          if DEBUG:
            print "> " + post_row

  return diff


if __name__ == "__main__":

  hosts     = []
  host_list = []

  pre_compatchapplied = []
  pre_patchapplied    = []
  pre_opatchversion   = []
  pre_weblogicversion = []
  pre_mountpoint      = []

  post_compatchapplied = []
  post_patchapplied    = []
  post_opatchversion   = []
  post_weblogicversion = []
  post_mountpoint      = []

  domains = get_domain_list ()

  for domain in domains:
    if DEBUG:
      print "--- " + domain + " ---"

    # read the pre patch log for this domain and store in a list
    pre_compatchapplied = read_pre_tmp_log(domain,'compatchapplied')
    pre_patchapplied    = read_pre_tmp_log(domain,'patchapplied')
    pre_opatchversion   = read_pre_tmp_log(domain,'opatchversion')
    pre_weblogicversion = read_pre_tmp_log(domain,'weblogicversion')
    pre_mountpoint      = read_pre_tmp_log(domain,'mountpoint')

    # read the post patch log for this domain and store in a list
    post_compatchapplied = read_post_tmp_log(domain,'compatchapplied')
    post_patchapplied    = read_post_tmp_log(domain,'patchapplied')
    post_opatchversion   = read_post_tmp_log(domain,'opatchversion')
    post_weblogicversion = read_post_tmp_log(domain,'weblogicversion')
    post_mountpoint      = read_post_tmp_log(domain,'mountpoint')

    # create diff files for compatchapplied
    #
    file = domain + "_compatchapplied.diff.log"
    f = open(file,"w")
    hosts = get_host_list (pre_compatchapplied)
    hosts = sorted(set(hosts))
    for host in hosts:
      line = "host:" + host
      print >>f,str(line)
      diff = diff_pre_and_post (host, \
             pre_compatchapplied, post_compatchapplied)
      if len(diff) > 0:
        for line in diff:
          print >>f,str(line)

    f.close()

    # create diff files for patchapplied
    #
    file = domain + "_patchapplied.diff.log"
    f = open(file,"w")
    hosts = get_host_list (pre_patchapplied)
    hosts = sorted(set(hosts))
    for host in hosts:
      line = "host:" + host
      print >>f,str(line)
      diff = diff_pre_and_post (host, \
             pre_patchapplied, post_patchapplied)
      if len(diff) > 0:
        for line in diff:
          print >>f,str(line)

    f.close()

    # create diff files for opatchversion
    #
    file = domain + "_opatchversion.diff.log"
    f = open(file,"w")
    hosts = get_host_list (pre_opatchversion)
    hosts = sorted(set(hosts))
    for host in hosts:
      line = "host:" + host
      print >>f,str(line)
      diff = diff_pre_and_post (host, \
             pre_opatchversion, post_opatchversion)
      if len(diff) > 0:
        for line in diff:
          print >>f,str(line)

    f.close()

    # create diff files for weblogicversion
    #
    file = domain + "_weblogicversion.diff.log"
    f = open(file,"w")
    hosts = get_host_list (pre_weblogicversion)
    hosts = sorted(set(hosts))
    for host in hosts:
      line = "host:" + host
      print >>f,str(line)
      diff = diff_pre_and_post (host, \
             pre_weblogicversion, post_weblogicversion)
      if len(diff) > 0:
        for line in diff:
          print >>f,str(line)

    f.close()

    # create diff files for mountpoint
    #
    file = domain + "_mountpoint.diff.log"
    f = open(file,"w")
    hosts = get_host_list (pre_mountpoint)
    hosts = sorted(set(hosts))
    for host in hosts:
      line = "host:" + host
      print >>f,str(line)
      diff = diff_pre_and_post (host, \
             pre_mountpoint, post_mountpoint)
      if len(diff) > 0:
        for line in diff:
          print >>f,str(line)

    f.close()

  exit
