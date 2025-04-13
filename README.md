# GX QA Ticket Evaluator 📊

A comprehensive quality assurance tool for evaluating guest service ticket interactions, built with Streamlit and OpenAI's GPT-4.5.

## Overview

The GX QA Ticket Evaluator is a sophisticated tool designed to analyze and evaluate guest service interactions using GPT-4.5-preview-2025-02-27, providing detailed insights across three key performance areas:

1. Agent Performance
2. Bot Performance (Emma)
3. Overall Guest Experience

## Features

### Recent Updates

- **New 5-Tier Evaluation System**
  - Exceptional
  - Good
  - Satisfactory
  - Needs Improvement
  - Poor

- **Separated Performance Categories**
  - Clear distinction between agent, bot, and guest experience metrics
  - Independent scoring for each category
  - Detailed evaluation criteria for each aspect

### Core Features

- **Comprehensive Ticket Analysis**
  - Real-time evaluation of customer service interactions
  - Detailed timeline analysis
  - SLA compliance monitoring
  - Tag and intent analysis

- **Multi-Dimensional Scoring**
  - Agent Performance (40% weight)
    - Response Time
    - Communication Quality
    - Process Adherence
  - Bot Performance (20% weight)
    - Intent recognition accuracy
    - Response appropriateness
    - Handoff timing
    - Issue classification
  - Guest Experience (40% weight)
    - Issue Resolution
    - Overall Experience

- **Detailed Reports**
  - Executive summaries
  - Key event timelines
  - Identified issues
  - Actionable recommendations
  - Performance metrics visualization

### Security Features
- Authenticated access
- Role-based permissions
- Secure API integrations

## Technical Details

### Prerequisites
- Python 3.x
- Streamlit
- OpenAI API access
- Front API access

### Environment Variables
```
FRONT_API_TOKEN=your_front_api_token
OPENAI_API_KEY=your_openai_api_key
BASE_URL=your_base_url
```

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run: `streamlit run evaluator.py`

## Evaluation Criteria

### Agent Performance

#### Response Time
- **Exceptional**: First response < 15 minutes
- **Good**: First response < 30 minutes
- **Satisfactory**: First response < 1 hour
- **Needs Improvement**: First response < 4 hours
- **Poor**: First response > 4 hours

#### Communication Quality
- **Exceptional**: Perfect clarity, highly personalized
- **Good**: Clear and consistently professional
- **Satisfactory**: Clear but could use more personalization
- **Needs Improvement**: Some clarity issues
- **Poor**: Unclear or inappropriate

#### Process Adherence
- **Exceptional**: Perfect protocol following
- **Good**: Most processes followed well
- **Satisfactory**: Key processes followed
- **Needs Improvement**: Multiple steps missed
- **Poor**: Major procedural failures

### Bot Performance
Evaluated qualitatively based on:
- Intent recognition accuracy
- Response appropriateness
- Handoff timing
- Issue classification
- Guest interaction handling

### Guest Experience

#### Issue Resolution
- **Exceptional**: Complete resolution with added value
- **Good**: Clear resolution
- **Satisfactory**: Main issues addressed
- **Needs Improvement**: Partial resolution
- **Poor**: Unresolved or incorrect handling

#### Overall Experience
- **Exceptional**: Guest delighted
- **Good**: Guest satisfied
- **Satisfactory**: Needs met
- **Needs Improvement**: Guest frustrated
- **Poor**: Guest dissatisfied

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

Proprietary - All rights reserved

## Support

For support, contact the GX team through the internal channels.