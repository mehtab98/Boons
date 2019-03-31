from flask import Flask, request, jsonify, render_template
from sortedcontainers import SortedDict
import collections 
import urllib.request 
import ssl 
import json 

#links of data we are attempting to GET 
dc_url = 'https://dc.jumpmobility.com/opendata'
sf_url = 'https://sf.jumpbikes.com/opendata'

# Create the application instance
app = Flask(__name__)


#following two are routes take area and count
@app.route('/bikes/freebikes/<string:area>/<int:count>',methods=['GET'])
@app.route('/bikes/freebikes/<string:area>/',methods=['GET'])



#following function takes paramter of SF/DC area and will GET bike data for given count parameter
#if count not given it will asume it to be 10 
def get_freebikes(area,count=10):
	
	#make input of area lowercase 
	area = area.lower()

	#bypass api certificate
	context = ssl._create_unverified_context()
		
	if(area == 'sf'):
		#GETS data 
		req = urllib.request.urlopen(sf_url + '/free_bike_status.json',context=context)
	elif(area == 'dc'):
		#GETS data  
		req = urllib.request.urlopen(dc_url + '/free_bike_status.json',context=context)
	else: 
		return "error"

	#loads data as a json format 
	html = req.read()
	data_json = json.loads(html)
	
	increment = 1
	context = {}
	context1 = {}

	#parse JSON and store information in a dictonary 
	for bike in data_json["data"]["bikes"]: 
		if increment > (count): 
				break 
		else:
			bike = {
					'Vehicle': bike["jump_vehicle_type"],
					'Bikeid' : bike["bike_id"],
					'name': bike["name"],
					'longitude':bike["lon"],
					'latitude':bike["lat"],
					'reservations':bike["is_reserved"],
					'is_disabled':bike["is_disabled"],
					'battery': bike["jump_ebike_battery_level"]
				}
			bikeVal = increment
			
			increment = increment + 1
			context[bikeVal] = bike
			
	#include a 'data' key in dictonary
	context1.update({'data': context})
	
	#sort and POST data 
	return jsonify(SortedDict(context1))
 
# If we're running in stand alone mode, run the application
if __name__ == "__main__":
	app.run(debug = True)

