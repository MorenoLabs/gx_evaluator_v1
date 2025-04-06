def create_detailed_ticket_audit(event_data):
    """Create a comprehensive timeline for ticket audit with all relevant details"""
    
    # Extract basic ticket information
    ticket_info = extract_ticket_info(event_data)
    
    # Build detailed timeline
    timeline = []
    
    # Process events in chronological order (oldest to newest)
    sorted_events = sorted(event_data, key=lambda x: x.get('emitted_at', 0))
    
    for event in sorted_events:
        event_details = {
            'timestamp': event.get('emitted_at'),
            'human_readable_time': format_timestamp(event.get('emitted_at')),
            'event_id': event.get('id'),
            'event_type': event.get('type'),
            'details': {}
        }
        
        # Extract source information (who/what triggered the event)
        source = event.get('source', {})
        source_type = source.get('_meta', {}).get('type')
        source_data = source.get('data')
        
        if source_type:
            event_details['initiated_by'] = {
                'type': source_type
            }
            
            if source_type == 'teammate' and source_data:
                event_details['initiated_by']['name'] = f"{source_data.get('first_name', '')} {source_data.get('last_name', '')}"
                event_details['initiated_by']['email'] = source_data.get('email')
                event_details['initiated_by']['id'] = source_data.get('id')
            
            elif source_type == 'rule' and source_data:
                event_details['initiated_by']['name'] = source_data.get('name')
                event_details['initiated_by']['id'] = source_data.get('id')
                event_details['initiated_by']['actions'] = source_data.get('actions')
            
            elif source_type == 'inboxes' and source_data:
                event_details['initiated_by']['inbox'] = source_data[0].get('name') if source_data else None
                event_details['initiated_by']['inbox_id'] = source_data[0].get('id') if source_data else None
            
            elif source_type == 'api':
                event_details['initiated_by']['description'] = "API or automated system"
        
        # Extract target information (what was changed)
        target = event.get('target', {})
        target_type = target.get('_meta', {}).get('type')
        target_data = target.get('data')
        
        if target_type:
            event_details['target'] = {
                'type': target_type
            }
            
            if target_type == 'tag' and target_data:
                event_details['target']['tag_name'] = target_data.get('name')
                event_details['target']['tag_id'] = target_data.get('id')
                event_details['target']['highlight'] = target_data.get('highlight')
                event_details['target']['description'] = target_data.get('description')
            
            elif target_type == 'message' and target_data:
                event_details['target']['message_id'] = target_data.get('id')
                event_details['target']['is_inbound'] = target_data.get('is_inbound')
                event_details['target']['content'] = target_data.get('text')
                
                author = target_data.get('author')
                if author:
                    event_details['target']['author'] = {
                        'id': author.get('id'),
                        'name': f"{author.get('first_name', '')} {author.get('last_name', '')}",
                        'type': 'teammate'
                    }
                else:
                    # Try to get customer info from recipients
                    for recipient in target_data.get('recipients', []):
                        if recipient.get('role') == 'from':
                            event_details['target']['author'] = {
                                'handle': recipient.get('handle'),
                                'type': 'customer'
                            }
                            break
            
            elif target_type == 'teammate' and target_data:
                event_details['target']['name'] = f"{target_data.get('first_name', '')} {target_data.get('last_name', '')}"
                event_details['target']['id'] = target_data.get('id')
                event_details['target']['email'] = target_data.get('email')
            
            elif target_type == 'inboxes' and target_data:
                event_details['target']['inbox'] = target_data[0].get('name') if target_data else None
                event_details['target']['inbox_id'] = target_data[0].get('id') if target_data else None
            
            elif target_type == 'custom_field':
                event_details['target']['field'] = "Custom field update"
        
        # Add event-specific details
        if event.get('type') == 'tag':
            event_details['details']['action'] = 'Added tag'
            if target_data:
                event_details['details']['tag_name'] = target_data.get('name')
        
        elif event.get('type') == 'untag':
            event_details['details']['action'] = 'Removed tag'
            if target_data:
                event_details['details']['tag_name'] = target_data.get('name')
        
        elif event.get('type') == 'assign':
            event_details['details']['action'] = 'Assigned conversation'
            if target_data:
                event_details['details']['assigned_to'] = f"{target_data.get('first_name', '')} {target_data.get('last_name', '')}"
        
        elif event.get('type') == 'move':
            event_details['details']['action'] = 'Moved conversation'
            if target_data:
                event_details['details']['destination'] = target_data[0].get('name') if target_data else None
        
        elif event.get('type') == 'archive':
            event_details['details']['action'] = 'Archived conversation'
        
        elif event.get('type') == 'reopen':
            event_details['details']['action'] = 'Reopened conversation'
        
        elif event.get('type') == 'out_reply':
            event_details['details']['action'] = 'Sent reply'
            if target_data:
                event_details['details']['message'] = target_data.get('text')
                event_details['details']['author'] = f"{target_data.get('author', {}).get('first_name', '')} {target_data.get('author', {}).get('last_name', '')}" if target_data.get('author') else 'System'
        
        elif event.get('type') == 'inbound':
            event_details['details']['action'] = 'Received message'
            if target_data:
                event_details['details']['message'] = target_data.get('text')
                
                # Try to extract customer info
                for recipient in target_data.get('recipients', []):
                    if recipient.get('role') == 'from':
                        event_details['details']['from'] = recipient.get('handle')
                        break
        
        elif event.get('type') == 'custom_field_updated':
            event_details['details']['action'] = 'Updated custom field'
            # Try to determine which field was updated from context
            conversation = event.get('conversation', {})
            custom_fields = conversation.get('custom_fields', {})
            if custom_fields:
                field_names = ", ".join(custom_fields.keys())
                event_details['details']['fields'] = field_names
        
        elif event.get('type') == 'comment':
            event_details['details']['action'] = 'Added comment'
            if target_data:
                event_details['details']['comment'] = target_data.get('body', '')
                event_details['details']['author'] = f"{target_data.get('author', {}).get('first_name', '')} {target_data.get('author', {}).get('last_name', '')}" if target_data.get('author') else 'Unknown'
        
        elif event.get('type') == 'link_added':
            event_details['details']['action'] = 'Added link'
            if target_data:
                event_details['details']['link_name'] = target_data.get('name')
                event_details['details']['link_type'] = target_data.get('type')
        
        timeline.append(event_details)
    
    # Extract all messages in order for conversation flow
    conversation_flow = extract_conversation_flow(timeline)
    
    # Calculate workflow metrics
    workflow_metrics = analyze_workflow(timeline)
    
    return {
        'ticket_info': ticket_info,
        'timeline': timeline,
        'conversation_flow': conversation_flow,
        'performance_metrics': calculate_performance_metrics(ticket_info, timeline),
        'workflow_metrics': workflow_metrics,
        'sla_compliance': analyze_sla_compliance(ticket_info, timeline, workflow_metrics)
    }

