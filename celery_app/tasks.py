import json

from utils.storage import EvaluationStore
from .worker import celery
from db.models import Candidate
from db.session import sync_session_factory


def get_store():
    return EvaluationStore()


@celery.task(bind=True, max_retries=3, default_retry_delay=10, acks_late=True)
def finalize_candidate_evaluation(self, session_id: str):
    session = None
    redis_store = get_store()
    try:
        session = sync_session_factory()
        data = redis_store.get(session_id)

        if not data:
            raise ValueError(f"No data found for session {session_id}")

        print("FINAL DATA FOR ORM:", json.dumps(data, indent=2))

        cand = session.query(Candidate).filter_by(id=session_id).one_or_none()

        if cand:
            cand.first_name = data.get("first_name") or cand.first_name
            cand.last_name = data.get("last_name") or cand.last_name
            cand.email = data.get("email") or cand.email
            cand.phone = data.get("phone") or cand.phone
            cand.cv_path = data.get("file_path") or cand.cv_path
            cand.quiz = data.get("quiz") or cand.quiz
            cand.responses = data.get("responses") or cand.responses
            cand.model_raw = data.get("evaluation", {}).get("raw_evaluation") or cand.model_raw
            cand.model_recommendation = data.get("evaluation", {}).get("recommendation") or cand.model_recommendation
            cand.evaluation_summary = json.dumps(data.get("evaluation")) or cand.evaluation_summary
            cand.status = "completed"
        else:
            cand = Candidate(
                id=session_id,
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                email=data.get("email"),
                phone=data.get("phone"),
                cv_path=data.get("file_path"),
                quiz=data.get("quiz"),
                responses=data.get("responses"),
                model_raw=data.get("evaluation", {}).get("raw_evaluation"),
                model_recommendation=data.get("evaluation", {}).get("recommendation"),
                evaluation_summary=json.dumps(data.get("evaluation")),
                status="completed"
            )
            session.add(cand)

        session.commit()
        return {"status": "ok"}

    except Exception as exc:
        if session:
            session.rollback()
        raise self.retry(exc=exc)
    finally:
        if session:
            session.close()
