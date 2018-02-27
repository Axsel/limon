import os
import websocket
import thread
import time
import datetime
import json
import csv
import threading
import requests


logdir = monconf["logdir"]
country_iso = monconf["country_iso"]
log_suffix = "_fortiguard.log"
log_fields = ["monsource", "timestamp", "src_country", "src_lng", "src_lat", "dst_country", "dst_lng", "dst_lat", "type", "severity"]


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
		if (message[0:3] == "[2,"):
			ws.send('[32,1418265569757468,{},"ips"]')
			return
			
		index = message.find('[{', 0)
		if (index > 1):
			data = message[index+1:len(message)-2]
			obj = json.loads(data)
			if (obj["src"]["countrycode"] == country_iso or obj["dst"]["countrycode"] == country_iso):
				#print obj
				now = datetime.datetime.now()
				logpth = logdir + now.strftime("%Y_%m_%d") + log_suffix
				if (not os.path.exists(logpth)):
					create_csv(logpth)

				with open(logpth, 'ab') as f:
					writer = csv.writer(f)
					writer.writerow(["fg",
						now.strftime("%Y-%m-%d %H:%M:%S"), 
						obj["src"]["countrycode"], 
						obj["src"]["longitude"], 
						obj["src"]["latitude"], 
						obj["dst"]["countrycode"], 
						obj["dst"]["longitude"], 
						obj["dst"]["latitude"],  
						obj[log_fields[8]],
						obj[log_fields[9]]])
		return
	except:
		print "[!] Message Unhandled"
		print message
		return

	

def on_open(ws):
	print "sending.."
	ws.send('[1,"threatmap",{"roles":{"caller":{"features":{"caller_identification":true,"progressive_call_results":true}},"callee":{"features":{"caller_identification":true,"pattern_based_registration":true,"shared_registration":true,"progressive_call_results":true,"registration_revocation":true}},"publisher":{"features":{"publisher_identification":true,"subscriber_blackwhite_listing":true,"publisher_exclusion":true}},"subscriber":{"features":{"publisher_identification":true,"pattern_based_subscription":true,"subscription_revocation":true}}}}]')

def main():
	while True:	
		print "[+] Initializing websocket.."		
		#websocket.enableTrace(True)
		custom_protocol = "wamp.2.json"
		protocol_str = "Sec-WebSocket-Protocol: " + custom_protocol
		ws = websocket.WebSocketApp("wss://threatmap.fortiguard.com/ws",
			on_message = on_message,
			on_error = on_error,
			on_close = on_close,
			header = [protocol_str])
		ws.on_open = on_open
		ws.run_forever()
		time.sleep(2)
		
if __name__ == "__main__":
	main()
