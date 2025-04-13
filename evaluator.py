import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime
import time
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
import os

# Set page configuration
st.set_page_config(
    page_title="Guest Experience Ticket Evaluator",
    page_icon="🎫",
    layout="wide"
)

load_dotenv()

API_TOKEN = os.getenv("FRONT_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")
print(API_TOKEN)
print(OPENAI_API_KEY)
print(BASE_URL)



# Create a container for the top section with the welcome message and logout button
top_container = st.container()
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Pre-hashing all plain text passwords once
# stauth.Hasher.hash_passwords(config['credentials'])

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


#import all functions from the eval_functions.py file
from eval_functions_v2 import (
    events_to_markdown
)

from llm_eval import (
    evaluate_ticket)

# audit_result = create_detailed_ticket_audit(events_data)

# API configuration

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}
    
    
    
def get_conversation_data(convo_id):
    base = f"{BASE_URL}/conversations/{convo_id}"

    convo = requests.get(base, headers=headers).json()
    messages = requests.get(f"{base}/messages", headers=headers).json()["_results"]
    events = requests.get(f"{base}/events", headers=headers).json()["_results"]

    return {
        "meta": convo,
        "messages": messages,
        "events": events
    }


    



# st.title("Guest Experience Ticket Evaluator")

st.sidebar.title("GX QA Ticket Evaluator📊")
# Custom CSS to improve the interface
st.markdown("""
<style>
    .main-header {
        font-size: 38px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 20px;
        text-align: center;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 20px;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 2px solid #E5E7EB;
    }
    .score-box {
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        font-size: 22px;
    }
    .metric-label {
        font-weight: bold;
        color: #4B5563;
    }
    .metric-value {
        font-size: 18px;
        color: #1F2937;
    }
    .high-score {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .medium-score {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .low-score {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .recommendation {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .key-issue {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .timeline-item {
        margin-bottom: 8px;
        padding-left: 20px;
        border-left: 2px solid #E5E7EB;
    }
    .sidebar-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    [data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
    }
    .score-container {
        display: flex;
        align-items: start;
        margin-bottom: 20px;
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 15px;
    }
    .score-left {
        flex: 0 0 150px;
        padding-right: 20px;
    }
    .score-right {
        flex: 1;
        padding-left: 20px;
        border-left: 2px solid #E5E7EB;
    }
    .score-title {
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 8px;
    }
    .score-details {
        margin-top: 8px;
    }
    .metric-evidence {
        font-style: italic;
        color: #4B5563;
        margin-top: 5px;
    }
    .metric-impact {
        margin-top: 5px;
        color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
authenticator.login('main')

# Then access the values from session state
if st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
    
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
    
    # Optional: Add registration link
    st.markdown("Need an account? [Contact the administrator](mailto:dirk.moreno@numastays.com)")
    
else:
    # User is authenticated, show the application
    # authenticator.logout('Logout', 'main')
    # st.success(f'Welcome *{st.session_state["name"]}*')

    # Sample evaluation data for demonstration
    sample_evaluations = {
        "cnv_jsqojgo": {
            "title": "Guest Experience Ticket Evaluation Report",
            "overall_score": 54,
            "executive_summary": "This ticket involves a guest at the Colmena property requesting luggage storage on their checkout day. The conversation began with a chatbot interaction that correctly identified there was no luggage storage at the property and offered an alternative service (Bounce). The guest then asked if they could keep their luggage in their room for one extra hour and expressed frustration about waiting for cleaning staff. The ticket was properly transferred to a human agent but experienced significant delays in response time, with the agent only responding after 43 minutes. The conversation was prematurely archived without confirming resolution of the guest's core issue.",
            "ticket_overview": {
                "conversation_id": "cnv_jsqojgo",
                "created": "April 5, 2025, 11:13:01",
                "guest": "Anna Pavlenko",
                "property": "Colmena (ES_BC_026)",
                "assigned_agent": "Rafaela Carneiro",
                "reservation": "IGBNCMGY-1 (April 3-5, 2025)",
                "status": "Archived (Resolved)",
                "core_issues": [
                    "Guest requesting to store luggage until 12:10",
                    "Guest requesting to keep luggage in room for one extra hour",
                    "Guest waiting for cleaning staff that hadn't arrived"
                ],
                "resolution_status": "Ticket marked as resolved without confirmation that the guest's issues were addressed."
            },
            "key_events": [
                {"time": "11:04:37 - 11:13:01", "description": "Guest initiates conversation asking about luggage storage until 12:10."},
                {"time": "11:05:39", "description": "Bot informs guest no luggage storage is available at Colmena."},
                {"time": "11:06:31 - 11:07:16", "description": "Bot suggests Bounce as an external luggage storage alternative."},
                {"time": "11:09:41", "description": "Guest asks a new question: \"Can I leave my luggage in the room 1 hour more?\""},
                {"time": "11:09:42 - 11:12:12", "description": "Bot continues to offer Bounce as alternative instead of addressing room request."},
                {"time": "11:12:12 - 11:13:16", "description": "Guest requests to speak with a human agent."},
                {"time": "11:13:37", "description": "Ticket moved to Tier 1 - WhatsApp queue."},
                {"time": "11:16:01", "description": "SLA breach occurs, KPI Warning tag applied."},
                {"time": "11:18:23", "description": "Guest acknowledges automated message with \"Ok\"."},
                {"time": "11:24:40", "description": "Ticket assigned to agent Rafaela Carneiro."},
                {"time": "11:32:04", "description": "Guest sends frustrated message: \"I'm sitting here waiting for cleaning and nobody has come yet\"."},
                {"time": "11:56:31", "description": "Agent responds (43 minutes after last guest message)."},
                {"time": "11:57:56", "description": "Agent archives conversation without confirming resolution."}
            ],
            "category_scores": {
                "response_time": {"score": 3, "max": 10},
                "communication_quality": {"score": 4, "max": 10},
                "issue_resolution": {"score": 2, "max": 10},
                "guest_experience": {"score": 3, "max": 10},
                "process_adherence": {"score": 7, "max": 10}
            },
            "key_issues": [
                "Intent Classification Failure: System incorrectly categorized request, leading to ineffective bot responses.",
                "Response Time Breach: 43-minute delay in human agent response to time-sensitive issue.",
                "Incomplete Resolution: Agent failed to address luggage storage request.",
                "Premature Closure: Ticket archived without confirming resolution.",
                "Agent Focus: Agent addressed only the cleaning issue, ignoring the original luggage request.",
                "No Service Recovery: No attempt to compensate for long wait or unresolved issues."
            ],
            "recommendations": [
                "Agent Training: Ensure agents review entire conversation history before responding. Train agents to address all issues raised, not just the most recent one. Implement mandatory resolution confirmation before ticket closure.",
                "Process Improvements: Adjust SLA thresholds for checkout day requests to prioritize time-sensitive issues. Implement automated escalation for guests waiting for cleaning staff. Create a dedicated process for late checkout/luggage storage requests.",
                "Bot Enhancements: Improve intent recognition to better distinguish between luggage locker issues and late checkout requests. Add direct options for requesting late checkout or extended room access. Program bot to recognize when a guest says \"No\" and try different solutions.",
                "Service Recovery: Implement automatic service recovery options for SLA breaches. Create a follow-up protocol for prematurely closed tickets. Add post-interaction survey to catch unresolved issues.",
                "Quality Assurance: Review tickets with SLA breaches for coaching opportunities. Implement mandatory supervisor review for prematurely closed tickets. Create specific guidelines for handling checkout day requests."
            ]
        },
        "cnv_jsqrfyg": {
            "title": "Guest Experience Ticket Evaluation Report #2",
            "overall_score": 72,
            "executive_summary": "This ticket involves a future guest of YAYS Amsterdam Prince Island by Numa inquiring about city tax payment for an upcoming stay scheduled for April 21-25, 2025. The guest asked two specific questions regarding the deadline for city tax payment and whether it is deductible from the room rate. The interaction experienced a KPI warning due to delayed agent response, but the ticket was handled professionally once assigned. The agent provided clear information about the payment deadline but requested clarification on the second question rather than attempting to interpret the guest's intent.",
            "ticket_overview": {
                "conversation_id": "cnv_jsqrfyg",
                "created": "April 5, 2025, 12:27:37",
                "guest": "Ahmed Aleid",
                "property": "YAYS Amsterdam Prince Island by Numa (NL_AM_005)",
                "assigned_agent": "Stefania Palermo",
                "reservation": "GYKJFDSL-1 (April 21-25, 2025)",
                "status": "Assigned (Open)",
                "core_issues": [
                    "Guest inquiring about the deadline for city tax payment",
                    "Guest asking if city tax is deductible from the room rate"
                ],
                "resolution_status": "Ticket still open; first question answered but second question pending clarification."
            },
            "key_events": [
                {"time": "12:27:37", "description": "Guest initiates conversation with two specific questions about city tax."},
                {"time": "12:27:44", "description": "System tags the ticket with \"SLA Applies\" and updates custom fields."},
                {"time": "12:27:59", "description": "Agent Catharina Ferro tags the ticket as \"Info Generic\"."},
                {"time": "12:28:05", "description": "Agent adds \"Move to Tier 1\" tag for routing."},
                {"time": "12:28:07", "description": "Ticket automatically moved to Tier 1 - WhatsApp queue."},
                {"time": "12:28:08", "description": "System sends automated acknowledgment message."},
                {"time": "12:30:37", "description": "SLA breach occurs (3 minutes after creation), KPI Warning tag applied."},
                {"time": "12:40:18", "description": "Ticket assigned to agent Stefania Palermo by auto-assignment rule."},
                {"time": "12:58:47", "description": "Agent responds (31 minutes after ticket creation), answering the first question and requesting clarification on the second."},
                {"time": "12:58:50", "description": "KPI Warning tag removed following agent response."}
            ],
            "category_scores": {
                "response_time": {"score": 5, "max": 10},
                "communication_quality": {"score": 8, "max": 10},
                "issue_resolution": {"score": 7, "max": 10},
                "guest_experience": {"score": 7, "max": 10},
                "process_adherence": {"score": 9, "max": 10}
            },
            "key_issues": [
                "Response Time Delay: 31-minute total response time exceeded SLA standards.",
                "Incomplete Resolution: Only one of two questions fully addressed in the initial response.",
                "Missed Interpretation Opportunity: Agent could have offered potential interpretations of \"deductible\" in this context.",
                "Assignment Delay: 13-minute gap between ticket creation and agent assignment.",
                "Post-Assignment Delay: 18-minute gap between assignment and response."
            ],
            "recommendations": [
                "Agent Training: Encourage agents to provide potential interpretations when seeking clarification (e.g., \"This could mean X or Y - could you clarify which you meant?\"). Enhance agent knowledge about common terminology misunderstandings in booking contexts.",
                "Process Improvements: Review assignment algorithms to reduce the 13-minute delay between ticket creation and agent assignment. Implement prioritization for tickets with upcoming reservations based on proximity to arrival date. Create quick-reference guides for common tax and payment questions to enable faster responses.",
                "System Enhancements: Develop templates for common tax-related questions that provide comprehensive answers addressing multiple interpretations. Implement predictive response suggestions based on question analysis.",
                "Knowledge Management: Create a FAQ document specifically addressing city tax questions that can be shared with guests. Develop clear definitions of financial terms as they apply in the hospitality context to reduce confusion.",
                "Workflow Optimization: Implement pre-assignment review to identify and resolve simple inquiries more quickly. Consider automated or semi-automated responses for common questions about payment deadlines. Set escalation paths for financial inquiries that might require accounting team input."
            ]
        }
    }

    # Function to simulate API call to get ticket evaluation data
    def get_ticket_evaluation(ticket_id):
        # In a real application, this would make an API call to the backend
        # For demonstration, we'll return the sample data if it exists
        if ticket_id in sample_evaluations:
            # Simulate API delay
            time.sleep(0.5)
            return sample_evaluations[ticket_id]
        else:
            return None

    # Function to generate score color class
    def get_score_class(score):
        if score == "Exceptional":
            return "high-score"
        elif score in ["Good", "Satisfactory"]:
            return "medium-score"
        else:  # "Needs Improvement" or "Poor"
            return "low-score"
        
    def get_ticket_solved_class(status):
        if status == "True":
            return "high-score"
        else:
            return "low-score"
        
        

    # # Title
    # st.markdown('<div class="main-header">GX QA Ticket Evaluator📊</div>', unsafe_allow_html=True)

    # add a line
    # st.markdown('<hr>', unsafe_allow_html=True)

    # Sidebar for ticket selection and filters
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Ticket Selection</div>', unsafe_allow_html=True)
        
        # Ticket ID input
        ticket_id = st.text_input("Enter Ticket ID:", "cnv_jsqojgo")
        
        # Button to trigger evaluation
        evaluate_button = st.button("Evaluate Ticket", type="primary", use_container_width=True)
        
        # Sample ticket selection
        st.markdown('<div class="sidebar-header">Sample Tickets</div>', unsafe_allow_html=True)
        sample_ticket = st.radio(
            "Or select the sample ticket:",
            ("cnv_jsqojgo - Luggage Storage Issue", "cnv_jsqrfyg - City Tax Inquiry"),
            captions=("Colmena property, low performance", "Amsterdam property, medium performance")
        )
        

        
        
        if st.button("Load Sample", use_container_width=True):
            if "Amsterdam" in sample_ticket:
                ticket_id = "cnv_jsqrfyg"
                evaluate_button = True
            else:
                ticket_id = "cnv_jsqojgo"
                evaluate_button = True
                
                # Add empty space to push the disclaimer to the bottom

            
            # Add disclaimer about LLM hallucinations
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #6c757d; font-size: 0.8em; margin-top: 10px;">
            <p><strong>⚠️ AI Disclaimer:</strong> This evaluation uses Large Language Models which may occasionally hallucinate or produce inaccurate information. Always verify critical assessments.</p>
        </div>
        """, unsafe_allow_html=True)
        
            # Add "Made with love" at the very bottom
        st.markdown("""
        <div style="text-align: center; margin-top: 20px; font-size: 0.8em; color: #6c757d;">
            Made with ❤️ by <a href="https://www.notion.so/numastays/GX-QA-Ticket-Evaluator-1cda39b9f204805184bfe326a530503d" style="color: #007bff;">Numa GX</a> V1.5
        </div>
        """, unsafe_allow_html=True)
                    
                

    # Main content area
    if evaluate_button or 'evaluation_data' in st.session_state:
        # Show a spinner while "loading"
        with st.spinner('Analyzing ticket data...'):
            # Get evaluation data (simulation)
            # evaluation_data = get_ticket_evaluation(ticket_id)
            raw = get_conversation_data(ticket_id)
            events_data = raw['events']
            with open("events_data.json", 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2, ensure_ascii=False)
            audit_result = events_to_markdown(events_data)
            
            
            with open("ticket_summary.md", 'w', encoding='utf-8') as f:
                f.write(audit_result)
            
            # Save the full audit data
            with open("ticket_audit_full.json", 'w', encoding='utf-8') as f:
                json.dump(audit_result, f, indent=2, ensure_ascii=False)
            evaluation_data = evaluate_ticket(audit_result)
            
            st.session_state.evaluation_data = evaluation_data
        
        # If we have data, display it
        if evaluation_data:
            # Create tabs for different sections of the report
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Detailed Evaluation", "Timeline", "Recommendations", "Bot Evaluation", "Summary"])
            
            with tab1:
                # Title and overall score
                st.markdown(f'<div class="section-header">{evaluation_data["title"]}</div>', unsafe_allow_html=True)
                # st.markdown(f"[Ticket Link]()", unsafe_allow_html=False)
                # st.markdown(f"[Apaleo Link]({evaluation_data["ticket_link"]})", unsafe_allow_html=False)
                # st.markdown(f'<div class="section-header">{evaluation_data["ticket_link"]}</div>', unsafe_allow_html=True)
                
                # Display the overall score in a colored box
                score_class = get_score_class(evaluation_data["overall_score"])
                st.markdown(f'<div class="score-box {score_class}">Overall Score: {evaluation_data["overall_score"]}</div>', unsafe_allow_html=True)
                
                #Display the ticket status in a colored box
                # status_class = get_ticket_solved_class(evaluation_data["was_issue_resolved"])
                # st.markdown(f'<div class="score-box {status_class}">Ticket Status: {evaluation_data["ticket_overview"]["status"]}</div>', unsafe_allow_html=True)
                
                # #Guest intent
                st.markdown('<div class="section-header">Guest Intent</div>', unsafe_allow_html=True)
                st.write(evaluation_data["guest_intent"])
                
                # Executive summary
                st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)
                st.write(evaluation_data["executive_summary"])
                
                # Ticket overview details
                st.markdown('<div class="section-header">Ticket Overview</div>', unsafe_allow_html=True)
                
                # Use columns for the ticket details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<span class="metric-label">Conversation ID:</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="metric-value">{evaluation_data["ticket_overview"]["conversation_id"]}</span>', unsafe_allow_html=True)
                    
                    st.markdown('<span class="metric-label">Created:</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="metric-value">{evaluation_data["ticket_overview"]["created"]}</span>', unsafe_allow_html=True)
                    
                    # st.markdown('<span class="metric-label">Guest:</span>', unsafe_allow_html=True)
                    # st.markdown(f'<span class="metric-value">{evaluation_data["ticket_overview"]["guest"]}</span>', unsafe_allow_html=True)
                    
                    st.markdown('<span class="metric-label">Property:</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="metric-value">{evaluation_data["ticket_overview"]["property"]}</span>', unsafe_allow_html=True)
                    
                with col2:                    
                    st.markdown('<span class="metric-label">Reservation:</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="metric-value">{evaluation_data["ticket_overview"]["reservation"]}</span>', unsafe_allow_html=True)
                    
                    st.markdown('<span class="metric-label">Status:</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="metric-value">{evaluation_data["ticket_overview"]["status"]}</span>', unsafe_allow_html=True)
                
                # Core issues
                st.markdown('<div class="section-header">Core Issues</div>', unsafe_allow_html=True)
                for issue in evaluation_data["ticket_overview"]["core_issues"]:
                    st.markdown(f"- {issue}")
                
                # Final resolution status
                st.markdown('<div class="section-header">Resolution Status</div>', unsafe_allow_html=True)
                st.write(evaluation_data["ticket_overview"]["resolution_status"])
            
            with tab2:
                st.markdown('<div class="section-header">Agent Performance</div>', unsafe_allow_html=True)
                
                # Response Time Score - using nested columns
                st.markdown('<div class="score-container">', unsafe_allow_html=True)
                score_col, details_col = st.columns([1, 3])
                
                with score_col:
                    score = evaluation_data["category_scores"]["response_time"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Response Time</div>', unsafe_allow_html=True)
                
                with details_col:
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> Immediate response</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• First response within 15 minutes</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Demonstrates excellent urgency</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> Quick response</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• First response within 30 minutes</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Good balance of speed and quality</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> Standard response</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• First response within 1 hour</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Met minimum requirements</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> Delayed response</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• First response within 4 hours</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Impacted guest satisfaction</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> Severe delay</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• First response over 4 hours</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Critical failure in response time</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Communication Quality Score
                st.markdown('<div class="score-container">', unsafe_allow_html=True)
                score_col, details_col = st.columns([1, 3])
                
                with score_col:
                    score = evaluation_data["category_scores"]["communication_quality"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Communication</div>', unsafe_allow_html=True)
                
                with details_col:
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Outstanding clarity</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Highly empathetic and professional</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Superior guest experience</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Clear and professional</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Well-structured with good personalization</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Effective communication style</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Clear but generic</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Professional but lacks personalization</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Basic communication needs met</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Communication issues</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Generic responses lacking clarity</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• May cause guest confusion</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Poor communication</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Unclear or inappropriate</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Severely impacts understanding</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-header">Guest Experience</div>', unsafe_allow_html=True)
                
                # Issue Resolution Score
                st.markdown('<div class="score-container">', unsafe_allow_html=True)
                score_col, details_col = st.columns([1, 3])
                
                with score_col:
                    score = evaluation_data["category_scores"]["issue_resolution"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Issue Resolution</div>', unsafe_allow_html=True)
                
                with details_col:
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Outstanding resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Complete resolution with added value</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Exceeded expectations</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Effective resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Clear solution provided</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Guest needs addressed</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Basic resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Main issues addressed</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Minimum standards met</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Incomplete resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Significant gaps present</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Guest needs partially unmet</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Failed resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Issue remains unresolved</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Critical service failure</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Process Adherence Score
                st.markdown('<div class="score-container">', unsafe_allow_html=True)
                score_col, details_col = st.columns([1, 3])
                
                with score_col:
                    score = evaluation_data["category_scores"]["process_adherence"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Process Adherence</div>', unsafe_allow_html=True)
                
                with details_col:
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Perfect protocol adherence</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Exemplary documentation and process following</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Sets standard for operational excellence</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Strong protocol adherence</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Good documentation with minor gaps</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Processes followed effectively</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Basic protocol adherence</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Key processes followed with some gaps</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Room for process improvement</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Process gaps present</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Multiple procedural steps missed</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Inconsistent protocol adherence</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Major process failures</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Critical procedures ignored</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Severe operational deficiencies</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="section-header">Agent Performance</div>', unsafe_allow_html=True)
                    
                    # Response Time Score
                    st.markdown('<div class="score-container">', unsafe_allow_html=True)
                    st.markdown('<div class="score-left">', unsafe_allow_html=True)
                    score = evaluation_data["category_scores"]["response_time"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Response Time</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="score-right">', unsafe_allow_html=True)
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> First response within 15 minutes</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Agent responded immediately to guest inquiry</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Demonstrates excellent urgency and guest-first mindset</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> First response within 30 minutes</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Quick response time maintaining guest satisfaction</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Good balance of speed and thoughtfulness</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> First response within 1 hour</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Met minimum response time requirements</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Room for improvement in response speed</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> First response within 4 hours</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Delayed response affecting guest experience</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• May lead to guest frustration and reduced satisfaction</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Response Speed:</strong> First response over 4 hours</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Severely delayed response time</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Significant negative impact on guest experience</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    # Communication Quality Score
                    st.markdown('<div class="score-container">', unsafe_allow_html=True)
                    st.markdown('<div class="score-left">', unsafe_allow_html=True)
                    score = evaluation_data["category_scores"]["communication_quality"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Communication</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="score-right">', unsafe_allow_html=True)
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Outstanding personalization and clarity</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Highly empathetic and professional tone</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Created a superior guest communication experience</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Clear and professional</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Well-structured responses with good personalization</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Effective and appropriate communication style</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Clear but generic</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Professional but lacks personalization</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Basic communication needs met</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Communication issues present</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Generic responses lacking clarity</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• May cause guest confusion or frustration</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Communication Quality:</strong> Significant issues</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Unclear or inappropriate communication</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Severely impacts guest understanding</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    # Process Adherence Score
                    st.markdown('<div class="score-container">', unsafe_allow_html=True)
                    st.markdown('<div class="score-left">', unsafe_allow_html=True)
                    score = evaluation_data["category_scores"]["process_adherence"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Process Adherence</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="score-right">', unsafe_allow_html=True)
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Perfect protocol adherence</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Exemplary documentation and process following</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Sets standard for operational excellence</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Strong protocol adherence</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Good documentation with minor gaps</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Processes followed effectively</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Basic protocol adherence</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Key processes followed with some gaps</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Room for process improvement</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Process gaps present</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Multiple procedural steps missed</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Inconsistent protocol adherence</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Process Quality:</strong> Major process failures</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Critical procedures ignored</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Severe operational deficiencies</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="section-header">Guest Experience</div>', unsafe_allow_html=True)
                    
                    # Issue Resolution Score
                    st.markdown('<div class="score-container">', unsafe_allow_html=True)
                    st.markdown('<div class="score-left">', unsafe_allow_html=True)
                    score = evaluation_data["category_scores"]["issue_resolution"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Issue Resolution</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="score-right">', unsafe_allow_html=True)
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Outstanding resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Complete resolution with added value</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Exceeded guest expectations</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Effective resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Clear solution and explanation provided</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Guest needs fully addressed</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Basic resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Main issues addressed with gaps</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Minimum resolution standards met</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Incomplete resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Significant gaps in resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Guest needs partially unmet</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Resolution Quality:</strong> Failed resolution</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Issue remains unresolved</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Critical failure in guest service</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    # Overall Guest Experience Score
                    st.markdown('<div class="score-container">', unsafe_allow_html=True)
                    st.markdown('<div class="score-left">', unsafe_allow_html=True)
                    score = evaluation_data["category_scores"]["guest_experience"]["score"]
                    score_class = get_score_class(score)
                    st.markdown(f'<div class="score-box {score_class}">{score}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="text-align: center;">Guest Experience</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="score-right">', unsafe_allow_html=True)
                    if score == "Exceptional":
                        st.markdown('<div class="score-details"><strong>Guest Satisfaction:</strong> Outstanding experience</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Guest likely delighted and impressed</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Created memorable positive experience</div>', unsafe_allow_html=True)
                    elif score == "Good":
                        st.markdown('<div class="score-details"><strong>Guest Satisfaction:</strong> Positive experience</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Guest likely satisfied with interaction</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Met guest expectations well</div>', unsafe_allow_html=True)
                    elif score == "Satisfactory":
                        st.markdown('<div class="score-details"><strong>Guest Satisfaction:</strong> Adequate experience</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Basic needs met with average effort</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Room for experience enhancement</div>', unsafe_allow_html=True)
                    elif score == "Needs Improvement":
                        st.markdown('<div class="score-details"><strong>Guest Satisfaction:</strong> Subpar experience</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Signs of guest frustration present</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Failed to meet guest expectations</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="score-details"><strong>Guest Satisfaction:</strong> Poor experience</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-evidence">• Clear guest dissatisfaction</div>', unsafe_allow_html=True)
                        st.markdown('<div class="metric-impact">• Significant negative experience</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)

                with col2:
                    # Bot Performance section (unchanged)
                    st.markdown('<div class="section-header">Bot Performance</div>', unsafe_allow_html=True)
                    st.write(evaluation_data["bot_evaluation"])
                    
                    for i, issue in enumerate(evaluation_data["bot_evaluation_details"]):
                        st.markdown(f'<div class="key-issue">{i+1}. {issue}</div>', unsafe_allow_html=True)

                # Key Issues section at the bottom
                st.markdown('<div class="section-header">Key Issues</div>', unsafe_allow_html=True)
                for i, issue in enumerate(evaluation_data["key_issues"]):
                    st.markdown(f'<div class="key-issue">{i+1}. {issue}</div>', unsafe_allow_html=True)
            
            with tab3:
                # Timeline
                st.markdown('<div class="section-header">Key Events Timeline</div>', unsafe_allow_html=True)
                for event in evaluation_data["key_events"]:
                    st.markdown(f'<div class="timeline-item"><strong>{event["time"]}</strong>: {event["description"]}</div>', unsafe_allow_html=True)
            
            with tab4:
                # Recommendations
                st.markdown('<div class="section-header">Recommendations</div>', unsafe_allow_html=True)
                for i, recommendation in enumerate(evaluation_data["recommendations"]):
                    st.markdown(f'<div class="recommendation"><strong>Recommendation {i+1}:</strong> {recommendation}</div>', unsafe_allow_html=True)
                    
            with tab5:
                # Bot Evaluation
                st.markdown('<div class="section-header">Bot Evaluation</div>', unsafe_allow_html=True)
                st.write(evaluation_data["bot_evaluation"])
                
                # Bot evaluation details
                st.markdown('<div class="section-header">Bot Evaluation Details</div>', unsafe_allow_html=True)
                for i, issue in enumerate(evaluation_data["bot_evaluation_details"]):
                    st.markdown(f'<div class="key-issue">{i+1}. {issue}</div>', unsafe_allow_html=True)
            with tab6:
                st.markdown(audit_result)
        else:
            st.error(f"No evaluation data found for ticket ID: {ticket_id}")
            st.write("Please check the ticket ID and try again, or select a sample ticket from the sidebar.")
    else:
        # Initial state - instructions
        st.info("Enter a ticket ID in the sidebar and click 'Evaluate Ticket' to see the evaluation report.")
        st.write("Or select one of the sample tickets to view a demonstration of the evaluation interface.")