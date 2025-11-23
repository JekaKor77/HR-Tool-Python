from datetime import datetime

from utils.cleanup import cleanup_old_evaluations
from utils.storage import EvaluationStore
from services.cv_comparator import CVComparator
from utils.file_processor import FileProcessor


class ComparisonManager:
    def __init__(self):
        self.file_processor = FileProcessor()
        self.store = EvaluationStore()
        self.comparator = CVComparator()

    def process_comparison(self, session_id, cv1_file, cv2_file, cv1_name, cv2_name):
        cleanup_old_evaluations(self.store)
        cv1_path = self.file_processor.save_file(cv1_file, f"{session_id}_cv1")
        cv2_path = self.file_processor.save_file(cv2_file, f"{session_id}_cv2")

        cv1_text = self.file_processor.extract_text(cv1_path)
        cv2_text = self.file_processor.extract_text(cv2_path)

        comparison_result = self.comparator.compare_cvs(cv1_text, cv2_text, cv1_name, cv2_name)
        questions = self.comparator.generate_comparison_questions(comparison_result)
        summary = self.comparator.format_comparison_summary(comparison_result, questions)

        data = {
            "cv1_text": cv1_text,
            "cv2_text": cv2_text,
            "cv1_name": cv1_name,
            "cv2_name": cv2_name,
            "cv1_path": cv1_path,
            "cv2_path": cv2_path,
            "comparison_result": comparison_result,
            "questions": questions,
            "summary": summary,
            "created_at": datetime.now().isoformat(),
            "type": "comparison"
        }

        self.store.set(session_id, data)
        return data

    def get_results(self, session_id):
        return self.store.get(session_id)

    def exists(self, session_id):
        return self.store.get(session_id) is not None

    def delete(self, session_id):
        self.store.delete(session_id)
