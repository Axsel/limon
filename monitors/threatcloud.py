import os
import websocket
import thread
import time
import json
import csv
import requests


logdir = monconf["logdir"]
country_iso = monconf["country_iso"]
log_suffix = "_threatcloud.log"
log_fields = ["monsource", 
	"timestamp", 
	"sourcecountry", 
	"sourcestate", 
	"sourcecity", 
	"destinationcountry", 
	"destinationstate", 
	"destinationcity", 
	"attackname", 
	"type",
	"sourcelongitude",
	"sourcelatitude",
	"destinationlongitude",
	"destinationlatitude"]

# create csv headers - mandatory
def create_csv(path):
	with open(path, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(log_fields)

def on_error(ws, error):
	print "[!] WS error"
	print(error)

def on_close(ws):
	print("[!] WS closed")

def on_message(ws, message):
	try:
		if (message[3] == '|'):
			obj = json.loads(message[4:])
			if (obj["sourcecountry"] == country_iso or obj["destinationcountry"] == country_iso):
				print obj

				now = datetime.datetime.now()
				logpth = logdir + now.strftime("%Y_%m_%d") + log_suffix
				if (not os.path.exists(logpth)):
					create_csv(logpth)
					
				with open(logpth, 'ab') as f:
					writer = csv.writer(f)
					writer.writerow(["tc",
						now.strftime("%Y-%m-%d %H:%M:%S"), 
						obj[log_fields[2]], 
						obj[log_fields[3]], 
						obj[log_fields[4]].encode("utf-8"), 
						obj[log_fields[5]], 
						obj[log_fields[6]],
						obj[log_fields[7]].encode("utf-8"), 
						obj[log_fields[8]],
						obj[log_fields[9]],
						obj[log_fields[10]],
						obj[log_fields[11]],
						obj[log_fields[12]],
						obj[log_fields[13]]])
	except:
		print "[!] Message Unhandled"
		print message
		return

def on_open(ws):
	return

def main():
	#websocket.enableTrace(True)
	while True:		
		ws = websocket.WebSocketApp("wss://threatmap.checkpoint.com/ThreatPortal/websocket?X-Atmosphere-tracking-id=0&X-Atmosphere-Framework=2.3.5-javascript&X-Atmosphere-Transport=websocket&X-Atmosphere-TrackMessageSize=true&Content-Type=application/json&X-atmo-protocol=true",
			on_message = on_message,
			on_error = on_error,
			on_close = on_close
			)

		ws.on_open = on_open
		ws.run_forever()
		time.sleep(5)

if __name__ == "__main__":
	main()