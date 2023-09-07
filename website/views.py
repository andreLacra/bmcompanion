from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, Response
from flask_login import login_required, current_user
from .models import Company, Seeking, Offering, User, MatchRequest, Matched, Message, Meeting, BackupMessage, Unmatched
from . import db
import vobject
from ics import Calendar, Event
import json
import re
import os
from collections import defaultdict
from sqlalchemy import select, desc, or_
from sqlalchemy.orm import joinedload
from datetime import datetime, date


views = Blueprint('views', __name__)

# Phone Number Validation
def is_valid_phone_number(phone_number_str):
    pattern = r'^\+?\d{1,2}?\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{4}$'
    return bool(re.match(pattern, phone_number_str))

def is_valid_desc(description):
    if len(description) < 6:
        return False
    else:
        return True

# Function to validate a YouTube URL
def is_valid_youtube_url(url):
    # Regular expression pattern for matching YouTube video URLs
    youtube_url_pattern = r"(https?://)?(www\.)?(youtube\.com/)([A-Za-z0-9_-]+)"
    
    # Use re.match to check if the URL matches the pattern
    match = re.match(youtube_url_pattern, url)
    
    # If there's a match and the video ID is not empty, consider it valid
    if match:
        return True
    else:
        return False

# Function to validate a LinkedIn URL
def is_valid_linkedin_url(url):
    # Regular expression pattern for matching LinkedIn profile and company URLs
    linkedin_url_pattern = r"(https?://)?(www\.)?linkedin\.com/(in|company)/[A-Za-z0-9_-]+"
    
    # Use re.match to check if the URL matches the pattern
    match = re.match(linkedin_url_pattern, url)
    
    # If there's a match, consider it valid
    if match:
        return True
    else:
        return False
    
# Function to validate a Facebook URL
def is_valid_facebook_url(url):
    # Regular expression pattern for matching Facebook profile and page URLs
    facebook_url_pattern = r"(https?://)?(www\.)?facebook\.com/([A-Za-z0-9_-]+)"
    
    # Use re.match to check if the URL matches the pattern
    match = re.match(facebook_url_pattern, url)
    
    # If there's a match, consider it valid
    if match:
        return True
    else:
        return False
    
# Function to validate a Twitter URL
def is_valid_twitter_url(url):
    # Regular expression pattern for matching Twitter profile URLs
    twitter_url_pattern = r"(https?://)?(www\.)?twitter\.com/([A-Za-z0-9_]+)"
    
    # Use re.match to check if the URL matches the pattern
    match = re.match(twitter_url_pattern, url)
    
    # If there's a match, consider it valid
    if match:
        return True
    else:
        return False


# FLASK ---------

currentBusinessID = None
requestMatchMessage = None
dateMessage = None

@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    global currentBusinessID, requestMatchMessage

    requestMatchMessage = None

    # Set current business ID to none so users can't access other businesses or unselectted business
    currentBusinessID = None  
    isDisplay = False
    isDisplay = 0

    businessCount = 0
    allBusinessCount = 0

    company = Company.query.filter_by(user_id=current_user.id).all()
    allCompany = Company.query.all()    

    # Display Business Count 
    if(company):
        for countC in company:
            businessCount += 1

    if(allCompany):
        for countAC in allCompany:
            allBusinessCount += 1

    meetings = db.session.query(Meeting, Company).join(Company, or_(Meeting.receiver_id == Company.id, Meeting.request_id == Company.id)).filter(Company.user_id == current_user.id, Meeting.status == 'Accepted').all()

    meetings_data = []
    for meeting, company1 in meetings:
        meeting_data = {
            'id': meeting.id,
            'request_id': meeting.request_id,
            'title': meeting.title,
            'mode': meeting.mode,
            'duration': meeting.duration,
            'time': meeting.time.strftime('%I:%M %p'),
            'date': meeting.date.strftime('%Y-%b-%d'),
            'dateDay': meeting.date.strftime('%d'),
            'dateMonth': meeting.date.strftime('%b'),
            'link': meeting.link,
            'details': meeting.details,
            'status': meeting.status.upper(),
            'business_name': company1.business_name,
            # Add other company details as needed
        }
        meetings_data.append(meeting_data)

    # Get the Seeking data for the user's company
    user_company = db.session.query(Company).join(User).filter(User.id == current_user.id).first()
    # user_seeking = user_company.seeking


    return render_template('dashboard.html',isDisplay=isDisplay, user=current_user, 
                           company=company, allCompany=allCompany, 
                           businessCount=businessCount, allBusinessCount=allBusinessCount,
                           meetings_data=meetings_data)


