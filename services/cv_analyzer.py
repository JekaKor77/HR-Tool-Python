import json

from prompts.cv_prompts import cv_analysis_prompt, cv_analysis_system_prompt
from services.base_service import BaseOpenAIService


class CVAnalyzer(BaseOpenAIService):
    
    def analyze_cv(self, cv_text):
        """
        Analyze CV and extract key information about the candidate
        """
        user_prompt = cv_analysis_prompt(cv_text)
        result = self.chat(
            system_prompt=cv_analysis_system_prompt(),
            user_prompt=user_prompt,
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.3
        )

        if result.startswith("Error:"):
            return {"error": result}

        try:
            parsed = json.loads(result)
            return parsed
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw": result}
