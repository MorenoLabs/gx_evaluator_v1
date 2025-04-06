import json
import sys
import re
from datetime import datetime

def load_json_file(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        sys.exit(1)

def format_conversation_content(content, max_length=10000):
    """Format conversation content with an optional length limit."""
    if len(content) > max_length:
        return content[:max_length] + "..."
    return content

def get_highlight_emoji(highlight):
    """Convert highlight value to emoji."""
    if highlight == "green":
        return "🟢"
    elif highlight == "red":
        return "🔴"
    elif highlight == "blue":
        return "🔵"
    elif highlight == "🔥":
        return "🔥"
    else:
        return highlight if highlight else ""

def generate_markdown(data):
    """Generate markdown from the JSON data."""
    ticket_info = data.get("ticket_info", {})
    conversation_flow = data.get("conversation_flow", [])
    performance_metrics = data.get("performance_metrics", {})
    sla_compliance = data.get("sla_compliance", {})
    timeline = data.get("timeline", [])
    
    # Start building the markdown
    markdown = "# Support Ticket Details\n\n"
    
    # Ticket Information
    markdown += "## Ticket Information\n"
    markdown += f"- **Conversation ID**: {ticket_info.get('conversation_id', 'N/A')}\n"
    markdown += f"- **Status**: {ticket_info.get('status', 'N/A').capitalize()} ({ticket_info.get('status_category', 'N/A').capitalize()})\n"
    markdown += f"- **Created**: {ticket_info.get('human_readable_created_at', 'N/A')}\n"
    markdown += f"- **Intent**: {ticket_info.get('intent', 'N/A')}\n\n"
    
    # Guest Information
    guest_info = ticket_info.get("guest_info", {})
    reservation_info = ticket_info.get("reservation_info", {})
    markdown += "## Guest Information\n"
    markdown += f"- **Name**: {guest_info.get('name', 'N/A')}\n"
    markdown += f"- **Reservation ID**: {reservation_info.get('id', 'N/A')}\n"
    markdown += f"- **Status**: {reservation_info.get('status', 'N/A')}\n"
    markdown += f"- **Stay Period**: {reservation_info.get('arrival', 'N/A')} - {reservation_info.get('departure', 'N/A')}\n"
    markdown += f"- **VIP Status**: {reservation_info.get('vip', 'No').capitalize()}\n\n"
    
    # Property Information
    property_info = ticket_info.get("property_info", {})
    markdown += "## Property Information\n"
    markdown += f"- **Name**: {property_info.get('name', 'N/A')}\n"
    markdown += f"- **ID**: {property_info.get('id', 'N/A')}\n\n"
    
    # Assignee
    assignee = ticket_info.get("assignee", {})
    if assignee:
        markdown += "## Assignee\n"
        markdown += f"- **Name**: {assignee.get('name', 'N/A')}\n"
        markdown += f"- **Email**: {assignee.get('email', 'N/A')}\n\n"
    
    # Tags
    tags = ticket_info.get("tags", [])
    if tags:
        markdown += "## Tags\n"
        for tag in tags:
            highlight = get_highlight_emoji(tag.get("highlight", ""))
            name = tag.get('name', 'N/A')
            description = tag.get('description', '')
            
            if description:
                # Replace newlines with commas for better readability
                cleaned_desc = description.replace("\n", ", ")
                markdown += f"- {highlight} **{name}** - {cleaned_desc}\n"
            else:
                markdown += f"- {highlight} **{name}**\n"
        markdown += "\n"
    
    # Performance Metrics
    markdown += "## Performance Metrics\n"
    markdown += f"- **First Response Time**: {performance_metrics.get('first_response_time_formatted', 'N/A')}\n"
    markdown += f"- **Resolution Time**: {performance_metrics.get('resolution_time_formatted', 'N/A')}\n"
    markdown += f"- **Agent Response Count**: {performance_metrics.get('agent_response_count', 'N/A')}\n"
    markdown += f"- **Customer Message Count**: {performance_metrics.get('customer_message_count', 'N/A')}\n"
    markdown += f"- **Total Messages**: {performance_metrics.get('total_messages', 'N/A')}\n"
    markdown += f"- **Average Response Time**: {performance_metrics.get('average_response_time_formatted', 'N/A')}\n"
    markdown += f"- **Transfers**: {performance_metrics.get('transfers', 'N/A')}\n"
    
    # SLA compliance
    sla_breached = sla_compliance.get("sla_breached", False)
    warning_triggered = sla_compliance.get("warning_triggered", False)
    markdown += f"- **SLA Breach**: {'Yes' if sla_breached else 'No'}"
    if warning_triggered:
        markdown += " (Warning triggered)"
    markdown += "\n\n"
    
    # Conversation Flow
    markdown += "## Conversation Flow\n\n"
    for message in conversation_flow:
        direction = message.get("direction", "")
        time = message.get("human_readable_time", "")
        content = message.get("content", "")
        
        markdown += f"### {direction} ({time})\n"
        markdown += "```\n"
        markdown += format_conversation_content(content)
        markdown += "\n```\n\n"
    
    # Timeline Summary
    markdown += "## Timeline Summary\n\n"
    
    # Extract key events from timeline
    key_events = []
    
    # Initial conversation
    first_message = next((event for event in timeline if event.get("event_type") == "inbound"), None)
    if first_message:
        time = first_message.get("human_readable_time", "")
        key_events.append((time, "Customer initiates conversation about luggage storage"))
    
    # Transfer events
    transfer_events = [event for event in timeline if event.get("event_type") == "move"]
    for event in transfer_events:
        time = event.get("human_readable_time", "")
        key_events.append((time, f"Conversation transferred from bot to human agent"))
    
    # System responses
    system_responses = [event for event in timeline if event.get("event_type") == "out_reply" and 
                        event.get("details", {}).get("author") == "System"]
    for event in system_responses:
        time = event.get("human_readable_time", "")
        key_events.append((time, "System acknowledgment sent to customer"))
    
    # Customer responses after transfer
    customer_responses = [event for event in timeline if event.get("event_type") == "inbound" and 
                          event.get("timestamp", 0) > (transfer_events[0].get("timestamp", 0) if transfer_events else 0)]
    for event in customer_responses:
        time = event.get("human_readable_time", "")
        message = event.get("details", {}).get("message", "")
        
        if message and message.lower() == "ok":
            key_events.append((time, "Customer acknowledges"))
        elif message and "limpieza" in message.lower():
            key_events.append((time, "Customer reports issue with cleaning service not arriving"))
    
    # Assignment events
    assign_events = [event for event in timeline if event.get("event_type") == "assign"]
    for event in assign_events:
        time = event.get("human_readable_time", "")
        details = event.get("details", {})
        assigned_to = details.get("assigned_to", "")
        key_events.append((time, f"Ticket assigned to {assigned_to}"))
    
    # Agent responses
    agent_responses = [event for event in timeline if event.get("event_type") == "out_reply" and 
                       event.get("details", {}).get("author") != "System"]
    for event in agent_responses:
        time = event.get("human_readable_time", "")
        message = event.get("details", {}).get("message", "")
        author = event.get("details", {}).get("author", "agent")
        
        if message and "limpieza" in message.lower():
            key_events.append((time, f"Agent {author} responds about cleaning service issue"))
    
    # Archive events
    archive_events = [event for event in timeline if event.get("event_type") == "archive"]
    for i, event in enumerate(archive_events):
        time = event.get("human_readable_time", "")
        initiated_by = event.get("initiated_by", {})
        
        # Get initiator name - could be rule name, teammate name, or 'api'
        if initiated_by.get("type") == "teammate":
            initiator = initiated_by.get("name", "Unknown")
            key_events.append((time, f"Conversation archived by {initiator}"))
    
    # Conversation termination
    termination_events = [event for event in timeline if event.get("event_type") == "comment" and 
                           event.get("details", {}).get("comment", "").find("terminated by timeout") >= 0]
    for event in termination_events:
        time = event.get("human_readable_time", "")
        key_events.append((time, "Conversation terminated by timeout"))
    
    # Sort events by timestamp
    key_events.sort(key=lambda x: x[0])
    
    # Add key events to markdown
    for i, (time, description) in enumerate(key_events):
        markdown += f"{i+1}. **{time}** - {description}\n"
    
    markdown += "\n"
    
    # Key Issues
    markdown += "## Key Issues\n"
    
    # Look for key phrases in the conversation flow and timeline
    key_issues = []
    
    # Check for luggage storage issues
    luggage_12_10 = False
    luggage_extra_hour = False
    no_storage = False
    cleaning_delay = False
    
    # Check conversation flow
    for msg in conversation_flow:
        content = msg.get("content", "").lower()
        if "dejar mi maleta hasta las 12-10" in content:
            luggage_12_10 = True
        if "dejar mi equipaje en la habitación 1 hora más" in content:
            luggage_extra_hour = True
        if "no ofrecemos consigna de equipaje" in content:
            no_storage = True
        if "esperando la limpieza" in content:
            cleaning_delay = True
    
    # Add found issues
    if luggage_12_10:
        key_issues.append("Initial request about leaving luggage until 12:10")
    if luggage_extra_hour:
        key_issues.append("Customer wanted to keep luggage in room for 1 extra hour")
    if no_storage:
        key_issues.append("Property doesn't offer luggage storage (suggested Bounce service)")
    if cleaning_delay:
        key_issues.append("Cleaning service delay reported by customer")
    
    # If no issues found, check message details in timeline as fallback
    if not key_issues:
        for event in timeline:
            if event.get("event_type") == "inbound":
                message = event.get("details", {}).get("message", "").lower()
                if "dejar mi maleta hasta las 12-10" in message:
                    key_issues.append("Initial request about leaving luggage until 12:10")
                if "dejar mi equipaje en la habitación 1 hora más" in message:
                    key_issues.append("Customer wanted to keep luggage in room for 1 extra hour")
                if "limpieza" in message and ("espera" in message or "todavía no" in message):
                    key_issues.append("Cleaning service delay reported by customer")
    
    for i, issue in enumerate(key_issues, 1):
        markdown += f"{i}. {issue}\n"
    
    return markdown

def save_markdown(markdown, output_file):
    """Save markdown to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(markdown)
        print(f"Markdown successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving markdown file: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python support_ticket_to_markdown.py input.json [output.md]")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "support_ticket.md"
    
    data = load_json_file(json_file)
    markdown = generate_markdown(data)
    save_markdown(markdown, output_file)

if __name__ == "__main__":
    main()