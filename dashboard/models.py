# Copyright (C) 2016 Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


from sqlalchemy import Integer, Numeric, SmallInteger, Text, String
from sqlalchemy import DateTime, Boolean, create_engine
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from dashboard import db



"""
Database Models
"""

class Sroutes(db.Model):
    __tablename__ = "sroutes"
    id = Column(Integer, primary_key = True)
    surveyor = Column(Text, ForeignKey("surveyors.surveyor"))
    surveyors = relationship("Surveyors", foreign_keys=surveyor)
    rte = Column(Text)
    num_surveys = Column(Integer)
    pct_rte = Column(Numeric)
    pct = Column(Numeric)


    def __init__(self, surveyor, rte, num_surveys, pct_rte, pct):
        self.surveyor = surveyor
        self.rte = rte
        self.num_surveys = num_surveys
        self.pct_rte = pct_rte
        self.pct = pct

    def __repr__(self):
        return '<Surveyor: %r Route: %r Num_sur:%r >' %\
            (self.surveyor, self.rte, self.num_surveys)

class Surveyors(db.Model):
    __tablename__ = "surveyors"
    id = Column(Integer, primary_key = True)
    surveyor = Column(Text)
    name = Column(Text)


    def __init__(self, surveyor, name):
        self.surveyor = surveyor
        self.name = name


    def __repr__(self):
        return '<Surveyor: %r >' %\
            (self.name)

class Scount(db.Model):
    __tablename__ = 'scount'
    id = Column(Integer, primary_key = True)
    surveyor = Column(Text)
    willing = Column(Text)
    count = Column(Integer)
    pct_surveyor = Column(Numeric)
    pct = Column(Numeric)
    

    def __init__(self, surveyor, willing, count, pct_surveyor, pct):
        self.surveyor = surveyor
        self.willing = willing
        self.count = count
        self.pct_surveyor = surveyor
        self.pct = pct
        

    def __repr__(self):
        return '<Surveyor: %r willing: %r count: %r >' %\
            (self.surveyor, self.willing, self.count)

class Surveywkd(db.Model):
    __tablename__ = 'surveywkd'
    id = Column(Integer, primary_key = True)
    dow = Column(Text)
    count = Column(Integer)
    
    def __init__(self, dow, count):
        self.dow = dow
        self.count = count
    
    
    def __repr__(self):
        return '<dow: %r count: %r >' %\
            (self.dow, self.count)


class Survey(db.Model):
    __tablename__ = 'fare_survey_2016'
    id = Column(Integer, primary_key = True)
    _uri = Column(Text)
    _surveyor = Column(Text)
    _device = Column(Text)
    _phone = Column(Text)
    _date = Column(DateTime)
    _complete = Column(Boolean)
    _startdate = Column(DateTime)
    _start = Column(DateTime)
    _enddate = Column(DateTime)
    _end = Column(DateTime)
    willing = Column(Text)
    rte = Column(Text)
    dir = Column(Text)
    language = Column(Text)
    other_language = Column(Text)
    english_prof = Column(Text)
    q1_transfer = Column(Text)
    q2_transfer_routes = Column(Text)
    q3_trip_count = Column(Integer)
    q4_fare_agency = Column(Text)
    q5_fare_type = Column(Text)
    q5_fare_type_other = Column(Text)
    q6_purchase_type = Column(Text)
    q7_day_fare = Column(Text)
    q8_single_fare = Column(Text)
    q9_purchase_loc = Column(Text)
    q9_purchase_loc_other = Column(Text)
    q10_purchase_types = Column(Text)
    q11_college = Column(Text)
    q12_college_attend = Column(Text)
    q12_college_attend_other = Column(Text)
    q13_smartphone = Column(Text)
    q14_internet = Column(Text)
    q15_age = Column(Text)
    q16_gender = Column(Text)
    q17_race = Column(Text)
    q17_race_other = Column(Text)
    q18_disability = Column(Text)
    q19_transit_options = Column(Text)
    q19_transit_options_other = Column(Text)
    q20_vehicle_available = Column(Text)
    q21_house_count = Column(Text)
    q22_vehicle_count = Column(Text)
    q23_income = Column(Text)
    q24_english_prof = Column(Text)


    def __init__(self, _version, _uri, _surveyor, _device, _phone, _date, _complete, _startdate, _start, _enddate, _end,
                 willing, rte, dir, language, other_language, english_prof, q1_transfer, q2_transfer_routes, q3_trip_count,
                 q4_fare_agency, q5_fare_type, q5_fare_type_other, q6_purchase_type, q7_day_fare, q8_single_fare, q9_purchase_loc,
                 q10_purchase_types, q11_college, q12_college_attend, q12_college_attend_other, q13_smartphone, q14_internet,
                 q15_age, q16_gender, q17_race, q17_race_other, q18_disability, q19_transit_options, q19_transit_options_other,
                 q20_vehicle_available, q21_house_count, q22_vehicle_count, q23_income, q24_english_prof):
        self._version = _version
        self._uri = _uri
        self._surveyor = _surveyor
        self._device = _device
        self._phone = _phone
        self._date = _date
        self._complete = _complete
        self._startdate = _startdate
        self._start = _start
        self._enddate = _enddate
        self._end = _end
        self.willing = willing
        self.rte = rte
        self.dir = dir
        self.language = language
        self.other_language = other_language
        self.english_prof = english_prof
        self.q1_transfer = q1_transfer
        self.q2_transfer_routes = q2_transfer_routes
        self.q3_trip_count = q3_trip_count
        self.q4_fare_agency = q4_fare_agency
        self.q5_fare_type = q5_fare_type
        self.q5_fare_type_other = q5_fare_type_other
        self.q6_purchase_type = q6_purchase_type
        self.q7_day_fare = q7_day_fare
        self.q8_single_fare =q8_single_fare
        self.q9_purchase_loc = q9_purchase_loc
        self.q9_purchase_loc_other = q9_purchase_loc_other
        self.q10_purchase_types = q10_purchase_types
        self.q11_college = q11_college
        self.q12_college_attend = q12_college_attend
        self.q12_college_attend_other = q12_college_attend_other
        self.q13_smartphone = q13_smartphone
        self.q14_internet = q14_internet
        self.q15_age = q15_age
        self.q16_gender = q16_gender
        self.q17_race = q17_race
        self.q17_race_other = q17_race_other
        self.q18_disability = q18_disability
        self.q19_transit_options = q19_transit_options
        self.q20_vehicle_available = q20_vehicle_available
        self.q21_house_count = q21_house_count
        self.q22_vehicle_count = q22_vehicle_count
        self.q23_income = q23_income
        self.q24_english_prof = q24_english_prof
