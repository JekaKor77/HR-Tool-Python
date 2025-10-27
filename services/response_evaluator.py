import openai
from config import Config

class ResponseEvaluator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def evaluate_responses(self, cv_text, quiz, responses):
        """
        Evaluate candidate responses and provide recommendations
        """
        # Prepare the evaluation prompt
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
        
        prompt += """
        
        Please provide a comprehensive evaluation including:
        
        1. TECHNICAL ASSESSMENT:
           - Overall technical level (Junior/Mid/Senior)
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
        
        Format as a structured JSON response.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst and technical recruiter specializing in Salesforce Developer positions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            evaluation_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text if parsing fails
            try:
                import json
                return json.loads(evaluation_text)
            except:
                return {
                    "raw_evaluation": evaluation_text,
                    "technical_level": "Unknown",
                    "recommendation": "Review manually",
                    "proceed_to_interview": "Unknown"
                }
                
        except Exception as e:
            return {
                "error": f"Error evaluating responses: {str(e)}",
                "technical_level": "Unknown",
                "recommendation": "Review manually",
                "proceed_to_interview": "Unknown"
            }
