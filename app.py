from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import uuid
import json
import tempfile
from datetime import datetime
from config import Config
from services.cv_analyzer import CVAnalyzer
from services.cv_comparator import CVComparator
from services.quiz_generator import QuizGenerator
from services.response_evaluator import ResponseEvaluator
from utils.file_processor import FileProcessor

app = Flask(__name__)
app.config.from_object(Config)

# Store evaluation data in memory instead of session to avoid cookie size limits
evaluation_store = {}

def cleanup_old_evaluations():
    """Remove evaluations older than 24 hours to prevent memory issues"""
    from datetime import datetime, timedelta
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    to_remove = []
    for session_id, data in evaluation_store.items():
        created_at = data.get('created_at')
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at)
                if created_dt < cutoff_time:
                    to_remove.append(session_id)
            except:
                # If we can't parse the date, remove it to be safe
                to_remove.append(session_id)
    
    for session_id in to_remove:
        del evaluation_store[session_id]

# Initialize services
cv_analyzer = CVAnalyzer()
cv_comparator = CVComparator()
quiz_generator = QuizGenerator()
response_evaluator = ResponseEvaluator()
file_processor = FileProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_cv():
    try:
        # Clean up old evaluations first
        cleanup_old_evaluations()
        
        if 'cv_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['cv_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate session ID for this candidate
        session_id = str(uuid.uuid4())
        session['candidate_id'] = session_id
        
        # Process and save file
        file_path = file_processor.save_file(file, session_id)
        
        # Extract text from CV
        cv_text = file_processor.extract_text(file_path)
        
        # Analyze CV
        analysis = cv_analyzer.analyze_cv(cv_text)
        
        # Generate quiz
        quiz = quiz_generator.generate_quiz(cv_text)
        
        # Store data in memory store instead of session
        evaluation_store[session_id] = {
            'cv_text': cv_text,
            'analysis': analysis,
            'quiz': quiz,
            'file_path': file_path,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'analysis': analysis,
            'quiz': quiz
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/quiz')
def quiz_page():
    if 'candidate_id' not in session:
        return redirect(url_for('index'))
    
    session_id = session['candidate_id']
    if session_id not in evaluation_store:
        return redirect(url_for('index'))
    
    return render_template('quiz.html', quiz=evaluation_store[session_id]['quiz'])

@app.route('/evaluate', methods=['POST'])
def evaluate_responses():
    try:
        if 'candidate_id' not in session:
            return jsonify({'error': 'No active session'}), 400
        
        session_id = session['candidate_id']
        if session_id not in evaluation_store:
            return jsonify({'error': 'Session expired'}), 400
        
        responses = request.json.get('responses', {})
        candidate_data = evaluation_store[session_id]
        
        # Evaluate responses
        evaluation = response_evaluator.evaluate_responses(
            candidate_data['cv_text'], 
            candidate_data['quiz'], 
            responses
        )
        
        # Store evaluation in memory store
        evaluation_store[session_id]['evaluation'] = evaluation
        evaluation_store[session_id]['responses'] = responses
        evaluation_store[session_id]['evaluated_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    if 'candidate_id' not in session:
        return redirect(url_for('index'))
    
    session_id = session['candidate_id']
    if session_id not in evaluation_store or 'evaluation' not in evaluation_store[session_id]:
        return redirect(url_for('index'))
    
    candidate_data = evaluation_store[session_id]
    return render_template('results.html', 
                         evaluation=candidate_data['evaluation'],
                         analysis=candidate_data.get('analysis', {}),
                         quiz=candidate_data.get('quiz', {}),
                         responses=candidate_data.get('responses', {}),
                         session_id=session_id)

@app.route('/export/<session_id>')
def export_results(session_id):
    """Export evaluation results as JSON"""
    if session_id not in evaluation_store:
        return jsonify({'error': 'Session not found'}), 404
    
    candidate_data = evaluation_store[session_id]
    
    # Create export data
    export_data = {
        'candidate_id': session_id,
        'created_at': candidate_data.get('created_at'),
        'evaluated_at': candidate_data.get('evaluated_at'),
        'cv_analysis': candidate_data.get('analysis', {}),
        'quiz_questions': candidate_data.get('quiz', {}),
        'candidate_responses': candidate_data.get('responses', {}),
        'evaluation_results': candidate_data.get('evaluation', {}),
        'exported_at': datetime.now().isoformat()
    }
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(export_data, temp_file, indent=2)
    temp_file.close()
    
    return send_file(temp_file.name, 
                    as_attachment=True, 
                    download_name=f'candidate_evaluation_{session_id}.json',
                    mimetype='application/json')

@app.route('/export_pdf/<session_id>')
def export_pdf(session_id):
    """Export evaluation results as PDF"""
    if session_id not in evaluation_store:
        return jsonify({'error': 'Session not found'}), 404
    
    candidate_data = evaluation_store[session_id]
    
    # Create HTML content for PDF
    html_content = f"""
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
            <div class="recommendation {'hire' if 'hire' in str(candidate_data.get('evaluation', {}).get('recommendation', '')).lower() else 'review' if 'review' in str(candidate_data.get('evaluation', {}).get('recommendation', '')).lower() else 'no-hire'}">
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
    
    # Add technical questions and responses
    quiz = candidate_data.get('quiz', {})
    responses = candidate_data.get('responses', {})
    
    for i, question in enumerate(quiz.get('technical_questions', []), 1):
        response = responses.get('technical', {}).get(f'q{i}', 'No response provided')
        html_content += f"""
            <div class="question">
                <strong>Q{i}:</strong> {question}
                <div class="response"><strong>Response:</strong> {response}</div>
            </div>
        """
    
    html_content += """
        </div>
        
        <div class="section">
            <h2>Soft Skills Questions & Responses</h2>
    """
    
    # Add soft skills questions and responses
    for i, question in enumerate(quiz.get('soft_skills_questions', []), 1):
        response = responses.get('soft_skills', {}).get(f'sq{i}', 'No response provided')
        html_content += f"""
            <div class="question">
                <strong>Q{i}:</strong> {question}
                <div class="response"><strong>Response:</strong> {response}</div>
            </div>
        """
    
    html_content += f"""
        </div>
        
        <div class="section">
            <h2>Detailed Evaluation</h2>
            <pre>{candidate_data.get('evaluation', {}).get('raw_evaluation', 'No detailed evaluation available')}</pre>
        </div>
    </body>
    </html>
    """
    
    # Create temporary HTML file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    temp_file.write(html_content)
    temp_file.close()
    
    return send_file(temp_file.name, 
                    as_attachment=True, 
                    download_name=f'candidate_evaluation_{session_id}.html',
                    mimetype='text/html')

@app.route('/compare')
def compare_page():
    return render_template('compare.html')

@app.route('/upload_compare', methods=['POST'])
def upload_compare_cvs():
    try:
        # Clean up old evaluations first
        cleanup_old_evaluations()
        
        if 'cv1_file' not in request.files or 'cv2_file' not in request.files:
            return jsonify({'error': 'Both CV files are required'}), 400
        
        cv1_file = request.files['cv1_file']
        cv2_file = request.files['cv2_file']
        
        if cv1_file.filename == '' or cv2_file.filename == '':
            return jsonify({'error': 'Both files must be selected'}), 400
        
        # Get CV names from form data
        cv1_name = request.form.get('cv1_name', 'CV 1')
        cv2_name = request.form.get('cv2_name', 'CV 2')
        
        # Generate session ID for this comparison
        session_id = str(uuid.uuid4())
        session['comparison_id'] = session_id
        
        # Process and save files
        cv1_path = file_processor.save_file(cv1_file, f"{session_id}_cv1")
        cv2_path = file_processor.save_file(cv2_file, f"{session_id}_cv2")
        
        # Extract text from both CVs
        cv1_text = file_processor.extract_text(cv1_path)
        cv2_text = file_processor.extract_text(cv2_path)
        
        # Compare CVs
        comparison_result = cv_comparator.compare_cvs(cv1_text, cv2_text, cv1_name, cv2_name)
        
        # Generate questions based on comparison
        questions = cv_comparator.generate_comparison_questions(comparison_result)
        
        # Create summary
        summary = cv_comparator.format_comparison_summary(comparison_result, questions)
        
        # Store data in memory store
        evaluation_store[session_id] = {
            'cv1_text': cv1_text,
            'cv2_text': cv2_text,
            'cv1_name': cv1_name,
            'cv2_name': cv2_name,
            'cv1_path': cv1_path,
            'cv2_path': cv2_path,
            'comparison_result': comparison_result,
            'questions': questions,
            'summary': summary,
            'created_at': datetime.now().isoformat(),
            'type': 'comparison'
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'comparison_result': comparison_result,
            'questions': questions,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/comparison_results')
def comparison_results():
    if 'comparison_id' not in session:
        return redirect(url_for('compare_page'))
    
    session_id = session['comparison_id']
    if session_id not in evaluation_store or evaluation_store[session_id].get('type') != 'comparison':
        return redirect(url_for('compare_page'))
    
    comparison_data = evaluation_store[session_id]
    return render_template('comparison_results.html', 
                         comparison_data=comparison_data,
                         session_id=session_id)

@app.route('/new_candidate')
def new_candidate():
    # Get current session ID before clearing session
    current_session_id = session.get('candidate_id')
    comparison_session_id = session.get('comparison_id')
    
    # Clear session
    session.clear()
    
    # Clear evaluation store for this session if it exists
    if current_session_id and current_session_id in evaluation_store:
        del evaluation_store[current_session_id]
    if comparison_session_id and comparison_session_id in evaluation_store:
        del evaluation_store[comparison_session_id]
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
