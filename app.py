from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash,make_response
from flask_uploads import UploadSet, configure_uploads, DATA
import os
from flask_sqlalchemy import SQLAlchemy
import pymysql
from sqlalchemy.exc import IntegrityError, NoReferencedTableError , SQLAlchemyError
import json
from werkzeug.security import generate_password_hash, check_password_hash
import random
from random import choices
import string
import time
from datetime import datetime
from functools import wraps
import requests
import re
import pandas as pd
from io import TextIOWrapper
import csv
import uuid
from werkzeug.utils import secure_filename
import validate
import json
app = Flask(__name__)
#app.secret_key = os.urandom(24)  # Randomly generated secret key for sessions
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static\\uploads'
app.config['UPLOADS_DEFAULT_DEST'] = 'static/uploads'  # This is the folder where uploaded files will be saved
datafiles = UploadSet('data', DATA)
configure_uploads(app, datafiles)
##################################################################################
# DB CONFIG
# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:NewPassword@localhost/template_manager'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/template_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
##################################################################################
# User Model
class User(db.Model):
    __tablename__ = 'Users'  # Explicit table name
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    assigned_to = db.Column(db.String(1000), nullable=False)

# Template Model
class Template(db.Model):
    __tablename__ = 'Templates'  # Explicit table name
    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    template_type = db.Column(db.String(50), nullable=True)
    submitted_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False)
    TemplateID = db.Column(db.String(50), nullable=True)
    Internal_ID = db.Column(db.String(255))
    usagetype = db.Column(db.String(25)) 
# AgentInformation Model
class AgentInformation(db.Model):
    __tablename__ = 'AgentInformation'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Created_Date = db.Column(db.BigInteger)
    customerId = db.Column(db.String(255))
    subAccountId = db.Column(db.String(255))
    agentId = db.Column(db.String(255))
    Internal_ID = db.Column(db.String(255))
    Status = db.Column(db.String(50))
    Created_By = db.Column(db.String(50))
    Status_Updated_By = db.Column(db.String(50))
    template_user = db.Column(db.String(255))
##### Campaign Table
class Campaign(db.Model):
    __tablename__ = 'Campaigns'
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    TemplateID = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    Internal_ID = db.Column(db.String(255), nullable=False)
    campaign_uid=db.Column(db.String(36), nullable=False)
    has_variables=db.Column(db.String(1), nullable=False)
###### Campaign Data
class CampaignData(db.Model):
    __tablename__ = 'campaigndata'
    id = db.Column(db.Integer, primary_key=True)
    mobile_number = db.Column(db.String(12), nullable=False)
    variables = db.Column(db.JSON, nullable=True)  # Storing variables as JSON
    campaign_uid = db.Column(db.String(36), nullable=False)
    TemplateID = db.Column(db.Integer, nullable=False)
    internal_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String, default="pending")
###### Campaign Report
class CampaignReport(db.Model):
    __tablename__ = 'campaign_reports'
    ID = db.Column(db.Integer, primary_key=True)
    TemplateID = db.Column(db.String(255), nullable=False)
    Total = db.Column(db.Integer)
    Sent = db.Column(db.Integer)
    wasRead = db.Column(db.Integer)
    Delivered = db.Column(db.Integer)
    Blacklisted = db.Column(db.Integer)
    Failed = db.Column(db.Integer)
    campaign_uid=db.Column(db.String(255), nullable=False)


##################################################################################
# Cache control decorator
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache
##################################################################################


##################################################################################
@app.route('/', methods=['GET'])
def start():
        if 'username' in session:
            # role = session['role']
            # if role!="User":
            #     return render_template('admin-layout.html')
            # else:
            #     return render_template('brand-layout.html')
            return redirect(url_for('login'))
        return redirect(url_for('login'))


@app.route('/admin-dashboard', methods=['GET'])
def handle_inbound_GET_AdminDashboard():
    return render_template('admin-dashboard.html')

@app.route('/brand-dashboard', methods=['GET'])
def handle_inbound_GET_BrandDashboard():
    return render_template('brand-dashboard.html')

@app.route('/brand-home', methods=['GET'])
def brandhome():
        if 'username' in session:
            role = session['role']
            if role!="User":
                return redirect(url_for('login'))
            else:
                return redirect(url_for('campaign_dashboard'))
        return redirect(url_for('login'))

@app.route('/admin-home', methods=['GET'])
def adminhome():
        if 'username' in session:
            role = session['role']
            if role!="Admin":
                return redirect(url_for('login'))
            else:
                return redirect(url_for('campaign_dashboard_admin'))
                
                #return render_template('admin-dashboard.html')
        return redirect(url_for('login'))

@app.route('/createnewtext', methods=['GET'])
def createnewtext():
        if 'username' in session:
            role = session['role']
            if role =="User":
                return render_template('text-template.html')
            if role =="Admin":
                return render_template('text-template-admin.html')
            else:
                redirect(url_for('login'))
        
@app.route('/createnewrich', methods=['GET'])
def createnewrich():
        if 'username' in session:
            role = session['role']
            if role =="User":
                return render_template('rich-template.html')
            if role =="Admin":
                return render_template('rich-template-admin.html')
            else:
                redirect(url_for('login'))

@app.route('/createnewrichcc', methods=['GET'])
def createnewrichcc():
        if 'username' in session:
            role = session['role']
            if role =="User":
                return render_template('rich-carousel.html')
            if role =="Admin":
                return render_template('rich-carousel-admin.html')
            else:
                redirect(url_for('login'))
@app.route('/managetemplate', methods=['GET'])
def managetemplate():
        if 'username' in session:
            return render_template('plate-manage.html')
        redirect(url_for('login'))        
#################################################################################
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
##################################################################################
##################################################################################

#### Register
@app.route('/register', methods=['GET'])
def registerget():
    if request.method == 'GET':
        return render_template('register.html')
@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Hash the password
        hashed_password = generate_password_hash(password)  
        
        new_user = User(username=username, password=hashed_password,role=role)
        db.session.add(new_user)
        db.session.commit()
        
        return  redirect(url_for('login'))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

