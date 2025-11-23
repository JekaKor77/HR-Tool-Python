from flask import Blueprint, jsonify, send_file
from managers.export_manager import ExportManager


bp = Blueprint("export", __name__, url_prefix="/export")
manager = ExportManager()


@bp.route("/json/<session_id>", methods=["GET"])
def export_json(session_id):
    file_path, error = manager.export_json(session_id)
    if error:
        return jsonify({"error": error}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"candidate_evaluation_{session_id}.json",
        mimetype="application/json"
    )


@bp.route("/pdf/<session_id>", methods=["GET"])
def export_pdf(session_id):
    file_path, error = manager.export_pdf(session_id)
    if error:
        return jsonify({"error": error}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"candidate_evaluation_{session_id}.html",
        mimetype="text/html"
    )