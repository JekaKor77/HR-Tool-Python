import openai
from config import Config

class CVAnalyzer:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def analyze_cv(self, cv_text):
        """
        Analyze CV and extract key information about the candidate
        """
        prompt = f"""
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
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst specializing in technical recruitment for Salesforce positions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error analyzing CV: {str(e)}"
