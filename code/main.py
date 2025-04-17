from flask import Flask, request, redirect, url_for, flash, session, render_template, jsonify
from models import db, Admin, User, Influencer, Sponsor, Campaign, AdRequest
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
from sqlalchemy.orm import Session,joinedload
import matplotlib.pyplot as plt
import io
import base64 

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Zi9iSTTniKKJfIV3dEX72A'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myproject.db"

db.init_app(app)
migrate = Migrate(app, db)
app.app_context().push()

@app.route("/")
def first():
    return render_template("welcome.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")
    if request.method == "POST":
        try:
            admin_id = request.form.get("admin_id")
            password = request.form.get("password")

            admin = Admin.query.filter_by(admin=admin_id).first()
            if admin and check_password_hash(admin.password, password):
                session['logged_in'] = True
                session['username'] = admin_id
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid admin ID or password. Try again'
                return render_template('admin_login.html', error=error)

        except Exception as e:
            error = 'An error occurred. Please contact the administrator.'
            return render_template("admin_login.html", error=error)

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type

            flash('You were successfully logged in', 'success')
            if user.user_type == 'sponsor':
                # Fetch the sponsor's username
                sponsor = Sponsor.query.filter_by(id=session['user_id']).first()
                if sponsor:
                    return redirect(url_for('sponsor_profile', username=sponsor.username))
                else:
                    flash('Error: Sponsor not found.', 'error')
                    return redirect(url_for('user_login'))  # Redirect back to login on error
            elif user.user_type == 'influencer':
                return redirect(url_for('influencer_profile'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('user_login.html')

@app.route('/register/influencer', methods=['POST'])
def register_influencer():
    username = request.form['username']
    password = request.form['password']
    platform_presence = ','.join(request.form.getlist('platform_presence'))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_influencer = Influencer(username=username, password=hashed_password, user_type='influencer', platform_presence=platform_presence)

    try:
        db.session.add(new_influencer)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    except IntegrityError:
        db.session.rollback()
        flash('Username already exists. Please log in.', 'error')
        return redirect(url_for('user_login'))

@app.route('/user/influencer_register')
def influencer_register_page():
    return render_template('influencer_register.html')

@app.route('/register/sponsor', methods=['POST'])
def register_sponsor():
    username = request.form['username']
    password = request.form['password']
    industry = request.form['industry']

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_sponsor = Sponsor(username=username, password=hashed_password, user_type='sponsor', industry=industry)

    try:
        db.session.add(new_sponsor)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_login'))
    except IntegrityError:
        db.session.rollback()
        flash('Username already exists. Please log in.', 'error')
        return redirect(url_for('user_login'))

@app.route('/user/sponsor_register')
def sponsor_register_page():
    return render_template('sponsor_register.html')

@app.route('/influencer/profile')
def influencer_profile():
    if 'logged_in' in session and session.get('user_type') == 'influencer':
        username = session.get('username')
        influencer = Influencer.query.filter_by(username=username).first()

        if influencer:
            # Get active (public) campaigns
            active_campaigns = AdRequest.query.filter(
                AdRequest.influencer_id == influencer.id,
                AdRequest.status == 'Accepted' 
            ).join(Campaign).all()
            # Correctly filter ad requests using filter()
            new_requests = AdRequest.query.filter(
            AdRequest.status == 'Pending',
            Campaign.visibility == 'private',
            (AdRequest.influencer_id == influencer.id) | (AdRequest.influencer_id == None) # Add this OR condition
        ).join(Campaign).all()
            print(new_requests)
            
            return render_template(
                'influencer_profile.html', 
                username=username,
                active_campaigns=active_campaigns,
                ad_requests=new_requests 
            )
        else:
            flash('Error: Influencer not found.', 'error')
            return redirect(url_for('user_login'))
    else:
        return redirect(url_for('user_login'))

@app.route('/sponsor/profile/<string:username>')
def sponsor_profile(username):
    print(session)
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        username = session.get('username')
        sponsor = Sponsor.query.filter_by(username=username).first()
        if sponsor:
            active_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).order_by(Campaign.date.desc()).all()

            ad_requests = AdRequest.query.join(Campaign).filter(
            Campaign.sponsor_id == sponsor.id,
            AdRequest.status == 'Pending',
            Campaign.visibility == 'public'  # Filter for public campaigns
        ).all()

            influencer_ids = {req.influencer_id for req in ad_requests if req.influencer_id}
            influencers = Influencer.query.filter(Influencer.id.in_(influencer_ids)).all()
            influencer_names = {influencer.id: influencer.username for influencer in influencers}

            active_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()  # Updated filter

            return render_template(
                'sponsor_profile.html', 
                username=username, 
                campaigns=active_campaigns, 
                ad_requests=ad_requests,  
                influencers=influencers,
                influencer_names=influencer_names,
                sponsor=sponsor,
                active_campaigns=active_campaigns,
                date=date
            )
        else:
            flash('Error: Sponsor not found.', 'error')
            return redirect(url_for('user_login'))
    else:
        return redirect(url_for('user_login'))

@app.route('/sponsor/campaigns', methods=['GET', 'POST'])
def sponsor_campaigns():
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        sponsor = Sponsor.query.filter_by(username=session['username']).first()
        if sponsor:
            if request.method == 'POST':
                campaign_id = request.form.get('campaign_id')
                title = request.form['title']
                description = request.form['description']
                image = request.form['image']
                niche = request.form['niche']
                date_str = request.form['date']
                visibility = request.form['visibility']
                budget = request.form['budget']

                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if date_obj < date.today():
                        flash('Invalid date: Date cannot be in the past.', 'error')
                        return redirect(url_for('sponsor_campaigns'))  # Redirect to itself on error
                except ValueError:
                    flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
                    return redirect(url_for('sponsor_campaigns'))  # Redirect to itself on error

                if campaign_id:  # Update existing campaign
                    campaign = Campaign.query.get(campaign_id)
                    if campaign and campaign.sponsor_id == sponsor.id:
                        campaign.title = title
                        campaign.description = description
                        campaign.image = image
                        campaign.niche = niche
                        campaign.date = date_obj
                        campaign.visibility = visibility
                        campaign.budget = budget
                        db.session.commit()
                        flash('Campaign updated successfully!', 'success')
                    else:
                        flash('Campaign not found or unauthorized access.', 'error')
                else:  # Create new campaign
                    new_campaign = Campaign(
                        title=title,
                        description=description,
                        image=image,
                        niche=niche,
                        date=date_obj,
                        sponsor_id=sponsor.id,
                        budget=budget,
                        visibility=visibility
                    )
                    db.session.add(new_campaign)
                    db.session.commit()
                    flash('Campaign added successfully!', 'success')

            campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()  # Fetch all campaigns
            return render_template('sponsor_campaign.html', campaigns=campaigns, date=date)

    return redirect(url_for('user_login'))

@app.route('/sponsor/campaign/edit/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = get_campaign_by_id(campaign_id)
    if request.method == 'POST':
        title = request.form.get('title')
        budget = request.form.get('budget')
        description = request.form.get('description')
        date_str = request.form.get('date')

        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('edit_campaign', campaign_id=campaign_id))

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            if date_obj < date.today():
                flash('Invalid date: Date cannot be in the past.', 'error')
                return redirect(url_for('edit_campaign', campaign_id=campaign_id))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('edit_campaign', campaign_id=campaign_id))

        if campaign:
            campaign.title = title
            campaign.budget = float(budget) if budget else None
            campaign.description = description
            campaign.date = date_obj
            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('sponsor_profile', username=session.get('username')))  # Redirect to sponsor profile
        else:
            flash('Campaign not found!', 'error')
            return redirect(url_for('sponsor_profile', username=session.get('username')))

    return render_template('sponsor_profile', campaign=campaign, date=date) 