def extract_ticket_info(event_data):
    """Extract general ticket information from event data"""
    
    # Find most recent event to get latest conversation state
    sorted_events = sorted(event_data, key=lambda x: x.get('emitted_at', 0), reverse=True)
    latest_event = sorted_events[0] if sorted_events else {}
    conversation = latest_event.get('conversation', {})
    
    # Get the earliest event to find creation time
    earliest_event = sorted(event_data, key=lambda x: x.get('emitted_at', 0))[0] if event_data else {}
    
    # Extract basic info
    ticket_info = {
        'conversation_id': conversation.get('id'),
        'status': conversation.get('status'),
        'status_category': conversation.get('status_category'),
        'created_at': earliest_event.get('emitted_at') or conversation.get('created_at'),
        'human_readable_created_at': format_timestamp(earliest_event.get('emitted_at') or conversation.get('created_at')),
        'custom_fields': conversation.get('custom_fields', {}),
        'intent': conversation.get('custom_fields', {}).get('Boost EBD intent'),
        'guest_info': {},
        'property_info': {},
        'reservation_info': {}
    }
    
    # Extract reservation and guest info from links
    for link in conversation.get('links', []):
        if link.get('type') == 'app_f9660bd9f0c89d04':  # Reservation link
            custom_fields = link.get('custom_fields', {})
            
            ticket_info['guest_info']['name'] = custom_fields.get('Guest Name')
            ticket_info['property_info']['name'] = custom_fields.get('Property Name')
            ticket_info['property_info']['id'] = custom_fields.get('Property Id')
            ticket_info['reservation_info']['id'] = link.get('name')
            ticket_info['reservation_info']['status'] = custom_fields.get('Reservation Status')
            ticket_info['reservation_info']['arrival'] = custom_fields.get('Arrival Date')
            ticket_info['reservation_info']['departure'] = custom_fields.get('Departure Date')
            ticket_info['reservation_info']['vip'] = custom_fields.get('Vip')
    
    # Get assignee info
    assignee = conversation.get('assignee', {})
    if assignee:
        ticket_info['assignee'] = {
            'id': assignee.get('id'),
            'name': f"{assignee.get('first_name', '')} {assignee.get('last_name', '')}",
            'email': assignee.get('email')
        }
    
    # Get tags
    tags = []
    for tag in conversation.get('tags', []):
        tags.append({
            'id': tag.get('id'),
            'name': tag.get('name'),
            'highlight': tag.get('highlight'),
            'description': tag.get('description')
        })
    ticket_info['tags'] = tags
    
    # Extract inbox information
    ticket_info['inboxes'] = []
    for event in event_data:
        if event.get('type') == 'move':
            target_data = event.get('target', {}).get('data')
            if target_data and len(target_data) > 0:
                inbox = {
                    'id': target_data[0].get('id'),
                    'name': target_data[0].get('name'),
                    'moved_at': event.get('emitted_at'),
                    'human_readable_moved_at': format_timestamp(event.get('emitted_at'))
                }
                if inbox not in ticket_info['inboxes']:
                    ticket_info['inboxes'].append(inbox)
    
    return ticket_info