##################################################################################
### Login
@app.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    
    if request.method == 'GET':
        # if 'username' in session:
        #     return redirect(url_for('brandhome'))
        return render_template('signin.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database to find the user
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            session['user_id'] = user.user_id
            session['role'] = user.role
            if session['role']=="User":
                return  redirect(url_for('brandhome'))
            else:
                
                return  redirect(url_for('adminhome'))
            
        else:
            return "Invalid credentials"
##################################################################################
@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('user_id', None)
        session.pop('role', None)
        flash('You have been logged out.')
    return redirect(url_for('login'))
##################################################################################
### Text Template GET and POST
@app.route('/text', methods=['GET'])
def returntextform():
    return render_template('texttemplate.html')
@app.route('/text', methods=['POST'])
def createtexttemplate():
    if 'user_id' not in session:
        return render_template('signin.html')
    user_id = session['user_id']
    role = session['role']
    username=session['username']
    response = request.json
    agent_info = AgentInformation.query.filter_by(template_user=username).first()
    if not agent_info:
        return "No matching agent information found for this user."
    internal_id = agent_info.Internal_ID
    suggestions = []
    agentContentMessage = {}
    text = response["txtName"]
    usagetype=response["typeSelect"]
    if len(response["suggestions"]) != 0:
        for items in response["suggestions"]:
            if items["typeOfAction"] == "1":
                toadd = {
                    "reply": {
                        "text": items["text"],
                        "postbackData": items["postback"]
                    }
                }
                suggestions.append(toadd)
            if items["typeOfAction"] == "2":
                toadd = {
                    "action": {
                        "text": items["text"],
                        "postbackData": items["postback"],
                        "openUrlAction": {
                            "url": items["url"]
                        }
                    }
                }
                suggestions.append(toadd)
            if items["typeOfAction"] == "3":
                toadd = {
                    "action": {
                        "text": items["text"],
                        "postbackData": items["postback"],
                        "dialAction": {
                            "phoneNumber": items["phoneNo"]
                        }
                    }
                }
                suggestions.append(toadd)

    # Create the JSON object
    agentContentMessage["agentContentMessage"] = {
        "suggestions": suggestions,
        "text": text
    }
    # Convert JSON object to a string
    content_str = json.dumps(agentContentMessage)

    # Generate a 16-digit alphanumeric string for TemplateID
    template_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    current_user_id = user_id  

    # Insert into database
    new_template = Template(
        content=content_str,
        created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
        template_type='text',
        submitted_by=current_user_id,
        status='Pending',
        TemplateID=template_id,
        Internal_ID=internal_id,
        usagetype=usagetype
    )
    db.session.add(new_template)
    db.session.commit()
    alert =f"New Template Created! Template ID is {template_id}"
    #return render_template("alert.html",alert=alert)
    return alert
###################################################################################
#### RichCard - Get And Post
@app.route('/rich', methods=['GET'])
def returnrichcard():
    return render_template('richcardtemplate.html')
@app.route('/rich', methods=['POST'])
def rich():
    if 'user_id' not in session:
       return render_template('signin.html')

    user_id = session['user_id']
    role = session['role']
    username=session['username']
    agent_info = AgentInformation.query.filter_by(template_user=username).first()
    if not agent_info:
        return "No matching agent information found for this user."

    internal_id = agent_info.Internal_ID
    try:
        # Get the image file from the request
        image = request.files['image']
        filename, file_extension = os.path.splitext(image.filename)
        unique_filename = f"{filename}_{int(time.time() * 1000)}{file_extension}"
        # Save the image
        image_filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        image.save(image_filename)
        image_filename = image_filename.replace("\\", "/")
        print(image_filename) # This is where the file is getting saved 
        imageurl="https://rcstemplate.ngrok.dev/"+image_filename
        # Get the suggestions and richCard JSON strings from the request
        suggestions_str = request.form['suggestions']
        suggestionjson = json.loads(suggestions_str)
        suggestions=[]
        if len(suggestionjson)!=0:
        # If not empty, means we got suggestion
        # Open the suggestions and see what type of suggestion we got
            for items in suggestionjson:
                # We are expecting the type of action to be 1 or 2 or 3
                if items["typeOfAction"]=="1":
                    toadd={
                        "reply": {
                            "text": items["text"],
                            "postbackData": items["postback"]
                        }
                    }
                    suggestions.append(toadd)
                if items["typeOfAction"]=="2":
                    toadd={
                            "action": {
                                "text": items["text"],
                                "postbackData":  items["postback"],
                                "openUrlAction": {
                                    "url": items["url"]
                                }
                            }
                        }
                    suggestions.append(toadd)
                if items["typeOfAction"]=="3":
                    phoneNo="+"+items["phoneNo"]
                    toadd={
                    "action": {
                    "text": items["text"],
                    "postbackData": items["postback"],
                    "dialAction": {
                        "phoneNumber": phoneNo
                    }
                    }}
                    suggestions.append(toadd)

        richCard_str = request.form['richCard']

        # Convert the JSON strings back to Python objects
        richCard = json.loads(richCard_str)
        ### Remember we are passing a fake path from front end, here we update it
        richCard['standaloneCard']['cardContent']['media']['contentInfo']['fileUrl'] = imageurl
        richCard['standaloneCard']['cardContent']['suggestions'] = suggestions
        final_structure = {"agentContentMessage": {"richCard": richCard}}
        final_structure_str = json.dumps(final_structure)
        template_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # Assuming we have a variable 'current_user_id' that holds the ID of the logged-in user
        current_user_id = user_id  
        new_template = Template(
        created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
        content=final_structure_str,
        template_type='rich',
        submitted_by=current_user_id,  
        status='Pending',
        TemplateID=template_id,
        Internal_ID=internal_id
    )
        db.session.add(new_template)
        db.session.commit()
        alert =f"New Template Created! Template ID is {template_id}"
        #return render_template("alert.html",alert=alert)
        return alert
    except Exception as e:
        print("An error occurred:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 400
###################################################################################

#############
@app.route('/richcarousel', methods=['POST'])
def richcarousel():
    if 'user_id' not in session:
       return render_template('signin.html')

    user_id = session['user_id']
    role = session['role']
    username=session['username']
    agent_info = AgentInformation.query.filter_by(template_user=username).first()
    if not agent_info:
        return "No matching agent information found for this user."

    internal_id = agent_info.Internal_ID
    # Get the JSON string received from the FormData in the request object
    all_card_contents_str = request.form.get('allCardContents')

    # Convert the JSON string to Python dictionary
    all_card_contents = json.loads(all_card_contents_str)

    # Get the uploaded images from the request object
    uploaded_files = request.files.getlist("images[]")

    saved_file_paths = []  # List to keep track of the paths where images are saved

    # Loop through each uploaded file
    for file in uploaded_files:
        # Secure the filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = str(int(time.time() * 1000)) + str(random.randint(1000, 9999)) + file_ext
        # Create the full path to save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        # Save the file to the specified path
        imageurl="https://rcstemplate.ngrok.dev/static/uploads/"+unique_name
        file.save(filepath)
        saved_file_paths.append(imageurl)

    # Loop through each card content and update fileUrl
    for index, card in enumerate(all_card_contents):
        # Only proceed if there are sufficient saved files to match the cards
        if index < len(saved_file_paths):
            card['media']['contentInfo']['fileUrl'] = saved_file_paths[index]

        # Rebuild and replace suggestions, just as before
        suggestions = []
        suggestionjson = card.get('suggestions', [])

        for items in suggestionjson:
            if items["typeOfAction"] == "1":
                toadd = {
                    "reply": {
                        "text": items["text"],
                        "postbackData": items["postback"]
                    }
                }
                suggestions.append(toadd)
            if items["typeOfAction"] == "2":
                toadd = {
                    "action": {
                        "text": items["text"],
                        "postbackData": items["postback"],
                        "openUrlAction": {
                            "url": items["url"]
                        }
                    }
                }
                suggestions.append(toadd)
            if items["typeOfAction"] == "3":
                phoneNo = "+" + items["phoneNo"]
                toadd = {
                    "action": {
                        "text": items["text"],
                        "postbackData": items["postback"],
                        "dialAction": {
                            "phoneNumber": phoneNo
                        }
                    }
                }
                suggestions.append(toadd)

        card['suggestions'] = suggestions

    agent_content_message = {
        "agentContentMessage": {
            "richCard": {
                "carouselCard": {
                    "cardWidth": "MEDIUM",
                    "cardContents": []
                }
            }
        }
    }
    agent_content_message["agentContentMessage"]["richCard"]["carouselCard"]["cardContents"] = all_card_contents
    agent_content_message_str = json.dumps(agent_content_message)
    template_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    current_user_id = user_id  
    new_template = Template(
    created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
    content=agent_content_message_str,
    template_type='richCarousel',
    submitted_by=current_user_id,  
    status='Pending',
    TemplateID=template_id,
    Internal_ID=internal_id
)
    db.session.add(new_template)
    db.session.commit()
    alert =f"New Template Created! Template ID is {template_id}"
    #return render_template("alert.html",alert=alert)
    return alert
###################################################################################
@app.route('/createaccount', methods=['POST'])
def create_account():
    # Parse the incoming JSON
    data = request.get_json()
    # User Registration
    username = data.get('username')
    password = data.get('password')
    role = "User"
    hashed_password = generate_password_hash(password) 
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    # Additional Information
    Created_Date = int(time.time() * 1000)
    customerId = data.get('customerId')
    subAccountId = data.get('subAccountId')
    agentId = data.get('agentId')
    first_part = ''.join(random.choices(string.digits, k=4))
    middle_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    last_part = ''.join(random.choices(string.digits, k=4))
    Internal_ID = first_part + "-" + middle_part + "-" + last_part
    Status = "Active"
    Created_By = "Admin"
    Status_Updated_By = "Admin"
    template_user = username  # from the form
    new_info = AgentInformation(
        Created_Date=Created_Date,
        customerId=customerId,
        subAccountId=subAccountId,
        agentId=agentId,
        Internal_ID=Internal_ID,
        Status=Status,
        Created_By=Created_By,
        Status_Updated_By=Status_Updated_By,
        template_user=template_user
    )
    db.session.add(new_info)
    db.session.commit()
    return jsonify({"Account ID Created": Internal_ID})
######GET
@app.route('/createaccount', methods=['GET'])
def handle_inbound_GET_Createaccount():
    role = session['role']
    if role!="Admin":
        return render_template('signin.html')
    return render_template('create-account.html')
###################################################################################

@app.route('/mytemplates', methods=['GET'])
def mytemplates():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    role = session['role']

    page = request.args.get('page', 1, type=int)
    per_page = 10  # You can adjust this value based on the number of items you want to display per page

    if role == 'Admin':
        # Show all templates for admin with pagination
        templates = Template.query.paginate(page=page, per_page=per_page)
        return render_template('brand-template-manage-admin.html', templates=templates)
    else:
        # Show only user-specific templates with pagination
        templates = Template.query.filter_by(submitted_by=user_id).paginate(page=page, per_page=per_page)
        return render_template('brand-template-manage.html', templates=templates)
##################################################################################
@app.route('/approvetemplate', methods=['GET'])
def approvetemplate():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    role = session['role']

    page = request.args.get('page', 1, type=int)
    per_page = 10  # You can adjust this value based on the number of items you want to display per page

    if role == 'Admin':
        # Show all templates for admin with pagination
        templates = Template.query.paginate(page=page, per_page=per_page)
        return render_template('admin-template-manage.html', templates=templates)
    else:
        return redirect(url_for('login'))
###################################################################################
@app.route('/approve/<int:id>', methods=['GET'])
def approve_template(id):
    if 'role' in session and session['role'] == 'Admin':
        template = Template.query.get(id)
        if template:
            template.status = "Approved"
            template.approved_by = session['user_id']
            template.approved_date = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('mytemplates'))
    return "Permission Denied!"

@app.route('/reject/<int:id>', methods=['GET'])
def reject_template(id):
    if 'role' in session and session['role'] == 'Admin':
        template = Template.query.get(id)
        if template:
            template.status = "Declined"
            template.approved_by = session['user_id']
            template.approved_date = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('mytemplates'))
    return "Permission Denied!"

