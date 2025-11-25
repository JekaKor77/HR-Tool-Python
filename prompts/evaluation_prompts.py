

def build_response_evaluation_prompt(cv_text: str, quiz: dict, responses: dict) -> str:
    technical_responses = responses.get('technical', {})
    soft_skills_responses = responses.get('soft_skills', {})

    prompt = f"""
    As an expert HR analyst, evaluate this Salesforce Developer candidate based on their CV and quiz responses.

    CV Context:
    {cv_text}

    Technical Questions and Responses:
    """

    for i, question in enumerate(quiz.get('technical_questions', []), 1):
        response = technical_responses.get(f'q{i}', 'No response provided')
        prompt += f"\n{i}. {question}\nResponse: {response}\n"

    prompt += "\nSoft Skills Questions and Responses:\n"
    for i, question in enumerate(quiz.get('soft_skills_questions', []), 1):
        response = soft_skills_responses.get(f'sq{i}', 'No response provided')
        prompt += f"\n{i}. {question}\nResponse: {response}\n"

    prompt += static_evaluation_guidelines()

    return prompt


def static_evaluation_guidelines() -> str:
    return """
        
        Please provide a comprehensive evaluation including:
        
        1. TECHNICAL ASSESSMENT:
           - Overall technical level (Junior/Mid/Senior)
           - Always infer a level (Junior/Mid/Senior) even if limited info is available. If uncertain, choose Junior.
           - Strengths in Salesforce development
           - Areas of concern or gaps
           - Specific technical skills demonstrated
        
        2. SOFT SKILLS ASSESSMENT:
           - Communication quality
           - Problem-solving approach
           - Motivation and enthusiasm
           - Teamwork indicators
        
        3. RECOMMENDATIONS:
           - Proceed to technical interview: Yes/No
           - If Yes: Focus areas for technical interview
           - If No: Reasons and suggested next steps
           - Overall hiring recommendation (Strong Hire/Hire/No Hire)
           - Salary level recommendation based on assessment
        
        4. INTERVIEW FOCUS AREAS:
           - Specific technical topics to explore deeper
           - Behavioral questions to ask
           - Red flags to investigate
           
           
        **Important Decision Rules:**
        - Base your judgment primarily on the candidate's responses to technical and soft skills questions.
        - CV is only secondary context; do NOT recommend Hire if responses do not demonstrate Salesforce knowledge or problem-solving ability.
        - If technical answers are missing, incorrect, or irrelevant → recommendation must be "No Hire".
        - If answers show only basic knowledge → recommendation should be cautious (e.g., Junior level, likely No Hire).
        - Only recommend "Hire" if responses clearly demonstrate required Salesforce skills and reasoning.
        
        **Return ONLY valid JSON in this exact format:**
        {
          "recommendation": "Hire",
          "technical_level": "Mid",
          "technical_assessment": {
            "Overall technical level": "...",
            "Strengths": "...",
            "Areas of concern": "...",
            "Specific technical skills": "..."
          },
          "soft_skills_assessment": {
            "Communication quality": "...",
            "Problem-solving approach": "...",
            "Motivation and enthusiasm": "...",
            "Teamwork indicators": "..."
          },
          "interview_focus_areas": {
            "Technical topics": "...",
            "Behavioral questions": "...",
            "Red flags": "..."
          }
        }
        
        Do not include any extra keys, nesting, or text outside JSON.
        If information is missing, make reasonable assumptions and fill with best guess.
        """


def response_evaluation_system_prompt() -> str:
    return """
        You are an expert HR analyst and technical recruiter specializing in Salesforce Developer positions.
    """