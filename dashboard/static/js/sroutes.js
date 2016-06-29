

//function for expanding/collapsing div content

function toggle_tb(div_id_tb){
    var div = $(div_id_tb);
    $('#toggle').unbind("click").click(function(){
         //div.slideToggle('fast');
         
         if ($(this).attr('value') == 'Hide') {
            console.log(this + 'hide selected')
            div.animate({
                height: '0%'
                }).hide()
            $(this).attr('value','Show')
            
        } else {
            console.log(this + 'show selected')
            div.animate({
                height: '100%'
                }).show()
            $(this).attr('value','Hide')
        
            }
       });
}

//append a svg file based on selected rte to div-id: line-chart

function append_img(div_id){
    var div = $(div_id);
    var rte = routeskey[sel_line]
    div.empty().prepend('<object data='+base+'static/image/' + rte + '.svg?1222259157.415" type="image/svg+xml" width="100%" />');
}

//build table using JSON data in jquery
function build_table(data,tb_id){

    var table = $(tb_id)
    console.log(table)
    $(".data-row").empty()
    for(var i = 0;i < data.length; i++){
        console.log(data[i]);
        var row = $("<tr>",{class: "data-row"});
        for(var j = 0; j < data[i].length; j++){
            var cell = $("<td>", {align:"center",valign:"middle"}).text(data[i][j]);
            console.log(data[i][j])
            row.append(cell)
        }
        table.append(row)
    }
}

//build chart function
function build_chart(chart){
    $("#surveyor-pie-chart").empty().append(chart)
}

//update line graph image 
function update_chart(div_id){
    var div =$(div_id);
    new_data = "http://localhost:5000/static/image/' + rte + '.svg" + new Date().getTime();
    div.attr("data",new_data);
    console.log("newsrc:" + new_data);
    console.log("update chart");
}


var sel_line = null;

    //console.log(routes)
var routeskey = buildkey(routes);

for (var key in routeskey){
    var val = routeskey[key];
    console.log("Key: "+key+" Value:"+val);
}

//builds reference routeskey list
function buildkey(routes){
    var routeskey = {};
    for (var i = 0; i < routes.length; i++){
        routeskey[routes[i][1]] = routes[i][0];
    }
    routeskey['Surveyor Count'] = 300;
    routeskey['Route Count'] = 310;
    routeskey['DOW Count'] = 320;
    return routeskey
}

function reset(){
    $("#surveyor-route").hide();
    $("#line-chart").hide();
    $("#surveyor-count").hide();
    $("#surveyor-pie-chart").hide();
    $("#route-count").hide();
    $("#route-pie-chart").hide();
    $("#wk-bar-chart").hide();
    $("#button-header").hide();
    $("#toggle").attr('value','Hide');
}


$('#filter_line a').on('click', function() {
    reset();
    sel_line = this.text
    console.log(sel_line)
    console.log(routeskey[sel_line])
    var rte = routeskey[sel_line];
    var args = {"rte":(routeskey[sel_line])};
    console.log("rte: " + rte)
    $("#line_btn").text(this.text+' ').append('<span class="caret"></span>');
    // for all the bus and max routes selected (<300)
    if (routeskey[sel_line] < 300) {
        console.log(routeskey[sel_line])
        
        $("#surveyor-route").show();
        $("#line-chart").show();
        $("#button-header").show();
        $.getJSON('srdata', args, function(data) {
            tb_id = "#route-pct"
            div_id_ln = "#line-chart"
            div_id_tb = "#surveyor-route"
            var chart = data.line_chart;
            console.log(chart);
            data = data.data;
            console.log(data);
            build_table(data,tb_id);
            append_img(div_id_ln);
            toggle_tb(div_id_tb);
            
        });

    }
    else if (routeskey[sel_line] == 300) {
        
        $("#surveyor-count").show();
        $("#surveyor-pie-chart").show();
        $("#button-header").show();
        $.getJSON('userdata', args, function(data) {
            tb_id = "#surveyor-pct"
            div_id = "#surveyor-pie-chart"
            div_id_tb = "#surveyor-count"
            data = data.data;
            console.log(data)
            build_table(data,tb_id);
            append_img(div_id);
            toggle_tb(div_id_tb);
           
        });
    }
    else if (routeskey[sel_line] == 310) {
      
        $("#route-count").show();
        $("#route-pie-chart").show();
        $("#button-header").show();
        
        
        $.getJSON('rtedata', args, function(data) {
            tb_id = "#rte-count"
            div_id_ch = "#route-pie-chart"
            div_id_tb = "#route-count"
            data = data.data;
            console.log(data)
            build_table(data,tb_id);
            append_img(div_id_ch);
            toggle_tb(div_id_tb);
           
        });
    }
    else if (routeskey[sel_line] == 320) {
        
        $("#wk-bar-chart").show();
        
        $.getJSON('surveywkd', args, function(data) {
            div_id = "#wk-bar-chart"
            data = data.data;
            console.log(data)
            append_img(div_id);
        });
    }

});