def extract_conversation_flow(timeline):
    """Extract just the message flow from the timeline for easy review"""
    
    conversation = []
    
    for event in timeline:
        if event['event_type'] in ['inbound', 'out_reply']:
            message = {
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'is_inbound': event['event_type'] == 'inbound',
                'direction': 'Customer → Agent' if event['event_type'] == 'inbound' else 'Agent → Customer'
            }
            
            # Get message content
            if 'message' in event['details']:
                message['content'] = event['details']['message']
            elif 'content' in event.get('target', {}):
                message['content'] = event['target']['content']
            else:
                message['content'] = "[No message content available]"
            
            # Get author
            if 'author' in event['details']:
                message['author'] = event['details']['author']
            elif 'author' in event.get('target', {}):
                if isinstance(event['target']['author'], dict):
                    if event['target']['author'].get('type') == 'teammate':
                        message['author'] = event['target']['author'].get('name', 'Agent')
                    else:
                        message['author'] = event['target']['author'].get('handle', 'Customer')
            
            conversation.append(message)
    
    return conversation

def analyze_workflow(timeline):
    """Analyze workflow patterns from the timeline"""
    
    workflow = {
        'ticket_routing': [],
        'tag_changes': [],
        'assignment_changes': [],
        'status_changes': [],
        'automation_events': [],
        'human_interactions': []
    }
    
    for event in timeline:
        # Categorize events by type
        if event['event_type'] == 'move':
            workflow['ticket_routing'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'destination': event['details'].get('destination', 'Unknown'),
                'initiated_by': event.get('initiated_by', {}).get('type', 'Unknown')
            })
        
        elif event['event_type'] in ['tag', 'untag']:
            workflow['tag_changes'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'action': event['details'].get('action'),
                'tag_name': event['details'].get('tag_name'),
                'initiated_by': event.get('initiated_by', {}).get('type', 'Unknown')
            })
        
        elif event['event_type'] == 'assign':
            workflow['assignment_changes'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'assigned_to': event['details'].get('assigned_to', 'Unknown'),
                'initiated_by': event.get('initiated_by', {}).get('type', 'Unknown')
            })
        
        elif event['event_type'] in ['archive', 'reopen']:
            workflow['status_changes'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'action': event['details'].get('action'),
                'initiated_by': event.get('initiated_by', {}).get('type', 'Unknown')
            })
        
        # Track automated vs. human actions
        if event.get('initiated_by', {}).get('type') in ['rule', 'api']:
            workflow['automation_events'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'event_type': event['event_type'],
                'details': event['details'],
                'automation': event.get('initiated_by', {}).get('name', 'Unknown automation')
            })
        
        elif event.get('initiated_by', {}).get('type') == 'teammate':
            workflow['human_interactions'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'event_type': event['event_type'],
                'details': event['details'],
                'teammate': event.get('initiated_by', {}).get('name', 'Unknown teammate')
            })
    
    return workflow

