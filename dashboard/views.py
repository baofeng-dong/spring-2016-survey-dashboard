# Copyright (C) 2016 Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from flask import render_template,request,jsonify,url_for,Blueprint,redirect
from sqlalchemy.orm import sessionmaker,scoped_session 
from dashboard import app,db
from dashboard.models import Sroutes,Scount,Surveyors,Surveywkd, Survey
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey, cast, Numeric
from sqlalchemy.sql import func
import pygal
from pygal.style import DarkSolarizedStyle, LightStyle, CleanStyle, DarkStyle
import codecs
import json
import base64
import os,sys
import time
from datetime import datetime
from .metadata import metadata
from dashboard.auth import Auth

DIRPATH = os.path.dirname(os.path.realpath(__file__))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/introduction')
def intro():
    return render_template("introduction.html")

@app.route('/map')
def map():

    return render_template("map.html", rtejsonlist=getrtejson())

def getrtejson():
    d = os.path.join(DIRPATH, "static/geojson")
    return [f for f in os.listdir(d)]

@app.route('/rtejsondata')
def getjson():
    d = os.path.join(DIRPATH, "static/geojson")
    rtejsonlist = [os.path.join(d, f) for f in os.listdir(d)]
    return jsonify(data=rtejsonlist)

@app.route('/mapviewdata')
def mapviewdata():
    sel_view = request.args.get('sel_view')
    data = None
    if sel_view == 'income':
        data = mapincome()

    if sel_view == 'race':
        data = maprace(sel_view)

    return jsonify(data=data)

def mapincome():
    lowincomeresults = {}

    results = db.session.execute("""
                                    WITH survey as (
                                        select *
                                                from fare_survey_2016_clean 
                                                where
                                                    willing = '1' and
                                                    q23_income is not null and
                                                    q23_income != '12'),
                                                    
                                        low_income as (
                                        select 

                                            rte,
                                            round( sum(weight_final) * 100 / (
                                                select sum(weight_final)
                                                from survey where s.rte=rte)::numeric,2) as pct
                                        from survey as s
                                        where q23_income in ('1','2','3')
                                        group by rte
                                        order by rte::integer)

                                        select * from low_income""")

    for row in results:
        print(row[0],row[1])
        lowincomeresults[row[0]] = float(row[1])
    return lowincomeresults

@app.route('/sroutes')
def sroutes():
    # return routes list dynamically
    app.logger.debug(url_for('index'))

    return render_template("sroutes.html", routes = getroutes())


def getroutes():
    routes = db.session.execute(""" 
        select rte,rte_desc
        from rtedesc_lookup""")

    return [(route[0],route[1]) for route in routes]

@app.route('/srdata')
def srdata():
    srresults = []
    rte = request.args.get('rte')
    line_chart = pygal.HorizontalBar(print_values=True, width=800, height=600, disable_xml_declaration=True)
    line_chart.title = 'Completed Surveys for Route %s' % (rte)


    for row in Sroutes.query.filter_by(rte=rte).order_by(Sroutes.pct_rte.desc()).all():
        srresults.append([row.surveyors.name,row.rte,row.num_surveys,float(row.pct_rte),float(row.pct)])
        line_chart.add(row.surveyors.name,row.num_surveys)

    line_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}.svg".format(rte)))
    
    
    
    return jsonify(data=srresults, rte=rte)


@app.route('/userdata')
def userdata():
    userresults = []
    rte = request.args.get('rte')

    pie_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True)
    pie_chart.title = 'Percentage of Completed Surveys by Surveyor'

    results = db.session.execute("""select 
                                    b.name,
                                    sum(num_surveys) as sum_survey,
                                    round(100*sum(num_surveys)/(select sum(num_surveys) from sroutes)::numeric,2) as pct 
                                    from sroutes a,surveyors b
                                    where a.surveyor = b.surveyor
                                    group by b.name
                                    order by sum_survey desc""")
    for row in results:
        print(row)
        print("type",type(row))
        userresults.append([row[0],int(row[1]),float(row[2])])
        pie_chart.add(row[0],float(row[2]))
    app.logger.debug(os.getenv('USER'))
    pie_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}.svg".format(rte)))
    
    return jsonify(data=userresults)


