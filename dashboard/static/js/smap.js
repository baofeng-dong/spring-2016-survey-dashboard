
//initialize map 
var mymap = L.map('mapid', {scrollWheelZoom:true}).setView([45.517562, -122.625613], 12);


    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoidG11c2VyMTk3IiwiYSI6ImNpc254cHk1YTA1dngydm14bjkyamQ1NmsifQ.8ya7T1hHXtVmYOwMrVIuFw', {
    attribution: '<a href="https://www.mapbox.com/about/maps/" target="_blank">&copy; Mapbox &copy; OpenStreetMap</a>'
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
var controlLayers = L.control.layers().addTo(mymap, true);

function getJson(jsonname) {

    var pathjson = base + 'static/geojson/'

    // Loading a GeoJSON file (using jQuery's $.getJSON)    
    $.getJSON(pathjson + jsonname, function (data) {

    // Use the data to create a GeoJSON layer and add it to the map
    var geoLayer = L.geoJson(data).addTo(mymap);

    // Add the geojson layer to the layercontrol
    controlLayers.addOverlay(geoLayer, jsonname.slice(0,-9));

    });
}

//getJson("4_0_routes.geojson");

for (var i=0; i<rtejsonlist.length; i++) {
    console.log("rtejsonlist: " +rtejsonlist[i])
    getJson(rtejsonlist[i]);
}
