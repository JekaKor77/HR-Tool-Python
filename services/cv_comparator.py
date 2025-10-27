import openai
import json
from config import Config
from datetime import datetime

class CVComparator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def compare_cvs(self, cv1_text, cv2_text, cv1_name="CV 1", cv2_name="CV 2"):
        """
        Compare two CVs and identify differences, gaps, and inconsistencies
        """
        prompt = f"""
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
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst specializing in CV comparison and candidate evaluation. Provide objective, detailed analysis of differences between CVs."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            comparison_result = response.choices[0].message.content
            
            # Try to parse as JSON, if it fails, return as text
            try:
                return json.loads(comparison_result)
            except json.JSONDecodeError:
                return {
                    "raw_analysis": comparison_result,
                    "format": "text"
                }
            
        except Exception as e:
            return {
                "error": f"Error comparing CVs: {str(e)}",
                "format": "error"
            }
    
    def generate_comparison_questions(self, comparison_result):
        """
        Generate specific questions based on the comparison results
        """
        if isinstance(comparison_result, dict) and comparison_result.get("format") == "error":
            return []
        
        # Convert comparison result to text if it's a dict
        if isinstance(comparison_result, dict):
            comparison_text = comparison_result.get("raw_analysis", str(comparison_result))
        else:
            comparison_text = str(comparison_result)
        
        prompt = f"""
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
        
        Format as a JSON array of question objects, each with:
        - "question": The actual question text
        - "category": The type of discrepancy it addresses (e.g., "work_experience", "skills", "education", "projects")
        - "priority": "high", "medium", or "low" based on importance
        - "context": Brief explanation of what discrepancy this question addresses
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who creates targeted questions based on CV analysis. Generate professional, specific questions that help clarify discrepancies."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            questions_text = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                return json.loads(questions_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a simple structure
                questions = []
                for i, line in enumerate(questions_text.split('\n')):
                    if line.strip() and ('?' in line or line.strip().startswith('-')):
                        clean_question = line.strip().lstrip('- ').strip()
                        if clean_question:
                            questions.append({
                                "question": clean_question,
                                "category": "general",
                                "priority": "medium",
                                "context": f"Question {i+1} based on CV comparison"
                            })
                return questions
            
        except Exception as e:
            return [{
                "question": f"Error generating questions: {str(e)}",
                "category": "error",
                "priority": "low",
                "context": "System error occurred"
            }]
    
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
