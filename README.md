# AI-Powered Resume Intelligence System

AI-Powered Resume Intelligence System is an intelligent web-based tool designed to streamline the resume creation and optimization process. It allows users to effortlessly generate ATS-friendly resumes, tailored to specific job roles using AI. Additionally, it features a powerful resume analyzer that evaluates resumes against job descriptions.

## Features and Functionality

*   **AI-Powered Resume Analyzer:** Upload your resume and receive instant feedback on ATS compatibility, keyword optimization, formatting, and more.
    *   Analyzes resumes in PDF and DOCX formats using the `ResumeAnalyzer` class in `utils/resume_analyzer.py`.
    *   Provides scores for ATS compatibility, keyword matching, format, and sections.
    *   Offers suggestions for improvement based on analysis results.
    *   Example Usage: Uploading a resume triggers analysis through `app.py` using `self.analyzer.analyze_resume()`.
*   **AI-Driven Resume Builder:** Create professional resumes from scratch using an intuitive, form-based interface.
    *   Utilizes the `ResumeBuilder` class in `utils/resume_builder.py` to generate resumes in DOCX format.
    *   Supports multiple resume templates (Modern, Professional, Minimal, Creative).
    *   Users can input personal information, work experience, education, projects, and skills through a Streamlit UI.
    *   Example Usage: Clicking "Generate Resume" in `app.py` calls `self.builder.generate_resume()` to create the resume.
*   **Job Search Portal:** Explore featured jobs from top companies and easily search for relevant opportunities.
    *   Displays featured companies from the `jobs/companies.py` file.
    *   Provides links to company career pages.
*   **Resume Assistant Chatbot:**  Get instant answers to common resume-related questions.
*   **Admin Dashboard:** (Admin Access Only) Monitor resume submissions, view analytics, and manage user data.
    *   Accessed by verifying admin credentials using `verify_admin` function in `config/database.py`.
    *   Displays resume statistics, recent activity, and admin logs.
    *   Allows exporting resume data to Excel, CSV, or JSON format.
*   **User Feedback System:** Collect user feedback to improve the application.
    *   Uses a SQLite database (`feedback/feedback.db`) managed by `FeedbackManager` in `feedback/feedback.py`.
    *   Includes feedback form and statistics display.

## Technology Stack

*   **Python:** Core programming language.
*   **Streamlit:** Web framework for building the user interface.
*   **spaCy:** Natural Language Processing library for resume analysis.
*   **python-docx:** Library for creating DOCX files.
*   **PyPDF2:** Library for extracting text from PDF files.
*   **SQLite:** Database for storing resume data, analysis results, and feedback.
*   **pandas:** Data analysis library used for data manipulation and export.
*   **plotly:**  Library for creating interactive data visualizations.

## Prerequisites

*   Python 3.7 or higher
*   Required Python packages (install using `pip install -r requirements.txt`)

## Installation Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/amerthesavage/AI-Resume-Builder-and-Analyzer.git
    cd AI-Resume-Builder-and-Analyzer
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    * If you are facing issues related to `nltk`, make sure to install it separately with `pip install nltk` and download required resources with `nltk.download('punkt')` and `nltk.download('averaged_perceptron_tagger')` in your python environment
4.  **Database initialization:**

    *   The application uses an SQLite database (`resume_data.db`) to store resume data, analysis results, and admin logs.  The database is initialized automatically when the application starts through the `init_database()` function in `config/database.py`. No manual initialization is typically required.

## Usage Guide

1.  **Run the Streamlit application:**

    ```bash
    streamlit run app.py
    ```

2.  **Access the application in your web browser:**

    *   Open your web browser and go to the address displayed in the terminal (usually `http://localhost:8501`).

3.  **Using the Resume Analyzer:**

    *   Navigate to the "🔍 RESUME ANALYZER" page.
    *   Select the appropriate "Job Category" and "Specific Role".
    *   Upload your resume in PDF or DOCX format.
    *   Review the analysis results, including ATS score, keyword match, and suggestions for improvement.

4.  **Using the Resume Builder:**

    *   Navigate to the "📝 RESUME BUILDER" page.
    *   Select a resume template.
    *   Fill out the forms for each section (Personal Information, Summary, Experience, Education, Skills, Projects).
    *   Click the "Generate Resume 📄" button to create your resume.
    *   Download the generated DOCX file.

5.  **Exploring the Job Search Portal:**

    *   Navigate to the "🎯 JOB SEARCH" page.
    *   Browse featured companies and click the "View Careers" button to explore job openings.

6.  **Using the Chatbot:**
    * Navigate to the "💬 CHATBOT" page.
    * Browse available questions or create your own to get instant answers.
    
7.  **Admin Access:**

    *   To access the admin dashboard, you must first be registered as an admin in the database. This requires direct database interaction.
    *   Uncomment and execute the admin creation snippet at the bottom of `app.py` (after ensuring necessary variables are set). Then, comment it out again.
    *   Navigate to the Streamlit app and enter the admin credentials in the sidebar.

## API Documentation (N/A)

This project does not expose an external API.

## Contributing Guidelines

Contributions are welcome!  Follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Test your changes thoroughly.
5.  Submit a pull request to the `main` branch.

## License Information

This project does not currently have a specified license. All rights are reserved by the author.

## Contact/Support Information

*   **Developer:** Amer Ali Khan
*   **Email:** albaik.khan99@gmail.com
*   **GitHub:** [https://github.com/amerthesavage](https://github.com/amerthesavage)
