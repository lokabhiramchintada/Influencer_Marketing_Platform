from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(80), nullable=False)  # 'influencer' or 'sponsor'

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

class Influencer(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    platform_presence = db.Column(db.String(200), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'influencer',
    }
    
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    niche = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    budget = db.Column(db.Float, nullable=True)
    visibility = db.Column(db.String(10), nullable=False, default='public') 
    sponsor = db.relationship('Sponsor', backref='campaigns') 


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=True) 
    ad_name = db.Column(db.String(100), nullable=False)
    ad_description = db.Column(db.Text, nullable=False)
    ad_terms = db.Column(db.Text, nullable=False)
    payment = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending') 
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sponsor = db.relationship('Sponsor', backref=db.backref('ad_requests', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('ad_requests', lazy=True))
    campaign = db.relationship('Campaign', backref=db.backref('ad_requests', lazy=True))

class Sponsor(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    industry = db.Column(db.String(100), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'sponsor',
    }
    active_campaigns = db.relationship(
        'Campaign',
        secondary='ad_request',
        primaryjoin=(AdRequest.sponsor_id == id),
        secondaryjoin=(AdRequest.campaign_id == Campaign.id),
        lazy='dynamic',
        viewonly=True, 
        backref=db.backref('active_sponsors', lazy=True)
    )