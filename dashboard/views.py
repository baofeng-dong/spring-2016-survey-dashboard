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
from .metadata import metadata

DIRPATH = os.path.dirname(os.path.realpath(__file__))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/introduction')
def intro():
    return render_template("introduction.html")

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

@app.route('/questionsdata')
def questionsdata():
    qnum = int(request.args.get('qnum'))
    data = None
    if qnum == 1:
        data = transferdata(qnum)

    if qnum == 2:
        data = tripdata(qnum)

    if qnum == 3:
        data = agencydata(qnum)

    if qnum == 4:
        data = faretype(qnum)

    if qnum == 5:
        data = purchasetype(qnum)

    if qnum == 6:
        data = daypass(qnum)

    if qnum == 7:
        data = singlefare(qnum)
    if qnum == 8:
        data = purloc(qnum)
    if qnum == 9:
        data = payment(qnum)
    if qnum == 10:
        data = college(qnum)
    if qnum == 11:
        data = collegeattend(qnum)
    if qnum == 12:
        data = smartphone(qnum)
    if qnum == 13:
        data = internet(qnum)
    if qnum == 14:
        data = age(qnum)
    if qnum == 15:
        data = gender(qnum)
    if qnum == 16:
        data = race(qnum)
    if qnum == 17:
        data = disability(qnum)
    if qnum == 18:
        data = transit(qnum)
    if qnum == 19:
        data = vehicle(qnum)
    if qnum == 20:
        data = house(qnum)

    return jsonify(data=data, metadata=metadata[qnum])



#@app.route('/transferdata')
def transferdata(qnum):
    transferresults = []
    labels = []
    
    bar_chart = pygal.Bar(print_values=True)
    
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
    #return jsonify(data=transferresults)
    return transferresults


#@app.route('/tripdata')
def tripdata(qnum):
    tripresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
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

    #return jsonify(data=tripresults)
    return tripresults

#@app.route('/agencydata')
def agencydata(qnum):
    agencyresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
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

    #return jsonify(data=agencyresults)
    return agencyresults


#@app.route('/faretype')
def faretype(qnum):
    fareresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
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
    
    #return jsonify(data = fareresults)
    return fareresults
    
#@app.route('/purchasetype')
def purchasetype(qnum):
    purchaseresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
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
    
    #return jsonify(data = purchaseresults)
    return purchaseresults

#@app.route('/daypass')
def daypass(qnum):
    daypassresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
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
    
    #return jsonify(data = daypassresults)
    return daypassresults

#@app.route('/singlefaretrip')
def singlefare(qnum):
    singlefareresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Number of One-way/Round Trips on a Single Fare'
    results = db.session.execute("""select case
                                        when q8_single_fare= '1' then 'One-way trip'
                                        when q8_single_fare='2' then 'Round-trip'
                                        end as q8_single_fare,
                                        count(*) as count,
                                        round(100*count(*)/(select count(*) from fare_survey_2016
                                        where willing = '1' and q8_single_fare is not null)::numeric,2) as pct
                                        from fare_survey_2016
                                        where willing = '1' and q8_single_fare is not null
                                        group by q8_single_fare
                                        order by q8_single_fare""")
                
    for row in results:
        print(row[0],row[1],row[2])
        singlefareresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return singlefareresults


