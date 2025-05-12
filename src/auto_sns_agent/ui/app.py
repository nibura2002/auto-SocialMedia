import streamlit as st
import subprocess
import sys
import os

def build_ui():
    """Defines and builds the Streamlit user interface."""
    st.title("Auto-SocialMedia Agent")

    st.write("Welcome to the Auto-SocialMedia Agent UI!")
    st.write("Functionality will be added here.")

def main():
    """
    Entry point for the 'auto-sns-ui' script.
    This function launches the Streamlit app using subprocess.
    """
    # Get the absolute path to this script (app.py)
    # __file__ is the path to the current script
    script_path = os.path.abspath(__file__)
    
    # Construct the command to run Streamlit
    # We use sys.executable to ensure we're using the same Python interpreter
    # that uv is using.
    command = [sys.executable, "-m", "streamlit", "run", script_path]
    
    # Run the command
    # This will start the Streamlit server and open the app in a browser
    subprocess.run(command)

if __name__ == "__main__":
    # This block is executed when Streamlit runs this script directly
    # (e.g., via `streamlit run app.py` or when launched by the main() function above)
    build_ui() 