@app.route('/sponsor/find', methods=['GET', 'POST'])
def sponsor_find_page():
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        if request.method == 'POST':
            search_type = request.form.get('search_type')
            keyword = request.form.get('keyword')

            if search_type == 'campaigns':
                results = Campaign.query.filter(
                    (Campaign.title.ilike(f'%{keyword}%')) | 
                    (Campaign.description.ilike(f'%{keyword}%')) | 
                    (Campaign.niche.ilike(f'%{keyword}%'))
                ).all()
            elif search_type == 'influencers':
                results = Influencer.query.filter(
                    (Influencer.username.ilike(f'%{keyword}%')) | 
                    (Influencer.platform_presence.ilike(f'%{keyword}%'))
                ).all()
            else:
                results = []

            return render_template('sponsor_find.html', results=results, search_type=search_type)

        return render_template('sponsor_find.html', results=[], search_type=None)
    return redirect(url_for('user_login'))

@app.route('/sponsor/campaign/<int:campaign_id>')
def get_campaign_details(campaign_id):
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        campaign = Campaign.query.get_or_404(campaign_id)
        if campaign.sponsor_id == session['user_id']:
            return jsonify({
                'title': campaign.title,
                'description': campaign.description,
                'niche': campaign.niche,
                'date': campaign.date.strftime('%Y-%m-%d'),
                'budget': campaign.budget
            })
        else:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Not logged in'}), 401