@app.route('/delete/<int:id>', methods=['GET'])
def delete_template(id):
    #### Logic to delete a template by its ID
    if 'user_id' in session:
        template = Template.query.filter_by(template_id=id, submitted_by=session['user_id']).first()
        if template:
            db.session.delete(template)
            db.session.commit()
            return redirect(url_for('mytemplates'))
    return "Permission Denied!"
@app.route('/template_details/<int:template_id>', methods=['GET'])
def template_details(template_id):
    template = Template.query.get(template_id)
    if template:
       
        if template.submitted_by !=session['user_id']:
            if session['role']!="Admin":
                return redirect(url_for('login'))
        #### Check if template has variables
        tid = template.TemplateID
        Iid=template.Internal_ID
        mobilenumber = "msisdnfield" 
        agent_content_message_str = template.content
        agent_content_message_json = json.loads(agent_content_message_str)  # Convert string to JSON
        m1= f'{{"Internal_ID": "{Iid}", "TemplateID": "{tid}", "msisdn": "numbertosendto"}}'
        m2 = f'{{"Internal_ID": "{Iid}", "TemplateID": "{tid}", "msisdn": "919980113546"}}'
        m3=""
        content = json.loads(template.content)
        if template.template_type=="text":
            input_string  = agent_content_message_json['agentContentMessage']['text']
            numberofvariables = len(re.findall(r'\[([^]]+)\]', input_string))
            if numberofvariables!=0:
                varstr=""
                for i in range(1, numberofvariables + 1):
                    varstr += f"var{i}"
                    if i < numberofvariables:
                        varstr += ","
                
                m1= f'{{"Internal_ID": "{Iid}", "TemplateID": "{tid}", "msisdn": "numbertosendto", "variables": "{varstr}"}}'
                m2 = f'{{"Internal_ID": "{Iid}", "TemplateID": "{tid}", "msisdn": "919980113546", "variables": "{varstr}"}}'
                m3=f'PLEASE NOTE!! Your Templates has {numberofvariables} variables, and these need to be passed with your json'
        
        return render_template('template-detail.html', content=content, template=template, m1=m1, m2=m2, m3=m3)
    else:
        return "Template not found", 404
#####################################################################################


