import streamlit as st
import subprocess
import sys
import os
import asyncio # Required for Agno workflow interaction

# Attempt to import workflow and event, handle if not found during initial dev
try:
    from auto_sns_agent.workflows.content_creation_workflow import ContentCreationWorkflow
    from agno.workflow import RunEvent
except ImportError:
    ContentCreationWorkflow = None
    RunEvent = None 
    st.error("Failed to import ContentCreationWorkflow. Ensure it's correctly defined and paths are set.")


def get_workflow():
    if "workflow_instance" not in st.session_state:
        if ContentCreationWorkflow:
            # Ensure an event loop is available for Agno
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())
            st.session_state.workflow_instance = ContentCreationWorkflow()
        else:
            st.session_state.workflow_instance = None
    return st.session_state.workflow_instance

def build_ui():
    """Defines and builds the Streamlit user interface."""
    st.title("Auto-SocialMedia Agent")

    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = []
    if "workflow_generator" not in st.session_state:
        st.session_state.workflow_generator = None
    if "awaiting_confirmation" not in st.session_state:
        st.session_state.awaiting_confirmation = False
    if "draft_to_confirm" not in st.session_state:
        st.session_state.draft_to_confirm = None

    # Display chat messages
    for message in st.session_state.agent_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle pending workflow responses if not awaiting specific button confirmation
    if st.session_state.workflow_generator and not st.session_state.awaiting_confirmation:
        try:
            response = next(st.session_state.workflow_generator)
            st.session_state.agent_messages.append({"role": "assistant", "content": response.content})
            if response.event == RunEvent.run_response: # Expecting user input (confirmation)
                st.session_state.awaiting_confirmation = True
                st.session_state.draft_to_confirm = response.content # Store the content that needs confirmation
                # Rerun to display confirmation buttons
                st.rerun()
            elif response.event == RunEvent.workflow_completed:
                st.session_state.workflow_generator = None # Workflow finished
                st.rerun()
            else: # Other intermediate event
                st.rerun()
        except StopIteration:
            st.session_state.agent_messages.append({"role": "assistant", "content": "Workflow completed."})
            st.session_state.workflow_generator = None
            st.rerun()
        except Exception as e:
            st.error(f"Error processing workflow: {e}")
            st.session_state.workflow_generator = None
            st.rerun()

    # Confirmation UI
    if st.session_state.awaiting_confirmation and st.session_state.draft_to_confirm:
        st.info("Confirmation Required:")
        st.write(st.session_state.draft_to_confirm) # Display the content needing confirmation
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve Post", key="approve_post"):
                if st.session_state.workflow_generator:
                    try:
                        workflow = get_workflow()
                        if workflow:
                            workflow.user_provided_confirmation = "yes"
                        # The .send() is tricky because the generator might expect it via the main loop above.
                        # For now, we set the flag and let the main loop call send() or next().
                        # This part will need refinement based on exact generator behavior.
                        response = st.session_state.workflow_generator.send("yes")
                        st.session_state.agent_messages.append({"role": "assistant", "content": response.content})
                        if response.event == RunEvent.workflow_completed:
                            st.session_state.workflow_generator = None
                    except StopIteration:
                        st.session_state.agent_messages.append({"role": "assistant", "content": "Workflow completed after approval."})
                        st.session_state.workflow_generator = None
                    except Exception as e:
                        st.error(f"Error sending approval: {e}")
                        st.session_state.workflow_generator = None
                st.session_state.awaiting_confirmation = False
                st.session_state.draft_to_confirm = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel Post", key="cancel_post"):
                if st.session_state.workflow_generator:
                    try:
                        workflow = get_workflow()
                        if workflow:
                            workflow.user_provided_confirmation = "no"
                        response = st.session_state.workflow_generator.send("no")
                        st.session_state.agent_messages.append({"role": "assistant", "content": response.content})
                        if response.event == RunEvent.workflow_completed:
                            st.session_state.workflow_generator = None
                    except StopIteration:
                        st.session_state.agent_messages.append({"role": "assistant", "content": "Posting cancelled by user."})
                        st.session_state.workflow_generator = None
                    except Exception as e:
                        st.error(f"Error sending cancellation: {e}")
                        st.session_state.workflow_generator = None
                st.session_state.awaiting_confirmation = False
                st.session_state.draft_to_confirm = None
                st.rerun()

    # User input - only if not awaiting confirmation
    if not st.session_state.awaiting_confirmation:
        prompt = st.chat_input("Enter your prompt (e.g., 'create post about: AI ethics')")
        if prompt:
            st.session_state.agent_messages.append({"role": "user", "content": prompt})
            
            create_post_command = "create post about:"
            if prompt.lower().startswith(create_post_command) and ContentCreationWorkflow:
                topic = prompt[len(create_post_command):].strip()
                if topic:
                    workflow = get_workflow()
                    if workflow:
                        st.session_state.agent_messages.append({"role": "assistant", "content": f"Starting content creation for: {topic}"})
                        st.session_state.workflow_generator = workflow.run(topic=topic, platform="Twitter")
                        # Rerun to start processing the generator
                        st.rerun()
                    else:
                        st.error("Workflow could not be initialized.")
                else:
                    st.session_state.agent_messages.append({"role": "assistant", "content": "Please specify a topic after 'create post about:'"})
            else:
                # Placeholder for direct orchestrator or other commands
                st.session_state.agent_messages.append({"role": "assistant", "content": f"Received: {prompt}. Non-workflow commands not yet implemented in UI."})
            st.rerun()

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