# Get Company ID
@views.route('/getCompanyID', methods=['POST'])
@login_required
def companyID():
    global currentBusinessID

    company = json.loads(request.data)
    companyId = company['compID']
    company = Company.query.get(companyId)
    currentBusinessID = company

    return jsonify({}) #Returns nothing


@views.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    global currentBusinessID, dateMessage, dateMessage, requestMatchMessage

    currentBusinessID = Company.query.get(id)

    requestMatchMessage = None
    dateMessage = None

    if(id == None):
        return redirect(url_for('views.dashboard'))
    
    # Build a query
    queryOffering = select(Offering.category).where(Offering.company_id == id) # Query for offerings
    currentBusinessID = Company.query.get(id)

    # Execute the query
    offerings = db.session.execute(queryOffering).fetchall()


    # CHAT SYSTEM ----------
    # Get a list of user IDs matched with the current user
    # matched_business_ids = Matched.query.filter_by(company_id=id).with_entities(Matched.matched_id).order_by((Matched.priority.desc())).all()
    # print(f'MATCHED BUSINESSES ID: {matched_business_ids}')

    # matched_business_ids = [row[0] for row in matched_business_ids]  # Extract IDs from the list


    # matched_businesses = None
    # if matched_business_ids:
    #     matched_businesses_subquery = select(Company).where(Company.id.in_(matched_business_ids))
        
    #     matched_businesses = db.session.execute(matched_businesses_subquery).scalars().all()
    # else:
    #     print("No matched business IDs found.")

    # Query of all matched business in order of descending based on PRIO
    matched_businesses = Company.query.join(
                    Matched, Matched.matched_id == Company.id
                    ).filter(Matched.company_id == id).order_by(desc(Matched.priority)
                    ).all()


    # CHAT LIST FOR UNMATCHED USERS
    unmatched_business_ids = Unmatched.query.filter_by(company_id=id).with_entities(Unmatched.matched_id).all()
    unmatched_business_ids = [row[0] for row in unmatched_business_ids]  # Extract IDs from the list

    unmatched_businesses = None
    if unmatched_business_ids:
        unmatched_businesses_subquery = select(Company).where(Company.id.in_(unmatched_business_ids))
        
        unmatched_businesses = db.session.execute(unmatched_businesses_subquery).scalars().all()
    else:
        print("No unmatched business IDs found.")


    # Count number of matches to print out connections 
    connections = 0
    try:
        for connectionCount in matched_businesses:
            connections += 1
    except:
        connections = 0



    # MEETINGS ----------
    meetings = db.session.query(Meeting, Company).join(Company, Meeting.request_id == Company.id) \
                      .filter(Meeting.receiver_id == id).all()

    meetings_data = []
    for meeting, company1 in meetings:
        meeting_data = {
            'id': meeting.id,
            'request_id': meeting.request_id,
            'title': meeting.title,
            'mode': meeting.mode,
            'duration': meeting.duration,
            'time': meeting.time.strftime('%I:%M %p'),
            'date': meeting.date.strftime('%Y-%b-%d'),
            'dateDay': meeting.date.strftime('%d'),
            'dateMonth': meeting.date.strftime('%b'),
            'link': meeting.link,
            'details': meeting.details,
            'status': meeting.status.upper(),
            'company_id': company1.id, 
            'company_name': company1.business_name 
            # Add other company details as needed
        }
        meetings_data.append(meeting_data)


    requestedMeetings = db.session.query(Meeting, Company).join(Company, Meeting.receiver_id == Company.id) \
                      .filter(Meeting.request_id == id).all()
    
    requested_meetings_data = []
    for meeting1, company2 in requestedMeetings:
        requested_meeting_data = {
            'id': meeting1.id,
            'title': meeting1.title,
            'mode': meeting1.mode,
            'duration': meeting1.duration,
            'time': meeting1.time.strftime('%I:%M %p'),
            'date': meeting1.date.strftime('%Y-%b-%d'),
            'dateDay': meeting1.date.strftime('%d'),
            'dateMonth': meeting1.date.strftime('%b'),
            'link': meeting1.link,
            'details': meeting1.details,
            'status': meeting1.status.upper(),
            'company_id': company2.id, 
            'company_name': company2.business_name 
            # Add other company details as needed
        }
        requested_meetings_data.append(requested_meeting_data)    

    # Validate id in link
    showProfile = False
    
    # Get a list of user IDs matched with the current user
    matched_business_ids = Company.query.filter_by(user_id=current_user.id).all()

    for mm in matched_business_ids:
        if(mm.id == id):
            showProfile = (True)
    
    db.session.commit()

    return render_template('profileUser.html', company=currentBusinessID, offerings=offerings,
                           matched_businesses=matched_businesses,
                           showProfile=showProfile, connections=connections,
                           meetings_data=meetings_data, requested_meetings_data=requested_meetings_data,
                           unmatched_businesses=unmatched_businesses)


