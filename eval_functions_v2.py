import json
import datetime
from typing import Dict, List, Any, Optional, Tuple


def convert_timestamp(timestamp: float) -> str:
    """Convert a unix timestamp to a readable date and time string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def extract_message_content(message_data: Dict[str, Any]) -> str:
    """Extract the message content from a message data object."""
    # Prefer text over body (since body might contain HTML)
    return message_data.get("text", message_data.get("body", "")).strip()


def is_bot_message(message_data: Dict[str, Any]) -> bool:
    """Determine if the message is from a bot based on content."""
    content = extract_message_content(message_data)
    # Look for indicators of bot messages
    return "(bot)" in content or ">>>" in content


def get_sender_name(event: Dict[str, Any]) -> str:
    """Get the name of the sender from the event data."""
    if event["type"] == "inbound":
        if is_bot_message(event["target"]["data"]):
            return "Bot"
        return "Customer"
    elif event["type"] == "out_reply":
        author = event["target"]["data"].get("author", {})
        if author and author.get("first_name"):
            return f"{author.get('first_name')} {author.get('last_name', '')}".strip()
        return "Agent"
    return "Unknown"


def calculate_time_difference(timestamp1: float, timestamp2: float) -> str:
    """Calculate the time difference between two timestamps and format it nicely."""
    diff_seconds = abs(timestamp2 - timestamp1)
    hours, remainder = divmod(diff_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{int(seconds)} second{'s' if seconds != 1 else ''}")
    
    return " ".join(parts)


def find_conversation_escalation_info(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find information about when and why the conversation was escalated."""
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda e: e["emitted_at"])
    
    # Find the first bot interaction and the first human agent interaction
    first_bot_timestamp = None
    first_agent_timestamp = None
    escalation_reason = "Unknown"
    
    for event in sorted_events:
        if event["type"] in ["inbound", "out_reply"]:
            message_data = event["target"]["data"]
            content = extract_message_content(message_data)
            
            # Look for bot messages
            if first_bot_timestamp is None and is_bot_message(message_data):
                first_bot_timestamp = event["emitted_at"]
            
            # Look for escalation indicators
            if "Hablar con un agente" in content or "Talk to an agent" in content:
                escalation_reason = "Customer requested agent"
            
            # Look for first human agent reply
            if first_agent_timestamp is None and event["type"] == "out_reply" and not is_bot_message(message_data):
                first_agent_timestamp = event["emitted_at"]
                # If we found the first agent response after a bot interaction, we can stop
                if first_bot_timestamp is not None:
                    break
    
    # Calculate bot interaction duration if we have both timestamps
    bot_interaction_duration = None
    if first_bot_timestamp is not None and first_agent_timestamp is not None:
        bot_interaction_duration = calculate_time_difference(
            first_bot_timestamp, first_agent_timestamp
        )
    
    return {
        "first_bot_timestamp": first_bot_timestamp,
        "first_agent_timestamp": first_agent_timestamp,
        "bot_interaction_duration": bot_interaction_duration,
        "escalation_reason": escalation_reason
    }


def extract_conversation_metadata(conversation: Dict[str, Any]) -> Dict[str, str]:
    """Extract key metadata from the conversation object."""
    metadata = {
        "id": conversation.get("id", "Unknown"),
        "subject": conversation.get("subject", "No subject"),
        "status": conversation.get("status", "Unknown"),
        "status_category": conversation.get("status_category", "Unknown"),
        "created_at": convert_timestamp(conversation.get("created_at", 0)),
    }
    
    # Extract customer information
    recipient = conversation.get("recipient", {})
    metadata["customer_handle"] = recipient.get("handle", "Unknown")
    
    # Extract custom fields
    custom_fields = conversation.get("custom_fields", {})
    for key, value in custom_fields.items():
        metadata[key] = value
    
    # Extract tags
    tags = conversation.get("tags", [])
    metadata["tags"] = ", ".join([tag.get("name", "") for tag in tags])
    
    # Extract reservation info from links
    links = conversation.get("links", [])
    for link in links:
        if link.get("type", "").startswith("app_"):
            link_fields = link.get("custom_fields", {})
            if "Guest Name" in link_fields:
                metadata["guest_name"] = link_fields["Guest Name"]
            if "Property Name" in link_fields:
                metadata["property_name"] = link_fields["Property Name"]
            if "Arrival Date" in link_fields:
                metadata["arrival_date"] = link_fields["Arrival Date"]
            if "Departure Date" in link_fields:
                metadata["departure_date"] = link_fields["Departure Date"]
    
    return metadata


