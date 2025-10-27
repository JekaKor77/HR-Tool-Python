# HR CV Analysis System

An AI-powered application that helps HR professionals analyze candidate CVs, generate technical quizzes, and provide hiring recommendations for Salesforce Developer positions. Now includes advanced CV comparison functionality to identify differences and gaps between multiple CV versions.

## Features

### Single CV Analysis
- **CV Upload & Analysis**: Upload CVs in PDF, DOC, DOCX, or TXT format
- **AI-Powered Analysis**: Extract key information about candidate's experience and skills
- **Technical Quiz Generation**: Generate Salesforce-specific technical questions
- **Soft Skills Assessment**: Include questions about communication and teamwork
- **Response Evaluation**: AI analyzes candidate responses and provides recommendations

### CV Comparison (NEW!)
- **Dual CV Upload**: Compare two CVs side by side (e.g., LinkedIn vs ChatGPT generated)
- **Difference Detection**: Identify discrepancies in work experience, dates, skills, and projects
- **Gap Analysis**: Find missing information or inconsistencies between CVs
- **Targeted Questions**: Generate specific interview questions based on identified differences
- **Priority Assessment**: Categorize issues by importance (high/medium/low priority)

### User Interface
- **Modern Web Interface**: Clean, responsive design with Bootstrap
- **Interactive Dashboard**: Easy navigation between single CV analysis and comparison features
- **Real-time Processing**: Live feedback during CV analysis and comparison
- **Export Options**: Download results as PDF or JSON

## Workflows

### Single CV Analysis Workflow
1. **Upload CV** → HR uploads candidate's CV
2. **AI Analysis** → System analyzes CV and generates quiz
3. **Conduct Quiz** → HR asks generated questions to candidate
4. **Upload Responses** → HR records candidate's answers
5. **Get Recommendations** → AI evaluates and suggests next steps

### CV Comparison Workflow
1. **Upload Two CVs** → HR uploads both CV versions (e.g., LinkedIn + ChatGPT)
2. **AI Comparison** → System identifies differences, gaps, and inconsistencies
3. **Review Analysis** → HR reviews detailed comparison report
4. **Generate Questions** → System creates targeted interview questions
5. **Conduct Interview** → HR uses generated questions to clarify discrepancies
6. **Make Decision** → HR makes informed hiring decisions based on analysis

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone or download the project**
   ```bash
   cd /Users/evgenijkorovin/PythonProject
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: Flask secret key for sessions (required)
- `FLASK_ENV`: Set to 'development' for debug mode

### File Upload Settings

- Maximum file size: 16MB
- Supported formats: PDF, DOC, DOCX, TXT
- Upload directory: `uploads/` (created automatically)

## Usage

### For HR Professionals

#### Single CV Analysis
1. **Start New Evaluation**
   - Click "Start Single CV Analysis" or go to the home page
   - Upload the candidate's CV

2. **Review Analysis**
   - Review the AI-generated CV analysis
   - Click "Generate Quiz" to proceed

3. **Conduct Quiz**
   - Ask the generated technical and soft skills questions
   - Record the candidate's responses in the form

4. **Get Recommendations**
   - Submit responses for AI evaluation
   - Review detailed recommendations and next steps

#### CV Comparison
1. **Start Comparison**
   - Click "Start CV Comparison" from the home page
   - Upload both CV files and provide descriptive names

2. **Review Differences**
   - Review the detailed comparison analysis
   - Identify key discrepancies and gaps

3. **Use Generated Questions**
   - Copy the targeted interview questions
   - Use them to clarify discrepancies during interviews

4. **Make Informed Decisions**
   - Use the analysis to make better hiring decisions
   - Export results for record keeping

### AI Prompts

The system uses specialized prompts for:
- **CV Analysis**: Extracting technical skills, experience, and qualifications
- **CV Comparison**: Identifying differences, gaps, and inconsistencies between CVs
- **Quiz Generation**: Creating Salesforce-specific technical questions
- **Question Generation**: Creating targeted interview questions based on CV differences
- **Response Evaluation**: Providing hiring recommendations and next steps

## Project Structure

```
PythonProject/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── services/            # AI service modules
│   ├── cv_analyzer.py   # CV analysis service
│   ├── cv_comparator.py # CV comparison service (NEW!)
│   ├── quiz_generator.py # Quiz generation service
│   └── response_evaluator.py # Response evaluation service
├── utils/               # Utility modules
│   └── file_processor.py # File handling utilities
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page with feature selection
│   ├── compare.html    # CV comparison upload page (NEW!)
│   ├── comparison_results.html # Comparison results page (NEW!)
│   ├── quiz.html       # Quiz page
│   └── results.html    # Results page
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── main.js     # JavaScript functionality
└── uploads/            # Upload directory (created automatically)
```

## API Endpoints

### Single CV Analysis
- `GET /` - Home page with feature selection
- `POST /upload` - Upload and analyze CV
- `GET /quiz` - Quiz page
- `POST /evaluate` - Evaluate candidate responses
- `GET /results` - Results page

### CV Comparison (NEW!)
- `GET /compare` - CV comparison upload page
- `POST /upload_compare` - Upload and compare two CVs
- `GET /comparison_results` - Comparison results page

### General
- `GET /new_candidate` - Start new evaluation (clears all sessions)

## Troubleshooting

### Common Issues

1. **OpenAI API Error**
   - Ensure your API key is valid and has sufficient credits
   - Check your internet connection

2. **File Upload Issues**
   - Ensure file is in supported format (PDF, DOC, DOCX, TXT)
   - Check file size is under 16MB

3. **Import Errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Ensure you're using the correct Python version

### Debug Mode

To enable debug mode, set `FLASK_ENV=development` in your `.env` file.

## Security Notes

- Never commit your `.env` file to version control
- Use a strong secret key in production
- Consider implementing user authentication for production use
- Validate and sanitize all file uploads

## License

This project is for internal use. Please ensure compliance with your organization's policies regarding AI usage and data handling.

## Support

For issues or questions, please contact the development team.