@views.route('/matches/<int:compid>', methods=['GET', 'POST'])
@login_required
def matches(compid):
    global requestMatchMessage, currentBusinessID

    currentBusinessID = Company.query.get(compid) # This is for the global id


    pending_requests = MatchRequest.query.filter_by(status='pending').all()

    currentBusiness = currentBusinessID

    if(id == None):
        return redirect(url_for('views.dashboard'))
    
    company = Company.query.filter_by(user_id=current_user.id).all()
    allCompany = Company.query.all()


    # DISPLAY POTENTIAL MATCHES
    # Build a query
    query = select(Offering.category).where(Offering.company_id == compid)

    # Execute the query
    offerings = db.session.execute(query).fetchall()



    # DISPLAY MATCHED COMPANIES
    matched_business_ids = Matched.query.filter_by(company_id=compid).with_entities(Matched.matched_id).all()
    matched_business_ids = [row[0] for row in matched_business_ids]  # Extract IDs from the list
    

    matched_businesses = None
    if matched_business_ids:
        matched_businesses_subquery = select(Company).where(Company.id.in_(matched_business_ids))
        
        matched_businesses = db.session.execute(matched_businesses_subquery).scalars().all()
    else:
        print("No matched business IDs found.")



    # Get the current company's seeking and offerings
    current_company_id = compid  # Replace with the actual current company's ID
    current_company_seekings = (
        db.session.query(Seeking)
        .filter_by(company_id=current_company_id)
        .all()
    )

    # Get the categories of the current company's seekings
    current_company_seeking_categories = [seeking.category for seeking in current_company_seekings]

    # Query to find matching offerings for the current company's seekings
    matching_offerings = (
        db.session.query(Offering, Company)
        .join(Company, Offering.company)
        .filter(Offering.category.in_(current_company_seeking_categories))
        .filter(Company.user_id != current_user.id)  # Exclude current company's offerings
        .filter(Offering.company_id != current_company_id)  # Exclude offerings from current company
        .all()
    )

    # Create a dictionary to store offerings grouped by company
    company_offerings = defaultdict(list)

    # Group the offerings by company
    for offering, company1 in matching_offerings:
        company_offerings[company1].append(offering)

    # Print company details along with their offerings
    # for company1, offerings1 in company_offerings.items():
    #     print("Company Name:", company1.business_name)
    #     # existing_request = MatchRequest.query.filter_by(sender_id=currentBusinessID.id, receiver_id=company1.id).first()
    #     for offering in offerings1:
    #         print("Offering Category:", offering.category)
    #     # Print other company details as needed
    #     print("-------")

    # Demands
    matching_offerings = (
        db.session.query(Offering, Company)
        .join(Company, Offering.company)
        .filter(Offering.company_id == Company.id)  # Filter to match the company and offering
        .filter(Company.id.in_(
            db.session.query(MatchRequest.sender_id)
            .filter_by(receiver_id=current_company_id)
        ))
        .all()
    )

    # Create a dictionary to store offerings grouped by company
    requested_match = defaultdict(list)

    # Group the offerings by company
    for offering, company1 in matching_offerings:
        requested_match[company1].append(offering)


    # Validate id in link

    showMatches = False
    
    # Get a list of user IDs matched with the current user
    matched_business_ids = Company.query.filter_by(user_id=current_user.id).all()


    for mm in matched_business_ids:
        if(mm.id == compid):
            print(mm.id)
            showMatches = (True)

    return render_template('matches.html', user=current_user, currentBusiness=currentBusiness, 
                           allCompany=allCompany, company=company,
                           offerings=offerings, company_offerings=company_offerings,
                           pending_requests=pending_requests, requestMatchMessage=requestMatchMessage,
                           showMatches=showMatches, requested_match=requested_match, matched_businesses=matched_businesses)



