import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Specific X.com login credentials
X_EMAIL = os.getenv("X_EMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PHONE_NUMBER = os.getenv("X_PHONE_NUMBER")
X_PASSWORD = os.getenv("X_PASSWORD")

# Determine the primary login identifier to be used by the application
# Prioritize Username > Email > Phone Number if multiple are set, or just take the first one found.
X_LOGIN_IDENTIFIER = X_USERNAME or X_EMAIL or X_PHONE_NUMBER

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please ensure it is set in your .env file.")

# It's also good practice to check if at least one login identifier and password are set if X.com interaction is core
# For now, tools will handle cases where they might be None, but you could add a startup check here too.
# if not X_LOGIN_IDENTIFIER or not X_PASSWORD:
#     print("Warning: X_LOGIN_IDENTIFIER or X_PASSWORD not fully set in .env. X.com features may not work.") 