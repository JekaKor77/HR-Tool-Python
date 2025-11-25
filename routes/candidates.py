from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
import uuid
from managers.candidate_manager import CandidateManager
from middlewares.auth import login_required

bp = Blueprint("candidates", __name__)
manager = CandidateManager()


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/upload", methods=["POST"])
def upload_cv():
    try:

        if 'cv_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['cv_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        session_id = str(uuid.uuid4())
        session['candidate_id'] = session_id

        result = manager.process_candidate(file, session_id)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'analysis': result.get('analysis'),
            'quiz': result.get('quiz')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route("/quiz", methods=["GET"])
def quiz_page():
    if 'candidate_id' not in session:
        return redirect(url_for('candidates.index'))

    session_id = session['candidate_id']
    if not manager.exists(session_id):
        return redirect(url_for('candidates.index'))

    quiz = manager.get_quiz(session_id)
    return render_template('quiz.html', quiz=quiz)


@bp.route("/evaluate", methods=["POST"])
def evaluate_responses():
    try:
        if 'candidate_id' not in session:
            return jsonify({'error': 'No active session'}), 400

        session_id = session['candidate_id']
        if not manager.exists(session_id):
            return jsonify({'error': 'Session expired'}), 400

        payload = request.get_json(force=True, silent=True) or {}
        responses = payload.get('responses', {})

        evaluation = manager.evaluate_responses(session_id, responses)

        return jsonify({
            'success': True,
            'evaluation': evaluation
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route("/results", methods=["GET"])
def results_page():
    if 'candidate_id' not in session:
        return redirect(url_for('candidates.index'))

    session_id = session['candidate_id']
    data = manager.get_results(session_id)

    if not data or 'evaluation' not in data:
        return redirect(url_for('candidates.index'))

    return render_template('results.html',
                           evaluation=data.get('evaluation'),
                           analysis=data.get('analysis', {}),
                           quiz=data.get('quiz', {}),
                           responses=data.get('responses', {}),
                           session_id=session_id)


@bp.route("/new_candidate", methods=["GET"])
def new_candidate():
    current_session_id = session.get('candidate_id')
    comparison_session_id = session.get('comparison_id')

    session.clear()

    if current_session_id:
        manager.delete(current_session_id)
    if comparison_session_id:
        manager.delete(comparison_session_id)

    return redirect(url_for('candidates.index'))


