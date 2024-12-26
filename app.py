from flask import Flask, render_template, request, redirect, url_for, flash
from model import db, Influencer, Sponsor, Campaign, AdRequest, CampaignRequest
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db1.sqlite3'
app.config['SECRET_KEY'] = 'MY_SECRET_KEY'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')



@app.route("/influencer_signup", methods=['GET', 'POST'])
def influencer_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        platform = request.form['platform']
        reach = request.form['reach']
        niche = request.form['niche']
        
        new_user = Influencer(
            username=username, 
            password=password, 
            role="Influencer", 
            platform=platform, 
            reach=reach, 
            niche=niche
        )
        
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template("influencer_signup.html")


@app.route("/sponsor_signup", methods=['GET', 'POST'])
def sponsor_signup():
  if request.method== 'POST':
      username = request.form['username']
      password = request.form['password']
      industry = request.form['industry']
      new_user = Sponsor(username=username, password=password, role = "Sponsor",industry=industry)
      db.session.add(new_user)
      db.session.commit()
      flash('Signup successful! Please login.', 'success')
      return redirect(url_for('login'))

  return render_template("sponsor_signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Influencer.query.filter_by(username=username).first()
        user1 = Sponsor.query.filter_by(username=username).first()
        if username == 'admin' and password == 'password123':
            return redirect(url_for('admin_dashboard'))
        if user and user.password == password:
            return redirect(f"/{username}/influencer_dashboard")
        elif user1 and user1.password == password:
            return redirect(f"/{username}/sponsor_dashboard")
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin', methods=['GET'])
def admin_dashboard():
    campaigns = Campaign.query.all()
    flagged_influencers = Influencer.query.filter_by(flagged=True).all()
    flagged_sponsors = Sponsor.query.filter_by(flagged=True).all()
    flagged_campaigns = Campaign.query.filter_by(flagged=True).all()

    return render_template('admin.html', campaigns=campaigns, 
                           flagged_influencers=flagged_influencers, 
                           flagged_sponsors=flagged_sponsors, 
                           flagged_campaigns=flagged_campaigns)


@app.route('/remove_flag/<entity_id>/<entity_type>', methods=['POST', 'GET'])
def remove_flag(entity_id, entity_type):
    if entity_type == 'influencer':
        entity = Influencer.query.get(entity_id)
    elif entity_type == 'sponsor':
        entity = Sponsor.query.get(entity_id)
    elif entity_type == 'campaign':
        entity = Campaign.query.get(entity_id)

    if entity:
        entity.flagged = False
        db.session.commit()

    return redirect(url_for('admin_dashboard'))


@app.route('/find', methods=['GET', 'POST'])
def find():
    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()
    campaigns = Campaign.query.all()
    
    return render_template('find.html', influencers=influencers, sponsors=sponsors, campaigns=campaigns)

@app.route('/flag_user/<user_type>/<int:user_id>', methods=['POST'])
def flag_user(user_type, user_id):
    user = None
    
    if user_type == 'influencer':
        user = Influencer.query.get(user_id)
    elif user_type == 'sponsor':
        user = Sponsor.query.get(user_id)
    elif user_type == 'campaign':
        user = Campaign.query.get(user_id)
    else:
        flash('Invalid user type.', 'error')
        return redirect(url_for('find'))

    if user:
        user.flagged = True
        db.session.commit()
        flash(f'{user_type.capitalize()} flagged successfully.', 'success')
    else:
        flash(f'{user_type.capitalize()} not found.', 'error')

    return redirect(url_for('find'))


@app.route('/stats')
def stats():
    
    num_campaigns = Campaign.query.count()
    num_influencers = Influencer.query.count()
    num_sponsors = Sponsor.query.count()

   
    return render_template('stats.html',
                           num_campaigns=num_campaigns,
                           num_influencers=num_influencers,
                           num_sponsors=num_sponsors)


@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route('/<string:username>/influencer_dashboard')
def influencer(username):
    
    ad_requests = AdRequest.query.filter_by(influencer_username=username).all()
    
    
    active_adrequests = [request for request in ad_requests if request.status == 'Accepted' and request.progression_status != 'Completed']
    new_requests = [request for request in ad_requests if request.status == 'Pending']
    
    return render_template('influencer_dashboard.html', 
                           active_adrequests=active_adrequests, 
                           new_requests=new_requests, 
                           username=username)

@app.route('/<string:username>/accept_request/<int:id>', methods=['POST'])
def accept_request(username, id):
    
    ad_request = AdRequest.query.get(id)
    
    if ad_request and ad_request.influencer_username == username:
        
        ad_request.status = 'Accepted'
        
        db.session.commit()
   
    return redirect(url_for('influencer', username=username))

@app.route('/<string:username>/reject_request/<int:id>', methods=['POST'])
def reject_request(username, id):
    
    ad_request = AdRequest.query.get(id)
    
    if ad_request and ad_request.influencer_username == username:
        
        db.session.delete(ad_request)
        
        db.session.commit()
    
    return redirect(url_for('influencer', username=username))


@app.route('/<string:username>/find_campaigns')
def find_campaigns(username):
    
    campaigns = Campaign.query.all()  
    
    return render_template('find_campaigns.html', campaigns=campaigns, username=username)

@app.route('/request_campaign/<int:campaign_id>/<string:username>', methods=['GET'])
def request_campaign(campaign_id, username):
    
    new_request = CampaignRequest(campaign_id=campaign_id, influencer_username=username)
    db.session.add(new_request)
    db.session.commit()
    
    
    flash('Campaign requested successfully!', 'success')
    return redirect(url_for('find_campaigns', username=username))

@app.route('/<string:username>/sponsor_dashboard')
def sponsor_dashboard(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    
    
    active_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    
    
    for campaign in active_campaigns:
        total_requests = AdRequest.query.filter_by(campaign_id=campaign.id).count()
        completed_requests = AdRequest.query.filter_by(campaign_id=campaign.id, progression_status='Completed').count()
        campaign.progress_bar = (completed_requests / total_requests) * 100 if total_requests > 0 else 0
    
    
    new_requests = db.session.query(CampaignRequest, Campaign).join(Campaign).filter(
        Campaign.sponsor_id == sponsor.id, 
        CampaignRequest.request_status == 'Pending'
    ).all()
    
    return render_template('sponsor_dashboard.html', 
                           username=username, 
                           active_campaigns=active_campaigns, 
                           new_requests=new_requests)


@app.route('/<string:username>/accept_campaign_request/<int:id>', methods=['POST'])
def accept_campaign_request(username, id):
    
    campaign_request = CampaignRequest.query.get(id)
    
    if campaign_request:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        if campaign and campaign.sponsor.username == username:
           
            campaign_request.request_status = 'Accepted'
            
            db.session.commit()
   
    return redirect(url_for('sponsor_dashboard', username=username))

@app.route('/<string:username>/reject_campaign_request/<int:id>', methods=['POST'])
def reject_campaign_request(username, id):
    
    campaign_request = CampaignRequest.query.get(id)
    
    if campaign_request:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        if campaign and campaign.sponsor.username == username:
            
            db.session.delete(campaign_request)
            
            db.session.commit()
    
    return redirect(url_for('sponsor_dashboard', username=username))

@app.route('/<string:username>/complete_ad_request/<int:id>', methods=['POST'])
def complete_ad_request(username, id):
    ad_request = AdRequest.query.get(id)
    
    if ad_request and ad_request.influencer_username == username:
        ad_request.progression_status = 'Completed'
        db.session.commit()
   
    return redirect(url_for('influencer', username=username))



@app.route("/<string:username>/campaign", methods=['GET', 'POST'])
def campaign(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if not sponsor:
        flash('Sponsor not found', 'error')
        return redirect(url_for('campaign', username=username))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        budget = request.form['budget']
        goals = request.form['goals']

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError as e:
            flash('Invalid date format. Please try again.', 'error')
            return redirect(url_for('campaign', username=username))

        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            goals=goals,
            sponsor_id=sponsor.id
        )
        db.session.add(new_campaign)
        db.session.commit()

        flash('Campaign added successfully!', 'success')
        return redirect(url_for('campaign', username=username))

    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()

    return render_template("campaign.html", username=username, campaigns=campaigns)


@app.route("/<string:username>/campaign/update/<int:campaign_id>", methods=['POST'])
def update_campaign(username, campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        flash('Campaign not found.', 'error')
        return redirect(url_for('campaign', username=username))
    
    campaign.name = request.form['name']
    campaign.description = request.form['description']
    try:
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    except ValueError:
        flash('Invalid date format. Please try again.', 'error')
        return redirect(url_for('campaign', username=username))
    
    campaign.budget = request.form['budget']
    campaign.goals = request.form['goals']
    
    db.session.commit()
    flash('Campaign updated successfully!', 'success')
    return redirect(url_for('campaign', username=username))

@app.route("/<string:username>/campaign/delete/<int:campaign_id>", methods=['POST'])
def delete_campaign(username, campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        flash('Campaign not found.', 'error')
        return redirect(url_for('campaign', username=username))
    
    db.session.delete(campaign)
    db.session.commit()
    
    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('campaign', username=username))


@app.route('/<username>/<int:campaign_id>/ad_request', methods=['GET', 'POST'])
def ad_request(username, campaign_id):
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    
    if request.method == 'POST':
        messages = request.form['messages']
        requirements = request.form['requirements']
        payment_amount = float(request.form['payment_amount'])
        influencer_username = request.form['influencer_username']

        
        influencer = Influencer.query.filter_by(username=influencer_username).first()

        if influencer is None:
            flash('Invalid influencer name', 'danger')
            return redirect(url_for('ad_request', username=username, campaign_id=campaign_id))
        
        
        ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_username=influencer_username,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending'
        )
        db.session.add(ad_request)
        db.session.commit()

        return redirect(url_for('ad_request', username=username, campaign_id=campaign_id))
    
    return render_template("ad_request.html", username=username, campaign_id=campaign_id, ad_requests=ad_requests)








@app.route("/<string:username>/<int:campaign_id>/update_ad_request/<int:ad_request_id>", methods=['POST'])
def update_ad_request(username, campaign_id, ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.messages = request.form['messages']
    ad_request.requirements = request.form['requirements']
    ad_request.payment_amount = request.form['payment_amount']
    ad_request.influencer_username = request.form['influencer_username']
    
    db.session.commit()
    flash('Ad Request updated successfully!', 'success')
    return redirect(url_for('ad_request', username=username, campaign_id=campaign_id))


@app.route("/<string:username>/<int:campaign_id>/delete_ad_request/<int:ad_request_id>", methods=['POST'])
def delete_ad_request(username, campaign_id, ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad Request deleted successfully!', 'success')
    return redirect(url_for('ad_request', username=username, campaign_id=campaign_id))

@app.route('/<username>/<campaign_id>/ad_request/<ad_request_id>/accept', methods=['POST'])
def accept_ad_request(username, campaign_id, ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    ad_request.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('ad_request', username=username, campaign_id=campaign_id))

@app.route('/<username>/<campaign_id>/ad_request/<ad_request_id>/decline', methods=['POST'])
def decline_ad_request(username, campaign_id, ad_request_id):
    ad_request = AdRequest.query.get(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    return redirect(url_for('ad_request', username=username, campaign_id=campaign_id))



@app.route('/<username>/find_influencers')
def find_influencers(username):
    
    sponsor = Sponsor.query.filter_by(username=username).first()

    
    if sponsor is None:
        return "Sponsor not found", 404

   
    associated_influencers = db.session.query(AdRequest.influencer_username).join(Campaign).filter(
        Campaign.sponsor_id == sponsor.id
    ).all()

   
    associated_influencer_usernames = [influencer for (influencer,) in associated_influencers]

   
    influencers = Influencer.query.filter(~Influencer.username.in_(associated_influencer_usernames)).all()

    return render_template('find_influencers.html', username=username, influencers=influencers)

if "__main__" == __name__:
    app.run(debug=True)