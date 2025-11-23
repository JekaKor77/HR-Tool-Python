import uuid
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from managers.comparison_manager import ComparisonManager


bp = Blueprint('comparison', __name__, url_prefix="/compare")
manager = ComparisonManager()


@bp.route("/", methods=["GET"])
def compare_page():
    return render_template("compare.html")


@bp.route("/upload_compare", methods=["POST"])
def upload_compare_cvs():
    try:
        if "cv1_file" not in request.files or "cv2_file" not in request.files:
            return jsonify({"error": "Both CV files are required"}), 400

        cv1_file = request.files["cv1_file"]
        cv2_file = request.files["cv2_file"]

        if cv1_file.filename == "" or cv2_file.filename == "":
            return jsonify({"error": "Both files must be selected"}), 400

        cv1_name = request.form.get("cv1_name", "CV 1")
        cv2_name = request.form.get("cv2_name", "CV 2")

        session_id = str(uuid.uuid4())
        session["comparison_id"] = session_id

        result = manager.process_comparison(
            session_id=session_id,
            cv1_file=cv1_file,
            cv2_file=cv2_file,
            cv1_name=cv1_name,
            cv2_name=cv2_name
        )

        return jsonify({
            "success": True,
            "session_id": session_id,
            "comparison_result": result["comparison_result"],
            "questions": result["questions"],
            "summary": result["summary"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/results", methods=["GET"])
def comparison_results():
    if "comparison_id" not in session:
        return redirect(url_for("comparison.compare_page"))

    session_id = session["comparison_id"]
    if not manager.exists(session_id):
        return redirect(url_for("comparison.compare_page"))

    data = manager.get_results(session_id)

    return render_template(
        "comparison_results.html",
        comparison_data=data,
        session_id=session_id
    )