@views.route('/createBusiness', methods=['GET', 'POST'])
@login_required
def createBusiness():
    message = None

    if(request.method == 'POST'):
        image_file = request.files['logo-data']

        if image_file:
            allowed_extensions = {'jpeg', 'jpg', 'png'}
            imageFileName = image_file.filename.lower()
            
            input_businessName = request.form.get('business-name')   
            input_org = request.form.get('org-membership')   
            input_businessEmail = request.form.get('business-email')   
            input_businessAddress = request.form.get('business-address')   
            input_businessNumber = request.form.get('business-number')   
            input_viber = request.form.get('viber-number')   
            input_whatsapp = request.form.get('whatsapp-number')   
            input_youtube = request.form.get('youtube-link')   
            input_fb = request.form.get('fb-link')   
            input_linkedin = request.form.get('linkedin-link')   
            input_twt = request.form.get('twitter-link')   
            input_businessDesc = request.form.get('business-description')

            image_path = os.path.join("website/static/dashboard_img/", image_file.filename)
            image_file.save(image_path)

            # print("image_path:", image_path)
        

        
        # PLEASE PUT SOCIAL MEDIA LINK VERIFICATION !!!!!! TONIGHT!
        if '.' in imageFileName and imageFileName.rsplit('.', 1)[1] not in allowed_extensions:
            message = "Image logo can only be in a JPEG, JPG, or PNG format. Please try again"
        elif input_youtube and not is_valid_youtube_url(input_youtube):
            message = "Invalid YouTube link. Please try again."
        elif input_fb and not is_valid_facebook_url(input_fb):
             message = "Invalid Faebook link. Please try again."
        elif input_linkedin and not is_valid_linkedin_url(input_linkedin):
            message = "Invalid LinkedIn link. Please try again."
        elif input_twt and not is_valid_twitter_url(input_twt):
            message = "Invalid Twitter link. Please try again."
        elif not is_valid_phone_number(input_businessNumber):
            message = "Invalid inputted phone number. Please try again."
        elif not is_valid_desc(input_businessDesc):
            message = "Description seems too short. Please try again."

        else:
            new_company = Company(
                            logo_data=image_path,
                            business_name=input_businessName,
                            organization=input_org,
                            business_email=input_businessEmail,
                            business_address=input_businessAddress,
                            business_phone=input_businessNumber,
                            viber=input_viber,
                            whatsapp=input_whatsapp,
                            linkedin_link=input_linkedin,
                            youtube_link=input_youtube,
                            fb_link=input_fb,
                            twitter_link=input_twt,
                            business_desc=input_businessDesc,
                            user_id= current_user.id
                        )
            db.session.add(new_company)
            db.session.commit()

            return redirect(url_for('views.dashboard'))

    return render_template('createBusiness.html', message=message)

@views.route('/configureBusiness/<int:id>', methods=['GET', 'POST'])
@login_required
def configureBusiness(id):
    message = None

    business_to_configure = Company.query.get(id)

    # Validate id in link
    showConfigure = False
    
    # Get a list of user IDs matched with the current user
    companies_configure = Company.query.filter_by(user_id=current_user.id).all()

    for cc in companies_configure:
        if(cc.id == id):
            showConfigure = (True)

    if(request.method == 'POST'):
        image_file = request.files['logo-data']

        if image_file and business_to_configure:
            input_businessName = request.form.get('business-name')   
            input_businessEmail = request.form.get('business-email')   
            input_businessAddress = request.form.get('business-address')   
            input_businessNumber = request.form.get('business-number')   
            input_businessDesc = request.form.get('business-description')

            image_path = os.path.join("website/static/dashboard_img/", image_file.filename)
            image_file.save(image_path)

            # print("image_path:", image_path)
        
 
        if not is_valid_phone_number(input_businessNumber):
            message = "Invalid inputted phone number. Please try again."
        elif not is_valid_desc(input_businessDesc):
            message = "Description seems too short. Please try again."
        else:
            business_to_configure.logo_data = image_path
            business_to_configure.business_name = input_businessName
            business_to_configure.business_email = input_businessEmail
            business_to_configure.business_address = input_businessAddress
            business_to_configure.business_phone = input_businessNumber
            business_to_configure.business_desc = input_businessDesc
            business_to_configure.user_id = current_user.id

            db.session.commit()

            return redirect(url_for('views.dashboard'))

    return render_template('configureBusiness.html', message=message, business_to_configure=business_to_configure,
                           showConfigure=showConfigure)