def analyze_sla_compliance(ticket_info, timeline, workflow_metrics):
    """Analyze SLA compliance based on tags and timing"""
    
    sla_analysis = {
        'sla_breached': False,
        'warning_triggered': False,
        'first_response_time_seconds': None,
        'total_handle_time_seconds': None,
        'first_response_within_sla': None,
        'resolution_within_sla': None,
        'sla_related_events': []
    }
    
    # Check for SLA tags
    for tag_change in workflow_metrics['tag_changes']:
        if 'KPI Warning' in tag_change.get('tag_name', ''):
            sla_analysis['warning_triggered'] = True
            sla_analysis['sla_related_events'].append({
                'timestamp': tag_change['timestamp'],
                'human_readable_time': tag_change['human_readable_time'],
                'event': 'KPI Warning tag added',
                'initiated_by': tag_change.get('initiated_by')
            })
        
        if 'SLA Breach' in tag_change.get('tag_name', '') or 'SLA Applies' in tag_change.get('tag_name', ''):
            sla_analysis['sla_related_events'].append({
                'timestamp': tag_change['timestamp'],
                'human_readable_time': tag_change['human_readable_time'],
                'event': f"{tag_change.get('tag_name')} tag {tag_change.get('action', 'changed')}",
                'initiated_by': tag_change.get('initiated_by')
            })
    
    # Calculate first response time
    creation_time = ticket_info.get('created_at')
    first_response_time = None
    
    for event in timeline:
        if event['event_type'] == 'out_reply' and event.get('initiated_by', {}).get('type') == 'teammate':
            if first_response_time is None or event['timestamp'] < first_response_time:
                first_response_time = event['timestamp']
                sla_analysis['sla_related_events'].append({
                    'timestamp': event['timestamp'],
                    'human_readable_time': event['human_readable_time'],
                    'event': 'First agent response',
                    'initiated_by': event.get('initiated_by', {}).get('name', 'Unknown')
                })
    
    if first_response_time and creation_time:
        sla_analysis['first_response_time_seconds'] = first_response_time - creation_time
        
        # Assume SLA of 15 minutes (900 seconds) for first response - adjust as needed
        sla_threshold = 900  # 15 minutes
        sla_analysis['first_response_within_sla'] = sla_analysis['first_response_time_seconds'] <= sla_threshold
        
        if not sla_analysis['first_response_within_sla']:
            sla_analysis['sla_breached'] = True
    
    # Calculate total handle time
    resolution_time = None
    for event in timeline:
        if event['event_type'] == 'archive':
            resolution_time = event['timestamp']
            sla_analysis['sla_related_events'].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'event': 'Ticket archived/resolved',
                'initiated_by': event.get('initiated_by', {}).get('name', 'Unknown')
            })
    
    if resolution_time and creation_time:
        sla_analysis['total_handle_time_seconds'] = resolution_time - creation_time
        
        # Assume SLA of 24 hours (86400 seconds) for resolution - adjust as needed
        resolution_sla_threshold = 86400  # 24 hours
        sla_analysis['resolution_within_sla'] = sla_analysis['total_handle_time_seconds'] <= resolution_sla_threshold
        
        if not sla_analysis['resolution_within_sla']:
            sla_analysis['sla_breached'] = True
    
    # Format times for readability
    if sla_analysis['first_response_time_seconds'] is not None:
        sla_analysis['first_response_time'] = format_duration(sla_analysis['first_response_time_seconds'])
    
    if sla_analysis['total_handle_time_seconds'] is not None:
        sla_analysis['total_handle_time'] = format_duration(sla_analysis['total_handle_time_seconds'])
    
    return sla_analysis

