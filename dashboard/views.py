# Copyright (C) 2016 Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from flask import render_template,request,jsonify,url_for
from sqlalchemy.orm import sessionmaker,scoped_session 
from dashboard import app,db
from dashboard.models import Sroutes,Scount,Surveyors,Surveywkd, Survey
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey, cast, Numeric
from sqlalchemy.sql import func
import pygal
from pygal.style import DarkSolarizedStyle
from pygal.style import LightStyle
from pygal.style import CleanStyle
from pygal.style import DarkStyle
import codecs
import json
import base64
import os,sys
import time
from datetime import datetime

DIRPATH = os.path.dirname(os.path.realpath(__file__))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sroutes')
def sroutes():
    # return routes list dynamically
    app.logger.debug(url_for('index'))
    routes = db.session.execute(""" 
        select rte,rte_desc
        from rtedesc_lookup""")

    routes = [(route[0],route[1]) for route in routes]
    
    srresults = []
        
    return render_template("sroutes.html", routes = routes)
    
@app.route('/srdata')
def srdata():
    srresults = []
    rte = request.args.get('rte')
    line_chart = pygal.HorizontalBar(print_values=True, width=800, height=600, disable_xml_declaration=True, style=CleanStyle)
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

    pie_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True, style=CleanStyle)
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
    pie_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True, style=CleanStyle)
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
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
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


@app.route('/fareresults')
def fareresults():
    # return dropdown list dynamically
    #build a question list key value dropdown

    query = db.session.execute("""
                select num, questions
                from ques_lookup""")
    
    questions = []
    for question in query:
        questions.append([question[0],question[1]])


    return render_template("fareresults.html",questions=questions)


@app.route('/transferdata')
def transferdata():
    transferresults = []
    labels = []
    qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
    
    bar_chart.title = 'Number of Transfers in One Trip'
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016 
                    where
                        willing = '1' and
                        q23_income is not null and
                        language in ('1','2') and 
                        rte is not null
                    and rte != ''),
                    
            survey_tran as (
            select 
                case
                    when q1_transfer = '1' then 'No'
                    when q1_transfer = '2' then 'Transfer 1 time'
                    when q1_transfer = '3' then 'Transfer 2 times'
                    when q1_transfer = '4' then 'Transfer 3 or more'
                end as Transfer,
                count(*) as count,
                round( count(*) * 100 / (
                    select count(*)
                    from survey)::numeric,2) as pct
            from survey
            group by q1_transfer
            order by q1_transfer::integer)

            select * from survey_tran""")
    for row in results:
        print(row[0],row[1],row[2])
        transferresults.append([row[0],int(row[1]),float(row[2])])
        labels.append(row[0])
        bar_chart.add(row[0],[{'value':int(row[1])}])
    #bar_chart.x_labels = labels
    for label in labels:
        print(label)
    #bar_chart.x_labels = "No","Transfer 1 time", "Transfer 2 times", "Transfer 3 or more"
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    return jsonify(data=transferresults)


@app.route('/tripdata')
def tripdata():
    tripresults = []
    qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
    bar_chart.title = 'Number of Trips by Range in a Week'
    results = db.session.execute("""
            select 10 * s.d as trange, count(f.q3_trip_count) as count,
            round(count(f.q3_trip_count)*100/(select count (*) as sum from fare_survey_2016 where willing = '1' and 
            q3_trip_count is not null)::numeric,2) as pct
            from generate_series(0, 7) s(d)
            left outer join fare_survey_2016 f on s.d = floor(f.q3_trip_count / 10)
            where f.willing = '1' and f.q3_trip_count is not null
            group by s.d
            order by s.d""")
    for row in results:
        print(row[0],row[1],row[2])
        tripresults.append([str(row[0]),int(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))

    return jsonify(data=tripresults)


@app.route('/agencydata')
def agencydata():
    agencyresults = []
    qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
    bar_chart.title = 'Number of Faretypes by Agency'
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016 
                    where
                        willing = '1' and
                        q4_fare_agency is not null),
                    
            fare_agency as (
            select
                case 
                    when q4_fare_agency = '1' then 'TriMet'
                    when q4_fare_agency = '2' then 'C-TRAN fare'
                    when q4_fare_agency = '3' then 'Streetcar fare'
                end as Fareagency,
                count(*) as count,
                round( count(*) * 100 / (
                    select count(*)
                    from survey)::numeric,2) as pct
            from survey
            where q4_fare_agency is not null
            group by q4_fare_agency
            order by q4_fare_agency::integer)

            select * from fare_agency""")
    for row in results:
        print(row[0],row[1],row[2])
        agencyresults.append([str(row[0]),int(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))

    return jsonify(data=agencyresults)


@app.route('/faretype')
def faretype():
    fareresults = []
    qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
    bar_chart.title = 'Number of Fares by Faretypes'
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016 
                    where
                        willing = '1' and
                        language in ('1','2') and 
                        rte is not null),
                    
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
                count(*) as count,
                round( count(*) * 100 / (
                    select count(*)
                    from survey)::numeric,2) as pct
            from survey
            where q5_fare_type is not null
            group by q5_fare_type
            order by q5_fare_type::integer)

            select * from fare_type""")
            
    for row in results:
        print(row[0],row[1],row[2])
        fareresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    return jsonify(data = fareresults)
    
    
@app.route('/purchasetype')
def purchasetype():
    purchaseresults = []
    qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
    bar_chart.title = 'Number of Fares by Purchase Types'
    results = db.session.execute("""
            WITH survey as (
            select *
                    from fare_survey_2016 
                    where
                        willing = '1' and 
                        q6_purchase_type is not null and
                        q6_purchase_type != ''),
                    
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
                count(*) as count,
                round( count(*) * 100 / (
                    select count(*)
                    from survey)::numeric,2) as pct
            from survey
            where q6_purchase_type is not null
            group by q6_purchase_type
            order by count)

            select * from purchase_type""")
            
    for row in results:
        print(row[0],row[1],row[2])
        purchaseresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    return jsonify(data = purchaseresults)


@app.route('/daypass')
def daypass():
    daypassresults = []
    qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True, style=CleanStyle)
    bar_chart.title = 'Number of One-way Trips on a Day Pass'
    results = db.session.execute("""select q7_day_fare::integer,
            count(*) as count,
            round(100*count(*)/(select count(*) from fare_survey_2016
            where willing = '1' and q7_day_fare is not null)::numeric,2) as pct
            from fare_survey_2016
            where willing = '1' and q7_day_fare is not null
            group by q7_day_fare::integer
            order by q7_day_fare::integer""")
            
    for row in results:
        print(row[0],row[1],row[2])
        daypassresults.append([str(row[0]),int(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    return jsonify(data = daypassresults)


