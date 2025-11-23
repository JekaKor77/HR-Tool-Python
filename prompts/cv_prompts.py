

def cv_analysis_prompt(cv_text: str) -> str:
    return f"""
        Analyze the following CV and extract key information for a Salesforce Developer position:
        
        CV Text:
        {cv_text}
        
        Please provide a structured analysis including:
        1. Years of experience with Salesforce
        2. Technical skills (Apex, Lightning, Flows, etc.)
        3. Certifications
        4. Previous roles and responsibilities
        5. Education background
        6. Notable projects or achievements
        7. Overall technical level assessment (Junior/Mid/Senior)
        8. Key strengths
        9. Potential concerns or gaps
        
        Format as a JSON object with clear categories.
        
        
        Return ONLY a valid JSON object with these fields:
        {{
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "years_experience": "",
            "technical_skills": [],
            "certifications": [],
            "roles": [],
            "education": "",
            "projects": [],
            "technical_level": "",
            "strengths": [],
            "gaps": []
        }}
        
        
        Don't change the order of fields in the JSON response, let it be the same as in the example.
        Do not include any text outside the JSON. Ensure all fields exist, even if null.
        Do not include any text outside the JSON. Do not use markdown formatting or triple backticks.
        """


def cv_analysis_system_prompt() -> str:
    return """ 
        You are an expert HR analyst specializing in technical recruitment for Salesforce positions.
     """
