

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

//append a svg file based on selected question num to div-id: line-chart

function append_img(div_id){
    var div = $(div_id);
    var qnum = questionkey[sel_ques]
    div.empty().prepend('<object data='+ base + 'static/image/' + 'q' + qnum + '.svg?' + Math.random() + ' type="image/svg+xml" width="100%" />');
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

var sel_ques = null;

var sel_args = {
    qnum : "",
    vehicle: "",
    rtetype: "",
    day : "",
    tod : "",
    fpl : "",
    rte : ""
    }

var questionkey = buildkey(questions);

for (var key in questionkey){
    var val = questionkey[key];
    console.log("Key: "+key+" Value:"+val);
}

//builds reference questionkey list
function buildkey(questions){
    var questionkey = {};
    for (var i = 0; i < questions.length; i++){
        questionkey[questions[i][1]] = questions[i][0];
    }

    return questionkey
}


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
    $("#transfer").hide();
    $("#trip").hide();
    $("#agency").hide();
    $("#faretype").hide();
    $("#purchasetype").hide();
    $("#daypass").hide();
    $("#singlefare").hide();
    $("#purloc").hide();
    $("#payment").hide();
    $("#college").hide();
    $("#collegeattend").hide();
    $("#smartphone").hide();
    $("#internet").hide();
    $("#age").hide();
    $("#gender").hide();
    $("#race").hide();
    $("#disability").hide();
    $("#transit").hide();
    $("#vehicle").hide();
    $("#house").hide();
    $("#vecount").hide();
    $("#income").hide();
    $("#poverty").hide();
}

$('#filter_rte a').on('click', function() {
    reset();
    var sel_rte = this.text
    console.log(sel_rte)
    if (sel_rte == 'All') {
        sel_args.rte = null;
    }
    else {
    var rte = routeskey[sel_rte];
    //var args = {"rte":(routeskey[sel_rte])};
    sel_args.rte = routeskey[sel_rte];
    console.log("rte: " + rte)
    }

    $("#rte_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();
});


$('#filter_ques a').on('click', function() {
    reset();
    sel_ques = this.text
    console.log(sel_ques)
    console.log(questionkey[sel_ques])
    var qnum = questionkey[sel_ques];
    //var args = {"qnum":(questionkey[sel_ques])};
    sel_args.qnum = questionkey[sel_ques];
    console.log("qnum: " + qnum)
    $("#ques_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();

});


$('#filter_day a').on('click', function() {
    reset();
    var sel_day = this.text
    console.log("day selected: " + sel_day)
    if (sel_day == 'All') {
        sel_args.day = null;
    }
    else {
    sel_args.day = sel_day;
    }
    $("#day_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();

});


$('#filter_vehicle a').on('click', function() {
    reset();
    var sel_vehicle = this.text
    console.log("vehicle selected: " + sel_vehicle)
    if (sel_vehicle == 'All') {
        sel_args.vehicle = null;
    }
    else {
    sel_args.vehicle = sel_vehicle;
    }
    $("#vehicle_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();

});

$('#filter_rtetype a').on('click', function() {
    reset();
    var sel_rtetype = this.text
    console.log("route type selected: " + sel_rtetype)
    if (sel_rtetype == 'All') {
        sel_args.rtetype = null;
    }
    else {
    sel_args.rtetype = sel_rtetype;
    }
    $("#rtetype_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();

});


$('#filter_tod a').on('click', function() {
    reset();
    var sel_tod = this.text
    console.log("time of day selected: " + sel_tod)
    if (sel_tod == 'All') {
        sel_args.tod = null;
    }
    else {
    sel_args.tod = sel_tod;
    }
    $("#tod_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();

});


$('#filter_fpl a').on('click', function() {
    reset();
    var sel_fpl = this.text
    console.log("fpl selected: " + sel_fpl)
    if (sel_fpl == 'All') {
        sel_args.fpl = null;
    }
    else {
    sel_args.fpl = sel_fpl;
    }
    $("#fpl_btn").text(this.text+' ').append('<span class="caret"></span>');
    requestdata();

});

function requestdata() {
    $.getJSON('questionsdata', sel_args, function(data) {
        console.log(data);
        div_id_ln = "#line-chart"
        div_id = "#" + data.metadata.id
        tb_id = div_id + "-table"
        data = data.data;

        build_table(data,tb_id);
        append_img(div_id_ln);
        toggle_tb(div_id);
        $(div_id).show();
        $("#line-chart").show();
        $("#button-header").show();


    });

}