def find_resolution_info(events: List[Dict[str, Any]], conversation_created_at: float) -> Dict[str, Any]:
    """Find information about the resolution of the conversation."""
    # Find the archive events
    archive_events = [e for e in events if e["type"] == "archive"]
    
    if not archive_events:
        return {"resolution_time": "Unresolved"}
    
    # Get the last archive event
    last_archive = sorted(archive_events, key=lambda e: e["emitted_at"])[-1]
    resolution_time = calculate_time_difference(
        conversation_created_at, last_archive["emitted_at"]
    )
    
    # Find first response time
    out_replies = [e for e in events if e["type"] == "out_reply"]
    first_response_time = None
    if out_replies:
        first_reply = sorted(out_replies, key=lambda e: e["emitted_at"])[0]
        first_response_time = calculate_time_difference(
            conversation_created_at, first_reply["emitted_at"]
        )
    
    return {
        "resolution_time": resolution_time,
        "first_response_time": first_response_time
    }


def extract_routing_info(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract information about how the conversation was routed."""
    inbox_moves = []
    assignments = []
    
    for event in events:
        # Track inbox moves
        if event["type"] == "move":
            if "target" in event and "data" in event["target"] and isinstance(event["target"]["data"], list):
                for inbox in event["target"]["data"]:
                    inbox_name = inbox.get("name", "Unknown inbox")
                    inbox_moves.append({
                        "timestamp": event["emitted_at"],
                        "inbox": inbox_name,
                        "source": event.get("source", {}).get("_meta", {}).get("type", "Unknown")
                    })
        
        # Track assignments
        elif event["type"] == "assign":
            if "target" in event and "data" in event["target"]:
                assignee = event["target"]["data"]
                assignments.append({
                    "timestamp": event["emitted_at"],
                    "assignee": f"{assignee.get('first_name', '')} {assignee.get('last_name', '')}".strip(),
                    "source": event.get("source", {}).get("_meta", {}).get("type", "Unknown"),
                    "source_name": event.get("source", {}).get("data", {}).get("name", "Unknown")
                })
    
    result = {}
    
    # Format inbox routing
    if inbox_moves:
        inbox_moves.sort(key=lambda x: x["timestamp"])
        initial_inbox = inbox_moves[0]["inbox"]
        final_inbox = inbox_moves[-1]["inbox"]
        route = " → ".join([move["inbox"] for move in inbox_moves])
        result.update({
            "initial_inbox": initial_inbox,
            "final_inbox": final_inbox,
            "routing_path": route
        })
    
    # Format assignments
    if assignments:
        assignments.sort(key=lambda x: x["timestamp"])
        assignment_info = assignments[-1]  # Get the last assignment
        result.update({
            "assigned_to": assignment_info["assignee"],
            "assigned_via": (f"{assignment_info['source_name']} "
                            f"({assignment_info['source']})" if assignment_info["source_name"] != "Unknown" else "Unknown")
        })
    
    return result


def extract_messages(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract messages from the events in chronological order."""
    message_events = []
    
    for event in events:
        if event["type"] in ["inbound", "out_reply", "comment"]:  # Added "comment" for internal comments
            message_data = event["target"]["data"]
            
            # Set sender type based on event type
            if event["type"] == "inbound":
                sender_type = "Customer" if not is_bot_message(message_data) else "Bot"
            elif event["type"] == "out_reply":
                sender_type = "Agent"
            elif event["type"] == "comment":
                sender_type = "Internal Comment"
            else:
                sender_type = "Unknown"
            
            # Get content based on event type
            if event["type"] == "comment":
                content = message_data.get("body", "").strip()
            else:
                content = extract_message_content(message_data)
            
            message_events.append({
                "timestamp": event["emitted_at"],
                "formatted_time": convert_timestamp(event["emitted_at"]),
                "sender_type": sender_type,
                "sender_name": get_sender_name(event),
                "content": content
            })
    
    # Sort by timestamp
    message_events.sort(key=lambda x: x["timestamp"])
    return message_events


def calculate_agent_response_metrics(events: List[Dict[str, Any]], conversation_created_at: float) -> Dict[str, Any]:
    """Calculate detailed agent response time metrics from events timeline."""
    metrics = {
        'first_response_time': None,
        'first_response_time_formatted': None,
        'avg_response_time': None,
        'avg_response_time_formatted': None,
        'response_times': [],
        'response_intervals': [],  # Store all intervals between guest messages and agent responses
        'breached_responses': [],  # Track responses that breached SLA
        'total_agent_responses': 0,
        'last_guest_message_time': None
    }

    # Sort events chronologically
    sorted_events = sorted(events, key=lambda e: e['emitted_at'])
    
    for event in sorted_events:
        if event['type'] == 'inbound' and not is_bot_message(event['target']['data']):
            # Track guest message time for calculating response interval
            metrics['last_guest_message_time'] = event['emitted_at']
            
        elif event['type'] == 'out_reply' and not is_bot_message(event['target']['data']):
            metrics['total_agent_responses'] += 1
            current_time = event['emitted_at']
            
            # Calculate first response time from ticket creation
            if metrics['first_response_time'] is None:
                metrics['first_response_time'] = current_time - conversation_created_at
                metrics['first_response_time_formatted'] = calculate_time_difference(
                    conversation_created_at, current_time
                )
            
            # Calculate response interval if there was a preceding guest message
            if metrics['last_guest_message_time']:
                interval = current_time - metrics['last_guest_message_time']
                metrics['response_intervals'].append(interval)
                
                # Check if this response breached SLA (15 minutes)
                if interval > 900:  # 15 minutes in seconds
                    metrics['breached_responses'].append({
                        'response_time': interval,
                        'formatted_time': calculate_time_difference(metrics['last_guest_message_time'], current_time)
                    })
                
                metrics['last_guest_message_time'] = None  # Reset for next interaction
    
    # Calculate average response time
    if metrics['response_intervals']:
        metrics['avg_response_time'] = sum(metrics['response_intervals']) / len(metrics['response_intervals'])
        metrics['avg_response_time_formatted'] = calculate_time_difference(0, metrics['avg_response_time'])
    
    return metrics


def events_to_markdown(events: List[Dict[str, Any]]) -> str:
    """Convert Front event log to markdown format for LLM context."""
    if not events:
        return "# No events to process"
    
    # Get conversation data from the first event
    conversation = events[0]["conversation"]
    conversation_metadata = extract_conversation_metadata(conversation)
    
    # Get other important information
    escalation_info = find_conversation_escalation_info(events)
    resolution_info = find_resolution_info(events, conversation.get("created_at", 0))
    routing_info = extract_routing_info(events)
    messages = extract_messages(events)
    
    # Calculate detailed agent response metrics
    agent_metrics = calculate_agent_response_metrics(events, conversation.get("created_at", 0))
    
    # Start building the markdown
    markdown = f"# Conversation: {conversation_metadata['subject']}\n\n"
    
    # Customer & Conversation Details Section
    markdown += "## Customer & Conversation Details\n\n"
    
    if "guest_name" in conversation_metadata:
        markdown += f"- **Guest Name**: {conversation_metadata['guest_name']}\n"
    markdown += f"- **Customer Contact**: {conversation_metadata['customer_handle']}\n"
    
    if "Boost Reservation ID" in conversation_metadata:
        markdown += f"- **Reservation ID**: {conversation_metadata.get('Boost Reservation ID', 'Unknown')}\n"
    
    if "property_name" in conversation_metadata:
        markdown += f"- **Property**: {conversation_metadata['property_name']}\n"
    
    if "arrival_date" in conversation_metadata and "departure_date" in conversation_metadata:
        markdown += f"- **Stay Period**: {conversation_metadata['arrival_date']} to {conversation_metadata['departure_date']}\n"
    
    markdown += f"- **Conversation Created**: {conversation_metadata['created_at']}\n"
    markdown += f"- **Status**: {conversation_metadata['status']} ({conversation_metadata['status_category']})\n"
    
    if conversation_metadata.get('tags'):
        markdown += f"- **Tags**: {conversation_metadata['tags']}\n"
    
    if "Boost EBD intent" in conversation_metadata:
        markdown += f"- **Detected Intent**: {conversation_metadata.get('Boost EBD intent', 'Unknown')}\n"
    
    markdown += "\n"
    
    # Handling Information Section
    markdown += "## Conversation Processing\n\n"
    
    if agent_metrics['first_response_time_formatted']:
        markdown += f"- **First Response Time**: {agent_metrics['first_response_time_formatted']}\n"
    
    if agent_metrics['avg_response_time_formatted']:
        markdown += f"- **Average Response Time**: {agent_metrics['avg_response_time_formatted']}\n"
    
    if agent_metrics['breached_responses']:
        markdown += "- **SLA Breached Responses**:\n"
        for breach in agent_metrics['breached_responses']:
            markdown += f"  - Response delayed by {breach['formatted_time']}\n"
    
    markdown += f"- **Total Agent Responses**: {agent_metrics['total_agent_responses']}\n"
    markdown += f"- **Total Resolution Time**: {resolution_info['resolution_time']}\n"
    
    if routing_info.get("routing_path"):
        markdown += f"- **Routing Path**: {routing_info['routing_path']}\n"
    
    if routing_info.get("assigned_to"):
        markdown += f"- **Assigned To**: {routing_info['assigned_to']}\n"
        markdown += f"- **Assignment Method**: {routing_info.get('assigned_via', 'Unknown')}\n"
    
    # System Intelligence Section
    markdown += "\n## System Intelligence\n\n"
    
    if escalation_info.get("bot_interaction_duration"):
        markdown += f"- **Bot Interaction Duration**: {escalation_info['bot_interaction_duration']}\n"
    
    markdown += f"- **Early Bird Detection (EBD)**: {conversation_metadata.get('Boost EBD', 'No')}\n"
    markdown += f"- **LLM Assisted**: {conversation_metadata.get('Boost LLM', 'No')}\n"
    markdown += f"- **Escalation Reason**: {escalation_info['escalation_reason']}\n"
    markdown += f"- **Escalation Occurred**: {conversation_metadata.get('Boost Escalation', 'No')}\n"
    
    # Message History Section
    markdown += "\n## Conversation History\n\n"
    
    for msg in messages:
        markdown += f"### {msg['formatted_time']} - {msg['sender_name']} ({msg['sender_type']})\n\n"
        markdown += f"{msg['content']}\n\n"
    
    with open("ticket_summaryv2", "w") as file:
        file.write(markdown)
    
    return markdown


# def generate_audit_summary(audit_result):
#     """Generate a human-readable summary of the audit results"""
    
#     metrics = audit_result['performance_metrics']
#     sla = audit_result['sla_compliance']
#     ticket = audit_result['ticket_info']
    
#     summary = f"""
# TICKET AUDIT SUMMARY - {ticket['conversation_id']}
# ===========================================

# BASIC INFORMATION:
# Guest: {ticket['guest_info'].get('name', 'Unknown')}
# Property: {ticket['property_info'].get('name', 'Unknown')}
# Reservation: {ticket['reservation_info'].get('id', 'Unknown')}
# Created: {ticket['human_readable_created_at']}
# Intent: {ticket['intent']}
# Current Status: {ticket['status']}

# PERFORMANCE METRICS:
# First Response Time: {metrics.get('first_response_time_formatted', 'N/A')}
# Resolution Time: {metrics.get('resolution_time_formatted', 'N/A')}
# Average Response Time: {metrics.get('average_response_time_formatted', 'N/A')}
# Total Messages: {metrics['total_messages']} (Customer: {metrics['customer_message_count']}, Agent: {metrics['agent_response_count']})
# Transfers: {metrics['transfers']}
# Agent Actions: {metrics['agent_actions']}
# Automated Actions: {metrics['automations_triggered']}

# SLA COMPLIANCE:
# SLA Breached: {'Yes' if sla['sla_breached'] else 'No'}
# Warning Triggered: {'Yes' if sla['warning_triggered'] else 'No'}
# First Response Time: {sla.get('first_response_time', 'N/A')} (Within SLA: {'Yes' if sla.get('first_response_within_sla', False) else 'No'})
# Total Handle Time: {sla.get('total_handle_time', 'N/A')} (Within SLA: {'Yes' if sla.get('resolution_within_sla', False) else 'No'})

# KEY EVENTS:
# """
    
#     # Add key events
#     sorted_timeline = sorted(audit_result['timeline'], key=lambda x: x['timestamp'])
#     key_event_types = ['inbound', 'out_reply', 'assign', 'move', 'tag', 'archive', 'reopen']
    
#     for event in sorted_timeline:
#         if event['event_type'] in key_event_types:
#             action = event['details'].get('action', event['event_type'])
            
#             # Add additional context based on event type
#             details = ""
#             if event['event_type'] in ['inbound', 'out_reply']:
#                 message_preview = event['details'].get('message', '')
#                 if message_preview and len(message_preview) > 50:
#                     message_preview = message_preview[:50] + "..."
#                 details = f" - {message_preview}"
#             elif event['event_type'] == 'tag':
#                 details = f" - {event['details'].get('tag_name', '')}"
#             elif event['event_type'] == 'move':
#                 details = f" - To: {event['details'].get('destination', '')}"
#             elif event['event_type'] == 'assign':
#                 details = f" - To: {event['details'].get('assigned_to', '')}"
            
#             summary += f"- {event['human_readable_time']} - {action}{details}\n"
    
#     # Add assessment and recommendations
#     summary += """
# ASSESSMENT:
# """
    
#     # Automated assessment based on metrics
#     if sla['sla_breached']:
#         summary += "- SLA BREACH: Response time exceeded allowed threshold\n"
    
#     if metrics['transfers'] > 2:
#         summary += f"- HIGH TRANSFER COUNT: Ticket was transferred {metrics['transfers']} times\n"
    
#     good_response_time = metrics.get('average_response_time', float('inf')) < 900  # 15 minutes
#     if good_response_time:
#         summary += "- GOOD RESPONSE TIME: Agent responses were prompt\n"
#     else:
#         summary += "- SLOW RESPONSE TIME: Agent responses were delayed\n"
    
#     # Add overall assessment
#     if not sla['sla_breached'] and metrics['transfers'] <= 2 and good_response_time:
#         summary += "\nOVERALL: Ticket handled well within expected parameters\n"
#     else:
#         summary += "\nOVERALL: Ticket handling could be improved\n"
    
#     # Add recommendations
#     summary += """
# RECOMMENDATIONS:
# """
    
#     if sla['sla_breached']:
#         summary += "- Review staffing during this time period to ensure adequate coverage\n"
    
#     if metrics['transfers'] > 2:
#         summary += "- Improve initial routing to reduce unnecessary transfers\n"
    
#     if not good_response_time:
#         summary += "- Provide additional training on efficient response handling\n"
    
#     return summary