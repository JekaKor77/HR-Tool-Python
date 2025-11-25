from jinja2 import Template


def render_html_report(session_id, candidate_data):
    recommendation = str(
        candidate_data.get("evaluation", {}).get("recommendation", "")
    ).lower()

    recommendation_class = (
        "hire" if "hire" in recommendation
        else "review" if "review" in recommendation
        else "no-hire"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Candidate Evaluation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; }}
            .question {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; }}
            .response {{ margin: 5px 0; padding: 5px; background-color: #e9ecef; }}
            .recommendation {{ padding: 15px; border-radius: 5px; font-weight: bold; }}
            .hire {{ background-color: #d4edda; color: #155724; }}
            .review {{ background-color: #fff3cd; color: #856404; }}
            .no-hire {{ background-color: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Candidate Evaluation Report</h1>
            <p><strong>Candidate ID:</strong> {session_id}</p>
            <p><strong>Evaluation Date:</strong> {candidate_data.get('evaluated_at', 'N/A')}</p>
        </div>

        <div class="section">
            <h2>Overall Recommendation</h2>
            <div class="recommendation {recommendation_class}">
                {candidate_data.get('evaluation', {}).get('recommendation', 'No recommendation available')}
            </div>
        </div>

        <div class="section">
            <h2>Technical Level</h2>
            <p><strong>{candidate_data.get('evaluation', {}).get('technical_level', 'Unknown')}</strong></p>
        </div>

        <div class="section">
            <h2>CV Analysis</h2>
            <pre>{candidate_data.get('analysis', 'No analysis available')}</pre>
        </div>

        <div class="section">
            <h2>Technical Questions & Responses</h2>
    """

    quiz = candidate_data.get("quiz", {})
    responses = candidate_data.get("responses", {})

    for i, question in enumerate(quiz.get("technical_questions", []), 1):
        response = responses.get("technical", {}).get(f"q{i}", "No response provided")
        html += f"""
            <div class="question">
                <strong>Q{i}:</strong> {question}
                <div class="response"><strong>Response:</strong> {response}</div>
            </div>
        """

    html += """
        </div>
        <div class="section">
            <h2>Soft Skills Questions & Responses</h2>
    """

    for i, question in enumerate(quiz.get("soft_skills_questions", []), 1):
        response = responses.get("soft_skills", {}).get(f"sq{i}", "No response provided")
        html += f"""
            <div class="question">
                <strong>Q{i}:</strong> {question}
                <div class="response"><strong>Response:</strong> {response}</div>
            </div>
        """

    html += f"""
        </div>

        <div class="section">
            <h2>Detailed Evaluation</h2>
            <pre>{candidate_data.get('evaluation', {}).get('raw_evaluation', 'No detailed evaluation available')}</pre>
        </div>
    </body>
    </html>
    """

    return html

