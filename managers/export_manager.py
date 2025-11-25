import json
import tempfile
from datetime import datetime
from utils.storage import EvaluationStore
from renderers.html_report import render_html_report


class ExportManager:
    def __init__(self):
        self.store = EvaluationStore()

    def export_json(self, session_id):
        data = self.store.get(session_id)
        if not data:
            return None, "Session not found"

        export_data = {
            "candidate_id": session_id,
            "created_at": data.get("created_at"),
            "evaluated_at": data.get("evaluated_at"),
            "cv_analysis": data.get("analysis", {}),
            "quiz_questions": data.get("quiz", {}),
            "candidate_responses": data.get("responses", {}),
            "evaluation_results": data.get("evaluation", {}),
            "exported_at": datetime.now().isoformat()
        }

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(export_data, temp_file, indent=2)
        temp_file.close()

        return temp_file.name, None

    def export_pdf(self, session_id):
        data = self.store.get(session_id)
        if not data:
            return None, "Session not found"

        html_content = render_html_report(session_id, data)

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False)
        temp_file.write(html_content)
        temp_file.close()

        return temp_file.name, None