@app.route('/rtedata')
def rtedata():
    rteresults = []
    rte = request.args.get('rte')
    pie_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True)
    pie_chart.title = 'Percentage of Completed Surveys by Route'
    
    results = db.session.execute("""select 
                                    r.rte_desc,
                                    sum(s.num_surveys) as sum,
                                    round(100*sum(num_surveys)/(select sum(num_surveys) from sroutes)::numeric,2) as pct

                                    from sroutes s,rtedesc_lookup r
                                    where s.rte = r.rte::varchar
                                    group by r.rte_desc
                                    order by sum desc""")
    for row in results:
        print(row)
        rteresults.append([row[0],int(row[1]),float(row[2])])
        pie_chart.add(row[0],float(row[2]))
    pie_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}.svg".format(rte)))
    
    return jsonify(data=rteresults)


@app.route('/surveywkd')
def surveywkd():
    wkresults = []
    labels =[]
    rte = request.args.get('rte')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Completed Surveys by Day of Week'
    
    #results = Surveywkd.query.with_entities(Surveywkd.dow,Surveywkd.count).all()
    results = db.session.execute("""select dow,count
                                    from surveywkd""")
    for row in results:
        print(row[0],int(row[1]))
        wkresults.append([row.dow,int(row.count)])
        labels.append((row.dow))
        bar_chart.add(row[0],int(row[1]))
    for label in labels:
        print(label)
    #bar_chart.x_labels = 'Sunday','Friday','Monday','Tuesday','Wednesday','Thursday','Saturday'
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}.svg".format(rte)))

    return jsonify(data=wkresults)


@app.route('/willing')
def willing():
    willingresults = []
    labels =[]
    rte = request.args.get('rte')
    bar_chart = pygal.HorizontalBar(print_values=True)
    bar_chart.title = 'Survey Rejection Rate by Surveyor'
    
    #results = Surveywkd.query.with_entities(Surveywkd.dow,Surveywkd.count).all()
    results = db.session.execute("""select 
                                        su.name, sc.willing, sc.count, sc.pct_surveyor, sc.pct
                                        from surveyors su, scount sc
                                        where su.surveyor=sc.surveyor and
                                        sc.willing='No' and
                                        sc.count > 100
                                        order by sc.pct_surveyor desc""")
    for row in results:
        print(row[0],row[1],int(row[2]),float(row[3]),float(row[4]))
        willingresults.append([row[0],row[1],int(row[2]),float(row[3]),float(row[4])])

        bar_chart.add(row[0],float(row[3]))


    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}.svg".format(rte)))

    return jsonify(data=willingresults)


@app.route('/fareresults')
@Auth.requires_auth
def fareresults():
    # return dropdown list dynamically
    #build a question list key value dropdown

    query = db.session.execute("""
                select num, questions
                from ques_lookup""")

    questions = []
    for question in query:
        questions.append([question[0],question[1]])


    return render_template("fareresults.html",questions=questions, routes=getroutes())

@app.route('/questionsdata')
def questionsdata():
    qnum = int(request.args.get('qnum'))
    data = None
    if qnum == 1:
        data = transferdata(qnum, request.args)

    if qnum == 2:
        data = tripdata(qnum, request.args)

    if qnum == 3:
        data = agencydata(qnum, request.args)

    if qnum == 4:
        data = faretype(qnum, request.args)

    if qnum == 5:
        data = purchasetype(qnum, request.args)

    if qnum == 6:
        data = daypass(qnum, request.args)

    if qnum == 7:
        data = singlefare(qnum, request.args)
    if qnum == 8:
        data = purloc(qnum, request.args)
    if qnum == 9:
        data = payment(qnum, request.args)
    if qnum == 10:
        data = college(qnum, request.args)
    if qnum == 11:
        data = collegeattend(qnum, request.args)
    if qnum == 12:
        data = smartphone(qnum, request.args)
    if qnum == 13:
        data = internet(qnum, request.args)
    if qnum == 14:
        data = age(qnum, request.args)
    if qnum == 15:
        data = gender(qnum, request.args)
    if qnum == 16:
        data = race(qnum, request.args)
    if qnum == 17:
        data = disability(qnum, request.args)
    if qnum == 18:
        data = transit(qnum, request.args)
    if qnum == 19:
        data = vehicle(qnum, request.args)
    if qnum == 20:
        data = house(qnum, request.args)
    if qnum == 21:
        data = vecount(qnum, request.args)
    if qnum == 22:
        data = income(qnum, request.args)
    if qnum == 23:
        data = poverty(qnum, request.args)

    return jsonify(data=data, metadata=metadata[qnum])