def purloc(qnum):
    locationresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.HorizontalBar(print_values=True)
    bar_chart.title = 'Fare Purchase Location'
    results = db.session.execute("""WITH survey as (
                        select *
                                from fare_survey_2016 
                                where
                                    willing = '1' and
                                    q9_purchase_loc is not null),
                                
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
                            count(*) as count,
                            round( count(*) * 100 / (
                                select count(*)
                                from survey)::numeric,2) as pct
                        from survey
                        group by q9_purchase_loc
                        order by count desc)

                        select * from purchase_location""")
                
    for row in results:
        print(row[0],row[1],row[2])
        locationresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],int(row[1]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return locationresults


def payment(qnum):
    paymentresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'All Purchases Payment Options'
    results = db.session.execute("""with survey as (
                                    select unnest(string_to_array(q10_purchase_types, ' ')) as payment 
                                        from fare_survey_2016
                                        where willing = '1' and 
                                        q10_purchase_types is not null),

                                    paymentall as (
                                            select 
                                                unnest(string_to_array(q10_purchase_types,' ')) as payment, 
                                                count(*) as count,
                                                round(count(*)*100/(select count(*) from survey)::numeric,2) as pct
                                                from fare_survey_2016
                                                where willing = '1' and 
                                                q10_purchase_types is not null
                                                group by payment
                                                order by payment
                                        ),

                                    paymentpct as (
                                    select
                                        case
                                            when payment = '1' then 'Cash'
                                            when payment = '2' then 'Checking or saving account'
                                            when payment = '3' then 'Bank issued debit or credit card'
                                            when payment = '4' then 'Pre-paid debit or credit card'
                                            when payment = '5' then 'Pre-paid gift card'
                                            when payment = '6' then 'Money order or cashiers check'
                                            when payment = '7' then 'Smartphone payment apps'
                                        end as payment,
                                        count,
                                        pct
                                        from paymentall
                                        order by count desc)

                                    select * from paymentpct""")
                
    for row in results:
        print(row[0],row[1],row[2])
        paymentresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return paymentresults


def college(qnum):
    collegeresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Percentages of College Students'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q11_college is not null),
                                            
                                    survey_college as (
                                    select
                                        case 
                                            when q11_college = '1' then 'No'
                                            when q11_college = '2' then 'Yes part time'
                                            when q11_college = '3' then 'Yes full time'
                                        end as college,
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q11_college is not null
                                    group by q11_college)  

                                    select * from survey_college""")
                
    for row in results:
        print(row[0],row[1],row[2])
        collegeresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return collegeresults


def collegeattend(qnum):
    attendresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Colleges Attended'
    results = db.session.execute("""with survey as (
                                    select unnest(string_to_array(q12_college_attend, ' ')) as college 
                                        from fare_survey_2016
                                        where willing = '1' and 
                                        q12_college_attend is not null and
                                        q11_college in ('2','3') ),

                                    collegeall as (
                                            select 
                                                unnest(string_to_array(q12_college_attend,' ')) as college, 
                                                count(*) as count,
                                                round(count(*)*100/(select count(*) from survey)::numeric,2) as pct
                                                from fare_survey_2016
                                                where willing = '1' and 
                                                q11_college in ('2','3')
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

                                    select * from collegepct""")
                
    for row in results:
        print(row[0],row[1],row[2])
        attendresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return attendresults


def smartphone(qnum):
    smartphoneresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Smartphones'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q13_smartphone is not null),
                                            
                                    smart_phone as (
                                    select
                                        case 
                                            when q13_smartphone = '1' then 'Yes'
                                            when q13_smartphone = '2' then 'No'
                                            when q13_smartphone = '3' then 'Do not know'
                                        end as smartphone,
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q13_smartphone is not null
                                    group by q13_smartphone
                                    order by count desc)  

                                    select * from smart_phone""")
                
    for row in results:
        print(row[0],row[1],row[2])
        smartphoneresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return smartphoneresults


def internet(qnum):
    internetresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Access to Internet'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q14_internet is not null),
                                            
                                    internet as (
                                    select
                                        case 
                                            when q14_internet = '1' then 'Yes'
                                            when q14_internet = '2' then 'No'
                                            when q14_internet = '3' then 'Don not know'
                                        end as smartphone,
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    group by q14_internet
                                    order by count desc)

                                    select * from internet""")
                
    for row in results:
        print(row[0],row[1],row[2])
        internetresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return internetresults


def age(qnum):
    ageresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Age Distribution'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q15_age is not null),
                                                
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
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q15_age is not null
                                    group by age
                                    order by age)

                                    select * from survey_age""")
                
    for row in results:
        print(row[0],row[1],row[2])
        ageresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return ageresults