# SEEKING and OFFERING

@views.route('/seeking', methods=['GET', 'POST'])
@login_required
def seeking():
    global currentBusinessID

    selected_categories = request.form.getlist('optionSeeking')
    existing_categories = Seeking.query.all()
    # Update existing options
    for category in existing_categories:
        if(category.company_id == currentBusinessID.id):
            db.session.delete(category)
        # else:
        #     db.session.delete(category)


    # Add new options
    arrCat = []
    for categoryNew in selected_categories:
        new_category = Seeking(business_name=currentBusinessID.business_name, 
                                    category=categoryNew,
                                    user_id= current_user.id,
                                    company_id=currentBusinessID.id
                                )
        arrCat.append(new_category)
        
    db.session.add_all(arrCat)


    db.session.commit()

    return redirect(url_for('views.profile', id=currentBusinessID.id))


@views.route('/offering', methods=['GET', 'POST'])
@login_required
def offering():
    global currentBusinessID

    selected_categories = request.form.getlist('optionOffering')
    existing_categories = Offering.query.all()
    # Update existing options
    for category in existing_categories:
        if(category.company_id == currentBusinessID.id):
            db.session.delete(category)
        # else:
        #     db.session.delete(category)


    # Add new options
    arrCat = []
    qualifier = request.form['business-qualifiers']
    for categoryNew in selected_categories:
        new_category = Offering(business_name=currentBusinessID.business_name, 
                                    category=categoryNew,
                                    qualifier=qualifier,
                                    user_id= current_user.id,
                                    company_id=currentBusinessID.id
                                )
        arrCat.append(new_category)
        
    db.session.add_all(arrCat)

    db.session.commit()

    return redirect(url_for('views.profile', id=currentBusinessID.id))


# MEETINGS
@views.route('/updateStatus/<int:meetingID>', methods=['POST'])
def update_status(meetingID):
    global currentBusinessID

    currentCompany = currentBusinessID.id

    setStatus = request.form['status']
    meeting_to_update = Meeting.query.get(meetingID)

    if meeting_to_update:
        meeting_to_update.status = setStatus
        db.session.commit()

    # Redirect to profile
    return redirect(f"/profile/{currentCompany}")

@views.route('/cancelMeeting/<int:meetingID>')
def cancel_meeting(meetingID):
    global currentBusinessID

    senderCompanyID = currentBusinessID.id

    meeting_to_cancel = Meeting.query.get(meetingID)

    if meeting_to_cancel:
        db.session.delete(meeting_to_cancel)
        db.session.commit()
    
    # Redirect to profile
    return redirect(f"/profile/{senderCompanyID}")


@views.route('/setMeeting/<int:receiverCompanyID>')
@login_required
def setMeeting(receiverCompanyID):
    global currentBusinessID, dateMessage

    displayMeeting = False

    company = Company.query.get(receiverCompanyID)

    # Get a list of user IDs matched with the current user
    matched_business_ids = Matched.query.filter_by(company_id=currentBusinessID.id).with_entities(Matched.matched_id).all()
    matched_business_ids = [row[0] for row in matched_business_ids]  # Extract IDs from the list

    matched_businesses = None
    if matched_business_ids:
        matched_businesses_subquery = select(Company).where(Company.id.in_(matched_business_ids))
        
        matched_businesses = db.session.execute(matched_businesses_subquery).scalars().all()
    else:
        print("No matched business IDs found.")

    for mm in matched_businesses:
        if(mm.id == receiverCompanyID):
            print(mm.id)
            displayMeeting = (True)

    return render_template('meeting.html', company=company, displayMeeting=displayMeeting, 
                           currentBusinessID=currentBusinessID, dateMessage=dateMessage)