#@app.route('/transferdata')
def transferdata(qnum, args):
    transferresults = []
    labels = []
    
    bar_chart = pygal.Bar(print_values=True)
    
    bar_chart.title = 'Number of Transfers in One Trip'
    where = buildconditions(args)
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016_clean
                    where
                        willing = '1' and
                        q1_transfer is not null {0}),
                    
            survey_tran as (
            select 
                case
                    when q1_transfer = '1' then 'No'
                    when q1_transfer = '2' then 'Transfer 1 time'
                    when q1_transfer = '3' then 'Transfer 2 times'
                    when q1_transfer = '4' then 'Transfer 3 or more'
                end as Transfer,
                round(sum(weight_final)::numeric,1) as count,
                round( sum(weight_final) * 100 / (
                    select sum(weight_final)
                    from survey)::numeric,2) as pct
            from survey
            group by q1_transfer
            order by q1_transfer::integer)

            select * from survey_tran""".format(where))
    for row in results:
        print(row[0],row[1],row[2])
        transferresults.append([row[0],float(row[1]),float(row[2])])
        labels.append(row[0])
        bar_chart.add(row[0],[{'value':float(row[1])}])
    #bar_chart.x_labels = labels
    for label in labels:
        print(label)
    #bar_chart.x_labels = "No","Transfer 1 time", "Transfer 2 times", "Transfer 3 or more"
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    #return jsonify(data=transferresults)
    return transferresults


#@app.route('/tripdata')
def tripdata(qnum, args):
    tripresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Number of Trips by Range in a Week'
    where = buildconditions(args)
    results = db.session.execute("""
                                WITH survey as (
                                select *
                                        from fare_survey_2016_clean 
                                        where
                                            willing = '1' and
                                            q3_trip_group is not null {0}),

                                tripgroup as (
                                    select
                                        case
                                            when q3_trip_group = '1' then 'Infrequent rider'
                                            when q3_trip_group = '2' then 'Occasional rider (up to 6 trips/month)'
                                            when q3_trip_group = '3' then 'Regular rider (7-17 trips/month)'
                                            when q3_trip_group = '4' then 'Frequent rider (18 trips/month or more)'
                                        end as triprider,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round(100*sum(weight_final)/(select sum(weight_final) from survey)::numeric,2) as pct
                                    from survey
                                    group by q3_trip_group::integer
                                    order by q3_trip_group::integer)

                                select * from tripgroup""".format(where))
    for row in results:
        print(row[0],row[1],row[2])
        tripresults.append([str(row[0]),float(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))

    #return jsonify(data=tripresults)
    return tripresults

#@app.route('/agencydata')
def agencydata(qnum, args):
    agencyresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Number of Faretypes by Agency'
    where = buildconditions(args)
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016_clean
                    where
                        willing = '1' and
                        q4_fare_agency is not null {0}),
                    
            fare_agency as (
            select
                case 
                    when q4_fare_agency = '1' then 'TriMet'
                    when q4_fare_agency = '2' then 'C-TRAN fare'
                    when q4_fare_agency = '3' then 'Streetcar fare'
                end as Fareagency,
                round(sum(weight_final)::numeric,1) as count,
                round( sum(weight_final) * 100 / (
                    select sum(weight_final)
                    from survey)::numeric,2) as pct
            from survey
            group by q4_fare_agency
            order by q4_fare_agency::integer)

            select * from fare_agency""".format(where))
    for row in results:
        print(row[0],row[1],row[2])
        agencyresults.append([str(row[0]),float(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))

    #return jsonify(data=agencyresults)
    return agencyresults


#@app.route('/faretype')
def faretype(qnum, args):
    fareresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Number of Fares by Faretypes'
    where = buildconditions(args)
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016_clean
                    where
                        willing = '1' and
                        q5_fare_type is not null {0}),
                    
            fare_type as (
            select
                case 
                    when q5_fare_type = '1' then 'Adult'
                    when q5_fare_type = '2' then 'Youth'
                    when q5_fare_type = '3' then 'Honored Citizen'
                    when q5_fare_type = '4' then 'LIFT'
                    when q5_fare_type = '5' then 'Employee ID with TriMet sticker'
                    when q5_fare_type = '6' then 'High School ID with TriMet fare'
                    when q5_fare_type = '7' then 'College ID with TriMet sticker'
                    when q5_fare_type = '8' then 'Honored Citizen Downtown Pass'
                    when q5_fare_type = '9' then 'Other'
                end as Faretype,
                round(sum(weight_final)::numeric,1) as count,
                round( sum(weight_final) * 100 / (
                    select sum(weight_final)
                    from survey)::numeric,2) as pct
            from survey
            group by q5_fare_type
            order by q5_fare_type::integer)

            select * from fare_type""".format(where))
            
    for row in results:
        print(row[0],row[1],row[2])
        fareresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = fareresults)
    return fareresults
    
#@app.route('/purchasetype')
def purchasetype(qnum, args):
    purchaseresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Number of Fares by Purchase Types'
    where = buildconditions(args)
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016_clean
                    where
                        willing = '1' and 
                        q6_purchase_type is not null and
                        q6_purchase_type != '' {0}),
                    
            purchase_type as (
            select
                case 
                    when q6_purchase_type = '1' then 'Single 2.5 hour ticket'
                    when q6_purchase_type = '2' then 'Book of 10 2.5 hour tickets'
                    when q6_purchase_type = '3' then '1-Day Pass'
                    when q6_purchase_type = '4' then 'Book of 5 1-Day Passes'
                    when q6_purchase_type = '5' then '7-Day Pass'
                    when q6_purchase_type = '6' then '14-Day Pass'
                    when q6_purchase_type = '7' then 'Monthly Pass'
                    when q6_purchase_type = '8' then 'Annual Pass'
                end as purchasetype,
                round(sum(weight_final)::numeric,1) as count,
                round( sum(weight_final) * 100 / (
                    select sum(weight_final)
                    from survey)::numeric,2) as pct
            from survey
            group by q6_purchase_type
            order by count desc)

            select * from purchase_type""".format(where))
            
    for row in results:
        print(row[0],row[1],row[2])
        purchaseresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = purchaseresults)
    return purchaseresults

