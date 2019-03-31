from flask import Flask, request, jsonify, render_template

from sortedcontainers import SortedDict
import collections 
import urllib.request 
import math
import ssl 
import json 

#links of DATA we are attempting to GET 
dc_url = 'https://dc.jumpmobility.com/opendata'
sf_url = 'https://sf.jumpbikes.com/opendata'

# Create the application instance
app = Flask(__name__)

#following function is a math function that finds the distance between two coordinates 
#the value returned from the function is the distance in meters 
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters

    #take tuple coordinates and split them into 2 variables latitude and longitude 
    lat1,lon1 = coord1
    lat2,lon2 = coord2
    
    #haversine formula
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    
    a = float(math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2) 
    
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

#following two are routes that take longitude/latitude and bike count 
@app.route('/bikes/freebikes/<string:longitude>/<string:latitude>/<int:count>',methods=['GET'])
@app.route('/bikes/freebikes/<string:longitude>/<string:latitude>',methods=['GET'])



#following function takes coordinates to determine if coordinate falls in 100 mile range 
#if function falls in 100 mile range of either SF/DC coordinates it will parse bike data
#if count not given it will asume it to be 10 
def get_freebikes(longitude,latitude,count=10):

	#convert coordinates from string to float
	longitude = float(longitude)
	latitude = float(latitude)
	
	#move coordinates into a touple 
	rawcoord = (latitude,longitude)

	#list of coordinates for each city
	cities = {'SFO': (37.7491384,-122.4540303), 'DC': (38.8950712,-77.0362758) }
	checker = 0
	
	#bypass api certificate
	context = ssl._create_unverified_context()
	
	#applies distance formula on both city coordinates to see if fall under range
	for city, coord in cities.items():

		#converts distance from meters to miles
		distanceKM = float (haversine(coord,rawcoord)) / float(1000)
		distanceMiles = distanceKM * 0.621371

		if (distanceMiles <= 100.00): 
			if(city == "SFO"): 
				#GETS data 
				req = urllib.request.urlopen(sf_url + '/free_bike_status.json',context=context)
				checker = checker + 1 

			if(city == "DC"): 
				#GETS data 
				req = urllib.request.urlopen(dc_url + '/free_bike_status.json',context=context)
				checker = checker + 1 

	#if in either iteration no match found run into error 			
	if(checker == 0): 
		return("Error")	
	
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

