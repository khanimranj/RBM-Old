import re

def is_valid_json_text(action_details):
    errors = []
    txt_name = action_details.get('txtName')
    type_select = action_details.get('typeSelect')
    suggestions = action_details.get('suggestions')
    # Validate txtName
    if not txt_name:
        errors.append("txtName cannot be blank.")
    
    # Validate typeSelect
    if not type_select or type_select not in ["OTP", "Transactional", "Promotion"]:
        errors.append("typeSelect cannot be blank and must be either 'OTP', 'Transactional', or 'Promotion'.")
    
    # Validate suggestions
    if len(suggestions) > 3:
        errors.append("suggestions cannot exceed 3 items.")
    
    for i, suggestion in enumerate(suggestions):
        type_of_action = suggestion.get('typeOfAction')
        text = suggestion.get('text')
        postback = suggestion.get('postback')
        url = suggestion.get('url')
        phone_no = suggestion.get('phoneNo')
        
        if not type_of_action or type_of_action not in ["1", "2", "3"]:
            errors.append(f"Suggestion {i+1} has an invalid typeOfAction.")
        if not text:
            errors.append(f"Suggestion {i+1} is missing the text field.")
        if not postback:
            errors.append(f"Suggestion {i+1} is missing the postback field.")
        
        if type_of_action == "2":
            print("CHECKING URL")
            if not url or not re.match(r'http[s]?://', url):
                print("CAME TO NOT URL")
                errors.append(f"Suggestion {i+1} has an invalid or missing URL.")
        if type_of_action == "3":
            if not phone_no or not re.fullmatch(r'\d{12}', phone_no):
                print("CHECKING PHONE NUMBER")
                errors.append(f"Suggestion {i+1} has an invalid or missing phone number.")
    
    return errors

def is_valid_json_rich(data):
    errors = []

    # Check if thumbnailImageAlignment is one of the allowed values
    if data.get('thumbnailImageAlignment') not in ['LEFT', 'RIGHT', 'CENTER']:
        errors.append("Invalid thumbnailImageAlignment")
    
    # Check if cardOrientation is one of the allowed values
    if data.get('cardOrientation') not in ['VERTICAL', 'HORIZONTAL']:
        errors.append("Invalid cardOrientation")
    
    # Check if mediaHeight is one of the allowed values
    if data.get('mediaHeight') not in ['SHORT', 'MEDIUM', 'TALL']:
        errors.append("Invalid mediaHeight")

    # Check if fileUrl is a string (assuming it's a URL)
    if not isinstance(data.get('fileUrl'), str):
        errors.append("Invalid fileUrl")
    
    # Check if forceRefresh is a string
    if not isinstance(data.get('forceRefresh'), str):
        errors.append("Invalid forceRefresh")
        
    # Validate suggestions if they exist
    suggestions = data.get('suggestions', [])
    if len(suggestions) > 3:
        errors.append("suggestions cannot exceed 3 items.")

    for i, suggestion in enumerate(suggestions):
        type_of_action = suggestion.get('typeOfAction')
        text = suggestion.get('text')
        postback = suggestion.get('postback')
        url = suggestion.get('url')
        phone_no = suggestion.get('phoneNo')

        if not type_of_action or type_of_action not in ["1", "2", "3"]:
            errors.append(f"Suggestion {i+1} has an invalid typeOfAction.")
        if not text:
            errors.append(f"Suggestion {i+1} is missing the text field.")
        if not postback:
            errors.append(f"Suggestion {i+1} is missing the postback field.")
        
        if type_of_action == "2":
            if not url or not re.match(r'http[s]?://', url):
                errors.append(f"Suggestion {i+1} has an invalid or missing URL.")
        if type_of_action == "3":
            if not phone_no or not re.fullmatch(r'\d{12}', phone_no):
                errors.append(f"Suggestion {i+1} has an invalid or missing phone number.")
    return errors

def is_valid_json_rich2(data):
    errors = []

    # Check if mediaWidth is one of the allowed values
    if data.get('mediaWidth') not in ['SMALL', 'MEDIUM']:
        errors.append("Invalid mediaHeight")
    
    # Check if mediaHeight is one of the allowed values
    if data.get('mediaHeight') not in ['SHORT', 'MEDIUM']:
        errors.append("Invalid mediaHeight")

    # Check if fileUrl is a string (assuming it's a URL)
    if not isinstance(data.get('fileUrl'), str):
        errors.append("Invalid fileUrl")
    
    # Check if forceRefresh is a string
    if not isinstance(data.get('forceRefresh'), str):
        errors.append("Invalid forceRefresh")
        
    # Validate suggestions if they exist
    suggestions = data.get('suggestions', [])
    if len(suggestions) > 3:
        errors.append("suggestions cannot exceed 3 items.")

    for i, suggestion in enumerate(suggestions):
        type_of_action = suggestion.get('typeOfAction')
        text = suggestion.get('text')
        postback = suggestion.get('postback')
        url = suggestion.get('url')
        phone_no = suggestion.get('phoneNo')

        if not type_of_action or type_of_action not in ["1", "2", "3"]:
            errors.append(f"Suggestion {i+1} has an invalid typeOfAction.")
        if not text:
            errors.append(f"Suggestion {i+1} is missing the text field.")
        if not postback:
            errors.append(f"Suggestion {i+1} is missing the postback field.")
        
        if type_of_action == "2":
            if not url or not re.match(r'http[s]?://', url):
                errors.append(f"Suggestion {i+1} has an invalid or missing URL.")
        if type_of_action == "3":
            if not phone_no or not re.fullmatch(r'\d{12}', phone_no):
                errors.append(f"Suggestion {i+1} has an invalid or missing phone number.")
    return errors

def is_valid_json_carousel(carousel_data):
    errors = []
    card_count = 0
    # Loop through each card in carousel_data
    for card_name, card_data in carousel_data.items():
        card_count += 1
        is_not_valid = is_valid_json_rich2(card_data)
        if  is_not_valid:
            errors.extend([f"{card_name}: {err}" for err in is_not_valid])
    
    # Check for the constraint that we can have up to 10 cards
    if card_count > 10:
        errors.append("Cannot have more than 10 cards.")
    return errors