#@app.route('/daypass')
def daypass(qnum, args):
    daypassresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Number of One-way Trips on a Day Pass'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean 
                                            where
                                                willing = '1' and
                                                q7_day_fare is not null {0}),

                                    dayfare as (
                                        select
                                            q7_day_fare::integer,
                                            round(sum(weight_final)::numeric,1) as count,
                                            round(100*sum(weight_final)/(select sum(weight_final) from survey)::numeric,2) as pct
                                        from survey
                                        group by q7_day_fare::integer
                                        order by q7_day_fare::integer)

                                    select * from dayfare""".format(where))
            
    for row in results:
        print(row[0],row[1],row[2])
        daypassresults.append([str(row[0]),float(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = daypassresults)
    return daypassresults

#@app.route('/singlefaretrip')
def singlefare(qnum, args):
    singlefareresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, print_values=True)
    bar_chart.title = 'Number of One-way/Round Trips on a Single Fare'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean 
                                            where
                                                willing = '1' and
                                                q8_single_fare in ('1','2') {0}),

                                    singlefare as (
                                        select
                                            case
                                                when q8_single_fare= '1' then 'One-way trip'
                                                when q8_single_fare='2' then 'Round-trip'
                                            end as faretrip,
                                            round(sum(weight_final)::numeric,1) as count,
                                            round(100*sum(weight_final)/(select sum(weight_final) from survey)::numeric,2) as pct
                                        from survey
                                        group by q8_single_fare
                                        order by q8_single_fare)

                                    select * from singlefare""".format(where))

    for row in results:
        print(row[0],row[1],row[2])
        singlefareresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return singlefareresults


