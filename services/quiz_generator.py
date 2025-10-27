import openai
from config import Config

class QuizGenerator:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_quiz(self, cv_text):
        """
        Generate technical quiz and soft skills questions based on CV
        """
        prompt = f"""
        You are an AI HR Assistant specialized in hiring Salesforce Developers.
        Your task is to generate a quick, focused technical quiz to help HR identify the candidate's technical level before a technical interview.
        
        IMPORTANT: Analyze the candidate's experience level from their CV and adjust question difficulty accordingly:
        - JUNIOR (0-2 years): Focus on basic concepts, simple scenarios, fundamental knowledge
        - MID-LEVEL (2-5 years): Include intermediate concepts, real-world scenarios, best practices
        - SENIOR (5+ years): Cover advanced topics, architectural decisions, complex problem-solving
        
        Requirements for the quiz:
        - Include up to 5 questions, maximum.
        - Questions should cover key Salesforce Developer skills relevant for screening:
          - Apex (triggers, classes, bulk-safe coding).
          - Flows vs. Apex use cases.
          - Governor limits.
          - Basic SOQL/DML best practices.
          - Understanding asynchronous processing (e.g., Queueable, Future).
        - Questions should be answerable briefly (1-3 sentences each) by the candidate in written form.
        - Questions should be clear, simple to understand for non-technical HR, but reveal the candidate's depth.
        - ADJUST DIFFICULTY based on the candidate's experience level mentioned in the CV.
        - Do not generate answer keys or commentary, only the quiz.

        After the technical quiz, generate 1–3 additional questions to assess the candidate's soft skills and motivation for the Salesforce Developer role. Focus on:
        - Communication and teamwork.
        - Analytical thinking.
        - Motivation and alignment with project needs.

        These questions should also be clear, direct, and easy to answer in 1–3 sentences.

        Here is the candidate's CV for context:
        {cv_text}
        
        Generate ONLY the quiz as a numbered list without additional commentary.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR assistant specialized in Salesforce Developer recruitment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            quiz_text = response.choices[0].message.content
            
            # Parse the quiz into structured format
            return self._parse_quiz(quiz_text)
            
        except Exception as e:
            return {
                "technical_questions": [f"Error generating quiz: {str(e)}"],
                "soft_skills_questions": []
            }
    
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
