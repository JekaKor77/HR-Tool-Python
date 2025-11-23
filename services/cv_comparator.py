import json
from datetime import datetime
from prompts.comparison_prompts import comparison_prompt, comparison_questions_prompt, compare_cvs_system_prompt, generate_comparison_questions_system_prompt
from services.base_service import BaseOpenAIService


class CVComparator(BaseOpenAIService):
    
    def compare_cvs(self, cv1_text, cv2_text, cv1_name="CV 1", cv2_name="CV 2"):
        """
        Compare two CVs and identify differences, gaps, and inconsistencies
        """
        user_prompt = comparison_prompt(cv1_text, cv2_text, cv1_name, cv2_name)

        result = self.chat(system_prompt=compare_cvs_system_prompt(),
                           user_prompt=user_prompt,
                           model="gpt-4",
                           max_tokens=2000
                           )

        if result.startswith("Error:"):
            return {"error": result,
                    "format": "error"}

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw_analysis": result,
                    "format": "text"}

    def generate_comparison_questions(self, comparison_result):
        """
        Generate specific questions based on the comparison results
        """
        if isinstance(comparison_result, dict) and comparison_result.get("format") == "error":
            return []
        
        comparison_text = (
            comparison_result.get("raw_analysis")
            if isinstance(comparison_result, dict)
            else str(comparison_result)
        )
        
        user_prompt = comparison_questions_prompt(comparison_text)
        result = self.chat(system_prompt=generate_comparison_questions_system_prompt(),
                           user_prompt=user_prompt,
                           model="gpt-4",
                           max_tokens=1000,
                           temperature=0.3
                           )

        if result.startswith("Error:"):
            return [{"question": result,
                     "category": "error",
                     "priority": "low",
                     "context": "System error occurred"}]

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [
                {"question": q.strip(), "category": "general", "priority": "medium"}
                for q in result.split("\n") if q.strip() and "?" in q
            ]
    
    def format_comparison_summary(self, comparison_result, questions):
        """
        Create a formatted summary of the comparison results
        """
        summary = {
            "comparison_date": datetime.now().isoformat(),
            "total_differences": 0,
            "high_priority_issues": 0,
            "categories_analyzed": [],
            "summary_text": "",
            "questions_generated": len(questions) if questions else 0
        }
        
        if isinstance(comparison_result, dict):
            if comparison_result.get("format") == "error":
                summary["summary_text"] = f"Error occurred during comparison: {comparison_result.get('error', 'Unknown error')}"
                return summary
            
            # Count high priority questions
            if questions:
                summary["high_priority_issues"] = len([q for q in questions if q.get("priority") == "high"])
                summary["total_differences"] = len(questions)
            
            # Extract categories from questions
            if questions:
                categories = set([q.get("category", "general") for q in questions])
                summary["categories_analyzed"] = list(categories)
            
            # Create summary text
            if questions:
                summary["summary_text"] = f"Found {len(questions)} areas requiring clarification, including {summary['high_priority_issues']} high-priority issues across {len(summary['categories_analyzed'])} categories."
            else:
                summary["summary_text"] = "No significant differences found between the CVs."
        
        return summary