def purloc(qnum, args):
    locationresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.HorizontalBar(print_values=True)
    bar_chart.title = 'Fare Purchase Location'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                        select *
                                from fare_survey_2016_clean
                                where
                                    willing = '1' and
                                    q9_purchase_loc is not null {0}),
                                
                        purchase_location as (
                        select
                            case 
                                when q9_purchase_loc = '1' then 'On board vehicle'
                                when q9_purchase_loc = '2' then 'Ticket Vending Machine'
                                when q9_purchase_loc = '3' then 'Retail Store'
                                when q9_purchase_loc = '4' then 'Work'
                                when q9_purchase_loc = '5' then 'School'
                                when q9_purchase_loc = '6' then 'Mobile Ticket App'
                                when q9_purchase_loc = '7' then 'TriMet Ticket Office'
                                when q9_purchase_loc = '8' then 'Online'
                                when q9_purchase_loc = '9' then 'Social Service Agency'
                                when q9_purchase_loc = '10' then 'Other'
                            end as Purchaseloc,
                            round(sum(weight_final)::numeric,1) as count,
                            round( sum(weight_final) * 100 / (
                                select sum(weight_final)
                                from survey)::numeric,2) as pct
                        from survey
                        group by q9_purchase_loc
                        order by count desc)

                        select * from purchase_location""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        locationresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return locationresults


def payment(qnum, args):
    paymentresults = []
    #qnum = request.args.get('qnum')
    # bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'All Purchases Payment Options'
    where = buildconditions(args)
    results = db.session.execute("""with survey as (
                                    select * 
                                        from fare_survey_2016_clean
                                        where willing = '1' and 
                                        q10_purchase_types is not null {0}),

                                    paymentpct as (
                                        select
                                        case
                                            when q10_purchase_types = '2' then 'Checking or savings account ONLY'
                                            when q10_purchase_types = '3' then 'Bank issued debit/credit card ONLY'
                                            when q10_purchase_types = '4' then 'Pre-paid debit or credit card ONLY'
                                            when q10_purchase_types = '5' then 'Pre-paid gift card ONLY'
                                            when q10_purchase_types = '6' then 'Money order or cashiers check ONLY'
                                            when q10_purchase_types = '7' then 'Smartphone payment apps ONLY'
                                            when q10_purchase_types = '8' then 'Cash ONLY'
                                            when q10_purchase_types = '9' then 'Cash + Ohter Ways'
                                            when q10_purchase_types = '10' then 'Not cash but other combinations'
                                        end as payment,
                                            round(sum(weight_final)::numeric,1) as count,
                                            round(sum(weight_final)*100/(select sum(weight_final) from survey)::numeric,2) as pct
                                            from survey
                                            group by payment
                                            order by payment
                                    )

                                    select * from paymentpct""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        paymentresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return paymentresults


def college(qnum, args):
    collegeresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Percentages of College Students'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean
                                            where
                                                willing = '1' and
                                                q11_college is not null {0}),
                                            
                                    survey_college as (
                                    select
                                        case 
                                            when q11_college = '1' then 'No'
                                            when q11_college = '2' then 'Yes part time'
                                            when q11_college = '3' then 'Yes full time'
                                        end as college,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    group by q11_college
                                    order by pct)

                                    select * from survey_college""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        collegeresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return collegeresults


def collegeattend(qnum, args):
    attendresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Colleges Attended'
    where = buildconditions(args)
    results = db.session.execute("""with survey as (
                                    select *
                                        from fare_survey_2016_clean
                                        where willing = '1' and 
                                        q12_college_attend is not null and
                                        q11_college in ('2','3') {0}),

                                    collegeall as (
                                            select 
                                                unnest(string_to_array(q12_college_attend,' ')) as college, 
                                                round(sum(weight_final)::numeric,1) as count,
                                                round(sum(weight_final)*100/(select sum(weight_final) from survey)::numeric,2) as pct
                                                from survey
                                                group by college
                                                order by college
                                        ),

                                    collegepct as (
                                    select
                                        case
                                            when college = '1' then 'Clackamas Community College'
                                            when college = '2' then 'Concordia University'
                                            when college = '3' then 'Lewis & Clark College'
                                            when college = '4' then 'Mount Hood Community College'
                                            when college = '5' then 'Oregon Health and Science University'
                                            when college = '6' then 'Pacific University'
                                            when college = '7' then 'Portland Community College'
                                            when college = '8' then 'Portland State University'
                                            when college = '9' then 'Reed College'
                                            when college = '10' then 'University of Portland'
                                            when college = '11' then 'Other'
                                        end as college,
                                        count,
                                        pct
                                        from collegeall
                                        order by count desc)

                                    select * from collegepct""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        attendresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return attendresults


def smartphone(qnum, args):
    smartphoneresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Smartphones'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean
                                            where
                                                willing = '1' and
                                                q13_smartphone is not null {0}),
                                            
                                    smart_phone as (
                                    select
                                        case 
                                            when q13_smartphone = '1' then 'Yes'
                                            when q13_smartphone = '2' then 'No'
                                            when q13_smartphone = '3' then 'Do not know'
                                        end as smartphone,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    group by q13_smartphone
                                    order by count desc)

                                    select * from smart_phone""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        smartphoneresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return smartphoneresults


