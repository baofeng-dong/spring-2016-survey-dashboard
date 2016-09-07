
//initialize map 
var mymap = L.map('mapid', {scrollWheelZoom:true}).setView([45.48661, -122.65343], 11);


    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoidG11c2VyMTk3IiwiYSI6ImNpc254cHk1YTA1dngydm14bjkyamQ1NmsifQ.8ya7T1hHXtVmYOwMrVIuFw', {
    attribution: '<a href="https://www.mapbox.com/about/maps/" target="_blank">&copy; Mapbox &copy; OpenStreetMap</a>',
    id: 'mapbox.light',
    maxZoom: 18,
    minZoom: 11
    }).addTo(mymap);


url = "https://hifld-dhs-gii.opendata.arcgis.com/datasets/85d3d0fc64924edbbd7c62e319d8a791_0.geojson"

function onEachFeature(feature, layer) {
    var popupContent = "<b>Route:</b> " + feature.properties.rte + '-' + feature.properties.rte_desc + '<br />'
                        + "<b>Direction:</b> " + feature.properties.dir_desc;

    layer.bindPopup(popupContent);
}

/*function addDataToMap(data, mymap) {
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
});*/

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
        var geoLayer = L.geoJson(data, {
                style: function (feature) {
                    return {
                        color: getColor(feature.properties.type),
                        weight: 3
                        };
                },
                
                onEachFeature: onEachFeature,

        }).addTo(mymap);

    // Add the geojson layer to the layercontrol
    controlLayers.addOverlay(geoLayer, jsonname.slice(0,-9));
    });
}

function getColor(rtetype) {
    return rtetype == "BUS" ? '#1c4ca5' :
           rtetype == "MAX" ? '#d1441e' :
           rtetype == "CR"  ? '#d95f0e' :
                              '#FFEDA0';
}

function style(feature) {
    return {
        color: getColor(feature.properties.type),
        weight: 1.5
    };

}

//getJson("4_0_routes.geojson");

for (var i=0; i<rtejsonlist.length; i++) {
    console.log("rtejsonlist: " +rtejsonlist[i])
    getJson(rtejsonlist[i]);
}

