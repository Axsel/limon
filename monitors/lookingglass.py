import os
import websocket
import time
import json
import csv
import requests
import datetime
import thread
import threading


logdir = monconf["logdir"]
country_iso = monconf["country_iso"]
log_suffix = "_lookingglass.log"
log_fields = ["monsource", "timestamp", "countrycode", "city", "lng", "lat", "botnet", "variant", "organization", "asn"]


# create csv headers - mandatory
def create_csv(path):
	with open(path, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(log_fields)

def get_auth_token():
	r = requests.get('https://map.lookingglasscyber.com/socket.io/?EIO=3&transport=polling&t=' + str(int(time.time())) + '-0')
	print r.text
	if (r.status_code == 200):
		index = r.text.find('{"sid', 0)
		if (index > 1):
			return json.loads(r.text[index:])["sid"]
	return ""
	
def on_error(ws, error):
	print "[!] WS error"
	print(error)

def on_close(ws):
	print("[!] WS closed")

def on_message(ws, message):
	try:
		if (message == "3probe"):
			ws.send("5")
		elif (message[0:2] == "42"):
			obj = json.loads(message[2:])
			if "botnet" in obj:
				obj = json.loads(obj[1])
				if (obj["countrycode"] != country_iso):
					return

				now = datetime.datetime.now()
				logpth = logdir + now.strftime("%Y_%m_%d") + log_suffix
				if (not os.path.exists(logpth)):
					create_csv(logpth)
					
				with open(logpth, 'ab') as f:
					writer = csv.writer(f)
					writer.writerow(["lg",
						now.strftime("%Y-%m-%d %H:%M:%S"), 
						obj[log_fields[2]], 
						obj[log_fields[3]].encode("utf-8"), 
						obj["location"]["geo"]["longitude"],
						obj["location"]["geo"]["latitude"],
						obj[log_fields[6]], 
						obj[log_fields[7]],
						obj[log_fields[8]].encode("utf-8"), 
						obj[log_fields[9]].encode("utf-8")])
						
		return

	except:
		print "[!] Message Unhandled"
		print message
		return
		
def on_open(ws):
	ws.send('2probe')

def main():	
	#websocket.enableTrace(True)
	while True:
		try:
			print "[+] Getting auth token.."
			token = get_auth_token()
			print "[+] Token: " + token
			#r = requests.get('https://map.lookingglasscyber.com/socket.io/?EIO=3&transport=polling&t=' + str(int(time.time())) + '-1' + "&sid=" + token)
			print "[+] Initializing websocket.."		
			ws = websocket.WebSocketApp("wss://map.lookingglasscyber.com/socket.io/?EIO=3&transport=websocket&sid=" + token,
				on_message = on_message,
				on_error = on_error,
				on_close = on_close)
			ws.on_open = on_open
			wst = threading.Thread(target=ws.run_forever)
			wst.daemon = True
			wst.start()

			time.sleep(5)
			
			while ws.sock.connected:
				ws.send("2")
				time.sleep(30)
		except:
			time.sleep(2)

		time.sleep(2)

if __name__ == "__main__":
	main()