def internet(qnum, args):
    internetresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Access to Internet'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean
                                            where
                                                willing = '1' and
                                                q14_internet is not null {0}),
                                            
                                    internet as (
                                    select
                                        case 
                                            when q14_internet = '1' then 'Yes'
                                            when q14_internet = '2' then 'No'
                                            when q14_internet = '3' then 'Don not know'
                                        end as smartphone,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    group by q14_internet
                                    order by count desc)

                                    select * from internet""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        internetresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return internetresults


def age(qnum, args):
    ageresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Age Distribution'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean
                                            where
                                                willing = '1' and
                                                q15_age is not null {0}),
                                                
                                    survey_age as (
                                    select 
                                        case 
                                            when q15_age = '1' then 'Under 18'
                                            when q15_age = '2' then '18-24'
                                            when q15_age = '3' then '25-34'
                                            when q15_age = '4' then '35-44'
                                            when q15_age = '5' then '45-54'
                                            when q15_age = '6' then '55-64'
                                            when q15_age = '7' then '65 or more'
                                        end as age,
                                        sum(weight_final) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    group by age
                                    order by age)

                                    select * from survey_age""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        ageresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return ageresults


def gender(qnum, args):
    # app.logger.debug(args)
    genderresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, print_values=True)
    bar_chart.title = 'Gender Distribution'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean
                                            where
                                                willing = '1' and
                                                q16_gender is not null {0}),
                                                
                                    survey_gender as (
                                    select 
                                        case 
                                            when q16_gender = '1' then 'Female'
                                            when q16_gender = '2' then 'Male'
                                            when q16_gender = '3' then 'Other'
                                        end as gender,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q16_gender is not null
                                    group by gender
                                    order by gender)

                                    select * from survey_gender""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        genderresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return genderresults


