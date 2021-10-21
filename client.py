#!/usr/bin/env python

import requests
import argparse
import json
from datetime import datetime

def poss_act(x):
  assert x in ["show_brief", "show_detail", "post_new", "delete"]
  return x

def load_config():
  parser = argparse.ArgumentParser(description="Queries the remote timer server")
  parser.add_argument('-ip', default="127.0.0.1", help="IP of the remote server")
  parser.add_argument('-port', default=7853, help="Port of the remote server")
  parser.add_argument('-action', default='show_brief', type=poss_act, 
    help="Possible actions out of post_new, delete, show_brief, show_detail"
  ) 
  parser.add_argument('additional', metavar='id or spec', nargs="*", 
    help="Either id when action delete or time (s or m:s or h:m:s or d:h:m:s) when action post_new"
  )
  return parser.parse_args()

def update_active(conf):
  req = requests.get("http://{}:{}/timers".format(conf.ip, conf.port))
  return req.json()

def _delete_timer(conf, i):
  h = {"Content-Type" : "application/json"}
  req = requests.delete(
    "http://{}:{}/timers".format(conf.ip, conf.port),
    data = json.dumps({"id" : i}),
    headers=h
  )
  return req.status_code

def delete_timer(conf):
   res = [_delete_timer(conf, i) for i in conf.additional]
   if all(x == 200 for x in res):
     print("Success")
   else:
     print("Failed to delete:", ", ".join(i for (i, r) in zip(conf.additional, res) if res != 200)) 

def to_t(s):
  s = list(reversed(s.split(":")))
  mult = [1, 60, 60**2, 60**2*24]
  t = zip(mult[:len(s)], (float(k) for k in s))
  time_s = sum(a*b for (a,b) in t)
  return time_s

def _create_timer(conf, t):
  h = {"Content-Type" : "application/json"}
  req = requests.post(
    "http://{}:{}/timers".format(conf.ip, conf.port),
    headers = h,
    data = json.dumps({"seconds" : t, "message" : conf.additional[-1]})
  )
  if req.status_code == 200:
    print("Success")
  else:
    print("Failed with code: %s" % req.status_code)

def create_timer(conf):
  if len(conf.additional) != 2:
    print("Provide 2 additional arguments: time message")
  else:
    _create_timer(conf, to_t(conf.additional[0]))

def get_time_diff(a, b):
  a = datetime.strptime(a, "%m/%d/%Y%H:%M:%S")
  b = datetime.strptime(b, "%m/%d/%Y%H:%M:%S")
  return (b - a)

def pretty_print_short(req):
  to_print = [
    "[{}]".format(get_time_diff(v['time_now'], v['end_time'])) for v in req.values()
  ]
  if to_print:
    print("".join(to_print))
  else:
    print("[No Timer]")

def pretty_print_long(req):
  to_print = [
    "[{}] ({} -> {}) [{}]".format(
      v['id'], 
      v['start_time'],
      v['end_time'],
      get_time_diff(v['time_now'], v['end_time'])
    ) for v in req.values()
  ]
  print("\n".join(to_print))

def main():
  conf = load_config()
  if conf.action == 'show_brief':
    active = update_active(conf)
    pretty_print_short(active)
  elif conf.action == 'show_detail':
    active = update_active(conf)
    pretty_print_long(active)
  elif conf.action == 'delete':
    delete_timer(conf)
  elif conf.action == 'post_new':
    create_timer(conf)

if __name__ == "__main__":
  main()
