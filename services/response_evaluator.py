import json
from prompts.evaluation_prompts import build_response_evaluation_prompt, response_evaluation_system_prompt
from services.base_service import BaseOpenAIService


class ResponseEvaluator(BaseOpenAIService):
    
    def evaluate_responses(self, cv_text, quiz, responses):
        """
        Evaluate candidate responses and provide recommendations
        """
        user_prompt = build_response_evaluation_prompt(cv_text, quiz, responses)
        result = self.chat(system_prompt=response_evaluation_system_prompt(),
                           user_prompt=user_prompt,
                           model="gpt-4",
                           max_tokens=1500,
                           temperature=0.3)

        if result.startswith("Error:"):
            return {
                "error": result,
                "technical_level": "Unknown",
                "recommendation": "Review manually",
                "proceed_to_interview": "Unknown"
            }

        try:
            parsed = json.loads(result)
            evaluation_block = parsed.get("Evaluation", {})

            normalized = {
                "recommendation": parsed.get("recommendation") or None,
                "technical_level": parsed.get("technical_level") or None,
                "technical_assessment": parsed.get("technical_assessment", {}),
                "soft_skills_assessment": parsed.get("soft_skills_assessment", {}),
                "interview_focus_areas": parsed.get("interview_focus_areas", {}),
                "raw_evaluation": result
            }

            return normalized

        except json.JSONDecodeError:
            return {
                "raw_evaluation": result,
                "technical_level": "Unknown",
                "recommendation": "Review manually",
                "proceed_to_interview": "Unknown"
            }