@views.route('/meeting_request/<int:receiverID>', methods=['POST'])
@login_required
def send_meeting_request(receiverID):
    global currentBusinessID, dateMessage

    dateMessage = None


    if(request.method == 'POST'):
        # Initialize sender and receiver Company ID
        senderCompanyID = currentBusinessID.id
        receiverCompanyID = receiverID

        title = request.form.get('meeting-title')
        mode = request.form.get('meetingMode')    
        duration = request.form.get('btnradio')    
        time = request.form.get('meeting_time')
        dateM = request.form.get('meetingDate')
        link = request.form.get('meeting-link')
        details = request.form.get('meeting-details')


        # CHANGE DURATION STRING INTO MINUTES
        try:
            military_time = datetime.strptime(time, "%H:%M").time()
            time = military_time.strftime("%H:%M:%S")
            timeNow = datetime.now().strftime("%H:%M:%S")

            date_string = dateM
            date_format = "%B %d, %Y"
            parsed_date = datetime.strptime(date_string, date_format)

            dateM = parsed_date.date()


            # Check date
            current_date = date.today()
            if((dateM == current_date) and (time < timeNow)):
                dateMessage = "You can't set a meeting with the time past current time."
                return redirect(f"/setMeeting/{receiverCompanyID}")
            if(dateM < current_date):
                dateMessage = "You can't set a meeting with the dates before today."
                return redirect(f"/setMeeting/{receiverCompanyID}")

            new_meeting = Meeting(title=title, mode=mode, request_id=senderCompanyID, receiver_id=receiverCompanyID,
                               duration=duration, time=time, date=dateM, link=link, details=details)
            db.session.add(new_meeting)
            db.session.commit()
            dateMessage = None
            return redirect(f"/profile/{senderCompanyID}")
        except:
            dateMessage = "Please select meeting date."
            return redirect(f"/setMeeting/{receiverCompanyID}")


    return jsonify({})



# MATCHINGS
@views.route('/removeMatch', methods=['POST'])
def removeMatch():

    company = json.loads(request.data)
    companyId = company['removeCompID']
    company = Company.query.get(companyId)
    removeID = company

    company_id = currentBusinessID.id
    matched_id = removeID.id

    unmatches = Unmatched.query.filter((Unmatched.company_id == company_id) | (Unmatched.matched_id == company_id),
                                       (Unmatched.company_id == matched_id) | (Unmatched.matched_id == matched_id)).all()
    
    unmatchedMessages = Unmatched.query.filter((Unmatched.company_id == company_id) | (Unmatched.matched_id == company_id),
                                       (Unmatched.company_id == matched_id) | (Unmatched.matched_id == matched_id)).first()
    unmatchedMessages = BackupMessage.query.filter_by(matched_id=unmatchedMessages.id).all()
    
    for unmatch in unmatches:
        db.session.delete(unmatch)
        db.session.commit()

    for unmatchMessage in unmatchedMessages:
        db.session.delete(unmatchMessage)
        db.session.commit()

    return jsonify({})

@views.route('/setPriority/<int:id>', methods=['POST'])
@login_required
def set_priority(id):

    company = Company.query.get(id)
    compSetPrio = company

    company_id = currentBusinessID.id
    receiver_id = compSetPrio.id

    matched = Matched.query.filter((Matched.company_id == company_id) | (Matched.matched_id == company_id),
                                       (Matched.company_id == receiver_id) | (Matched.matched_id == receiver_id)).first()

    priorityInput = request.form.get('priority')
    print(f'PRIO: {priorityInput}')

    if(priorityInput):
        matched.priority = priorityInput
        
    db.session.commit()
    # Redirect to profile
    return redirect(f"/matches/{company_id}")