def calculate_performance_metrics(ticket_info, timeline):
    """Calculate performance metrics from timeline"""
    
    metrics = {
        'first_response_time': None,
        'resolution_time': None,
        'agent_response_count': 0,
        'customer_message_count': 0,
        'total_messages': 0,
        'average_response_time': None,
        'transfers': 0,
        'tags_added': 0,
        'tags_removed': 0,
        'automations_triggered': 0,
        'agent_actions': 0
    }
    
    # Find creation time
    creation_time = ticket_info.get('created_at')
    
    # Initialize for average response time calculation
    response_times = []
    last_customer_message_time = None
    
    # Track the chronology
    for event in timeline:
        # Count messages and calculate response times
        if event['event_type'] == 'inbound':
            metrics['customer_message_count'] += 1
            metrics['total_messages'] += 1
            last_customer_message_time = event['timestamp']
        
        elif event['event_type'] == 'out_reply':
            metrics['agent_response_count'] += 1
            metrics['total_messages'] += 1
            
            # Calculate response time if we have a preceding customer message
            if last_customer_message_time:
                response_time = event['timestamp'] - last_customer_message_time
                response_times.append(response_time)
                last_customer_message_time = None  # Reset until next customer message
            
            # Check if this is the first response
            if metrics['first_response_time'] is None:
                metrics['first_response_time'] = event['timestamp'] - creation_time
        
        # Count other events
        if event['event_type'] == 'move':
            metrics['transfers'] += 1
        
        elif event['event_type'] == 'tag':
            metrics['tags_added'] += 1
        
        elif event['event_type'] == 'untag':
            metrics['tags_removed'] += 1
        
        elif event['event_type'] == 'archive':
            metrics['resolution_time'] = event['timestamp'] - creation_time
        
        # Count automations vs agent actions
        if event.get('initiated_by', {}).get('type') in ['rule', 'api']:
            metrics['automations_triggered'] += 1
        elif event.get('initiated_by', {}).get('type') == 'teammate':
            metrics['agent_actions'] += 1
    
    # Calculate average response time
    if response_times:
        metrics['average_response_time'] = sum(response_times) / len(response_times)
        metrics['response_times'] = response_times  # Store all response times for further analysis
    
    # Format times for readability
    if metrics['first_response_time'] is not None:
        metrics['first_response_time_formatted'] = format_duration(metrics['first_response_time'])
    
    if metrics['resolution_time'] is not None:
        metrics['resolution_time_formatted'] = format_duration(metrics['resolution_time'])
    
    if metrics['average_response_time'] is not None:
        metrics['average_response_time_formatted'] = format_duration(metrics['average_response_time'])
    
    return metrics