@app.route('/sponsor/campaign/delete/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        sponsor = Sponsor.query.filter_by(username=session['username']).first()
        campaign = Campaign.query.get(campaign_id)
        if campaign and campaign.sponsor_id == sponsor.id:
            # Delete associated AdRequests
            for ad_request in campaign.ad_requests: 
                db.session.delete(ad_request)

            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully!', 'success')
        else:
            flash('Campaign not found or unauthorized access.', 'error')
    return redirect(url_for('sponsor_profile', username=session['username']))

def get_campaign_by_id(campaign_id):
    return Campaign.query.get(campaign_id)

      
@app.route('/search_influencers')
def search_influencers():
    search_query = request.args.get('q')
    if search_query:
        influencers = Influencer.query.filter(Influencer.username.ilike(f'%{search_query}%')).all()
        influencer_data = [{'id': influencer.id, 'username': influencer.username} for influencer in influencers]
        return jsonify(influencer_data)
    else:
        return jsonify([])
    
@app.route('/ad_request/create', methods=['POST'])
def create_ad_request():
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        sponsor = Sponsor.query.filter_by(username=session['username']).first()
        if sponsor:
            try:
                campaign_id = request.form['campaign_id']
                ad_name = request.form['ad_name']
                ad_description = request.form['ad_description']
                ad_terms = request.form['ad_terms']
                payment = request.form['payment'] 
                influencer_id = request.form.get('influencer_id') # Get selected influencer ID

                new_ad_request = AdRequest(
                    sponsor_id=sponsor.id, 
                    campaign_id=campaign_id,
                    ad_name=ad_name,
                    ad_description=ad_description,
                    ad_terms=ad_terms,
                    payment=payment,
                    influencer_id=influencer_id  # Store influencer ID 
                )

                db.session.add(new_ad_request)
                db.session.commit()
                flash('Ad request submitted successfully!', 'success')
                return redirect(url_for('sponsor_campaigns'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating ad request: {str(e)}', 'error')
                return redirect(url_for('sponsor_profile'))
    else:
        return redirect(url_for('user_login'))



@app.route('/ad_request/<int:request_id>/accept', methods=['POST']) 
def accept_ad_request(request_id):
    if 'logged_in' in session and session.get('user_type') == 'influencer':
        ad_request = AdRequest.query.get_or_404(request_id)
        if ad_request.influencer_id == session['user_id']:
            ad_request.status = 'Accepted'
            db.session.commit()
            flash('Ad request accepted!', 'success')
        else:
            flash('Unauthorized!', 'error')
    return redirect(url_for('influencer_profile'))

@app.route('/ad_request/<int:request_id>/reject', methods=['POST'])
def reject_ad_request(request_id):
    if 'logged_in' in session and session.get('user_type') == 'influencer':
        ad_request = AdRequest.query.get_or_404(request_id)
        if ad_request.influencer_id == session['user_id']:
            ad_request.status = 'Rejected'
            db.session.commit()
            flash('Ad request rejected!', 'success')
        else:
            flash('Unauthorized!', 'error')
    return redirect(url_for('influencer_profile'))

@app.route('/ad_request/update', methods=['POST'])
def update_ad_request():
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        try:
            request_id = request.form['request_id']
            ad_name = request.form['ad_name']
            ad_description = request.form['ad_description']
            ad_terms = request.form['ad_terms']
            payment = request.form['payment']
            influencer_id = request.form.get('influencer_id')

            ad_request = AdRequest.query.get(request_id)
            if ad_request:
                ad_request.ad_name = ad_name
                ad_request.ad_description = ad_description
                ad_request.ad_terms = ad_terms
                ad_request.payment = payment
                ad_request.influencer_id = influencer_id if influencer_id else None
                db.session.commit()
                flash('Ad request updated successfully!', 'success')
            else:
                flash('Ad request not found!', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating ad request: {str(e)}', 'error')
    return redirect(url_for('sponsor_campaigns')) 


@app.route('/ad_request/delete/<int:request_id>', methods=['POST'])
def delete_ad_request(request_id):
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        ad_request = AdRequest.query.get(request_id)
        if ad_request:
            db.session.delete(ad_request)
            db.session.commit()
            flash('Ad request deleted successfully!', 'success')
        else:
            flash('Ad request not found!', 'error')
    return redirect(url_for('sponsor_campaigns')) 

@app.route('/sponsor/campaign/<int:campaign_id>/requests')
def get_campaign_ad_requests(campaign_id):
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        campaign = Campaign.query.get_or_404(campaign_id)
        if campaign.sponsor_id == session['user_id']:
            ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
            return jsonify([
                {
                    'ad_name': req.ad_name,
                    'campaign_title': req.campaign.title,
                    'influencer_username': req.influencer.username if req.influencer else 'None',
                    'ad_description': req.ad_description,
                    'ad_terms': req.ad_terms,
                    'payment': req.payment,
                    'status': req.status
                } 
                for req in ad_requests
            ])
        else:
            return jsonify({'error': 'Unauthorized'}), 403
    else:
        return jsonify({'error': 'Not logged in'}), 401
    
@app.route('/sponsor/find')
def find_page():
    return render_template('find.html')

@app.route('/influencer/find', methods=['GET', 'POST'])
def influencer_find_page():
    if 'logged_in' in session and session.get('user_type') == 'influencer':
        if request.method == 'POST':
            search_query = request.form.get('search')
            if search_query:
                campaigns = Campaign.query.filter(
                    Campaign.visibility == 'public',
                    Campaign.niche.ilike(f'%{search_query}%')
                ).all()
            else:
                campaigns = Campaign.query.filter_by(visibility='public').all() 
        else:
            campaigns = Campaign.query.filter_by(visibility='public').all()

        return render_template('influencer_find.html', campaigns=campaigns)
    else:
        return redirect(url_for('user_login'))
    
@app.route('/submit_ad_request', methods=['POST'])
def submit_ad_request():
    if 'logged_in' in session and session.get('user_type') == 'influencer':
        influencer = Influencer.query.filter_by(username=session['username']).first()
        if influencer:
            try:
                campaign_id = request.form['campaign_id']
                print(f"Campaign ID: {campaign_id}") #debug
            
                ad_name = request.form['ad_name']
                ad_description = request.form['ad_description']
                ad_terms = request.form['ad_terms']
                payment = float(request.form['payment'])

                campaign = Campaign.query.get(campaign_id)
                sponsor = campaign.sponsor

                ad_request = AdRequest(
                    sponsor_id=sponsor.id,  # Associate with the sponsor
                    influencer_id=influencer.id, 
                    campaign_id=campaign_id,
                    ad_name=ad_name,
                    ad_description=ad_description,
                    ad_terms=ad_terms,
                    payment=payment
                )
                print(ad_request) #debug
                db.session.add(ad_request)
                db.session.commit()
                flash('Ad request submitted successfully!', 'success')
                
                return redirect(url_for('influencer_find_page') ) 
            except Exception as e:
                db.session.rollback()
                flash(f'Error submitting ad request: {str(e)}', 'error')

        else:
            flash('Error: Influencer not found.', 'error')
    return redirect(url_for('influencer_find_page'))

@app.route('/sponsor/ad_request/<int:request_id>/accept', methods=['POST'])
def sponsor_accept_ad_request(request_id):
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        ad_request = AdRequest.query.get_or_404(request_id)
        if ad_request.sponsor_id == session['user_id']:
            ad_request.status = 'Accepted'
            db.session.commit()
            flash('Ad request accepted!', 'success')
        else:
            flash('Unauthorized!', 'error')
    return redirect(url_for('sponsor_profile', username=session.get('username'))) 

@app.route('/sponsor/ad_request/<int:request_id>/reject', methods=['POST'])
def sponsor_reject_ad_request(request_id):
    if 'logged_in' in session and session.get('user_type') == 'sponsor':
        ad_request = AdRequest.query.get_or_404(request_id)
        if ad_request.sponsor_id == session['user_id']:
            ad_request.status = 'Rejected'
            db.session.commit()
            flash('Ad request rejected!', 'success')
        else:
            flash('Unauthorized!', 'error')
    return redirect(url_for('sponsor_profile', username=session.get('username'))) 
@app.route('/admin/profile')
def admin_dashboard():
    if 'logged_in' in session and session.get('username'):
        return render_template("admin_dashboard.html")
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/search')
def admin_search():
    search_query = request.args.get('q')
    filter_type = request.args.get('filter', 'all')  # Default to 'all' if not specified

    results = []

    if filter_type in ('all', 'sponsors'):
        sponsors = Sponsor.query.filter(Sponsor.username.ilike(f'%{search_query}%')).all()
        results.extend([
            {'type': 'sponsor', 'id': sponsor.id, 'name': sponsor.username, 'details': f'Industry: {sponsor.industry}'}
            for sponsor in sponsors
        ])

    if filter_type in ('all', 'influencers'):
        influencers = Influencer.query.filter(Influencer.username.ilike(f'%{search_query}%')).all()
        results.extend([
            {'type': 'influencer', 'id': influencer.id, 'name': influencer.username, 'details': f'Platforms: {influencer.platform_presence}'}
            for influencer in influencers
        ])

    if filter_type in ('all', 'campaigns'):
        campaigns = Campaign.query.filter(Campaign.title.ilike(f'%{search_query}%')).all()
        results.extend([
            {'type': 'campaign', 'id': campaign.id, 'name': campaign.title, 'details': f'Niche: {campaign.niche}'}
            for campaign in campaigns
        ])

    return jsonify(results)

@app.route('/admin/flag/<string:item_type>/<int:item_id>', methods=['POST'])
def admin_flag_item(item_type, item_id):
    if item_type == 'sponsor':
        item = Sponsor.query.options(joinedload(Sponsor.campaigns).joinedload(Campaign.ad_requests)).get(item_id) 
    elif item_type == 'influencer':
        item = Influencer.query.options(joinedload(Influencer.ad_requests)).get(item_id) 
    elif item_type == 'campaign':
        item = Campaign.query.options(joinedload(Campaign.ad_requests)).get(item_id)
    else:
        return jsonify({'error': 'Invalid item type'}), 400

    if item:
        try:
            if item_type == 'sponsor':
                for campaign in item.campaigns:
                    for ad_request in campaign.ad_requests:
                        db.session.delete(ad_request)
                    db.session.delete(campaign)
            elif item_type == 'influencer':
                for ad_request in item.ad_requests:
                    db.session.delete(ad_request)  # Delete associated ad requests
            elif item_type == 'campaign':
                for ad_request in item.ad_requests:
                    db.session.delete(ad_request) 
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': f'{item_type.capitalize()} deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error deleting {item_type}: {str(e)}'}), 500
    else:
        return jsonify({'error': f'{item_type.capitalize()} not found'}), 404

@app.route('/admin/view/<string:item_type>/<int:item_id>')
def admin_view_item(item_type, item_id):
    if item_type == 'sponsor':
        item = Sponsor.query.get(item_id)
        if item:
            return jsonify({'name': item.username, 'details': f'Industry: {item.industry}'})
    elif item_type == 'influencer':
        item = Influencer.query.get(item_id)
        if item:
            return jsonify({'name': item.username, 'details': f'Platforms: {item.platform_presence}'})
    elif item_type == 'campaign':
        item = Campaign.query.get(item_id)
        if item:
            return jsonify({'name': item.title, 'details': f'Niche: {item.niche}'})
    return jsonify({'error': 'Item not found'}), 404

@app.route('/admin/stats')
def admin_stats():
    if 'logged_in' in session and session.get('username'):
        # Fetch statistics data
        influencer_count = Influencer.query.count()
        sponsor_count = Sponsor.query.count()
        public_campaign_count = Campaign.query.filter_by(visibility='public').count()
        private_campaign_count = Campaign.query.filter_by(visibility='private').count()

        # Create the first plot (Sponsors and Influencers)
        plt.figure(figsize=(8,6))
        plt.bar(['Sponsors', 'Influencers'], [sponsor_count, influencer_count])
        plt.xlabel('User Type')
        plt.ylabel('Count')
        plt.title('Sponsors and Influencers')
        img1 = io.BytesIO()
        plt.savefig(img1, format='png')
        img1.seek(0)
        plot_url1 = base64.b64encode(img1.getvalue()).decode()

        # Create the second plot (Public and Private Campaigns)
        plt.figure(figsize=(8,6))
        plt.bar(['Public Campaigns', 'Private Campaigns'], [public_campaign_count, private_campaign_count])
        plt.xlabel('Campaign Visibility')
        plt.ylabel('Count')
        plt.title('Public and Private Campaigns')
        img2 = io.BytesIO()
        plt.savefig(img2, format='png')
        img2.seek(0)
        plot_url2 = base64.b64encode(img2.getvalue()).decode()

        return render_template('admin_stats.html', plot_url1=plot_url1, plot_url2=plot_url2)
    else:
        return redirect(url_for('admin_login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_login'))

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