def gender(qnum):
    genderresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Gender Distribution'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q16_gender is not null),
                                                
                                    survey_gender as (
                                    select 
                                        case 
                                            when q16_gender = '1' then 'Female'
                                            when q16_gender = '2' then 'Male'
                                            when q16_gender = '3' then 'Other'
                                        end as gender,
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q16_gender is not null
                                    group by gender
                                    order by gender)

                                    select * from survey_gender""")
                
    for row in results:
        print(row[0],row[1],row[2])
        genderresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return genderresults


def race(qnum):
    raceresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Race Distribution'
    results = db.session.execute("""with survey as (
                                    select unnest(string_to_array(q17_race, ' ')) as race 
                                        from fare_survey_2016
                                        where willing = '1' and 
                                        q17_race is not null),

                                    raceall as (
                                            select 
                                                unnest(string_to_array(q17_race,' ')) as race, 
                                                count(*) as count,
                                                round(count(*)*100/(select count(*) from survey)::numeric,2) as pct
                                                from fare_survey_2016
                                                where willing = '1' and 
                                                q17_race is not null
                                                group by race
                                                order by race
                                        ),

                                    racepct as (
                                    select
                                        case
                                            when race = '1' then 'Asian/Pacific Islander'
                                            when race = '2' then 'African American/Black'
                                            when race = '3' then 'Caucasian/White'
                                            when race = '4' then 'Hispanic/Latino'
                                            when race = '5' then 'Native American Indian'
                                            when race = '6' then 'Multi-racial/bi-racial'
                                            when race = '7' then 'Other'
                                        end as race,
                                        count,
                                        pct
                                        from raceall
                                        order by race)

                                    select * from racepct""")
                
    for row in results:
        print(row[0],row[1],row[2])
        raceresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return raceresults


def disability(qnum):
    disabilityresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Disability'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q18_disability is not null),
                                                
                                    survey_disability as (
                                    select 
                                        case 
                                            when q18_disability = '1' then 'Yes'
                                            when q18_disability = '2' then 'No'
                                        end as disability,
                                        count(*) as count,
                                        round( count(*) * 100 / (
                                            select count(*)
                                            from survey)::numeric,2) as pct
                                    from survey
                                    where q18_disability is not null
                                    group by disability)

                                    select * from survey_disability""")
                
    for row in results:
        print(row[0],row[1],row[2])
        disabilityresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return disabilityresults


def transit(qnum):
    transitresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Non-transit Options'
    results = db.session.execute("""with survey as (
                                    select unnest(string_to_array(q19_transit_options, ' ')) as transit
                                        from fare_survey_2016
                                        where willing = '1' and 
                                        q19_transit_options is not null),

                                    transitall as (
                                            select 
                                                unnest(string_to_array(q19_transit_options,' ')) as transit, 
                                                count(*) as count,
                                                round(count(*)*100/(select count(*) from survey)::numeric,2) as pct
                                                from fare_survey_2016
                                                where willing = '1' and 
                                                q19_transit_options is not null
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
                                        order by count desc)

                                    select * from transitpct""")
                
    for row in results:
        print(row[0],row[1],row[2])
        transitresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return transitresults


def vehicle(qnum):
    vehicleresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Pie(inner_radius=.3, disable_xml_declaration=True,print_values=True)
    bar_chart.title = 'Vehicle Availability'
    results = db.session.execute("""WITH survey as (
                                    select *
                                            from fare_survey_2016 
                                            where
                                                willing = '1' and
                                                q20_vehicle_available is not null),
                                                
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

                                    select * from survey_vehicle""")
                
    for row in results:
        print(row[0],row[1],row[2])
        vehicleresults.append([row[0],int(row[1]),float(row[2])])
        bar_chart.add(row[0],float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return vehicleresults

def house(qnum):
    houseresults = []
    #qnum = request.args.get('qnum')
    bar_chart = pygal.Bar(print_values=True)
    bar_chart.title = 'Household Size Count'
    results = db.session.execute("""select q21_house_count::integer,
                                    count(*) as count,
                                    round(100*count(*)/(select count(*) from fare_survey_2016
                                    where willing = '1' and q21_house_count is not null)::numeric,2) as pct
                                    from fare_survey_2016
                                    where willing = '1' and q21_house_count is not null
                                    group by q21_house_count::integer
                                    order by q21_house_count::integer""")
                
    for row in results:
        print(row[0],row[1],row[2])
        houseresults.append([str(row[0]),int(row[1]),float(row[2])])
        bar_chart.add(str(row[0]),float(row[2]))
    
    bar_chart.render_to_file(os.path.join(DIRPATH, "static/image/{0}{1}.svg".format('q', qnum)))
    
    #return jsonify(data = singlefareresults)
    return houseresults