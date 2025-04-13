import streamlit as st
import pandas as pd
import random
import datetime
import time
from PIL import Image
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="GX Story Spotlight",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve the interface
st.markdown("""
<style>
    /* Main styling */
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
    .story-box {
        background-color: #F9FAFB;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #1E3A8A;
    }
    .highlight-story {
        border-left: 5px solid #059669;
    }
    .lowlight-story {
        border-left: 5px solid #DC2626;
    }
    .story-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .story-meta {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 10px;
    }
    .story-content {
        font-size: 16px;
        line-height: 1.6;
    }
    .story-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    .highlight-tag {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .lowlight-tag {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .learning-tag {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    .guest-tag {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .process-tag {
        background-color: #E0E7FF;
        color: #3730A3;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 15px;
    }
    .metric-container {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 14px;
        color: #6B7280;
    }
    
    /* Fix sidebar top margin */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0rem !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #fc9d20;
    }
    
    /* Sidebar text adjustments */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiselect label,
    [data-testid="stSidebar"] .sidebar-header,
    [data-testid="stSidebar"] .stDateInput label {
        color: #ffffff;
    }
    
    /* Sidebar content styling */
    [data-testid="stSidebar"] .sidebar-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* Additional button styling */
    div.stButton > button:first-child {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #3151B7;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sample data for stories
sample_stories = [
    {
        "id": "ST-001",
        "title": "Going Above and Beyond for a Stranded Guest",
        "type": "highlight",
        "date": "2025-04-01",
        "agent": "Sophia Chen",
        "property": "NUMA Barcelona Central",
        "conversation_id": "cnv_abc123",
        "tags": ["exceptional service", "problem solving", "guest satisfaction"],
        "summary": "A guest's flight was canceled late at night leaving them stranded with no accommodation. Our agent not only found them a room at our fully booked property by identifying a same-day cancellation but also arranged special transportation and a complimentary welcome package.",
        "story": "It was 11:30 PM when we received a distressed message from Alex, whose flight had been suddenly canceled due to severe weather. All hotels in the area were showing as fully booked, and Alex was facing the prospect of spending the night at the airport with their family including two small children.\n\nSophia immediately checked our system and spotted that a cancellation had just come through minutes before. She quickly secured this room for Alex, but then realized another challenge - the guest had no transportation to reach our property at this late hour.\n\nGoing beyond protocol, Sophia coordinated with our local transportation partner who agreed to make a special late-night pickup. She also prepared a complimentary welcome package with snacks and essential items for the children, which she arranged to have waiting in the room.\n\nThe guest was overwhelmed with gratitude and later wrote a glowing review specifically mentioning Sophia's exceptional assistance during their time of need. This story exemplifies our commitment to finding solutions even in seemingly impossible situations.",
        "learning_points": [
            "Always check for real-time cancellations when dealing with urgent accommodation needs",
            "Having established relationships with local service providers can be crucial in emergency situations",
            "Small personal touches during stressful situations create lasting positive impressions"
        ],
        "score": 98
    },
    {
        "id": "ST-002",
        "title": "Creative Solution for Broken Air Conditioning",
        "type": "highlight",
        "date": "2025-03-28",
        "agent": "Miguel Sanchez",
        "property": "NUMA Vienna Mozart",
        "conversation_id": "cnv_def456",
        "tags": ["problem solving", "service recovery", "guest experience"],
        "summary": "When a guest reported a broken air conditioning unit during a heatwave and no maintenance was available until morning, Miguel arranged for a portable unit to be delivered within an hour and offered compensation, turning a potentially negative experience into a positive one.",
        "story": "During an unexpected heatwave in Vienna, Emma received an urgent message from a guest reporting that their air conditioning had stopped working. It was already evening, and our maintenance team would not be available until morning. The temperature in the apartment had reached uncomfortable levels, and the guest was considering checking out and finding alternative accommodation.\n\nMiguel quickly assessed the situation and realized that waiting until morning was not an acceptable solution. Instead of offering the standard response of a room change (which wasn't possible due to full occupancy) or asking the guest to wait, Miguel took initiative.\n\nHe contacted a local equipment rental company that we occasionally partner with and arranged for a portable air conditioning unit to be delivered to the property within the hour. He also dispatched a team member to purchase a large fan from a nearby store that was still open.\n\nMiguel kept the guest updated throughout the process, personally ensured the delivery of both cooling solutions, and added a complimentary bottle of wine and a credit for a future stay as a gesture of goodwill.\n\nThe guest, who had initially been quite upset, was so impressed by the swift and creative response that they extended their stay by two additional nights and specifically mentioned Miguel's exceptional service in their review.",
        "learning_points": [
            "Having alternative solution providers on hand for common emergency issues",
            "Proactive compensation before complaints escalate can turn experiences around",
            "Continuous communication during issue resolution significantly reduces guest anxiety"
        ],
        "score": 96
    },
    {
        "id": "ST-003",
        "title": "Missed Early Check-in Promise",
        "type": "lowlight",
        "date": "2025-04-02",
        "agent": "Thomas Miller",
        "property": "NUMA Paris Belleville",
        "conversation_id": "cnv_ghi789",
        "tags": ["communication breakdown", "expectations management", "process improvement"],
        "summary": "A guest was promised early check-in but arrived to find their room not ready, resulting in a 3-hour wait. Investigation revealed the promise was made without checking cleaning schedules or communicating with the property team.",
        "story": "A guest contacted us two days before arrival to request an early check-in at 11:00 AM instead of our standard 3:00 PM time. Thomas responded positively, saying \"We'd be happy to arrange an early check-in for you,\" without confirming with the property team or checking the cleaning schedule for that day.\n\nWhen the guest arrived at 11:00 AM with their family after an overnight flight, they were informed that their room wouldn't be ready until at least 2:00 PM. This created significant frustration as the guest had specifically arranged their travel plans based on the promised early check-in.\n\nThe guest had to wait in our lobby for three hours with their luggage and tired children. Despite efforts to make them comfortable and offering to store their luggage, the situation resulted in a negative review and a complaint escalation.\n\nOur investigation showed that the property was fully booked the previous night and operating with a reduced cleaning team that day, making the 11:00 AM check-in impossible from the start. Had this been checked, we could have informed the guest in advance or made alternative arrangements.",
        "learning_points": [
            "Never confirm early check-in without verifying availability with the property team",
            "Develop a standardized process for checking early check-in possibilities",
            "Set clear expectations with guests about the conditional nature of early check-ins",
            "Implement calendar integration between guest communications and cleaning schedules"
        ],
        "score": 32
    },
    {
        "id": "ST-004",
        "title": "Resolving a Complex Billing Dispute",
        "type": "highlight",
        "date": "2025-03-15",
        "agent": "Aisha Johnson",
        "property": "NUMA Berlin Kreuzberg",
        "conversation_id": "cnv_jkl101",
        "tags": ["problem solving", "financial resolution", "communication"],
        "summary": "A business traveler discovered multiple incorrect charges on their folio, creating a complicated situation involving split payments and tax documentation issues. Aisha patiently worked through each line item, coordinated with accounting, and created a clear explanation document.",
        "story": "A business traveler contacted us with concerns about multiple discrepancies on their billing statement. The guest had a complex reservation that included a split payment between personal and company credit cards, special VAT documentation requirements for business expense reimbursement, and several on-property additional charges.\n\nThe initial review showed at least six different points of confusion, some of which were errors on our part and others that were misunderstandings about how certain charges were categorized. Rather than providing a piecemeal response or dismissing the guest's concerns, Aisha took ownership of the entire situation.\n\nShe first organized a detailed breakdown of every charge, created a comparison document showing the guest's understanding versus the actual billing, and identified specifically where the discrepancies occurred. She then coordinated with our accounting team to correct the actual errors, generated new VAT documentation in the proper format, and created a clear timeline of when all corrections would be processed.\n\nAisha maintained contact with the guest throughout the resolution process, providing updates and ensuring that each step was addressing their specific concerns. Once all issues were resolved, she proactively scheduled a brief call with the guest to walk through the final documentation and answer any remaining questions.\n\nThe guest, who had been understandably frustrated, expressed appreciation for the thoroughness and clarity of the resolution. They specifically noted that Aisha's approach had restored their confidence in staying with us for future business trips.",
        "learning_points": [
            "Complex financial issues benefit from visual documentation and comparisons",
            "For business travelers, tax documentation is often as important as the actual charges",
            "Proactive communication throughout resolution processes significantly reduces anxiety",
            "Investment of time in complex resolutions can secure valuable future business"
        ],
        "score": 95
    },
    {
        "id": "ST-005",
        "title": "Noise Complaint Handling Failure",
        "type": "lowlight",
        "date": "2025-03-20",
        "agent": "Marcus Wilson",
        "property": "NUMA Madrid Sol",
        "conversation_id": "cnv_mno202",
        "tags": ["escalation failure", "guest dissatisfaction", "policy issues"],
        "summary": "Multiple guests reported noise from a neighboring apartment over two nights, but our response was inconsistent, delayed, and ultimately ineffective, resulting in several negative reviews and compensation requests.",
        "story": "Over a weekend, we received multiple complaints from three different apartments about excessive noise coming from another guest's unit. The first complaint came in Friday at 11:30 PM, and Marcus sent a standard message asking the noisy guests to be mindful of others. No follow-up was conducted to ensure compliance.\n\nWhen second and third complaints came in around 1:15 AM, they were not seen until the next morning because our night monitoring process failed. The complaining guests reported they had a sleepless night and were extremely dissatisfied.\n\nThe next evening, similar problems occurred starting around 10:00 PM. This time, different agents were handling the communications, and there was no reference to the previous night's issues. The responses were inconsistent - one guest was told action would be taken immediately, another was told to 'use the earplugs provided in the room,' and the third received a message that we would 'look into it tomorrow.'\n\nBy Sunday, we had received formal complaints from all three affected apartments, including one guest who checked out a day early without refund rather than spend another night. Investigation showed that our noise policy was applied inconsistently, follow-up was inadequate, and there was no escalation to property management despite the severity and repeat nature of the issue.\n\nThis case highlighted serious gaps in our noise complaint handling process, particularly during weekend evenings when staffing is reduced.",
        "learning_points": [
            "Develop a clear escalation path for repeated noise complaints with specific thresholds for action",
            "Implement a system to tag and link related complaints to provide context for all agents",
            "Create a standardized response protocol for noise issues that occurs after hours",
            "Review staffing and monitoring processes for weekend evening communications",
            "Establish a direct contact protocol with property management for urgent quality-of-stay issues"
        ],
        "score": 24
    }
]

# Sample data for metrics
story_metrics = {
    "total_stories": 87,
    "highlights": 58,
    "lowlights": 29,
    "this_month": 12,
    "featured": 15,
    "properties": {
        "NUMA Barcelona": 18,
        "NUMA Berlin": 15,
        "NUMA Vienna": 14,
        "NUMA Paris": 12,
        "NUMA Madrid": 10,
        "NUMA Amsterdam": 9,
        "NUMA Lisbon": 9
    },
    "top_tags": {
        "problem solving": 32,
        "guest satisfaction": 28,
        "communication": 24,
        "process improvement": 19,
        "exceptional service": 17
    },
    "top_agents": {
        "Sophia Chen": 12,
        "Miguel Sanchez": 10,
        "Aisha Johnson": 9,
        "Thomas Miller": 7,
        "Emma Garcia": 6
    }
}

# Login simulation (in a real app, use streamlit-authenticator)
def simulate_login():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="main-header">GX Guest Story Spotlight</div>', unsafe_allow_html=True)
            with st.form("login_form"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                submit = st.form_submit_button("Login")
                if submit:
                    # Simulate login (accept any credentials)
                    st.session_state['logged_in'] = True
                    st.session_state['name'] = "Demo User"
                    st.rerun()
        return False
    return True

# Function to show story detail
def show_story_detail(story):
    st.markdown(f"<div class='section-header'>{story['title']}</div>", unsafe_allow_html=True)
    
    # Story metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**ID:** {story['id']}")
        st.markdown(f"**Property:** {story['property']}")
    with col2:
        st.markdown(f"**Agent:** {story['agent']}")
        st.markdown(f"**Date:** {story['date']}")
    with col3:
        st.markdown(f"**Type:** {story['type'].capitalize()}")
        st.markdown(f"**Conversation:** [{story['conversation_id']}](https://app.frontapp.com/open/{story['conversation_id']})")
    
    # Tags
    st.markdown("**Tags:**")
    tag_html = ""
    for tag in story['tags']:
        tag_class = "learning-tag" if "improvement" in tag or "solving" in tag else "guest-tag" if "guest" in tag or "satisfaction" in tag else "process-tag"
        tag_html += f"<span class='story-tag {tag_class}'>{tag}</span>"
    st.markdown(f"<div>{tag_html}</div>", unsafe_allow_html=True)
    
    # Summary
    st.markdown("### Summary")
    st.markdown(f"{story['summary']}")
    
    # Full story
    st.markdown("### Full Story")
    st.markdown(f"{story['story']}")
    
    # Learning points
    st.markdown("### Key Learning Points")
    for point in story['learning_points']:
        st.markdown(f"- {point}")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.button("Edit Story", key=f"edit_{story['id']}")
    with col2:
        st.button("Feature at Townhall", key=f"feature_{story['id']}")
    with col3:
        st.button("Export as Slide", key=f"export_{story['id']}")
    with col4:
        st.button("Back to List", key=f"back_{story['id']}", on_click=lambda: st.session_state.update({"selected_story": None}))

# Main application function
def main():
    if not simulate_login():
        return
    
    # Create top container with welcome message and logout
    top_container = st.container()
    with top_container:
        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown(f"<div style='text-align: right; padding-right: 1rem;'>Welcome, <i>{st.session_state['name']}</i></div>", unsafe_allow_html=True)
            _, button_col, _ = col2.columns([1, 2, 1])
            with button_col:
                if st.button("Logout"):
                    st.session_state['logged_in'] = False
                    st.experimental_rerun()
    
    # App title
    st.markdown('<div class="main-header">GX Guest Story Spotlight</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Story Explorer</div>', unsafe_allow_html=True)
        
        # Search and filters
        st.text_input("Search Stories", placeholder="Enter keywords...")
        
        st.markdown('<div class="sidebar-header">Filters</div>', unsafe_allow_html=True)
        story_type = st.multiselect("Story Type", ["Highlight", "Lowlight"], default=["Highlight", "Lowlight"])
        
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            st.date_input("From Date", datetime.date(2025, 1, 1))
        with date_col2:
            st.date_input("To Date", datetime.date.today())
        
        properties = st.multiselect("Properties", 
                                   list(story_metrics["properties"].keys()),
                                   default=[])
        
        agents = st.multiselect("Agents", 
                               list(story_metrics["top_agents"].keys()),
                               default=[])
        
        tags = st.multiselect("Tags", 
                             list(story_metrics["top_tags"].keys()),
                             default=[])
        
        st.markdown('<div class="sidebar-header">Actions</div>', unsafe_allow_html=True)
        if st.button("Apply Filters", use_container_width=True):
            st.session_state['filtered'] = True
        
        if st.button("Reset Filters", use_container_width=True):
            st.session_state['filtered'] = False
        
        if st.button("Add New Story", use_container_width=True):
            st.session_state['adding_story'] = True
        
        if st.button("Generate Report", use_container_width=True):
            st.session_state['generating_report'] = True
            
        st.markdown('<div class="sidebar-header">Quick Tools</div>', unsafe_allow_html=True)
        if st.button("Weekly Highlights", use_container_width=True):
            st.session_state['view'] = 'weekly'
            
        if st.button("Townhall Picks", use_container_width=True):
            st.session_state['view'] = 'townhall'
        
        st.markdown("---")
        st.markdown("Need help? [View Documentation](https://notion.yourdomain.com/gx-spotlight-docs)")
    
    # Main content area based on state
    if st.session_state.get('selected_story'):
        # Show detailed view of selected story
        selected_story = next((s for s in sample_stories if s['id'] == st.session_state['selected_story']), None)
        if selected_story:
            show_story_detail(selected_story)
    
    elif st.session_state.get('adding_story'):
        # Show form to add new story
        st.markdown('<div class="section-header">Add New Story</div>', unsafe_allow_html=True)
        
        with st.form("add_story_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Conversation ID", placeholder="e.g., cnv_abc123")
                st.selectbox("Story Type", ["Highlight", "Lowlight"])
                st.text_input("Agent Name", placeholder="Who handled this interaction?")
            with col2:
                st.selectbox("Property", list(story_metrics["properties"].keys()))
                st.text_input("Tags", placeholder="Comma-separated tags")
                st.date_input("Date", datetime.date.today())
            
            st.text_input("Story Title", placeholder="A descriptive title for this story")
            st.text_area("Summary", placeholder="Brief 1-2 sentence summary of what happened", height=100)
            st.text_area("Full Story", placeholder="Detailed description of what happened, how it was handled, and the outcome", height=200)
            st.text_area("Learning Points", placeholder="Key takeaways and learning points (one per line)", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                st.form_submit_button("Fetch from Ticket", type="secondary", help="Automatically populate fields from the conversation ID")
            with col2:
                if st.form_submit_button("Submit Story"):
                    st.session_state['adding_story'] = False
                    st.success("Story submitted successfully!")
                    time.sleep(2)
                    st.experimental_rerun()
                    
    elif st.session_state.get('generating_report'):
        # Show report generation options
        st.markdown('<div class="section-header">Generate Report</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Report Type", ["Weekly Summary", "Monthly Digest", "Quarterly Review", "Custom Period"])
            st.multiselect("Include Story Types", ["Highlights", "Lowlights"], default=["Highlights", "Lowlights"])
            st.multiselect("Properties to Include", list(story_metrics["properties"].keys()), default=list(story_metrics["properties"].keys()))
        with col2:
            st.selectbox("Format", ["PDF", "PowerPoint", "Excel", "Google Slides"])
            st.selectbox("Grouping", ["By Property", "By Agent", "By Tag", "By Date"])
            st.text_input("Report Title", value="GX Story Spotlight - Weekly Digest")
        
        st.multiselect("Sections to Include", ["Executive Summary", "Story Highlights", "Metrics & Trends", "Learning Points", "Action Items"], 
                      default=["Executive Summary", "Story Highlights", "Metrics & Trends", "Learning Points"])
        
        if st.button("Generate Report"):
            with st.spinner("Generating your report..."):
                time.sleep(3)
                st.success("Report generated successfully!")
                st.session_state['generating_report'] = False
                st.markdown("[Download Report](#)")
                    
    else:
        # Default view - story list and metrics
        tab1, tab2 = st.tabs(["Stories", "Metrics & Insights"])
        
        with tab1:
            # Create filtering/sorting options
            col1, col2, col3 = st.columns(3)
            with col1:
                sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Score", "Lowest Score"])
            with col2:
                view_mode = st.radio("View", ["All", "Highlights Only", "Lowlights Only"], horizontal=True)
            with col3:
                st.text_input("Quick Search", placeholder="Filter by keyword...")
            
            # Display stories
            for story in sample_stories:
                # Apply filtering based on view mode
                if view_mode == "Highlights Only" and story["type"] != "highlight":
                    continue
                if view_mode == "Lowlights Only" and story["type"] != "lowlight":
                    continue
                
                # Story card
                story_class = "highlight-story" if story["type"] == "highlight" else "lowlight-story"
                st.markdown(f"""
                <div class="story-box {story_class}">
                    <div class="story-title">{story["title"]}</div>
                    <div class="story-meta">
                        {story["date"]} | {story["property"]} | Agent: {story["agent"]} | 
                        <span class="story-tag {'highlight-tag' if story['type'] == 'highlight' else 'lowlight-tag'}">
                            {story["type"].upper()}
                        </span>
                    </div>
                    <div class="story-content">{story["summary"]}</div>
                    <div style="text-align: right; margin-top: 10px;">
                        <span style="font-weight: bold;">Quality Score: {story["score"]}/100</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Buttons for each story
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("View Details", key=f"view_{story['id']}"):
                        st.session_state['selected_story'] = story['id']
                        st.experimental_rerun()
                with col2:
                    st.button("View Conversation", key=f"convo_{story['id']}")
                with col3:
                    st.button("Feature Story", key=f"feat_{story['id']}")
            
        with tab2:
            # Metrics overview
            st.markdown('<div class="section-header">Story Collection Metrics</div>', unsafe_allow_html=True)
            
            # Top metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{story_metrics['total_stories']}</div>
                    <div class="metric-label">Total Stories</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{story_metrics['highlights']}</div>
                    <div class="metric-label">Highlights</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{story_metrics['lowlights']}</div>
                    <div class="metric-label">Lowlights</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{story_metrics['this_month']}</div>
                    <div class="metric-label">This Month</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts and visualizations
            st.markdown('<div class="section-header">Insights</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                # Create a properties chart
                st.subheader("Stories by Property")
                property_data = pd.DataFrame({
                    'Property': list(story_metrics['properties'].keys()),
                    'Count': list(story_metrics['properties'].values())
                })
                st.bar_chart(property_data.set_index('Property'))
                
            with col2:
                # Create a tags chart
                st.subheader("Top Tags")
                tags_data = pd.DataFrame({
                    'Tag': list(story_metrics['top_tags'].keys()),
                    'Count': list(story_metrics['top_tags'].values())
                })
                st.bar_chart(tags_data.set_index('Tag'))
            
            # Trending topics
            st.markdown('<div class="section-header">Trending Topics</div>', unsafe_allow_html=True)
            
            # Generate some random trend data
            trend_data = pd.DataFrame({
                'Week': [f"Week {i}" for i in range(1, 11)],
                'Problem Solving': [random.randint(5, 15) for _ in range(10)],
                'Communication': [random.randint(3, 12) for _ in range(10)],
                'Guest Satisfaction': [random.randint(4, 14) for _ in range(10)],
                'Process Improvement': [random.randint(2, 10) for _ in range(10)]
            })
            
            st.line_chart(trend_data.set_index('Week'))
            
            # Add additional insights or metrics sections
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Quality Score Distribution")
                # Create histogram data for quality scores
                quality_bins = pd.DataFrame({
                    'Score Range': ['0-20', '21-40', '41-60', '61-80', '81-100'],
                    'Count': [5, 7, 12, 25, 38]  # Sample distribution
                })
                st.bar_chart(quality_bins.set_index('Score Range'))
                
            with col2:
                st.subheader("Highlight vs Lowlight Ratio")
                # Monthly ratio data
                ratio_data = pd.DataFrame({
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
                    'Highlights': [12, 15, 18, 13],
                    'Lowlights': [8, 6, 9, 6]
                })
                st.bar_chart(ratio_data.set_index('Month'))

# Run the application
if __name__ == "__main__":
    main()
                