def format_timestamp(timestamp):
    """Convert Unix timestamp to human readable format"""
    from datetime import datetime
    if not timestamp:
        return None
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def format_duration(seconds):
    """Format duration in seconds to a readable format"""
    if not seconds:
        return "N/A"
    
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(sec)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(sec)}s"
    else:
        return f"{int(sec)}s"

def test_audit_script_with_data(events_data):
    """Test the audit script with provided event data"""
    
    # Run the audit function
    audit_result = create_detailed_ticket_audit(events_data)
    
    # Save the formatted output
    with open("ticket_audit_output.json", 'w', encoding='utf-8') as f:
        json.dump(audit_result, f, indent=2, ensure_ascii=False)
    
    # Print a summary
    print(f"Ticket ID: {audit_result['ticket_info']['conversation_id']}")
    print(f"Guest: {audit_result['ticket_info']['guest_info'].get('name')}")
    print(f"Property: {audit_result['ticket_info']['property_info'].get('name')}")
    print(f"Intent: {audit_result['ticket_info']['intent']}")
    print(f"Created at: {audit_result['ticket_info']['human_readable_created_at']}")
    print(f"Total events in timeline: {len(audit_result['timeline'])}")
    
    # Print performance metrics
    metrics = audit_result['performance_metrics']
    print("\nPerformance Metrics:")
    print(f"First response time: {metrics.get('first_response_time_formatted', 'N/A')}")
    print(f"Resolution time: {metrics.get('resolution_time_formatted', 'N/A')}")
    print(f"Average response time: {metrics.get('average_response_time_formatted', 'N/A')}")
    print(f"Total messages: {metrics['total_messages']} (Customer: {metrics['customer_message_count']}, Agent: {metrics['agent_response_count']})")
    print(f"Transfers: {metrics['transfers']}")
    print(f"Agent actions: {metrics['agent_actions']}")
    print(f"Automations triggered: {metrics['automations_triggered']}")
    
    # Print SLA information
    sla = audit_result['sla_compliance']
    print("\nSLA Compliance:")
    print(f"SLA breached: {'Yes' if sla['sla_breached'] else 'No'}")
    print(f"Warning triggered: {'Yes' if sla['warning_triggered'] else 'No'}")
    print(f"First response time: {sla.get('first_response_time', 'N/A')} (Within SLA: {sla.get('first_response_within_sla', 'Unknown')})")
    print(f"Total handle time: {sla.get('total_handle_time', 'N/A')} (Within SLA: {sla.get('resolution_within_sla', 'Unknown')})")
    
    # Print sample timeline events
    print("\nSample timeline events:")
    for event in audit_result['timeline'][:5]:  # Print first 5 events
        print(f"{event['human_readable_time']} - {event['event_type']}: {event['details'].get('action', '')}")
    
    # Print conversation sample
    # Print conversation sample
    print("\nConversation sample:")
    for message in audit_result['conversation_flow'][:3]:  # Print first 3 messages
        content = message.get('content', '')
        if len(content) > 100:
            content_preview = f"{content[:100]}..."
        else:
            content_preview = content
        print(f"{message['human_readable_time']} - {message['direction']}: {content_preview}")
        
        return audit_result

