# Copyright (C) 2016 Jeffrey Meyers, Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.

from flask import render_template,request,jsonify
from sqlalchemy.orm import sessionmaker,scoped_session 
from dashboard import app,db
from dashboard.models import Sroutes,Scount,Surveyors,Surveywkd, Survey
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey, cast, Numeric
from sqlalchemy.sql import func
import pygal
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
    line_chart = pygal.HorizontalBar(print_values=True, width=800, height=600, disable_xml_declaration=True)
    line_chart.title = 'Completed Surveys for Route %s' % (rte)
    
    for row in Sroutes.query.filter_by(rte=rte).order_by(Sroutes.pct_rte.desc()).all():
        srresults.append([row.surveyors.name,row.rte,row.num_surveys,float(row.pct_rte),float(row.pct)])
        line_chart.add(row.surveyors.name,row.num_surveys)

    line_chart.render_to_file(os.path.join(DIRPATH, "static\\image\\{0}.svg".format(rte)))
    
    
    
    return jsonify(data=srresults)


@app.route('/userdata')
def userdata():
    userresults = []
    rte = request.args.get('rte')
    """subq = db.session.query(func.sum(Sroutes.num_surveys).label('sumall')).\
        select_from(Sroutes).scalar()
    app.logger.debug(subq)
    qry_pct = db.session.query(Sroutes.surveyor,
                func.sum(Sroutes.num_surveys).label('Count'),
                (cast(100*func.sum(Sroutes.num_surveys), Float) / subq).label('surveyor_pct')).\
                group_by(Sroutes.surveyor).order_by((cast(100*func.sum(Sroutes.num_surveys), Float) / subq).desc()).all()

    for row in qry_pct:
        userresults.append([row.surveyor,int(row.Count),round(row.surveyor_pct,2)])"""

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
    
    pie_chart.render_to_file(os.path.join(DIRPATH, "static\\image\\{0}.svg".format(rte)))
    
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
    pie_chart.render_to_file(os.path.join(DIRPATH, "static\\image\\{0}.svg".format(rte)))
    
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
    bar_chart.render_to_file(os.path.join(DIRPATH, "static\\image\\{0}.svg".format(rte)))

    return jsonify(data=wkresults)


@app.route('/fareresults')
def fareresults():
    # return dropdown list dynamically
    #build a question list key value dropdown

    questions = [("Transfer Rate","1"),("Fare Agency","2")]
    srresults = []
        
    return render_template("fareresults.html",questions = questions)


@app.route('/transferdata')
def transferdata():
    transferresults = []
    rte = request.args.get('rte')
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
        
    return jsonify(data=transferresults)


@app.route('/faretype')
def faretype():
    fareresults = []
    rte = request.args.get('rte')
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
    
    return jsonify(data = fareresults)
    
    
def purtype():
    fareresults = []
    rte = request.args.get('rte')
    results = db.session.execute("""""")