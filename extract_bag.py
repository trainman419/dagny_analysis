#!/usr/bin/env python

import sys
import yaml
import rosbag

def build_fieldlist(fields, prefix=""):
  res = []
  if type(fields) == dict:
    for f in fields:
      res += build_fieldlist(fields[f], prefix + f + ".")
  elif type(fields) == list:
    for f in fields:
      res.append(prefix + f)
  else:
      res.append(prefix + fields)
  return res
    
def extract_fields(msg, fields):
  res = []
  if type(fields) == dict:
    for f in fields:
      res += extract_fields(getattr(msg, f), fields[f])
  elif type(fields) == list:
    for f in fields:
      res.append(str(getattr(msg, f)))
  else:
      res.append(str(getattr(msg, fields)))
  return res


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Usage: extract_bag.py <settings.yaml> <bag>"
    sys.exit(1)

  bag = rosbag.Bag(sys.argv[2])

  settings = yaml.load(open(sys.argv[1]))

  topics = settings['topics']

  files = {}

  for topic in topics:
    topic_file = "%s.csv"%(topic)
    topic_file = topic_file.replace('/','_')
    files[topic] = open(topic_file, "w")
    fields = ["time"]
    fields += build_fieldlist(topics[topic])
    s = ",".join(fields)
    files[topic].write(s + "\n")

  for topic,msg,t in bag.read_messages():
    if topic[0] == '/':
      topic = topic[1:]
    if topic in files:
      stamp = t.to_sec()
      if hasattr(msg, 'header'):
        stamp = msg.header.stamp.to_sec()
        if stamp == 0:
          stamp = t.to_sec()
      fields = [ str(stamp) ]
      fields += extract_fields(msg, topics[topic])
      s = ",".join(fields)
      files[topic].write(s + "\n")
#      print stamp
#      fields = dir(msg)
#      print fields
#      print "[%s] %s: "%(stamp, topic_file)

  bag.close()

  for f in files:
    files[f].close()
