"""
References:
    - https://discourse.onlinedegree.iitm.ac.in/t/using-browser-cookies-to-access-discourse-api-in-python/173605
"""

import requests

from ..settings import SETTINGS

# ############## [ END IMPORTS ] ##############


def create_session_with_browser_cookies(discourse_url, cookies):
    """
    Create a requests session with cookies extracted from browser
    
    Parameters:
        discourse_url (str): Base URL of the IIT Madras Discourse instance
        cookies (dict): Dictionary of cookie names and values from browser
        
    Returns:
        requests.Session: Session object with authentication cookies
    """
    session = requests.Session()
    
    # Add each cookie to the session
    for name, value in cookies.items():
        session.cookies.set(name, value, domain=discourse_url.split('//')[1])
    
    return session

# Verify authentication
def verify_session_authentication(_session: requests.Session):
    response = _session.get(f"{SETTINGS.DISCOURSE_URL}/session/current.json")
    if response.status_code == 200:
        resp = response.json()

        # if SETTINGS.DEBUG:
        #     print(resp)
        # print(f"Authenticated as: {user_data['current_user']['username']}")
        # print(f"Successfully connected to IIT Madras BS Program forum")

        return True
    else:
        # print("Authentication failed using browser cookies")
        return False

