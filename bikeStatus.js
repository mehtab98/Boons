const express = require('express'); 
const haversine = require('haversine')
const app = express(); 

const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;



function Get(yourUrl){
	//create a http request 
    var Httpreq = new XMLHttpRequest(); // a new request

    //making a GET request to the url 
    Httpreq.open("GET",yourUrl,false);
    Httpreq.send(null);

    //return responseText in JSON format
    return Httpreq.responseText;          
}


function bikeGenerator(yourUrl){
	var json_obj = JSON.parse(Get(yourUrl));

	var bikes_json = json_obj.data.bikes

	var jsonData = {};

	for(i = 1; i <= bikeAmount; ++i){
		jsonData[i] = Object.assign(bikes_json[i])
	}

	return jsonData
}


app.get('/bikes/freebikes/:area/:totalAmount?',function(req,res){

	//lowercase the area paramater 
	area = req.params.area.toLowerCase()

	//choose the url link you would prefer 
	if(area == 'sf'){
		yourUrl = 'https://sf.jumpbikes.com/opendata/free_bike_status.json'
	}else if(area == 'dc'){
		yourUrl = 'https://dc.jumpbikes.com/opendata/free_bike_status.json'
	}else{
		res.send('The area paramater you gave us is currently not supported please try again.');
		return;
	}

	//assigns the paramater for bikeAmount if not given then assign to 10 
	if(!req.params.totalAmount){
		bikeAmount = 10
	}else{
		bikeAmount = parseInt(req.params.totalAmount)
	}

	
	//create a json object 
	var json_obj = JSON.parse(Get(yourUrl));

	//select all of the bike data 
	var bikes_json = json_obj.data.bikes

	//create a new jsonData object
	var jsonData = {last_updated: json_obj.last_updated, total_bikes: bikeAmount};

	//assign the amount of bikes necessary to a given object 
	for(i = 1; i <= bikeAmount; ++i){
		jsonData[i] = Object.assign(bikes_json[i])
	}
	
	res.json(jsonData)

	return 
  	
});


app.get('/bikes/freebikes/:lat/:long/:totalAmount?',function(req,res){

	//coordinates for both sf and dc 
	var sf_coord = { latitude: 37.7491384, longitude: -122.4540303}
	var dc_coord = {latitude:38.8950712,longitude: -77.0362758}



	if(!req.params.long || !req.params.lat){
		res.send('Sorry, you did not input the correct paramaters. Please, try again.');
		return
	}else{
		//assigns the longitude and latitude to variables 
		long = parseFloat(req.params.long)
		lat = parseFloat(req.params.lat)
	}

	//assigns the paramater for bikeAmount if not given then assign to 10 
	if(!req.params.totalAmount){
		bikeAmount = 10
	}else{
		bikeAmount = parseInt(req.params.totalAmount)
	}

	var param_coord = {latitude: lat, longitude: long} 

	//find the distance between sf/dc
	sf_distance = haversine(sf_coord,param_coord,{unit: 'mile'});
	dc_distance = haversine(dc_coord,param_coord,{unit: 'mile'}); 

	//assign a url if between the range otherwise print a error statement 
	if(sf_distance <= 100.0){
		yourUrl = 'https://sf.jumpbikes.com/opendata/free_bike_status.json'
	}else if(dc_distance <= 100.0){
		yourUrl = 'https://dc.jumpbikes.com/opendata/free_bike_status.json'
	}else{
		res.send('Sorry, your coordinates are out of range of service. Please, try closer coordinates.');
		return
	}
	
	//create a json object 
	var json_obj = JSON.parse(Get(yourUrl));

	//select all of the bike data 
	var bikes_json = json_obj.data.bikes

	//create a new jsonData object 
	var jsonData = {last_updated: json_obj.last_updated, total_bikes: bikeAmount};

	//assign json bike data according to bikeAmount
	for(i = 1; i <= bikeAmount; ++i){
		jsonData[i] = Object.assign(bikes_json[i])
	}

	//display jsonData 
	res.json(jsonData)

	return 


	});




const port = process.env.PORT || 3000; 

app.listen(port, () => console.log('Listening on port 3000...')); 
