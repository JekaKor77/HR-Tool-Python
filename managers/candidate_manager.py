import json

from utils.cleanup import cleanup_old_evaluations
from utils.file_processor import FileProcessor
from utils.storage import EvaluationStore
from services.cv_analyzer import CVAnalyzer
from services.quiz_generator import QuizGenerator
from services.response_evaluator import ResponseEvaluator
from datetime import datetime
from celery_app.tasks import finalize_candidate_evaluation


class CandidateManager:
    def __init__(self):
        self.file_processor = FileProcessor()
        self.store = EvaluationStore()
        self.cv_analyzer = CVAnalyzer()
        self.quiz_generator = QuizGenerator()
        self.response_evaluator = ResponseEvaluator()

    def process_candidate(self, file, session_id):
        cleanup_old_evaluations(self.store)
        file_path = self.file_processor.save_file(file, session_id)
        cv_text = self.file_processor.extract_text(file_path)

        # Analyze and generate quiz
        analysis = self.cv_analyzer.analyze_cv(cv_text)
        quiz = self.quiz_generator.generate_quiz(cv_text)

        data = {
            'cv_text': cv_text,
            'analysis': analysis,
            'quiz': quiz,
            'file_path': file_path,
            'created_at': datetime.now().isoformat(),
            'first_name': analysis.get('first_name'),
            'last_name': analysis.get('last_name'),
            'email': analysis.get('email'),
            'phone': analysis.get('phone')

        }

        self.store.set(session_id, data)
        return data

    def get_quiz(self, session_id: str):
        data = self.store.get(session_id)
        if not data:
            raise KeyError("Session not found")
        return data.get('quiz', {})

    def evaluate_responses(self, session_id: str, responses: dict):
        data = self.store.get(session_id)
        if not data:
            raise KeyError("Session not found")

        cv_text = data.get('cv_text', '')
        quiz = data.get('quiz', {})

        evaluation = self.response_evaluator.evaluate_responses(cv_text, quiz, responses)
        print("RAW AI RESULT:", evaluation)

        data.update({
            'evaluation': evaluation,
            'responses': responses,
            'evaluated_at': datetime.now().isoformat()
        })
        self.store.set(session_id, data)
        finalize_candidate_evaluation.apply_async(args=[session_id], countdown=0)
        return evaluation

    def get_results(self, session_id: str):
        return self.store.get(session_id)

    def exists(self, session_id: str) -> bool:
        return self.store.get(session_id) is not None

    def delete(self, session_id: str):
        self.store.delete(session_id)
