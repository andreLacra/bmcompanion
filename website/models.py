from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import json


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_data = db.Column(db.db.String(255))
    business_name = db.Column(db.String(100))
    organization = db.Column(db.String(100), nullable=True)
    business_email = db.Column(db.String(150), unique=True)
    business_address = db.Column(db.String(300))
    business_phone = db.Column(db.String(80))
    viber = db.Column(db.String(80))
    whatsapp = db.Column(db.String(80))
    linkedin_link = db.Column(db.String(80), nullable=True)
    youtube_link = db.Column(db.String(80), nullable=True)
    fb_link = db.Column(db.String(80), nullable=True)
    twitter_link = db.Column(db.String(80), nullable=True)
    business_desc = db.Column(db.String(2000))
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seeking = db.relationship('Seeking', back_populates='company')
    offering = db.relationship('Offering', back_populates='company')


class Seeking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100))
    category = db.Column(db.String(80))
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship('Company', back_populates='seeking')

class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100))
    category = db.Column(db.String(80))
    qualifier = db.Column(db.String(400), nullable=True)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship('Company', back_populates='offering')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    companies = db.relationship('Company')


# MATCHINGS 
class Matched(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    matched_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=1)
    date = db.Column(db.Date(), default=func.now())

class MatchRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')

class Unmatched(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    matched_id = db.Column(db.Integer,  nullable=False)
    umatched_date = db.Column(db.Date(), default=func.now())

# MESSAGES
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matched_id = db.Column(db.Integer, db.ForeignKey('matched.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime(timezone=True), default=func.now())

class BackupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matched_id = db.Column(db.Integer, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime(timezone=True))




# MEETING
class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    link = db.Column(db.String(400), nullable=False)
    details = db.Column(db.String(2000), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