@views.route('/unmatch', methods=['POST'])
@login_required
def unmatch():
    global currentBusinessID

    company = json.loads(request.data)
    companyId = company['unmatchID']
    company = Company.query.get(companyId)
    unmatchID = company

    company_id = currentBusinessID.id
    matched_id = unmatchID.id


    if company_id and matched_id:
        matched = Matched.query.filter((Matched.company_id == company_id) | (Matched.matched_id == company_id),
                                       (Matched.company_id == matched_id) | (Matched.matched_id == matched_id)).all()
        
        
        match_request = MatchRequest.query.filter((MatchRequest.sender_id == company_id) | (MatchRequest.receiver_id == company_id),
                                       (MatchRequest.sender_id == matched_id) | (MatchRequest.receiver_id == matched_id)).first()

        meetings = Meeting.query.filter((Meeting.request_id == company_id) | (Meeting.receiver_id == company_id),
                                       (Meeting.request_id == matched_id) | (Meeting.receiver_id == matched_id)).all()
        
        matchedMessages = Matched.query.filter((Matched.company_id == company_id) | (Matched.matched_id == company_id),
                                       (Matched.company_id == matched_id) | (Matched.matched_id == matched_id)).first()
        messages = Message.query.filter_by(matched_id=matchedMessages.id).all()


        if(matched):
            if(messages):
                for message in messages:
                    backupMessageQuery = BackupMessage(
                        matched_id=message.matched_id,
                        sender_id=message.sender_id,
                        receiver_id=message.receiver_id,
                        text=message.text,
                        time=message.time 
                    )
                    db.session.add(backupMessageQuery)
                    db.session.delete(message)
                    db.session.commit()
            if(meetings):
                for meeting in meetings:
                    db.session.delete(meeting)
                    db.session.commit()
            if(match_request):
                db.session.delete(match_request)
                db.session.commit()

            # Will delete the official matched datas, and store them seprately as backup
            # so that users can also view the old messages of previous matches
            for m in matched:
                unmatchQuery = Unmatched(
                    id=m.id,
                    company_id=m.company_id,
                    matched_id=m.matched_id
                )
                db.session.add(unmatchQuery)  # store previous matched datas into backups
                db.session.delete(m)
                db.session.commit()

    return jsonify({})


@views.route('/matchRequest', methods=['POST'])
@login_required
def send_request():
    global currentBusinessID
    
    company = json.loads(request.data)
    companyId = company['requestCompID']
    company = Company.query.get(companyId)
    requestMatchCompanyID = company

    sender_id = currentBusinessID.id
    receiver_id = requestMatchCompanyID.id

    global requestMatchMessage
    requestMatchMessage = None


    if sender_id and receiver_id:
        existing_request = MatchRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
        existing_request2 = MatchRequest.query.filter_by(sender_id=receiver_id, receiver_id=sender_id).first()

        if existing_request2:
            if existing_request2.status == 'accepted':
                requestMatchMessage = "You already matched with this Business."
            else:
                requestMatchMessage = "This user's Business already requested a match with you."

        elif existing_request:
            if existing_request.status == 'pending':
                requestMatchMessage = "You already requested a match with this Business."
            else:
                requestMatchMessage = "You already matched with this Business."
            
        else:
            requestMatchMessage = "Match requested successfully."
            matchRequestQuery = MatchRequest(sender_id=sender_id, receiver_id=receiver_id)
            db.session.add(matchRequestQuery)
            db.session.commit()

    else:
        return jsonify({})
    

@views.route('/matchAccept', methods=['POST'])
@login_required
def accept_request():
    global requestMatchMessage

    company = json.loads(request.data)
    companyId = company['acceptCompID']
    company = Company.query.get(companyId)
    requestCompanyID = company

    sender_id = requestCompanyID.id
    receiver_id = currentBusinessID.id

    if sender_id and receiver_id:
        match_request = MatchRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id)
        if match_request:
            matched1 = Matched(company_id=sender_id, matched_id=receiver_id)
            matched2 = Matched(company_id=receiver_id, matched_id=sender_id)

            for mr in match_request:
                mr.status = 'accepted'

            db.session.add_all([matched1, matched2])
            db.session.commit()
            requestMatchMessage = "Matched successfully"
        else:
            requestMatchMessage = "Matched not found"
    else:
        requestMatchMessage = "Matched not found111"

    return jsonify({})

@views.route('/cancelRequest', methods=['POST'])
@login_required
def cancel_request():

    company = json.loads(request.data)
    companyId = company['cancelCompID']
    company = Company.query.get(companyId)
    requestCompanyID = company

    sender_id = requestCompanyID.id
    receiver_id = currentBusinessID.id

    if sender_id and receiver_id:
        match_request = MatchRequest.query.filter_by(sender_id=sender_id, receiver_id=receiver_id).first()
        if match_request and match_request.status == 'pending':
            db.session.delete(match_request)
            db.session.commit()
        else:
            return jsonify({})
    else:
        return jsonify({})

    return jsonify({})


