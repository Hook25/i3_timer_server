from enum import Enum
from flask import Flask, request, abort
from threading import Lock
from copy import deepcopy
from datetime import datetime, timedelta
from multiprocessing import Process, Event
from os import system
import hashlib

import json

api = Flask(__name__)

started_timers = {}
started_timers_lock = Lock()

KEY_LEN = 5 #prob of collision is 1/KEY_LEN due to hash uniformity

config = None #gets set by load_config

def get_timers(request):
  """
  Cleans up the list and encodes it into json
  """
  time_now = datetime.now().strftime("%m/%d/%Y%H:%M:%S")
  started_timers_lock.acquire()
  to_remove = [k for (k, ts) in started_timers.items() if not ts.process.is_alive()]
  for tr in to_remove:
    del started_timers[tr]
  to_send = { 
    i : {
      "id" : v.get_id(),
      "start_time" : v.start_time,
      "time_now" : time_now,
      "end_time" : v.end_time,
      "message" : v.message 
    } for (i, v) in started_timers.items()
  }
  started_timers_lock.release()
  return json.dumps(to_send) 

def post_timers(request):
  """
  Tries to create a timer with the given spec starting now
  """
  err = False
  to_ins = request.json
  ts = TimerSpec(to_ins["seconds"], to_ins["message"], config.command)
  ts_id = ts.get_id()
  started_timers_lock.acquire()
  if ts_id not in started_timers:
    started_timers[ts_id] = ts
  else:
    err = True
  started_timers_lock.release()
  ts.start_spec()
  if err:
    abort(404)
  return "200"

def del_timers(request):
  err = False
  key = request.json["id"]
  started_timers_lock.acquire()
  try:
    started_timers[key].process.kill()
    del started_timers[key]
  except KeyError:
    err = True
  started_timers_lock.release()
  if err:
    abort(404)
  return "200"

@api.route('/timers', methods=['GET', 'POST', 'DELETE'])
def timers():
  if request.method == 'GET':
    return get_timers(request)
  elif request.method == 'POST':
    return post_timers(request)
  elif request.method == 'DELETE':
    return del_timers(request)

class TimerSpec:
  def __init__(self, seconds, msg, cmd):
    self.message = msg
    self.cmd = cmd
    now = datetime.now()
    self.start_time = now.strftime("%m/%d/%Y%H:%M:%S")
    self.end_time = (now + timedelta(seconds=float(seconds))).strftime(
      "%m/%d/%Y%H:%M:%S"
    )
    self.time_span = seconds
  def get_id(self):
    m = hashlib.sha256()
    m.update("{}{}{}".format(self.message, self.start_time, self.time_span).encode())
    return m.hexdigest()[:KEY_LEN]
  def _runner(self, t, msg, cmd):
    from shlex import quote
    e = Event()
    e.wait(t)
    system(cmd.format(quote(msg)))
  def start_spec(self):
    p = Process(
      target = self._runner, args=(float(self.time_span), self.message, self.cmd)
    )
    p.start()
    self.process = p
    self.pid = p.pid

def load_config():
  global config
  import argparse
  parser = argparse.ArgumentParser(description="Queries the remote timer server")
  parser.add_argument('-ip', default="127.0.0.1", help="IP of the remote server")
  parser.add_argument('-port', default=7853, help="Port of the remote server")
  parser.add_argument(
    '-command', default='zenity --info --title="ExpiredTimer" --text="{}"',
    help="Command to run on timer expired"
  )
  config = parser.parse_args()
  return {"port" : int(config.port), "ip" : config.ip}

def start_server(config):
  api.run(host = config["ip"], port = config["port"], threaded = True)

def main():
  config = load_config()
  start_server(config)

if __name__ == "__main__":
  main()