@app.route('/start_campaign/<int:id>', methods=['GET', 'POST'])
def start_campaign(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  
    # Query the Templates table to get the template with the given id
    input_string = ""
    template = Template.query.get(id)
    if template.status!="Approved":
        error1="This Template is either Pending Approval or has been Rejected"
        return render_template("error.html",error=error1)
    if template.template_type == "text":
        agent_content_message_str = template.content
        agent_content_message_json = json.loads(agent_content_message_str)
        input_string = agent_content_message_json['agentContentMessage']['text']
        # Count the required variables based on the template
        number_of_required_variables = len(re.findall(r'\[([^]]+)\]', input_string))
    else:
        number_of_required_variables = 0

    if request.method == 'POST':
        data_file = request.files['data_file']
        filename = secure_filename(data_file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()

        # Verify file extension
        if file_ext not in ['csv', 'xlsx']:
            error1 = "Wrong File Type! Only xlsx or csv allowed"
            return render_template("error.html", error=error1)

        # Load the data into a pandas DataFrame
        try:
            if file_ext == 'csv':
                df = pd.read_csv(data_file)
            elif file_ext == 'xlsx':
                df = pd.read_excel(data_file)
        except:
            error1 = "Unable to read data, file corrupt or invalid"
            return render_template("error.html", error=error1)
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        # Check number of columns
        num_columns = df.shape[1]
        required_columns = number_of_required_variables + 1
        if num_columns < required_columns:
            error1 = f"This template requires {required_columns} columns, only {num_columns} found"
            return render_template("error.html", error=error1)
        elif num_columns > required_columns:
            # Drop extra columns
            df.drop(df.columns[required_columns:], axis=1, inplace=True)
        
        # Validate the mobile numbers in the first column
        for number in df.iloc[:, 0]:
            if not re.match(r'^91\d{10}$', str(number)):
                error1 = "Invalid mobile number found!! Mobile numbers should be 12 digits and start with 91."
                return render_template("error.html", error=error1)
        

        if number_of_required_variables > 0:
            # Concatenate values with '|' and create a new column 'variables'
            df['variables'] = df.iloc[:, 1:].apply(lambda x: '|'.join(x.dropna().astype(str)), axis=1)
            # Drop the original columns used for concatenation
            df.drop(df.columns[1:-1], axis=1, inplace=True)
        else:
            # Create a new column 'variables' with null values
            df['variables'] = None
        #################
        campaign_uid = str(uuid.uuid4())
        df['campaign_uid'] = campaign_uid
        df['template_id'] = template.TemplateID 
        df['internal_id'] = template.Internal_ID
        df.rename(columns={df.columns[0]: 'mobile_number', df.columns[1]: 'variables'}, inplace=True)
        df['status']="pending"
        
        #################
        ## Save
            # Create a list of CampaignData objects for batch insertion
        rows_to_insert = [
            CampaignData(
                mobile_number=row['mobile_number'],
                variables=row['variables'],
                campaign_uid=row['campaign_uid'],
                TemplateID=row['template_id'],
                internal_id=row['internal_id'],
                status=row['status']
            ) for index, row in df.iterrows()
        ]

        # Perform batch insert
        try:
            db.session.bulk_save_objects(rows_to_insert)
            db.session.commit()
            print("Inserted")
        except Exception as e:
            db.session.rollback()
            error1 = f"Failed to insert data into CampaignData table. Error: {str(e)}"
            return render_template("error.html", error=error1)
        ######################
        try:
            # Fetch form data
            campaign_name = request.form['campaign_name']
            start_date_str = request.form['start_date']
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')  # Convert string to datetime
            
            # Other variables
            
            has_variables = "1" if number_of_required_variables > 0 else "0"
            
            # Create new Campaign record
            new_campaign = Campaign(
                name=campaign_name,
                TemplateID=template.TemplateID,
                start_date=start_date,
                status="Created",
                created_by=session["user_id"],
                created_date=datetime.utcnow(),
                Internal_ID=template.Internal_ID,
                campaign_uid=campaign_uid,
                has_variables=has_variables
            )
            
            db.session.add(new_campaign)
            db.session.commit()
        except SQLAlchemyError as e:
            error1 = "Database error: " + str(e)
            return render_template("error.html", error=error1)
        except Exception as e:
            error1 = "An unknown error occurred: " + str(e)
            return render_template("error.html", error=error1)

        # If everything goes well
        if session['role']=="Admin":
            alert = f"Campaign Created succesfully! Campaign ID is {campaign_uid}"
            return render_template("alert-admin.html", alert=alert)
        else:
            alert = f"Campaign Created succesfully! Campaign ID is {campaign_uid}"
            return render_template("alert.html", alert=alert)

    ##########################################################################

    ################### Get ##################################################

    return render_template(
        'start-campaign.html',
        id=id,
        number_of_required_variables=number_of_required_variables,
        template=template,
        input_string=input_string
    )

#####################################################################################


@app.route('/manage_campaigns', methods=['GET'])
def manage_campaigns():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session["user_id"]
    role = session['role']

    if not user_id:
        return redirect(url_for('login'))

    # Get the page number from the query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Adjust the number of items per page as needed

    # Use paginate to get the paginated campaigns
    campaigns = Campaign.query.filter_by(created_by=user_id).paginate(page=page, per_page=per_page)

    return render_template('campaign-manage.html', campaigns=campaigns)
#####################################################################################
@app.route('/manage_campaigns-admin', methods=['GET'])
def manage_campaigns_admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session["user_id"]
    role = session['role']
    if not user_id or role != "Admin":
        return redirect(url_for('login'))

    # Get the admin's username using user_id
    admin_user = User.query.filter_by(user_id=user_id).first()
    if admin_user is None:
        return redirect(url_for('login'))  # or handle error appropriately

    admin_username = admin_user.username

    # Get all user_ids of users assigned to this admin
    assigned_user_ids = [user.user_id for user in User.query.filter_by(assigned_to=admin_username).all()]

    # Include the admin's user_id in the list
    all_user_ids = assigned_user_ids + [user_id]

    # Get the page number from the query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Adjust the number of items per page as needed

    # Modify the query to get campaigns created by the admin and assigned users
    campaigns = Campaign.query.filter(Campaign.created_by.in_(all_user_ids)).paginate(page=page, per_page=per_page)

    return render_template('campaign-manage-admin.html', campaigns=campaigns)

#####################################################################################
@app.route('/view_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def view_campaign(campaign_id):
    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if not campaign:
        return redirect(url_for('manage_campaigns'))

    template = Template.query.filter_by(TemplateID=campaign.TemplateID).first() 
    content = json.loads(template.content) if template and template.content else {}

    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.status = request.form['status']
        db.session.commit()
        return redirect(url_for('view_campaign_a', campaign_id=campaign_id))

    campaign_metrics = calculate_campaign_metrics_single(campaign.campaign_uid)
    if campaign_metrics:
        # Unpack the metrics and cumulative values
        campaign_metrics_data, total_cumulative, sent_cumulative, was_read_cumulative, delivered_cumulative, blacklisted_cumulative, failed_cumulative = campaign_metrics
    else:
        # Handle the case where no metrics are found
        campaign_metrics_data = {}
        total_cumulative = sent_cumulative = was_read_cumulative = delivered_cumulative = blacklisted_cumulative = failed_cumulative = 0
 

    return render_template('campaign-detail.html',
                           campaign_metrics=campaign_metrics_data, 
                           total_cumulative=total_cumulative, 
                           sent_cumulative=sent_cumulative, 
                           was_read_cumulative=was_read_cumulative, 
                           delivered_cumulative=delivered_cumulative, 
                           blacklisted_cumulative=blacklisted_cumulative, 
                           failed_cumulative=failed_cumulative, 
                           content=content, 
                           campaign=campaign, 
                           template=template)
##################################################################################
@app.route('/view_campaign_a/<int:campaign_id>', methods=['GET', 'POST'])
def view_campaign_a(campaign_id):
    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if not campaign:
        return redirect(url_for('manage_campaigns-admin'))

    template = Template.query.filter_by(TemplateID=campaign.TemplateID).first() 
    content = json.loads(template.content) if template and template.content else {}

    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.status = request.form['status']
        db.session.commit()
        return redirect(url_for('view_campaign_a', campaign_id=campaign_id))

    campaign_metrics = calculate_campaign_metrics_single(campaign.campaign_uid)
    if campaign_metrics:
        # Unpack the metrics and cumulative values
        campaign_metrics_data, total_cumulative, sent_cumulative, was_read_cumulative, delivered_cumulative, blacklisted_cumulative, failed_cumulative = campaign_metrics
    else:
        # Handle the case where no metrics are found
        campaign_metrics_data = {}
        total_cumulative = sent_cumulative = was_read_cumulative = delivered_cumulative = blacklisted_cumulative = failed_cumulative = 0


    return render_template('campaign-detail-admin.html',
                           campaign_metrics=campaign_metrics_data, 
                           total_cumulative=total_cumulative, 
                           sent_cumulative=sent_cumulative, 
                           was_read_cumulative=was_read_cumulative, 
                           delivered_cumulative=delivered_cumulative, 
                           blacklisted_cumulative=blacklisted_cumulative, 
                           failed_cumulative=failed_cumulative, 
                           content=content, 
                           campaign=campaign, 
                           template=template)

##################################################################################
@app.route('/update_campaign_status', methods=['POST'])
def update_campaign_status():
    try:
        action = request.form.get('action')
        campaign_id = request.form.get('campaign_id') 

        if action == 'Paused':
            new_status = 'Paused'
        elif action == 'Start':
            new_status = 'Running'
        elif action != 'update_leads':
            error1 = "Invalid action."
            return render_template("error.html", error=error1)
        else:
            #########################################################
            alert = "Contact Admin"
            return render_template("alert.html", alert=alert)
            #########################################################
            # Handle other actions or return an error
            
        # Query the campaign to update
        campaign_to_update = Campaign.query.filter_by(campaign_id=campaign_id).first()

        if campaign_to_update:
            campaign_to_update.status = new_status
            db.session.commit()

            alert = "Campaign updated successfully!"
            return render_template("alert.html", alert=alert)
        else:
            error1 = "Error: Campaign not found."
            return render_template("error.html", error=error1)

    except Exception as e:
        # Log the error for debugging
        error1 = SystemError(e)
        return render_template("error.html", error=error1)

###################################################################################
@app.route('/sendmessage', methods=['POST'])
def send_message():
    incoming_payload = request.json

    # Fetch the Internal_ID and TemplateID from JSON payload
    internal_id = incoming_payload.get('Internal_ID')
    template_id = incoming_payload.get('TemplateID')
    msisdn = incoming_payload.get('msisdn')

    if not internal_id or not template_id or not msisdn:
        return jsonify({"error": "Internal_ID, TemplateID, and msisdn are required"}), 400

    # Query the Templates table to check if the template is approved
    template = Template.query.filter_by(Internal_ID=internal_id, TemplateID=template_id, status='Approved').first()
    if not template:
        return jsonify({"error": "Invalid template"}), 400

    # Query the AgentInformation table to check if the user is active
    agent_info = AgentInformation.query.filter_by(Internal_ID=internal_id, Status='Active').first()
    if not agent_info:
        return jsonify({"error": "Invalid User"}), 400

    # Prepare the payload for further processing
    agent_content_message_str = template.content  # This is the agentContentMessage as a string from DB
    agent_content_message_json = json.loads(agent_content_message_str)  # Convert string to JSON
    if "variables" in incoming_payload:
        if template.template_type!="text":
            return "Invalid Template Variables allowed only in text templates"
        input_string  = agent_content_message_json['agentContentMessage']['text']
        variables_field = incoming_payload.get("variables", "")
        variable_values = variables_field.split(",")
        placeholders = re.findall(r'\[([^]]+)\]', input_string)
        if len(variable_values) != len(placeholders):
            # Return an error message if the counts do not match
            error_message = f"Error: Expected {len(placeholders)} values in 'variables' field, but received {len(variable_values)}."
            return error_message
        for placeholder, value in zip(placeholders, variable_values):
            input_string = input_string.replace(f"[{placeholder}]", value)
        agent_content_message_json['agentContentMessage']['text']=input_string

        
    # Prepare the final payload
    final_payload = {
        "customerId": agent_info.customerId,
        "subAccountId": agent_info.subAccountId,
        "agentId": agent_info.agentId,
        "msisdn": msisdn
    }
    print("=================================")
    print(agent_content_message_json)
    print("=================================")
    final_payload.update(agent_content_message_json)  # Merge the two dictionaries
    url = "https://iqwhatsapp.airtel.in/gateway/airtel-xchange/whatsapp-message-acceptor/v1/rcs/message/send"
     # Headers for the POST request
    headers = {
        "Content-Type": "application/json",
        "X-Consumer-Username": agent_info.customerId
    }
    response = requests.post(url, headers=headers, json=final_payload)
    print(response)
    print("Payload====>")
    print(final_payload)
    return "Done"

###################################################################################
###################################################################################
###################################################################################
@app.route('/apiendpoint', methods=['POST'])
def api_endpoint():
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400

        action = data.get('action')
        action_details = data.get('actiondetails')
        if action=="deletetemplate" or action=="previewtemplate" or action=="approvetemplate" or action=="rejecttemplate":
            action_details="temp"
        if action is None or action_details is None:
            return jsonify({"error": "Missing action or actiondetails field"}), 400
        if action == 'createaccount':
            # Check for all fields 
            username = action_details.get('username')
            password = action_details.get('password')
            # Check if username already exists
            exists = User.query.filter_by(username=username).first()
            if exists:
                return jsonify({"error": "Username Already Exits"}), 500
            role = "User"
            hashed_password = generate_password_hash(password) 
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            # Additional Information
            Created_Date = int(time.time() * 1000)
            customerId = data.get('customerId')
            subAccountId = data.get('subAccountId')
            agentId = data.get('agentId')
            first_part = ''.join(random.choices(string.digits, k=4))
            middle_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            last_part = ''.join(random.choices(string.digits, k=4))
            Internal_ID = first_part + "-" + middle_part + "-" + last_part
            Status = "Active"
            Created_By = "Admin"
            Status_Updated_By = "Admin"
            template_user = username  # from the form
            new_info = AgentInformation(
                Created_Date=Created_Date,
                customerId=customerId,
                subAccountId=subAccountId,
                agentId=agentId,
                Internal_ID=Internal_ID,
                Status=Status,
                Created_By=Created_By,
                Status_Updated_By=Status_Updated_By,
                template_user=template_user
            )
            db.session.add(new_info)
            db.session.commit()
            return jsonify({"Account ID Created": Internal_ID})
        elif action =="createtext":
            Internal_ID = data.get('IID')
            template_user=data.get('user')
            agent_info = AgentInformation.query.filter_by(template_user=template_user,Internal_ID=Internal_ID).first()
            if not agent_info:
                return jsonify({"error": "Invalid IID or User"}), 400
            errors=validate.is_valid_json_text(action_details)
            if errors:
                return jsonify({"errors": errors}), 400
            else:
                
                suggestions = []
                agentContentMessage = {}
                text = action_details["txtName"]
                usagetype=action_details["typeSelect"]
                if len(action_details["suggestions"]) != 0:
                    for items in action_details["suggestions"]:
                        if items["typeOfAction"] == "1":
                            toadd = {
                                "reply": {
                                    "text": items["text"],
                                    "postbackData": items["postback"]
                                }
                            }
                            suggestions.append(toadd)
                        if items["typeOfAction"] == "2":
                            toadd = {
                                "action": {
                                    "text": items["text"],
                                    "postbackData": items["postback"],
                                    "openUrlAction": {
                                        "url": items["url"]
                                    }
                                }
                            }
                            suggestions.append(toadd)
                        if items["typeOfAction"] == "3":
                            toadd = {
                                "action": {
                                    "text": items["text"],
                                    "postbackData": items["postback"],
                                    "dialAction": {
                                        "phoneNumber": items["phoneNo"]
                                    }
                                }
                            }
                            suggestions.append(toadd)

                # Create the JSON object
                agentContentMessage["agentContentMessage"] = {
                    "suggestions": suggestions,
                    "text": text
                }
                # Convert JSON object to a string
                content_str = json.dumps(agentContentMessage)

                # Generate a 16-digit alphanumeric string for TemplateID
                template_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

                current_user_id = (User.query.filter_by(username=template_user).first()).user_id

                # Insert into database
                new_template = Template(
                    content=content_str,
                    created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
                    template_type='text',
                    submitted_by=current_user_id,
                    status='Pending',
                    TemplateID=template_id,
                    Internal_ID=Internal_ID,
                    usagetype=usagetype
                )
                db.session.add(new_template)
                db.session.commit()
                alert =f"New Template Created! Template ID is {template_id}"
                return jsonify({"Success": alert}), 200
        elif action =="createrich":
            Internal_ID = data.get('IID')
            template_user=data.get('user')
            agent_info = AgentInformation.query.filter_by(template_user=template_user,Internal_ID=Internal_ID).first()
            if not agent_info:
                return jsonify({"error": "Invalid IID or User"}), 400
            errors=validate.is_valid_json_rich(action_details)
            if errors:
                return jsonify({"error": errors}), 400
            else:
                suggestions=[]
                suggestionjson=action_details.get('suggestions')
            if len(suggestionjson)!=0:
            # If not empty, means we got suggestion
            # Open the suggestions and see what type of suggestion we got
                for items in suggestionjson:
                    # We are expecting the type of action to be 1 or 2 or 3
                    if items["typeOfAction"]=="1":
                        toadd={
                            "reply": {
                                "text": items["text"],
                                "postbackData": items["postback"]
                            }
                        }
                        suggestions.append(toadd)
                    if items["typeOfAction"]=="2":
                        toadd={
                                "action": {
                                    "text": items["text"],
                                    "postbackData":  items["postback"],
                                    "openUrlAction": {
                                        "url": items["url"]
                                    }
                                }
                            }
                        suggestions.append(toadd)
                    if items["typeOfAction"]=="3":
                        phoneNo="+"+items["phoneNo"]
                        toadd={
                        "action": {
                        "text": items["text"],
                        "postbackData": items["postback"],
                        "dialAction": {
                            "phoneNumber": phoneNo
                        }
                        }}
                        suggestions.append(toadd)

            richacard = {
    "richCard": {
        "standaloneCard": {
            "thumbnailImageAlignment": action_details.get('thumbnailImageAlignment', "LEFT"),
            "cardOrientation": action_details.get('cardOrientation', "VERTICAL"),
            "cardContent": {
                "title": action_details.get('title', ""),
                "description": action_details.get('description', ""),
                "media": {
                    "height": action_details.get('mediaHeight', "SHORT"),
                    "contentInfo": {
                        "fileUrl": action_details.get('fileUrl', ""),
                        "forceRefresh": action_details.get('forceRefresh', "false")
                    }
                },
                "suggestions": suggestions  # Moved suggestions inside cardContent
            }
        }
    }
}
            final_structure={"agentContentMessage":richacard}
            final_structure_str = json.dumps(final_structure)
            template_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        # Assuming we have a variable 'current_user_id' that holds the ID of the logged-in user
            current_user_id = (User.query.filter_by(username=template_user).first()).user_id
            new_template = Template(
            created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
            content=final_structure_str,
            template_type='rich',
            submitted_by=current_user_id,  
            status='Pending',
            TemplateID=template_id,
            Internal_ID=Internal_ID
        )
            db.session.add(new_template)
            db.session.commit()
            alert =f"New Template Created! Template ID is {template_id}"
            return jsonify({"Success": alert}), 200
  
        elif action =="createcarousel":
            Internal_ID = data.get('IID')
            template_user=data.get('user')
            agent_info = AgentInformation.query.filter_by(template_user=template_user,Internal_ID=Internal_ID).first()
            if not agent_info:
                return jsonify({"error": "Invalid IID or User"}), 400
            errors=validate.is_valid_json_carousel(action_details)
            if errors:
                return jsonify({"error": errors}), 400
            else:
                cardcontent=[]
                for card_name, card_data in action_details.items():
                    suggestions=[]
                    suggestionjson = card_data.get('suggestions', [])
                    if len(suggestionjson)!=0:
                        for items in suggestionjson:
                            # We are expecting the type of action to be 1 or 2 or 3
                            if items["typeOfAction"]=="1":
                                toadd={
                                    "reply": {
                                        "text": items["text"],
                                        "postbackData": items["postback"]
                                    }
                                }
                                suggestions.append(toadd)
                            if items["typeOfAction"]=="2":
                                toadd={
                                        "action": {
                                            "text": items["text"],
                                            "postbackData":  items["postback"],
                                            "openUrlAction": {
                                                "url": items["url"]
                                            }
                                        }
                                    }
                                suggestions.append(toadd)
                            if items["typeOfAction"]=="3":
                                phoneNo="+"+items["phoneNo"]
                                toadd={
                                "action": {
                                "text": items["text"],
                                "postbackData": items["postback"],
                                "dialAction": {
                                    "phoneNumber": phoneNo
                                }
                                }}
                                suggestions.append(toadd)
                    carditem={
                        "title": card_data.get("title"),
                        "description": card_data.get("description"),
                        "suggestions": suggestions,
                        "media": {
                        "height": card_data.get("mediaHeight"),
                        "contentInfo": {
                            "fileUrl": card_data.get("fileUrl"),
                            "forceRefresh": "false"
                        }
                        }
                    }
                    cardcontent.append(carditem)
                final_structure={"agentContentMessage": {
                                "richCard": {
                                "carouselCard": {
                                    "cardWidth": "MEDIUM",
                                    "cardContents": cardcontent
                                }
                                }
                            }}
                final_structure_str = json.dumps(final_structure)
                template_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            # Assuming we have a variable 'current_user_id' that holds the ID of the logged-in user
                current_user_id = (User.query.filter_by(username=template_user).first()).user_id
                new_template = Template(
                created_date=time.strftime('%Y-%m-%d %H:%M:%S'),
                content=final_structure_str,
                template_type='rich',
                submitted_by=current_user_id,  
                status='Pending',
                TemplateID=template_id,
                Internal_ID=Internal_ID
            )
                db.session.add(new_template)
                db.session.commit()
                alert =f"New Template Created! Template ID is {template_id}"
                return jsonify({"Success": alert}), 400
        elif action=="deletetemplate":
            Internal_ID = data.get('IID')
            username=data.get('user')
            templateid=data.get("TemplateID")
            tuser=User.query.filter_by(username=username).first()
            if not tuser:
                alert =f"User Not Found"
                return jsonify({"Error": alert}), 400
            if tuser.role=="Admin":
                template_to_delete = db.session.query(Template).filter_by(
                TemplateID=templateid,
                Internal_ID=Internal_ID
            ).first()
                if template_to_delete is None:
                    alert =f"Error deleting Template {templateid} , Template not found or access denied"
                    return jsonify({"Error": alert}) ,400
                db.session.delete(template_to_delete)
                db.session.commit()
                alert =f"{templateid} Deleted!!"
                return jsonify({"Success": alert}) ,200
            else:
                template_to_delete = db.session.query(Template).filter_by(
                TemplateID=templateid,
                Internal_ID=Internal_ID,
                submitted_by=tuser.user_id
            ).first()
                if template_to_delete is None:
                    alert =f"Error deleting Template {templateid} , Template not found or access denied"
                    return jsonify({"Error": alert}) ,400
                db.session.delete(template_to_delete)
                db.session.commit()
                alert =f"{templateid} Deleted!!"
                return jsonify({"Success": alert}) ,200
        elif action=="previewtemplate":
            Internal_ID = data.get('IID')
            username=data.get('user')
            templateid=data.get("TemplateID")
            tuser=User.query.filter_by(username=username).first()
            if not tuser:
                alert =f"User Not Found"
                return jsonify({"Error": alert}), 400
            if tuser.role=="Admin":
                template_preview = db.session.query(Template).filter_by(
                TemplateID=templateid,
                Internal_ID=Internal_ID
            ).first()
                if template_preview is None:
                    alert =f"Error  Template {templateid} , Template not found or access denied"
                    return jsonify({"Error": alert}) ,400
                agentContentMessage=template_preview.content
                alert = agentContentMessage
                return jsonify({"agentContentMessage": agentContentMessage}) ,200
            else:
                template_preview = db.session.query(Template).filter_by(
                TemplateID=templateid,
                Internal_ID=Internal_ID,
                submitted_by=tuser.user_id
            ).first()
                if template_preview is None:
                    alert =f"Error  Template {templateid} , Template not found or access denied"
                    return jsonify({"Error": alert}) ,400
                agentContentMessage=template_preview.content
                alert = agentContentMessage
                return jsonify({"agentContentMessage": agentContentMessage}) ,200
        elif action=="approvetemplate":
            Internal_ID = data.get('IID')
            username=data.get('user')
            templateid=data.get("TemplateID")
            tuser=User.query.filter_by(username=username).first()
            if not tuser:
                alert =f"User Not Found"
                return jsonify({"Error": alert}), 400
            if tuser.role=="Admin":
                template = db.session.query(Template).filter_by(
                TemplateID=templateid,
                Internal_ID=Internal_ID
            ).first()
                if template is None:
                    alert =f"Error  Template {templateid} , Template not found or access denied"
                    return jsonify({"Error": alert}) ,400
                template.status = "Approved"
                template.approved_by = tuser.user_id
                template.approved_date = datetime.utcnow()
                db.session.commit()
                alert = f"Template {templateid} has been approved"
                return jsonify({"Success": alert}) ,200
            else:
                alert = "You do not have access to approve a template"
                return jsonify({"Error": alert}) ,400
        elif action=="rejecttemplate":
            Internal_ID = data.get('IID')
            username=data.get('user')
            templateid=data.get("TemplateID")
            tuser=User.query.filter_by(username=username).first()
            if not tuser:
                alert =f"User Not Found"
                return jsonify({"Error": alert}), 400
            if tuser.role=="Admin":
                template = db.session.query(Template).filter_by(
                TemplateID=templateid,
                Internal_ID=Internal_ID
            ).first()
                if template is None:
                    alert =f"Error  Template {templateid} , Template not found or access denied"
                    return jsonify({"Error": alert}) ,400
                template.status = "Declined"
                template.approved_by = tuser.user_id
                template.approved_date = datetime.utcnow()
                db.session.commit()
                alert = f"Template {templateid} has been Rejected"
                return jsonify({"Success": alert}) ,200
            else:
                alert = "You do not have access to approve a template"
                return jsonify({"Error": alert}) ,400


        else:
            return jsonify({"error": "Invalid action"}), 400
        

    except Exception as e:
        return jsonify({"error": str(e)}), 500
###################################################################################
@app.route('/campaign-dashboard')
def campaign_dashboard():
    campaign_metrics, total_cumulative, sent_cumulative, was_read_cumulative, delivered_cumulative, blacklisted_cumulative, failed_cumulative = calculate_campaign_metrics()
    campaign_labels = [campaign['template_id'] for campaign in campaign_metrics]
    delivery_rates = [campaign['delivery_rate'] for campaign in campaign_metrics]
    open_rates = [campaign['open_rate'] for campaign in campaign_metrics]
    bounce_rates = [campaign['bounce_rate'] for campaign in campaign_metrics]
    blacklist_rates = [campaign['blacklist_rate'] for campaign in campaign_metrics]
    sent_to_read_ratios = [campaign['sent_to_read_ratio'] for campaign in campaign_metrics]
     # Calculate additional stats
    total_campaigns_executed = len(campaign_metrics)
    best_performing_campaign = max(campaign_metrics, key=lambda x: x['sent_to_read_ratio'])
    best_performing_day = "Tuesday"  # Placeholder for best performing day
    best_call_to_action = "Link"  # Placeholder for best call to action

    # Pass the metrics and cumulative totals to the template
    return render_template('campaign-dashboard-brand.html', 
                           campaign_labels=campaign_labels, 
                           delivery_rates=delivery_rates,
                           open_rates=open_rates,
                           bounce_rates=bounce_rates,
                           blacklist_rates=blacklist_rates,
                           sent_to_read_ratios=sent_to_read_ratios,
                           total_cumulative=total_cumulative,
                           sent_cumulative=sent_cumulative,
                           was_read_cumulative=was_read_cumulative,
                           delivered_cumulative=delivered_cumulative,
                           blacklisted_cumulative=blacklisted_cumulative,
                           failed_cumulative=failed_cumulative,total_campaigns_executed=total_campaigns_executed,
                           best_performing_campaign=best_performing_campaign['template_id'],
                           best_performing_day=best_performing_day,
                           best_call_to_action=best_call_to_action)
###################################################################################
@app.route('/campaign-dashboard-admin')
def campaign_dashboard_admin():
    campaign_metrics, total_cumulative, sent_cumulative, was_read_cumulative, delivered_cumulative, blacklisted_cumulative, failed_cumulative = calculate_campaign_metrics()
    total_templates, Pending,Approved,Declined =calculate_template_metrics_admin()
    campaign_labels = [campaign['template_id'] for campaign in campaign_metrics]
    delivery_rates = [campaign['delivery_rate'] for campaign in campaign_metrics]
    open_rates = [campaign['open_rate'] for campaign in campaign_metrics]
    bounce_rates = [campaign['bounce_rate'] for campaign in campaign_metrics]
    blacklist_rates = [campaign['blacklist_rate'] for campaign in campaign_metrics]
    sent_to_read_ratios = [campaign['sent_to_read_ratio'] for campaign in campaign_metrics]
     # Calculate additional stats
    total_campaigns_executed = len(campaign_metrics)
    best_performing_campaign = max(campaign_metrics, key=lambda x: x['sent_to_read_ratio'])
    best_performing_day = "Tuesday"  # Placeholder for best performing day
    best_call_to_action = "Link"  # Placeholder for best call to action

    # Pass the metrics and cumulative totals to the template
    return render_template('campaign-dashboard.html', 
                           campaign_labels=campaign_labels, 
                           delivery_rates=delivery_rates,
                           open_rates=open_rates,
                           bounce_rates=bounce_rates,
                           blacklist_rates=blacklist_rates,
                           sent_to_read_ratios=sent_to_read_ratios,
                           total_cumulative=total_cumulative,
                           sent_cumulative=sent_cumulative,
                           was_read_cumulative=was_read_cumulative,
                           delivered_cumulative=delivered_cumulative,
                           blacklisted_cumulative=blacklisted_cumulative,
                           failed_cumulative=failed_cumulative,total_campaigns_executed=total_campaigns_executed,
                           best_performing_campaign=best_performing_campaign['template_id'],
                           best_performing_day=best_performing_day,
                           best_call_to_action=best_call_to_action,total_templates=total_templates, Pending=Pending,Approved=Approved,Declined=Declined)


###################################################################################
def calculate_campaign_metrics():
    campaigns = CampaignReport.query.all()
    campaign_metrics = []

    # Initialize cumulative totals
    total_cumulative = sent_cumulative = was_read_cumulative = 0
    delivered_cumulative = blacklisted_cumulative = failed_cumulative = 0

    for campaign in campaigns:
        # Increment cumulative totals
        total_cumulative += campaign.Total
        sent_cumulative += campaign.Sent
        was_read_cumulative += campaign.wasRead
        delivered_cumulative += campaign.Delivered
        blacklisted_cumulative += campaign.Blacklisted
        failed_cumulative += campaign.Failed

        if campaign.Sent:  # Avoid division by zero
            delivery_rate = (campaign.Delivered / campaign.Sent) * 100
            open_rate = (campaign.wasRead / campaign.Delivered) * 100 if campaign.Delivered else 0
            bounce_rate = (campaign.Failed / campaign.Sent) * 100
            blacklist_rate = (campaign.Blacklisted / campaign.Sent) * 100
            sent_to_read_ratio = (campaign.wasRead / campaign.Sent)
        else:
            delivery_rate = open_rate = bounce_rate = blacklist_rate = sent_to_read_ratio = 0

        campaign_metrics.append({
            'template_id': campaign.TemplateID,
            'delivery_rate': delivery_rate,
            'open_rate': open_rate,
            'bounce_rate': bounce_rate,
            'blacklist_rate': blacklist_rate,
            'sent_to_read_ratio': sent_to_read_ratio,
        })

    return campaign_metrics, total_cumulative, sent_cumulative, was_read_cumulative, delivered_cumulative, blacklisted_cumulative, failed_cumulative
###################################################################################
def calculate_campaign_metrics_single(cid):
    # Query for the campaign with the given campaign_uid
    campaign = CampaignReport.query.filter_by(campaign_uid=cid).first()
    if not campaign:
        return None, 0, 0, 0, 0, 0, 0  # Return None or appropriate error response

    # Calculate metrics for the single campaign
    total = campaign.Total
    sent = campaign.Sent
    was_read = campaign.wasRead
    delivered = campaign.Delivered
    blacklisted = campaign.Blacklisted
    failed = campaign.Failed

    delivery_rate = (delivered / sent) * 100 if sent else 0
    open_rate = (was_read / delivered) * 100 if delivered else 0
    bounce_rate = (failed / sent) * 100 if sent else 0
    blacklist_rate = (blacklisted / sent) * 100 if sent else 0
    sent_to_read_ratio = (was_read / sent) if sent else 0

    campaign_metrics = {
        'template_id': campaign.TemplateID,
        'delivery_rate': delivery_rate,
        'open_rate': open_rate,
        'bounce_rate': bounce_rate,
        'blacklist_rate': blacklist_rate,
        'sent_to_read_ratio': sent_to_read_ratio,
    }

    return campaign_metrics, total, sent, was_read, delivered, blacklisted, failed

###################################################################################
# Assuming db is the SQLAlchemy instance and Template is the model for the templates table

def calculate_template_metrics_admin():
    # Query for total number of templates
    total_templates = Template.query.count()

    # Query for count of different statuses

    Pending= Template.query.filter_by(status='Pending').count()
    Approved= Template.query.filter_by(status='Approved').count()
    Declined= Template.query.filter_by(status='Declined').count()
    print("Herererererer")
    return total_templates, Pending,Approved,Declined

# Example usage




###################################################################################

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/rbm_policy', methods=['GET'])
def rbm_policy():
    return render_template('rbm-policy.html')

@app.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')

@app.route('/brand-profile', methods=['GET'])
def brand_profile():
    return render_template('brand-profile.html')

@app.route('/change-password', methods=['GET'])
def change_password():
    return render_template('brand-change-password.html')

@app.route('/admin-change-password', methods=['GET'])
def admin_change_password():
    return render_template('admin-change-password.html')

@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/signup-verification-sent', methods=['GET'])
def signup_verification_sent():
    return render_template('signup-verification-sent.html')

@app.route('/signup-verification-success', methods=['GET'])
def signup_verification_sucess():
    return render_template('signup-verification-sucess.html')

@app.route('/set-account-password', methods=['GET'])
def set_account_password():
    return render_template('set-account-password.html')

@app.route('/password-set-success', methods=['GET'])
def password_set_success():
    return render_template('password-set-success.html')

@app.route('/mobile-number-verification', methods=['GET'])
def mobile_number_verification():
    return render_template('mobile-number-verification.html')

@app.route('/mobile-otp-verification', methods=['GET'])
def mobile_otp_verification():
    return render_template('mobile-otp-verification.html')

@app.route('/mobile-number-verification-success', methods=['GET'])
def mobile_number_verification_success():
    return render_template('mobile-number-verification-success.html')

@app.route('/aggregator-details', methods=['GET'])
def aggregator_details():
    return render_template('aggregator-details.html')

@app.route('/aggregator-details-review', methods=['GET'])
def aggregator_details_review():
    return render_template('aggregator-details-review.html')


###################################################################################

###################################################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9900, debug=True)