# CHATTING
@views.route('/chat_messages/<int:company_id>/<int:receiver_id>', methods=['GET', 'POST'])
def chat_messages(company_id, receiver_id):

    queryMatchings = None
    messages = None
    if request.method == 'GET':
        matched = Matched.query.filter((Matched.company_id == company_id) | (Matched.matched_id == company_id),
                                       (Matched.company_id == receiver_id) | (Matched.matched_id == receiver_id)).first()
        
        queryMatchings = matched
        if not matched:
            try:
                unmatched = Unmatched.query.filter((Unmatched.company_id == company_id) | (Unmatched.matched_id == company_id),
                                        (Unmatched.company_id == receiver_id) | (Unmatched.matched_id == receiver_id)).first()
                queryMatchings = unmatched
                messages = BackupMessage.query.filter_by(matched_id=queryMatchings.id).order_by(BackupMessage.time).all()
            except:
                None
        else:
            messages = Message.query.filter_by(matched_id=queryMatchings.id).order_by(Message.time).all()

        # Messages length
        if(len(messages) == 11):
            # Find the oldest message based on 'time' column
            oldest_message = Message.query.filter_by(matched_id=queryMatchings.id).order_by(Message.time).first()

            # Delete the oldest message
            db.session.delete(oldest_message)
            db.session.commit()

        businessName = Company.query.get(receiver_id) # get receiver business name to display in chat
        formatted_messages = [{'sender_id': message.sender_id,
                               'name': businessName.business_name,
                               'text': message.text,
                               'timestamp': message.time.strftime('%Y-%m-%d %H:%M')} for message in messages]
        

        return jsonify({'messages': formatted_messages})
    

    elif request.method == 'POST':
        matched = Matched.query.filter((Matched.company_id == company_id) | (Matched.matched_id == company_id),
                                       (Matched.company_id == receiver_id) | (Matched.matched_id == receiver_id)).first()
        if not matched:
            return jsonify({'status': 'failure'})  # No matched companies, return failure status
        
        sender_id = company_id
        text = request.form.get('text')

        new_message = Message(matched_id=matched.id, sender_id=sender_id, receiver_id=receiver_id, text=text)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'status': 'success'})



# Download VCF
@views.route('/download_vcf/<int:id>')
def download_vcf(id):

    # Pass in the ID to the query to fetch the company's data
    companyForVCF = Company.query.get(id)
    compGet = companyForVCF

    # Create a vCard
    contact = vobject.vCard()
    contact.add('fn').value = compGet.business_name
    contact.add('tel').value = compGet.business_phone
    contact.add('email').value = compGet.business_email

    # Serialize vCard to a VCF file
    vcf_data = contact.serialize()

    # Create a response with the VCF file as content
    response = Response(vcf_data, content_type='text/vcard')
    response.headers['Content-Disposition'] = f'attachment; filename={compGet.business_name}.vcf'

    return response

@views.route('/download_ics/<int:id>')
def generate_ics(id):
    # Create an iCalendar object
    c = Calendar()
    
    # Create an event and add it to the calendar
    meetingsQuery = db.session.query(Meeting, Company).join(Company, Meeting.receiver_id == Company.id) \
                      .filter(Meeting.request_id == id).all()

    meetings_data = []
    for meeting, company1 in meetingsQuery:
        meeting_data = {
            'id': meeting.id,
            'title': meeting.title,
            'mode': meeting.mode,
            'duration': meeting.duration,
            'time': meeting.time,
            'date': meeting.date,
            'dateDay': meeting.date.strftime('%d'),
            'dateMonth': meeting.date.strftime('%b'),
            'link': meeting.link,
            'details': meeting.details,
            'status': meeting.status.upper(),
            'company_id': company1.id, 
            'company_name': company1.business_name 
            # Add other company details as needed
        }
        meetings_data.append(meeting_data)

    event = Event()
    event.name = meetings_data[0]["title"]
    event.date = meetings_data[0]["date"]
    event.time = meetings_data[0]["time"]
    event.description = meetings_data[0]["details"]
    event.location = meetings_data[0]["link"]
    event.begin = meetings_data[0]["date"]
    event.end = meetings_data[0]["date"]
    c.events.add(event)
    
    # Generate the .ics content as a string
    ics_content = str(c)
    
    # Create a Flask response with the .ics content and set content type
    response = Response(ics_content, content_type='text/calendar')
    
    # Set the content disposition to trigger a download
    response.headers['Content-Disposition'] = 'attachment; filename=event.ics'
    
    return response