def race(qnum, args):
    # app.logger.debug(args)
    raceresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Race Distribution'
    where = buildconditions(args)
    results = db.session.execute("""with survey as (
                                    select *
                                        from fare_survey_2016_clean
                                        where willing = '1' and 
                                        q17_race is not null {0}),

                                    racepct as (
                                        select 
                                        case
                                            when q17_race = '1' then 'Asian/Pacific Islander'
                                            when q17_race = '2' then 'African American/Black'
                                            when q17_race = '3' then 'Caucasian/White'
                                            when q17_race = '4' then 'Hispanic/Latino'
                                            when q17_race = '5' then 'Native American Indian'
                                            when q17_race = '6' then 'Multi-racial/bi-racial'
                                            when q17_race = '7' then 'Other'
                                        end as race,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round(sum(weight_final)*100/(select sum(weight_final) from survey)::numeric,2) as pct
                                        from survey
                                        group by race
                                        order by race
                                        )

                                    select * from racepct""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        raceresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return raceresults


def disability(qnum, args):
    # app.logger.debug(args)
    disabilityresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Disability'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean
                                            where
                                                willing = '1' and
                                                q18_disability is not null {0}),
                                                
                                    survey_disability as (
                                    select 
                                        case 
                                            when q18_disability = '1' then 'Yes'
                                            when q18_disability = '2' then 'No'
                                        end as disability,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q18_disability is not null
                                    group by disability)

                                    select * from survey_disability""".format(where))

    for row in results:
        print(row[0],row[1],row[2])
        disabilityresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return disabilityresults


