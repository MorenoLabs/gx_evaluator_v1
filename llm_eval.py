from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv

API_TOKEN = os.getenv("FRONT_APP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")



client = OpenAI(api_key=OPENAI_API_KEY)

def evaluate_ticket(summary):
    with open("ticket_audit_full.json", "r") as file:
        ticket_event_log = json.load(file)
        
    with open("ticket_summary.md", "r") as file:
         support_ticket_log = file.read()
         
    with open("rules.md", "r") as file:
            rules = file.read()
    with open("prompt.md", "r") as file:
        prompt = file.read()

    response = client.responses.create(
        model="gpt-4.5-preview-2025-02-27",
        temperature=0.7,
        input=[
            {"role": "system", "content": "You are an expert guest service desk ticket evaluator. Analyze the provided ticket event log and generate a comprehensive evaluation according to the specified schema."},
            {"role": "user", "content": f"""
            
            Scoring rules and critera:
            {rules}
            
            {prompt}
            
            Do not use guest names or agent names in your response. Our automated system is called Emma. Do not use the term customer.
            Here is the guest service ticket summary to evaluate. Pay attention to internal comments as well for your output. Make sure you verify if the bot assigned guest intent was exact and correct: {summary}"""}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ticket_evaluation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the evaluation report as a single line summary of the guest intent. This should be a concise and informative title that captures the essence of the guest intent(s) in particular if our bot Emma has properly understood the specifics and nuances of the guest request / message.. Do only consider the guest intents and not the entire ticket event log. Use a emoji in the title to make it more engaging. The emoji should be relevant to the guest intent and add a touch of personality to the report."
                        },
                        "overall_score": {
                            "type": "string",
                            "enum": ["Exceptional", "Good", "Satisfactory", "Needs Improvement", "Poor"],
                            "description": "Overall evaluation using 5-tier system where Exceptional is the highest and Poor is the lowest. Be critical in your assessment."
                        },
                        "bot_evaluation": {
                            "type": "string",
                            "description": "Critical detailed evaluation of the Emmas's performance, including strengths and weaknesses. Focus on the bot's ability to understand and respond to guest inquiries, its efficiency in handling tasks, and any areas for improvement. Provide specific examples from the ticket event log to support your evaluation. Consider bot responses always be fast so this should not be a factor in the evaluation. Do not use guest names or agent names."
                        },
                        "bot_evaluation_details": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of very detailed descriptions of major issues identified in the bot's performance. Each item should be a specific example from the ticket event log that illustrates a strength or weakness in the bot's handling of the ticket."
                        },
                        "executive_summary": {
                            "type": "string",
                            "description": "A comprehensive analysis of the ticket that must include: \n1. Initial context (ticket type, core issue)\n2. Key performance metrics (response times, SLA status, handle time)\n3. Bot performance highlights with specific examples\n4. Agent performance analysis with conversation excerpts\n5. Critical decision points and their impact\n6. Resolution journey and outcome effectiveness\n7. Guest experience impact (frustration points, satisfaction elements)\n8. Most significant process gaps or exemplary handling\n9. Quantifiable impact (time lost, guest satisfaction affected)\n10. Primary improvement opportunities\nUse specific examples and quotes from the conversation to support key points. Maintain a critical and objective tone."
                        },
                        "guest_intent": {
                            "type": "string",
                            "description": "A concise summary of the guest's intent(s) if multiple, including their main concerns and expectations. Do only consider the inital guest inquiry and not the entire ticket event log. The Boost intent in the log might be wrong so evaluate."
                        },
                        "ticket_overview": {
                            "type": "object",
                            "properties": {
                                "conversation_id": {"type": "string"},
                                "created": {"type": "string"},
                                "guest": {"type": "string"},
                                "property": {"type": "string"},
                                "assigned_agent": {"type": "string"},
                                "reservation": {"type": "string"},
                                "status": {"type": "string"},
                                "core_issues": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "resolution_status": {"type": "string", "description": "The status of the ticket resolution, from a guest perspective. This should reflect the guest's satisfaction with the resolution process and whether their issues were adequately addressed."}
                            },
                            "required": ["conversation_id", "created", "guest", "property", "assigned_agent", "reservation", "status", "core_issues", "resolution_status"],
                            "additionalProperties": False
                        },
                        "key_events": {
                            "type": "array",
                            "description": "A chronological list of the most significant events in the ticket timeline, focusing on guest interactions, agent responses, status changes, and SLA breaches. Include 8-12 events that tell the complete story of the ticket.Double check the chronological order.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "time": {
                                        "type": "string",
                                        "description": "The timestamp of the event in HH:MM:SS format or relative time format (e.g., '12:30:45' or '2 minutes after ticket creation')"
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "A clear, concise description of what happened at this point in the timeline. Include who initiated the action, what specifically occurred, and its significance to the ticket flow. Do not use guest names or agent names."
                                    }
                                },
                                "required": ["time", "description"],
                                "additionalProperties": False
                            }
                        },
                        "category_scores": {
                            "type": "object",
                            "properties": {
                                "response_time": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "string", "enum": ["Exceptional", "Good", "Satisfactory", "Needs Improvement", "Poor"], "description": "Agent Performance: Score for response time from guest perspective"},
                                        "max": {"type": "string", "enum": ["Exceptional"], "description": "maximum possible score"}
                                    },
                                    "required": ["score", "max"],
                                    "additionalProperties": False
                                },
                                "communication_quality": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "string", "enum": ["Exceptional", "Good", "Satisfactory", "Needs Improvement", "Poor"], "description": "Agent Performance: Score for clarity, professionalism and effectiveness of human agent communication"},
                                        "max": {"type": "string", "enum": ["Exceptional"], "description": "maximum possible score"}
                                    },
                                    "required": ["score", "max"],
                                    "additionalProperties": False
                                },
                                "process_adherence": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "string", "enum": ["Exceptional", "Good", "Satisfactory", "Needs Improvement", "Poor"], "description": "Agent Performance: Score for following established protocols and procedures by human agents"},
                                        "max": {"type": "string", "enum": ["Exceptional"], "description": "maximum possible score"}
                                    },
                                    "required": ["score", "max"],
                                    "additionalProperties": False
                                },
                                "issue_resolution": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "string", "enum": ["Exceptional", "Good", "Satisfactory", "Needs Improvement", "Poor"], "description": "Guest Experience: Score for how effectively the issue was resolved"},
                                        "max": {"type": "string", "enum": ["Exceptional"], "description": "maximum possible score"}
                                    },
                                    "required": ["score", "max"],
                                    "additionalProperties": False
                                },
                                "guest_experience": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "string", "enum": ["Exceptional", "Good", "Satisfactory", "Needs Improvement", "Poor"], "description": "Guest Experience: Overall score for the guest's journey and satisfaction"},
                                        "max": {"type": "string", "enum": ["Exceptional"], "description": "maximum possible score"}
                                    },
                                    "required": ["score", "max"],
                                    "additionalProperties": False
                                }
                            },
                            "required": ["response_time", "communication_quality", "issue_resolution", "guest_experience", "process_adherence"],
                            "additionalProperties": False
                        },
                        "key_issues": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of very detailed descriptions of major issues identified in the ticket. Each item should be a specific example from the ticket event log that illustrates a strength or weakness in the handling of the ticket. This should include any major issues that were not addressed or resolved, as well as any areas where the bot or agent could have improved their performance. Do not only focus on bot issues as we are aware of the limitations of the bot. Do not use guest names or agent names."
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of very detailed recommendations with actionable steps"
                        },
                        "ticket_link": {
                            "type": "string",
                            "description": "Link to the ticket in the ticketing system. This should be a URL that directs to the specific ticket for further review."
                        }
                    },
                    "required": ["title", "overall_score", "bot_evaluation", "bot_evaluation_details","executive_summary", "guest_intent", "ticket_overview", "key_events", "category_scores", "key_issues", "recommendations", "ticket_link"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    evaluation = json.loads(response.output_text)
    return evaluation
    # print(json.dumps(evaluation, indent=2))