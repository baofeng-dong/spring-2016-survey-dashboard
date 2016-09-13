
//initialize map 
var mymap = null; 
var controlLayers = null;
var rtegeoJson = {};
var sel_view = null;
var sel_args = {
    view : "",
    day : ""
    }

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
    // add the list of routes geojson to the map by calling the getJson function
    for (var i=0; i<rtejsonlist.length; i++) {
        //console.log("rtejsonlist: " +rtejsonlist[i])
        getJson(rtejsonlist[i]);
    }

    console.log(rtegeoJson)

    $('.mapview').click(function() {
        console.log($(this).attr("value"))
        sel_view = $(this).attr("value");
        console.log("sel_view: " + sel_view);
        sel_args.view = sel_view;

        requestmapdata();
        });
    $('.checkweek').click(function() {
        if ($(this).prop("checked")) {
            var sel_day = $(this).val();
            console.log("sel_day: " + sel_day);
            sel_args.day = sel_day;
        }

        if (sel_day == 'All') {
            sel_args.day = null;
        }
        else {
        sel_args.day = sel_day;
        }

        requestmapdata();

    });
    $('input[type="checkbox"]').on('change', function() {
        $('input[type="checkbox"]').not(this).prop('checked', false);
    });
})

function onEachFeature(feature, layer) {
    var popupContent = "<b>Route:</b> " + feature.properties.rte + '-' + feature.properties.rte_desc + '<br />'
                        + "<b>Direction:</b> " + feature.properties.dir_desc;
    // specify popup options 
    var customOptions =
        {
        'maxWidth': '300',
        'className' : 'custom'
        }

    layer.bindPopup(popupContent, customOptions);

    /*layer.on('mouseover', function(e) {
        this.openPopup();
    });
    layer.on('mouseout', function(e) {
        this.closePopup();
    });

    /*layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight
        
    });*/
}

function getJson(jsonname) {

    var pathjson = base + 'static/geojson/'

    // Loading a GeoJSON file (using jQuery's $.getJSON)
    $.getJSON(pathjson + jsonname, function (data) {
        //console.log(data);

        // create a dict called retegeoJson with rte as key and the route geojson as value
        rtegeoJson[data.features[0].properties.rte] = data;

        var geoLayer = L.geoJson(data, {
                style: function (feature) {
                    return {
                        color: getBaseColor(feature.properties.rte),
                        weight: 2.5,
                        opacity: 0.80
                        };
                },
                
                onEachFeature: onEachFeature,

        }).addTo(mymap);

    // Add the geojson layer to the layercontrol
    controlLayers.addOverlay(geoLayer, data.features[0].properties.rte + " " + "-" + " " + data.features[0].properties.rte_desc);
    });
}

function getBaseColor(rte) {
    return rte == 90  ? '#d02c0f' :
           rte == 100 ? '#0069AA' :
           rte == 190 ? '#FFC425' :
           rte == 200 ? '#008752' :
           rte == 203 ? '#c044ec' :
           rte == 290 ? '#D15F27' :
                        '#1c4ca5' ;
}


function getColor(pct) {
 return pct > 80 ? '#990000' :
        pct > 60 ? '#992600' :
        pct > 40 ? '#997300' :
        pct > 20 ? '#739900' :
                   '#269900';
}


function requestmapdata() {
    $.getJSON('mapviewdata', sel_args, function(data) {

        data = data.data;
        console.log(data);
        addGeoJson(data);
        addLabel(sel_view);

    });

}

function addGeoJson(data) {
    //console.log(data);
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
            // add the list of geojson routes and style the color based on the income pct value (data)
            var geoLayer = L.geoJson(routegeoJson, {
                style: function (feature) {
                    return {
                        color: getColor(data[rte]),
                        weight: 3,
                        opacity: 0.8
                        };
                },
                
                onEachFeature: onEachFeature,

            }).addTo(mymap);
            // Add the geojson layer to the layercontrol
            controlLayers.addOverlay(geoLayer, rte + " " + "-" + " " + routegeoJson.features[0].properties.rte_desc);
        }
     }
     


}

//add label to map
function addLabel(sel_view) {
    console.log(sel_view);
    var title = sel_view.toUpperCase();
    if(hasLegend) {
        return
    }

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 20, 40, 60, 80],
        labels = [(title.bold()).fontsize(3)],
        from, to;

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        from = grades [i];
        to = grades[i+1]-1;

    labels.push(
        '<i style="background:' + getColor(from + 1) + '"></i> ' +
        from + (to ? '&ndash;' + to : '+'));
        }
        div.innerHTML = labels.join('<br>');
        return div;


        };

    legend.addTo(mymap);
    hasLegend = true;
}
