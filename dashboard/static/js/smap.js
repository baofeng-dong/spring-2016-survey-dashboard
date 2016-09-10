
//initialize map 
var mymap = null; 
var controlLayers = null;
var rtegeoJson = {};
var sel_view = null;
var hasLegend = false;

$(document).ready(function() {
    mymap = L.map('mapid', {scrollWheelZoom:true}).setView([45.48661, -122.65343], 11);
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoidG11c2VyMTk3IiwiYSI6ImNpc254cHk1YTA1dngydm14bjkyamQ1NmsifQ.8ya7T1hHXtVmYOwMrVIuFw', {
    attribution: '<a href="https://www.mapbox.com/about/maps/" target="_blank">&copy; Mapbox &copy; OpenStreetMap</a>',
    id: 'mapbox.light',
    maxZoom: 18,
    minZoom: 11
    }).addTo(mymap);

    // Create the layercontrol and add it to the map
    controlLayers = L.control.layers().addTo(mymap, true);

    for (var i=0; i<rtejsonlist.length; i++) {
        //console.log("rtejsonlist: " +rtejsonlist[i])
        getJson(rtejsonlist[i]);
    }

    console.log(rtegeoJson)

    $('.mapview').click(function() {
        console.log($(this).attr("value"))
        sel_view = $(this).attr("value");
        console.log("sel_view: " + sel_view)

        requestmapdata();
        });
})

function onEachFeature(feature, layer) {
    var popupContent = "<b>Route:</b> " + feature.properties.rte + '-' + feature.properties.rte_desc + '<br />'
                        + "<b>Direction:</b> " + feature.properties.dir_desc;

    layer.bindPopup(popupContent);
}

function getJson(jsonname) {

    var pathjson = base + 'static/geojson/'

    // Loading a GeoJSON file (using jQuery's $.getJSON)
    $.getJSON(pathjson + jsonname, function (data) {

        // Use the data to create a GeoJSON layer and add it to the map
        rtegeoJson[data.features[0].properties.rte] = data;
        var geoLayer = L.geoJson(data, {
                style: function (feature) {
                    return {
                        color: getBaseColor(feature.properties.type),
                        weight: 3
                        };
                },
                
                onEachFeature: onEachFeature,

        }).addTo(mymap);

    // Add the geojson layer to the layercontrol
    controlLayers.addOverlay(geoLayer, jsonname.slice(0,-9));
    });
}

function getBaseColor(rtetype) {
    return rtetype == "BUS" ? '#1c4ca5' :
           rtetype == "MAX" ? '#d1441e' :
           rtetype == "CR"  ? '#d95f0e' :
                              '#FFEDA0';
}


function getColor(pct) {
 return pct > 80 ? '#800026' :
        pct > 60  ? '#BD0026' :
        pct > 50  ? '#E31A1C' :
        pct > 40  ? '#FC4E2A' :
        pct > 30   ? '#FD8D3C' :
        pct > 20   ? '#FEB24C' :
        pct > 10   ? '#FED976' :
                      '#FFEDA0';
}


function requestmapdata() {
    $.getJSON('mapviewdata', {sel_view: sel_view}, function(data) {

        data = data.data;
        console.log(data);
        addGeoJson(data);
        addLabel();

    });

}

function addGeoJson(data) {
    mymap.eachLayer(function (layer) {
    if (layer instanceof L.TileLayer == false) {
        mymap.removeLayer(layer);
        controlLayers.removeLayer(layer);
    console.log(layer instanceof L.TileLayer);
    }
    });

    for (var rte in rtegeoJson) {
        if (rtegeoJson.hasOwnProperty(rte)) {
            var routegeoJson = rtegeoJson[rte]
            var geoLayer = L.geoJson(routegeoJson, {
                style: function (feature) {
                    return {
                        color: getColor(data[rte]),
                        weight: 3
                        };
                },
                
                onEachFeature: onEachFeature,

            }).addTo(mymap);
            // Add the geojson layer to the layercontrol
            controlLayers.addOverlay(geoLayer, rte + " " + routegeoJson.features[0].properties.rte_desc);
        }
     }
     


}

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 3,
        color: '#666',

    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

function addLabel() {
    if(hasLegend) {
        return
    }

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 10, 20, 30, 40, 50, 60, 80],
        labels = [];

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }

    return div;
    };

    legend.addTo(mymap);
    hasLegend = true;
}
