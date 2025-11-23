from prompts.quiz_prompts import quiz_prompt, quiz_system_prompt
from services.base_service import BaseOpenAIService


class QuizGenerator(BaseOpenAIService):
    
    def generate_quiz(self, cv_text):
        """
        Generate technical quiz and soft skills questions based on CV
        """
        user_prompt = quiz_prompt(cv_text)
        result = self.chat(system_prompt=quiz_system_prompt(),
                           user_prompt=user_prompt,
                           model="gpt-3.5-turbo",
                           max_tokens=800,
                           temperature=0.4)

        if result.startswith("Error"):
            return {
                "technical_questions": [f"Error generating quiz: {result}"],
                "soft_skills_questions": []
            }
            
        # Parse the quiz into structured format
        return self._parse_quiz(result)

    def _parse_quiz(self, quiz_text):
        """
        Parse the generated quiz text into structured format
        """
        try:
            lines = quiz_text.strip().split('\n')
            technical_questions = []
            soft_skills_questions = []
            current_section = "technical"
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if we're moving to soft skills section
                if any(keyword in line.lower() for keyword in ['soft skills', 'motivation', 'communication', 'teamwork']):
                    current_section = "soft_skills"
                    continue
                
                # Check if line starts with a number (question)
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Clean up the question text
                    question = line
                    try:
                        if line[0].isdigit():
                            # Remove number and period
                            if '.' in line:
                                parts = line.split('.', 1)
                                question = parts[1].strip() if len(parts) > 1 else line[1:].strip()
                            else:
                                question = line[1:].strip()
                        elif line.startswith('-'):
                            question = line[1:].strip()
                        
                        # Only add non-empty questions
                        if question and len(question) > 10:  # Ensure it's a meaningful question
                            if current_section == "technical":
                                technical_questions.append(question)
                            else:
                                soft_skills_questions.append(question)
                    except Exception as e:
                        print(f"Error parsing line: {line}, Error: {e}")
                        continue
            
            # Ensure we have at least some questions
            if not technical_questions and not soft_skills_questions:
                technical_questions = ["Error: Could not parse quiz questions from AI response"]
            
            return {
                "technical_questions": technical_questions[:3],  # Max 5 technical questions
                "soft_skills_questions": soft_skills_questions[:3]  # Max 3 soft skills questions
            }
        except Exception as e:
            return {
                "technical_questions": [f"Error parsing quiz: {str(e)}"],
                "soft_skills_questions": []
            }