def transit(qnum,args):
    # app.logger.debug(args)
    transitresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Non-transit Options'
    where = buildconditions(args)
    results = db.session.execute("""with survey as (
                                    select *
                                        from fare_survey_2016_clean
                                        where willing = '1' and 
                                        q19_transit_options is not null {0}),

                                    transitall as (
                                            select 
                                                unnest(string_to_array(q19_transit_options,' ')) as transit, 
                                                round(sum(weight_final)::numeric,1) as count,
                                                round(sum(weight_final)*100/(select sum(weight_final) from survey)::numeric,2) as pct
                                                from survey
                                                group by transit
                                                order by transit
                                        ),

                                    transitpct as (
                                    select
                                        case
                                            when transit = '1' then 'Drive my own car, truck, van or motorcycle'
                                            when transit = '2' then 'Get rides from someone else'
                                            when transit = '3' then 'Walk'
                                            when transit = '4' then 'Bike'
                                            when transit = '5' then 'Use carshare services like Zipcar or Car2Go'
                                            when transit = '6' then 'Use ride hail services like taxi, Lyft or Uber '
                                            when transit = '7' then 'I would not be able to go where I need to go'
                                            when transit = '8' then 'Other'
                                        end as transit,
                                        count,
                                        pct
                                        from transitall
                                        order by transit)

                                    select * from transitpct""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        transitresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return transitresults


def vehicle(qnum,args):
    # app.logger.debug(args)
    vehicleresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Vehicle Availability'
    where = buildconditions(args)
    app.logger.debug(where)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q20_vehicle_available is not null {0}),
                                                
                                    survey_vehicle as (
                                    select 
                                        case 
                                            when q20_vehicle_available = '1' then 'Yes'
                                            when q20_vehicle_available = '2' then 'No'
                                        end as vehicle,
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q20_vehicle_available is not null
                                    group by vehicle
                                    order by count)

                                    select * from survey_vehicle""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        vehicleresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return vehicleresults

def house(qnum,args):
    # app.logger.debug(args)
    houseresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Household Size Count'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean 
                                            where
                                                willing = '1' and
                                                q21_house_count is not null {0}),
                                    housecount as (
                                            select q21_house_count::integer,
                                            round(sum(weight_final)::numeric,1) as count,
                                            round(100*sum(weight_final)/(select sum(weight_final) from survey)::numeric,2) as pct
                                            from survey
                                            group by q21_house_count::integer
                                            order by q21_house_count::integer)

                                    select * from housecount""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        houseresults.append([str(row[0]),float(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return houseresults


def vecount(qnum, args):
    vecountresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Working Vehicles Count'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean 
                                            where
                                                willing = '1' and
                                                q22_vehicle_count is not null {0}),

                                    vehiclecount as (
                                    select q22_vehicle_count::integer,
                                    round(sum(weight_final)::numeric,1) as count,
                                    round(100*sum(weight_final)/(select sum(weight_final) from survey)::numeric,2) as pct
                                    from survey
                                    group by q22_vehicle_count::integer
                                    order by q22_vehicle_count::integer)

                                    select * from vehiclecount""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        vecountresults.append([str(row[0]),float(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return vecountresults


def income(qnum,args):
    # app.logger.debug(args)
    incomeresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Income Distribution'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean 
                                            where
                                                willing = '1' and
                                                q23_income is not null and
                                                q23_income != '12' {}),
                                                
                                    survey_income as (
                                    select 
                                        case 
                                            when q23_income = '1' then 'Under $10,000'
                                            when q23_income = '2' then '$10,000 - $19,000'
                                            when q23_income = '3' then '$20,000 - $29,999'
                                            when q23_income = '4' then '$30,000 - $39,999'
                                            when q23_income = '5' then '$40,000 - $49,999'
                                            when q23_income = '6' then '$50,000 - $59,999'
                                            when q23_income = '7' then '$60,000 - $69,999'
                                            when q23_income = '8' then '$70,000 - $79,999'
                                            when q23_income = '9' then '$80,000 - $89,999'
                                            when q23_income = '10' then '$90,000 - $99,999'
                                            when q23_income = '11' then '$100,000 or more'
                                        end as income,
                                        round(sum(weight_final)::numeric,1) as count,
                                        round( sum(weight_final) * 100 / (
                                            select sum(weight_final)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    group by q23_income
                                    order by q23_income::integer)

                                    select * from survey_income""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        incomeresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return incomeresults


def poverty(qnum,args):
    # app.logger.debug(args)
    povertyresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius = .3, print_values=True)
    bar_chart.title = '150% Federal Poverty Level'
    where = buildconditions(args)
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016_clean 
                                            where
                                                willing = '1' and
                                                fpl_150 is not null {0}),

                                    fplcount as (
                                        select
                                            case
                                                when fpl_150 = '0' then 'Above 150% poverty level'
                                                when fpl_150 = '1' then 'At or below 150% poverty level'
                                            end as povertylevel,
                                            round(sum(weight_final)::numeric,1) as count,
                                            round(100*sum(weight_final)/(select sum(weight_final) from survey)::numeric,2) as pct
                                        from survey
                                        group by fpl_150
                                        order by fpl_150::integer)

                                    select * from fplcount""".format(where))
                
    for row in results:
        print(row[0],row[1],row[2])
        povertyresults.append([row[0],float(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return povertyresults

def buildconditions(args):
    where = ""
    lookupwd = {
    "Weekday": "(1,2,3,4,5)",
    "Weekend": "(0,6)",
    "Saturday": "(6)",
    "Sunday": "(0)"
    }

    lookupvehicle = {
    "MAX": "IN ('90','100','190','200','290')",
    "WES": "IN ('203')",
    "Bus": "NOT IN ('90','100','190','200','290','203')"
    }

    lookuprtetype = {
    "MAX": "1",
    "Bus Crosstown": "2",
    "Bus Eastside Feeder": "3",
    "Bus Westside Feeder": "4",
    "Bus Radial": "5",
    "WES": "6"
    }

    lookuptod = {
    "Weekday Early AM": "1",
    "Weekday AM Peak": "2",
    "Weekday Midday": "3",
    "Weekday PM Peak": "4",
    "Weekday Night": "5",
    "Weekend Morning": "6",
    "Weekend Midday": "7",
    "Weekend Night": "8"
    }

    lookupfpl = {
    "Above 150% FPL": "0",
    "Below 150% FPL": "1"
    }

    for key, value in args.items():
        # app.logger.debug(key,value)
        if key == "qnum" or not value: continue

        if key == "vehicle" and value in lookupvehicle:
            where += " AND rte {0}".format(lookupvehicle[value])

        if key == "rtetype" and value in lookuprtetype:
            where += " AND rte_type='{0}'".format(lookuprtetype[value])

        if key == "day" and value in lookupwd:
            where += " AND extract(dow from _date) in {0}".format(lookupwd[value])

        if key == "tod" and value in lookuptod:
            where += " AND time_of_day='{0}'".format(lookuptod[value])

        if key == "fpl" and value in lookupfpl:
            where += " AND fpl_150='{0}'".format(lookupfpl[value])

        if key == "rte" and value.isnumeric():
            where += " AND rte='{0}'".format(value)


    # app.logger.debug(where)
    return where
