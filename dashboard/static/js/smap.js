
//initialize map 
var mymap = L.map('mapid', {scrollWheelZoom:true}).setView([45.517562, -122.625613], 12);


    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(mymap);

var myStyle = {
"color": "#ff7800",
"weight": 5,
"opacity": 0.65
};


url = "https://hifld-dhs-gii.opendata.arcgis.com/datasets/85d3d0fc64924edbbd7c62e319d8a791_0.geojson"


function addDataToMap(data, mymap) {
    var dataLayer = L.geoJson(data, {
    onEachFeature: function(feature, layer) {
        var popupText = "Name: " + feature.properties.NAME
                + "<br>City: " + feature.properties.CITY
                + "<br>State: " + feature.properties.STATE
                + "<br>Capacity: " + feature.properties.CAPACITY
                + "<br>Year: " + feature.properties.YEAR;
            layer.bindPopup(popupText); }
    
    
    });
    dataLayer.addTo(mymap);
}

$.getJSON(url, function(data) { 
addDataToMap(data, mymap); 
});

var popup = L.popup();

function onMapClick(e) {
    popup
        .setLatLng(e.latlng)
        .setContent("You clicked the map at " + e.latlng.toString())
        .openOn(mymap);
}

mymap.on('click', onMapClick);

    // Create the layercontrol and add it to the map
var controlLayers = L.control.layers().addTo(mymap);

function getJson(jsonname) {

    var pathjson = "../../static/geojson/"

    // Loading a GeoJSON file (using jQuery's $.getJSON)    
    $.getJSON(pathjson + jsonname, function (data) {

    // Use the data to create a GeoJSON layer and add it to the map
    var geoLayer = L.geoJson(data).addTo(mymap);

    // Add the geojson layer to the layercontrol
    controlLayers.addOverlay(geoLayer, jsonname.slice(0,-9));

    });
}

getJson("4_0_routes.geojson");

for (var i=0; i<rtejsonlist.length; i++) {
    console.log("rtejsonlist: " +rtejsonlist[i])
    getJson(rtejsonlist[i]);
}
