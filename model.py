from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    platform = db.Column(db.String(10), nullable=False)
    reach = db.Column(db.String(50), nullable=True)  # Existing column
    niche = db.Column(db.String(50), nullable=True)   # Added column for niche
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)
    flagged = db.Column(db.Boolean, default=False, nullable=False)


class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    industry = db.Column(db.String(20), nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    flagged = db.Column(db.Boolean, default=False, nullable=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime(timezone=True))
    budget = db.Column(db.Float, nullable=False)
    goals = db.Column(db.Text, nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    progress_bar = db.Column(db.Integer, default=0, nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_username = db.Column(db.String(255), db.ForeignKey('influencer.username'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')
    progression_status = db.Column(db.String(20), default='Pending', nullable=False)

class CampaignRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_username = db.Column(db.String(100), nullable=False)
    request_status = db.Column(db.String(10), nullable=False, default='Pending')
    campaign = db.relationship('Campaign', backref=db.backref('campaign_requests', lazy=True))