def analyze_tag_patterns(audit_result):
    """Analyze patterns in tag usage"""
    tag_patterns = {
        'tag_frequency': {},
        'tag_timings': {},
        'common_tag_sequences': []
    }
    
    # Count tag frequency
    for event in audit_result['timeline']:
        if event['event_type'] == 'tag' and 'tag_name' in event.get('details', {}):
            tag_name = event['details']['tag_name']
            tag_patterns['tag_frequency'][tag_name] = tag_patterns['tag_frequency'].get(tag_name, 0) + 1
            
            # Track when tags are added
            if tag_name not in tag_patterns['tag_timings']:
                tag_patterns['tag_timings'][tag_name] = []
            
            tag_patterns['tag_timings'][tag_name].append({
                'timestamp': event['timestamp'],
                'human_readable_time': event['human_readable_time'],
                'added_by': event.get('initiated_by', {}).get('name', 'Unknown')
            })
    
    # Look for common tag sequences
    tag_events = [event for event in audit_result['timeline'] if event['event_type'] in ['tag', 'untag']]
    if len(tag_events) >= 2:
        for i in range(len(tag_events) - 1):
            current = tag_events[i]
            next_event = tag_events[i+1]
            
            if 'tag_name' in current.get('details', {}) and 'tag_name' in next_event.get('details', {}):
                sequence = {
                    'first_event': f"{current['details'].get('action')} {current['details'].get('tag_name')}",
                    'second_event': f"{next_event['details'].get('action')} {next_event['details'].get('tag_name')}",
                    'time_between': format_duration(next_event['timestamp'] - current['timestamp'])
                }
                tag_patterns['common_tag_sequences'].append(sequence)
    
    return tag_patterns

def generate_audit_summary(audit_result):
    """Generate a human-readable summary of the audit results"""
    
    metrics = audit_result['performance_metrics']
    sla = audit_result['sla_compliance']
    ticket = audit_result['ticket_info']
    
    summary = f"""
TICKET AUDIT SUMMARY - {ticket['conversation_id']}
===========================================

BASIC INFORMATION:
Guest: {ticket['guest_info'].get('name', 'Unknown')}
Property: {ticket['property_info'].get('name', 'Unknown')}
Reservation: {ticket['reservation_info'].get('id', 'Unknown')}
Created: {ticket['human_readable_created_at']}
Intent: {ticket['intent']}
Current Status: {ticket['status']}

PERFORMANCE METRICS:
First Response Time: {metrics.get('first_response_time_formatted', 'N/A')}
Resolution Time: {metrics.get('resolution_time_formatted', 'N/A')}
Average Response Time: {metrics.get('average_response_time_formatted', 'N/A')}
Total Messages: {metrics['total_messages']} (Customer: {metrics['customer_message_count']}, Agent: {metrics['agent_response_count']})
Transfers: {metrics['transfers']}
Agent Actions: {metrics['agent_actions']}
Automated Actions: {metrics['automations_triggered']}

SLA COMPLIANCE:
SLA Breached: {'Yes' if sla['sla_breached'] else 'No'}
Warning Triggered: {'Yes' if sla['warning_triggered'] else 'No'}
First Response Time: {sla.get('first_response_time', 'N/A')} (Within SLA: {'Yes' if sla.get('first_response_within_sla', False) else 'No'})
Total Handle Time: {sla.get('total_handle_time', 'N/A')} (Within SLA: {'Yes' if sla.get('resolution_within_sla', False) else 'No'})

KEY EVENTS:
"""
    
    # Add key events
    sorted_timeline = sorted(audit_result['timeline'], key=lambda x: x['timestamp'])
    key_event_types = ['inbound', 'out_reply', 'assign', 'move', 'tag', 'archive', 'reopen']
    
    for event in sorted_timeline:
        if event['event_type'] in key_event_types:
            action = event['details'].get('action', event['event_type'])
            
            # Add additional context based on event type
            details = ""
            if event['event_type'] in ['inbound', 'out_reply']:
                message_preview = event['details'].get('message', '')
                if message_preview and len(message_preview) > 50:
                    message_preview = message_preview[:50] + "..."
                details = f" - {message_preview}"
            elif event['event_type'] == 'tag':
                details = f" - {event['details'].get('tag_name', '')}"
            elif event['event_type'] == 'move':
                details = f" - To: {event['details'].get('destination', '')}"
            elif event['event_type'] == 'assign':
                details = f" - To: {event['details'].get('assigned_to', '')}"
            
            summary += f"- {event['human_readable_time']} - {action}{details}\n"
    
    # Add assessment and recommendations
    summary += """
ASSESSMENT:
"""
    
    # Automated assessment based on metrics
    if sla['sla_breached']:
        summary += "- SLA BREACH: Response time exceeded allowed threshold\n"
    
    if metrics['transfers'] > 2:
        summary += f"- HIGH TRANSFER COUNT: Ticket was transferred {metrics['transfers']} times\n"
    
    good_response_time = metrics.get('average_response_time', float('inf')) < 900  # 15 minutes
    if good_response_time:
        summary += "- GOOD RESPONSE TIME: Agent responses were prompt\n"
    else:
        summary += "- SLOW RESPONSE TIME: Agent responses were delayed\n"
    
    # Add overall assessment
    if not sla['sla_breached'] and metrics['transfers'] <= 2 and good_response_time:
        summary += "\nOVERALL: Ticket handled well within expected parameters\n"
    else:
        summary += "\nOVERALL: Ticket handling could be improved\n"
    
    # Add recommendations
    summary += """
RECOMMENDATIONS:
"""
    
    if sla['sla_breached']:
        summary += "- Review staffing during this time period to ensure adequate coverage\n"
    
    if metrics['transfers'] > 2:
        summary += "- Improve initial routing to reduce unnecessary transfers\n"
    
    if not good_response_time:
        summary += "- Provide additional training on efficient response handling\n"
    
    return summary

