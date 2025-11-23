

def comparison_prompt(cv1_text: str, cv2_text: str, cv1_name: str, cv2_name) -> str:
    return f"""
        You are an expert HR analyst specializing in CV comparison and candidate evaluation. 
        Compare the following two CVs and identify key differences, gaps, and potential inconsistencies.
        
        CV 1 ({cv1_name}):
        {cv1_text}
        
        CV 2 ({cv2_name}):
        {cv2_text}
        
        Please provide a comprehensive comparison analysis including:
        
        1. **WORK EXPERIENCE COMPARISON:**
           - Differences in job titles, companies, and roles
           - Discrepancies in employment dates and duration
           - Missing or additional positions in either CV
           - Inconsistencies in job responsibilities and achievements
        
        2. **TECHNICAL SKILLS COMPARISON:**
           - Skills mentioned in one CV but not the other
           - Different levels of expertise claimed for the same skills
           - Missing certifications or qualifications
        
        3. **EDUCATION COMPARISON:**
           - Differences in educational background
           - Discrepancies in graduation dates or institutions
           - Missing degrees or certifications
        
        4. **PROJECTS AND ACHIEVEMENTS:**
           - Projects mentioned in one CV but not the other
           - Different descriptions of the same projects
           - Inconsistencies in project timelines or outcomes
        
        5. **POTENTIAL RED FLAGS:**
           - Major discrepancies that require clarification
           - Missing information that could be concerning
           - Inconsistencies that suggest potential issues
        
        6. **COMPARISON SUMMARY:**
           - Overall assessment of which CV appears more complete/accurate
           - Key areas where clarification is needed
           - Recommendations for follow-up questions
        
        Format the response as a structured JSON object with clear categories and specific examples.
        Be objective and focus on factual differences rather than subjective assessments.
        
        
        For each section:
        - List specific differences or discrepancies.
        - Be objective and factual.
        - Do not include generic commentary.
        
        **Return ONLY valid JSON in this format:**
        {{
          "work_experience": ["Difference 1", "Difference 2", ...],
          "technical_skills": ["Difference 1", "Difference 2", ...],
          "education": ["Difference 1", "Difference 2", ...],
          "projects": ["Difference 1", "Difference 2", ...],
          "red_flags": ["Issue 1", "Issue 2", ...],
          "summary": {{
            "overall_assessment": "...",
            "key_areas": ["Area 1", "Area 2"],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
          }}
        }}
        
        Do not include any text outside JSON

        """


def comparison_questions_prompt(comparison_text: str) -> str:
    return f"""
        Based on the following CV comparison analysis, generate 5-8 specific questions that an interviewer should ask the candidate to clarify discrepancies and gather more information.
        
        Comparison Analysis:
        {comparison_text}
        
        Generate questions that:
        1. Address specific discrepancies found in the comparison
        2. Seek clarification on missing information
        3. Explore inconsistencies in dates, roles, or achievements
        4. Are professional and non-confrontational
        5. Help determine which version of information is accurate
        6. Focus on the most significant differences that could impact hiring decisions
        
        
        **Return ONLY valid JSON as an array of objects in this format:**
        [
          {{
            "question": "Can you clarify the timeline of your employment at Company X?",
            "category": "work_experience",
            "priority": "high",
            "context": "Overlap in employment dates between CV versions"
          }},
          {{
            "question": "You've listed advanced proficiency in Python on one CV but not the other. Can you explain this?",
            "category": "skills",
            "priority": "medium",
            "context": "Skill discrepancy between CVs"
          }}
        ]
        
        Do not include any text outside JSON.

        """


def compare_cvs_system_prompt() -> str:
    return """
        You are an expert HR analyst specializing in CV comparison and candidate evaluation.
        Provide objective, detailed analysis of differences between CVs.
    """


def generate_comparison_questions_system_prompt() -> str:
    return """
        You are an expert interviewer who creates targeted questions based on CV analysis.
        Generate professional, specific questions that help clarify discrepancies.
    """