# # Main function to run the full audit
# def run_front_ticket_audit(events_data):
#     """Run a complete ticket audit and save all outputs"""
    
#     print("Running Front.com ticket audit...")
    
#     # Run the main audit
#     audit_result = create_detailed_ticket_audit(events_data)
    
#     # Save the full audit data
#     with open("ticket_audit_full.json", 'w', encoding='utf-8') as f:
#         json.dump(audit_result, f, indent=2, ensure_ascii=False)
    
#     # Generate and save a summary report
#     summary = generate_audit_summary(audit_result)
#     with open("ticket_audit_summary.txt", 'w', encoding='utf-8') as f:
#         f.write(summary)
    
#     # Run additional analyses
#     tag_analysis = analyze_tag_patterns(audit_result)
#     with open("ticket_tag_analysis.json", 'w', encoding='utf-8') as f:
#         json.dump(tag_analysis, f, indent=2, ensure_ascii=False)
    
#     # Extract conversation only
#     with open("ticket_conversation.json", 'w', encoding='utf-8') as f:
#         json.dump(audit_result['conversation_flow'], f, indent=2, ensure_ascii=False)
    
#     # Print summary statistics
#     print(f"Audit completed for ticket {audit_result['ticket_info']['conversation_id']}")
#     print(f"Total events analyzed: {len(audit_result['timeline'])}")
#     print(f"Total messages: {audit_result['performance_metrics']['total_messages']}")
#     print(f"SLA breached: {'Yes' if audit_result['sla_compliance']['sla_breached'] else 'No'}")
#     print(f"First response time: {audit_result['performance_metrics'].get('first_response_time_formatted', 'N/A')}")
#     print(f"Resolution time: {audit_result['performance_metrics'].get('resolution_time_formatted', 'N/A')}")
#     print("\nFull audit saved to ticket_audit_full.json")
#     print("Summary report saved to ticket_audit_summary.txt")
    
#     return {
#         'audit_result': audit_result,
#         'summary': summary,
#         'tag_analysis': tag_analysis
#     }

# Example usage
# if __name__ == "__main__":
#     # Assuming you have data in a variable called 'raw' with events in raw['events']
#     results = run_front_ticket_audit(raw['events'])
    
#     # Or test with provided data directly
#     # test_audit_script_with_data(events_data)
    
#     # Or load from a file
#     # with open('front_events.json', 'r') as f:
#     #     events_data = json.load(f)
#     #     run_front_ticket_audit(events_data)
    
#     print("Ready to run - uncomment the appropriate line to execute with your data")