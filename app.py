"""
AI Resume Builder & Analyzer - Main Application
"""
import streamlit as st
from jobs.companies import FEATURED_COMPANIES

# Set page config at the very beginning
st.set_page_config(
    page_title="AI Resume Builder & Analyzer",
    page_icon="🚀",
    layout="wide"
)

import json
import pandas as pd
import plotly.express as px
import traceback
from utils.resume_analyzer import ResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from config.database import (
    get_database_connection, save_resume_data, save_analysis_data, 
    init_database, verify_admin, log_admin_action
)
from config.job_roles import JOB_ROLES
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS, get_courses_for_role, get_category_for_role
from dashboard.dashboard import DashboardManager
import requests
from streamlit_lottie import st_lottie # type: ignore
import plotly.graph_objects as go
import base64
import io
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from feedback.feedback import FeedbackManager
from ui_components import (
    apply_modern_styles, hero_section, feature_card, about_section, 
    page_header, render_analytics_section, render_activity_section, 
    render_suggestions_section
)
from datetime import datetime
from jobs.job_search import render_job_search
from PIL import Image
import nltk

class ResumeApp:
    def __init__(self):
        """Initialize the application"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'linkedin': '',
                    'portfolio': ''
                },
                'summary': '',
                'experiences': [],
                'education': [],
                'projects': [],
                'skills_categories': {
                    'technical': [],
                    'soft': [],
                    'languages': [],
                    'tools': []
                }
            }
        
        # Initialize navigation state
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
            
        # Initialize admin state
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False
        
        self.pages = {
            "🏠 HOME": self.render_home,
            "🔍 RESUME ANALYZER": self.render_analyzer,
            "📝 RESUME BUILDER": self.render_builder,
            "🎯 JOB SEARCH": self.render_job_search,
            "💬 CHATBOT": self.render_chatbot,
            "ℹ️ ABOUT": self.render_about
        }
        
        # Initialize dashboard manager
        self.dashboard_manager = DashboardManager()
        
        self.analyzer = ResumeAnalyzer()
        self.builder = ResumeBuilder()
        self.job_roles = JOB_ROLES
        
        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None
        
        # Initialize database
        init_database()
        
        # Load external CSS
        with open('style/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
        # Load Google Fonts
        st.markdown("""
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """, unsafe_allow_html=True)

    def load_lottie_url(self, url: str):
        """Load Lottie animation from URL"""
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    def apply_global_styles(self):
        st.markdown("""
        <style>
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a1a;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }

        /* Global Styles */
        .main-header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 0%, rgba(255,255,255,0.1) 100%);
            z-index: 1;
        }

        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 600;
            margin: 0;
            position: relative;
            z-index: 2;
        }

        /* Template Card Styles */
        .template-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            padding: 1rem;
        }

        .template-card {
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            padding: 2rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .template-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border-color: #4CAF50;
        }

        .template-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 0%, rgba(76,175,80,0.1) 100%);
            z-index: 1;
        }

        .template-icon {
            font-size: 3rem;
            color: #4CAF50;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
        }

        .template-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1rem;
            position: relative;
            z-index: 2;
        }

        .template-description {
            color: #aaa;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
            line-height: 1.6;
        }

        /* Feature List Styles */
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1.5rem 0;
            position: relative;
            z-index: 2;
        }

        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: #ddd;
            font-size: 0.95rem;
        }

        .feature-icon {
            color: #4CAF50;
            margin-right: 0.8rem;
            font-size: 1.1rem;
        }

        /* Button Styles */
        .action-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
            z-index: 2;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(76,175,80,0.3);
        }

        .action-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
            transition: all 0.6s ease;
        }

        .action-button:hover::before {
            left: 100%;
        }

        /* Form Section Styles */
        .form-section {
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .form-section-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid #4CAF50;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            color: #ddd;
            font-weight: 500;
            margin-bottom: 0.8rem;
            display: block;
        }

        .form-input {
            width: 100%;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(30, 30, 30, 0.9);
            color: white;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76,175,80,0.2);
            outline: none;
        }

        /* Skill Tags */
        .skill-tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .skill-tag {
            background: rgba(76,175,80,0.1);
            color: #4CAF50;
            padding: 0.6rem 1.2rem;
            border-radius: 50px;
            border: 1px solid #4CAF50;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .skill-tag:hover {
            background: #4CAF50;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76,175,80,0.2);
        }

        /* Progress Circle */
        .progress-container {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 2rem auto;
        }

        .progress-circle {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }

        .progress-circle circle {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            stroke: #4CAF50;
            transform-origin: 50% 50%;
            transition: all 0.3s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
        }

        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-slide-in {
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .template-container {
                grid-template-columns: 1fr;
            }

            .main-header {
                padding: 1.5rem;
            }

            .main-header h1 {
                font-size: 2rem;
            }

            .template-card {
                padding: 1.5rem;
            }

            .action-button {
                padding: 0.8rem 1.6rem;
            }
        }

        .profile-section, .vision-section, .feature-card {
            text-align: center;
            padding: 2.5rem;
            background: rgba(15, 23, 42, 0.95);
            border-radius: 24px;
            margin: 1.5rem auto;
            max-width: 1200px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2.5rem;
            margin-bottom: 2.5rem;
        }
        
        .team-member {
            padding: 1.5rem;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 20px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(5px);
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            height: 100%;
        }
        
        .team-member:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .profile-image {
            width: 220px;
            height: 220px;
            border-radius: 50%;
            margin: 0 auto 1.5rem;
            display: block;
            object-fit: cover;
            border: 4px solid #6366f1;
            box-shadow: 0 8px 16px rgba(99, 102, 241, 0.2);
            transition: all 0.3s ease;
        }

        .profile-image:hover {
            transform: scale(1.05);
            border-color: #8b5cf6;
        }

        .profile-name {
            font-size: 2rem;
            color: #fff;
            margin-bottom: 0.5rem;
            font-weight: 600;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }

        .profile-title {
            font-size: 1.1rem;
            color: #94a3b8;
            margin-bottom: 1.5rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-align: center;
        }

        .social-links {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin: 0;
            padding: 0;
            width: 100%;
        }
        
        .social-link {
            font-size: 1.8rem;
            color: #6366f1;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 0.8rem;
            border-radius: 50%;
            background: rgba(99, 102, 241, 0.1);
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            border: 1px solid rgba(99, 102, 241, 0.2);
            margin: 0;
        }
        
        .social-link:hover {
            transform: translateY(-5px) scale(1.1);
            background: #6366f1;
            color: white;
            box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
        }
        
        .bio-text {
            color: #94a3b8;
            line-height: 1.8;
            font-size: 1.1rem;
            margin-top: 2.5rem;
            text-align: left;
            padding: 0 1rem;
        }

        .vision-section {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        }

        .vision-icon {
            font-size: 3rem;
            color: #6366f1;
            margin-bottom: 1.5rem;
            text-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
        }

        .vision-title {
            font-size: 2.2rem;
            color: #fff;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }

        .vision-text {
            color: #94a3b8;
            line-height: 1.8;
            font-size: 1.1rem;
            font-style: italic;
            margin: 1.5rem 0;
            text-align: left;
            padding: 0 1rem;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 2rem;
            padding: 2rem;
            max-width: 1800px;
            margin: 0 auto;
        }

        .feature-card {
            text-align: center;
            padding: 3rem 4rem;
            background: rgba(15, 23, 42, 0.95);
            border-radius: 24px;
            margin: 1rem auto;
            max-width: none;
            width: 100%;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 250px;
        }

        .feature-card i {
            font-size: 3.2rem;
            color: #6366f1;
            margin-bottom: 1.5rem;
            text-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
        }

        .feature-card h3 {
            font-size: 2rem;
            color: #fff;
            margin: 1rem 0;
            font-weight: 600;
        }

        .feature-card p {
            color: #94a3b8;
            line-height: 1.8;
            font-size: 1.2rem;
            margin: 0;
            padding: 0 2rem;
            max-width: 800px;
        }

        .hero-section {
            text-align: center;
            padding: 1.5rem 0;
            margin: 1rem auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .hero-title {
            font-size: 3.2rem;
            color: #fff;
            margin-bottom: 0.8rem;
            text-align: center;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
            font-size: 1.4rem;
            color: #94a3b8;
            margin: 0;
            text-align: center;
            max-width: 600px;
            line-height: 1.6;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 1rem 2rem !important;
            font-size: 1.2rem !important;
            font-weight: 500 !important;
            background: rgba(99, 102, 241, 0.1) !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
            border-radius: 12px !important;
            color: #94a3b8 !important;
            transition: all 0.3s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(99, 102, 241, 0.2) !important;
            transform: translateY(-2px);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            color: #fff !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }

        /* Existing company card styles */
        .company-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2.5rem;
            padding: 2rem;
            max-width: 1800px;
            margin: 0 auto;
        }

        .company-card {
            background: rgba(15, 23, 42, 0.95);
            border-radius: 24px;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            min-height: 380px;
            margin-bottom: 1rem;
        }

        .company-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
            border-color: rgba(99, 102, 241, 0.3);
        }

        .company-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin: 0 auto 1.5rem;
        }

        .company-name {
            font-size: 1.6rem;
            color: #fff;
            margin: 0 0 1rem 0;
            font-weight: 600;
            line-height: 1.3;
        }

        .company-description {
            color: #94a3b8;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            flex-grow: 1;
        }

        .company-categories {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            justify-content: center;
            margin-bottom: 1.5rem;
            width: 100%;
        }

        .category-tag {
            background: rgba(99, 102, 241, 0.1);
            color: #6366f1;
            padding: 0.4rem 0.8rem;
            border-radius: 50px;
            font-size: 0.85rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .career-link {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white !important;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            text-decoration: none !important;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-block;
            margin-top: auto;
            font-size: 1rem;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .career-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(99, 102, 241, 0.4);
            filter: brightness(110%);
        }
        </style>
        """, unsafe_allow_html=True)

    def load_image(self, image_name):
        """Load image from static directory"""
        try:
            image_path = f"c:/Users/shree/Downloads/smart-resume-ai/{image_name}"
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            encoded = base64.b64encode(image_bytes).decode()
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"Error loading image {image_name}: {e}")
            return None

    def export_to_excel(self):
        """Export resume data to Excel"""
        conn = get_database_connection()
        
        # Get resume data with analysis
        query = """
            SELECT 
                rd.name, rd.email, rd.phone, rd.linkedin, rd.github, rd.portfolio,
                rd.summary, rd.target_role, rd.target_category,
                rd.education, rd.experience, rd.projects, rd.skills,
                ra.ats_score, ra.keyword_match_score, ra.format_score, ra.section_score,
                ra.missing_skills, ra.recommendations,
                rd.created_at
            FROM resume_data rd
            LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
        """
        
        try:
            # Read data into DataFrame
            df = pd.read_sql_query(query, conn)
            
            # Create Excel writer object
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resume Data')
            
            return output.getvalue()
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            return None
        finally:
            conn.close()

    def render_dashboard(self):
        """Render the dashboard page"""
        self.dashboard_manager.render_dashboard()

    def render_empty_state(self, icon, message):
        """Render an empty state with icon and message"""
        return f"""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <i class='{icon}' style='font-size: 2rem; margin-bottom: 1rem; color: #00bfa5;'></i>
                <p style='margin: 0;'>{message}</p>
            </div>
        """

    def analyze_resume(self, resume_text):
        """Analyze resume and store results"""
        analytics = self.analyzer.analyze_resume(resume_text)
        st.session_state.analytics_data = analytics
        return analytics

    def handle_resume_upload(self):
        """Handle resume upload and analysis"""
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'])
        
        if uploaded_file is not None:
            try:
                # Extract text from resume
                if uploaded_file.type == "application/pdf":
                    resume_text = self.analyzer.extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = self.analyzer.extract_text_from_docx(uploaded_file)
                
                # Store resume data
                st.session_state.resume_data = {
                    'filename': uploaded_file.name,
                    'content': resume_text,
                    'upload_time': datetime.now().isoformat()
                }
                
                # Analyze resume
                analytics = self.analyze_resume(resume_text)
                
                return True
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                return False
        return False

    def render_builder(self):
        # Title with modern gradient styling
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(88, 28, 135, 0.95) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1.5rem auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: none;
            width: 100%;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, 
                    rgba(99, 102, 241, 0.15) 0%,
                    rgba(139, 92, 246, 0.15) 50%,
                    rgba(147, 51, 234, 0.15) 100%
                );
                z-index: 1;
            "></div>
            <div style="position: relative; z-index: 2;">
                <h1 style="
                    font-size: 3.2rem;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #9333ea 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 1rem;
                    font-weight: 700;
                ">Resume Builder</h1>
                <p style="
                    font-size: 1.4rem;
                    color: #94a3b8;
                    margin: 0;
                    line-height: 1.6;
                ">Create your professional resume</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Template selection
        template_options = ["Modern", "Professional", "Minimal", "Creative"]
        selected_template = st.selectbox("Select Resume Template", template_options)
        st.success(f"🎨 Currently using: {selected_template} Template")

        # Personal Information
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            # Get existing values from session state
            existing_name = st.session_state.form_data['personal_info']['full_name']
            existing_email = st.session_state.form_data['personal_info']['email']
            existing_phone = st.session_state.form_data['personal_info']['phone']
            
            # Input fields with existing values
            full_name = st.text_input("Full Name", value=existing_name)
            email = st.text_input("Email", value=existing_email, key="email_input")
            phone = st.text_input("Phone", value=existing_phone)

            # Immediately update session state after email input
            if 'email_input' in st.session_state:
                st.session_state.form_data['personal_info']['email'] = st.session_state.email_input
        
        with col2:
            # Get existing values from session state
            existing_location = st.session_state.form_data['personal_info']['location']
            existing_linkedin = st.session_state.form_data['personal_info']['linkedin']
            existing_portfolio = st.session_state.form_data['personal_info']['portfolio']
            
            # Input fields with existing values
            location = st.text_input("Location", value=existing_location)
            linkedin = st.text_input("LinkedIn URL", value=existing_linkedin)
            portfolio = st.text_input("Portfolio Website", value=existing_portfolio)

        # Update personal info in session state
        st.session_state.form_data['personal_info'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'portfolio': portfolio
        }

        # Professional Summary
        st.subheader("Professional Summary")
        summary = st.text_area("Professional Summary", value=st.session_state.form_data.get('summary', ''), height=150,
                             help="Write a brief summary highlighting your key skills and experience")
        
        # Experience Section
        st.subheader("Work Experience")
        if 'experiences' not in st.session_state.form_data:
            st.session_state.form_data['experiences'] = []
            
        if st.button("Add Experience"):
            st.session_state.form_data['experiences'].append({
                'company': '',
                'position': '',
                'start_date': '',
                'end_date': '',
                'description': '',
                'responsibilities': [],
                'achievements': []
            })
        
        for idx, exp in enumerate(st.session_state.form_data['experiences']):
            with st.expander(f"Experience {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    exp['company'] = st.text_input("Company Name", key=f"company_{idx}", value=exp.get('company', ''))
                    exp['position'] = st.text_input("Position", key=f"position_{idx}", value=exp.get('position', ''))
                with col2:
                    exp['start_date'] = st.text_input("Start Date", key=f"start_date_{idx}", value=exp.get('start_date', ''))
                    exp['end_date'] = st.text_input("End Date", key=f"end_date_{idx}", value=exp.get('end_date', ''))
                
                exp['description'] = st.text_area("Role Overview", key=f"desc_{idx}", 
                                                value=exp.get('description', ''),
                                                help="Brief overview of your role and impact")
                
                # Responsibilities
                st.markdown("##### Key Responsibilities")
                resp_text = st.text_area("Enter responsibilities (one per line)", 
                                       key=f"resp_{idx}",
                                       value='\n'.join(exp.get('responsibilities', [])),
                                       height=100,
                                       help="List your main responsibilities, one per line")
                exp['responsibilities'] = [r.strip() for r in resp_text.split('\n') if r.strip()]
                
                # Achievements
                st.markdown("##### Key Achievements")
                achv_text = st.text_area("Enter achievements (one per line)", 
                                       key=f"achv_{idx}",
                                       value='\n'.join(exp.get('achievements', [])),
                                       height=100,
                                       help="List your notable achievements, one per line")
                exp['achievements'] = [a.strip() for a in achv_text.split('\n') if a.strip()]
                
                if st.button("Remove Experience", key=f"remove_exp_{idx}"):
                    st.session_state.form_data['experiences'].pop(idx)
                    st.rerun()
        
        # Projects Section
        st.subheader("Projects")
        if 'projects' not in st.session_state.form_data:
            st.session_state.form_data['projects'] = []
            
        if st.button("Add Project"):
            st.session_state.form_data['projects'].append({
                'name': '',
                'technologies': '',
                'description': '',
                'responsibilities': [],
                'achievements': [],
                'link': ''
            })
        
        for idx, proj in enumerate(st.session_state.form_data['projects']):
            with st.expander(f"Project {idx + 1}", expanded=True):
                proj['name'] = st.text_input("Project Name", key=f"proj_name_{idx}", value=proj.get('name', ''))
                proj['technologies'] = st.text_input("Technologies Used", key=f"proj_tech_{idx}", 
                                                   value=proj.get('technologies', ''),
                                                   help="List the main technologies, frameworks, and tools used")
                
                proj['description'] = st.text_area("Project Overview", key=f"proj_desc_{idx}", 
                                                 value=proj.get('description', ''),
                                                 help="Brief overview of the project and its goals")
                
                # Project Responsibilities
                st.markdown("##### Key Responsibilities")
                proj_resp_text = st.text_area("Enter responsibilities (one per line)", 
                                            key=f"proj_resp_{idx}",
                                            value='\n'.join(proj.get('responsibilities', [])),
                                            height=100,
                                            help="List your main responsibilities in the project")
                proj['responsibilities'] = [r.strip() for r in proj_resp_text.split('\n') if r.strip()]
                
                # Project Achievements
                st.markdown("##### Key Achievements")
                proj_achv_text = st.text_area("Enter achievements (one per line)", 
                                            key=f"proj_achv_{idx}",
                                            value='\n'.join(proj.get('achievements', [])),
                                            height=100,
                                            help="List the project's key achievements and your contributions")
                proj['achievements'] = [a.strip() for a in proj_achv_text.split('\n') if a.strip()]
                
                proj['link'] = st.text_input("Project Link (optional)", key=f"proj_link_{idx}", 
                                           value=proj.get('link', ''),
                                           help="Link to the project repository, demo, or documentation")
                
                if st.button("Remove Project", key=f"remove_proj_{idx}"):
                    st.session_state.form_data['projects'].pop(idx)
                    st.rerun()
        
        # Education Section
        st.subheader("Education")
        if 'education' not in st.session_state.form_data:
            st.session_state.form_data['education'] = []
            
        if st.button("Add Education"):
            st.session_state.form_data['education'].append({
                'school': '',
                'degree': '',
                'field': '',
                'graduation_date': '',
                'gpa': '',
                'achievements': []
            })
        
        for idx, edu in enumerate(st.session_state.form_data['education']):
            with st.expander(f"Education {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edu['school'] = st.text_input("School/University", key=f"school_{idx}", value=edu.get('school', ''))
                    edu['degree'] = st.text_input("Degree", key=f"degree_{idx}", value=edu.get('degree', ''))
                with col2:
                    edu['field'] = st.text_input("Field of Study", key=f"field_{idx}", value=edu.get('field', ''))
                    edu['graduation_date'] = st.text_input("Graduation Date", key=f"grad_date_{idx}", 
                                                         value=edu.get('graduation_date', ''))
                
                edu['gpa'] = st.text_input("GPA (optional)", key=f"gpa_{idx}", value=edu.get('gpa', ''))
                
                # Educational Achievements
                st.markdown("##### Achievements & Activities")
                edu_achv_text = st.text_area("Enter achievements (one per line)", 
                                           key=f"edu_achv_{idx}",
                                           value='\n'.join(edu.get('achievements', [])),
                                           height=100,
                                           help="List academic achievements, relevant coursework, or activities")
                edu['achievements'] = [a.strip() for a in edu_achv_text.split('\n') if a.strip()]
                
                if st.button("Remove Education", key=f"remove_edu_{idx}"):
                    st.session_state.form_data['education'].pop(idx)
                    st.rerun()
        
        # Skills Section
        st.subheader("Skills")
        if 'skills_categories' not in st.session_state.form_data:
            st.session_state.form_data['skills_categories'] = {
                'technical': [],
                'soft': [],
                'languages': [],
                'tools': []
            }
        
        col1, col2 = st.columns(2)
        with col1:
            tech_skills = st.text_area("Technical Skills (one per line)", 
                                     value='\n'.join(st.session_state.form_data['skills_categories']['technical']),
                                     height=150,
                                     help="Programming languages, frameworks, databases, etc.")
            st.session_state.form_data['skills_categories']['technical'] = [s.strip() for s in tech_skills.split('\n') if s.strip()]
            
            soft_skills = st.text_area("Soft Skills (one per line)", 
                                     value='\n'.join(st.session_state.form_data['skills_categories']['soft']),
                                     height=150,
                                     help="Leadership, communication, problem-solving, etc.")
            st.session_state.form_data['skills_categories']['soft'] = [s.strip() for s in soft_skills.split('\n') if s.strip()]
        
        with col2:
            languages = st.text_area("Languages (one per line)", 
                                   value='\n'.join(st.session_state.form_data['skills_categories']['languages']),
                                   height=150,
                                   help="Programming or human languages with proficiency level")
            st.session_state.form_data['skills_categories']['languages'] = [l.strip() for l in languages.split('\n') if l.strip()]
            
            tools = st.text_area("Tools & Technologies (one per line)", 
                               value='\n'.join(st.session_state.form_data['skills_categories']['tools']),
                               height=150,
                               help="Development tools, software, platforms, etc.")
            st.session_state.form_data['skills_categories']['tools'] = [t.strip() for t in tools.split('\n') if t.strip()]
        
        # Update form data in session state
        st.session_state.form_data.update({
            'summary': summary
        })
        
        # Generate Resume button
        if st.button("Generate Resume 📄", type="primary"):
            print("Validating form data...")
            print(f"Session state form data: {st.session_state.form_data}")
            print(f"Email input value: {st.session_state.get('email_input', '')}")
            
            # Get the current values from form
            current_name = st.session_state.form_data['personal_info']['full_name'].strip()
            current_email = st.session_state.email_input if 'email_input' in st.session_state else ''
            
            print(f"Current name: {current_name}")
            print(f"Current email: {current_email}")
            
            # Validate required fields
            if not current_name:
                st.error("⚠️ Please enter your full name.")
                return
            
            if not current_email:
                st.error("⚠️ Please enter your email address.")
                return
                
            # Update email in form data one final time
            st.session_state.form_data['personal_info']['email'] = current_email
            
            try:
                print("Preparing resume data...")
                # Prepare resume data with current form values
                resume_data = {
                    "personal_info": st.session_state.form_data['personal_info'],
                    "summary": st.session_state.form_data.get('summary', '').strip(),
                    "experience": st.session_state.form_data.get('experiences', []),
                    "education": st.session_state.form_data.get('education', []),
                    "projects": st.session_state.form_data.get('projects', []),
                    "skills": st.session_state.form_data.get('skills_categories', {
                        'technical': [],
                        'soft': [],
                        'languages': [],
                        'tools': []
                    }),
                    "template": selected_template
                }
                
                print(f"Resume data prepared: {resume_data}")
                
                try:
                    # Generate resume
                    resume_buffer = self.builder.generate_resume(resume_data)
                    if resume_buffer:
                        try:
                            # Save resume data to database
                            save_resume_data(resume_data)
                            
                            # Offer the resume for download
                            st.success("✅ Resume generated successfully!")
                            st.download_button(
                                label="Download Resume 📥",
                                data=resume_buffer,
                                file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        except Exception as db_error:
                            print(f"Warning: Failed to save to database: {str(db_error)}")
                            # Still allow download even if database save fails
                            st.warning("⚠️ Resume generated but couldn't be saved to database")
                            st.download_button(
                                label="Download Resume 📥",
                                data=resume_buffer,
                                file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    else:
                        st.error("❌ Failed to generate resume. Please try again.")
                        print("Resume buffer was None")
                except Exception as gen_error:
                    print(f"Error during resume generation: {str(gen_error)}")
                    print(f"Full traceback: {traceback.format_exc()}")
                    st.error(f"❌ Error generating resume: {str(gen_error)}")
                        
            except Exception as e:
                print(f"Error preparing resume data: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                st.error(f"❌ Error preparing resume data: {str(e)}")
    
    def render_about(self):
        """Render the about page"""
        # Apply modern styles
        from ui_components import apply_modern_styles
        import base64
        import os
        
        # Function to load image as base64
        def get_image_as_base64(file_path):
            try:
                with open(file_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode()
                    return f"data:image/jpeg;base64,{encoded}"
            except:
                return None
        
        # Get image paths and convert to base64
        image_paths = {
            "amer": "assets/amerpic.jpg",
            "kushendra": "assets/Kushpic.png",
            "shafi": "assets/Shafipic.png"
        }

      ###  st.image(image_paths["amer"], caption="Amer")
       ### st.image(image_paths["kushendra"], caption="Kushendra")
      ###  st.image(image_paths["shafi"], caption="Shafi")
        
        image_base64s = {name: get_image_as_base64(path) for name, path in image_paths.items()}
        
        apply_modern_styles()
        
        # Add Font Awesome icons and custom CSS
        st.markdown("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                .profile-section, .vision-section, .feature-card {
                    text-align: center;
                    padding: 2.5rem;
                    background: rgba(15, 23, 42, 0.95);
                    border-radius: 24px;
                    margin: 1.5rem auto;
                    max-width: 1200px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                }
                
                .team-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 2.5rem;
                    margin-bottom: 2.5rem;
                }
                
                .team-member {
                    padding: 1.5rem;
                    background: rgba(30, 41, 59, 0.8);
                    border-radius: 20px;
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(5px);
                    position: relative;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: space-between;
                    height: 100%;
                }
                
                .team-member:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
                    border-color: rgba(99, 102, 241, 0.3);
                }
                
                .profile-image {
                    width: 220px;
                    height: 220px;
                    border-radius: 50%;
                    margin: 0 auto 1.5rem;
                    display: block;
                    object-fit: cover;
                    border: 4px solid #6366f1;
                    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.2);
                    transition: all 0.3s ease;
                }
                
                .profile-image:hover {
                    transform: scale(1.05);
                    border-color: #8b5cf6;
                }
                
                .profile-name {
                    font-size: 2rem;
                    color: #fff;
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    text-align: center;
                }
                
                .profile-title {
                    font-size: 1.1rem;
                    color: #94a3b8;
                    margin-bottom: 1.5rem;
                    font-weight: 500;
                    letter-spacing: 0.5px;
                    text-align: center;
                }
                
                .social-links {
                    display: flex;
                    justify-content: center;
                    gap: 1.5rem;
                    margin: 0;
                    padding: 0;
                    width: 100%;
                }
                
                .social-link {
                    font-size: 1.8rem;
                    color: #6366f1;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    padding: 0.8rem;
                    border-radius: 50%;
                    background: rgba(99, 102, 241, 0.1);
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-decoration: none;
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    margin: 0;
                }
                
                .social-link:hover {
                    transform: translateY(-5px) scale(1.1);
                    background: #6366f1;
                    color: white;
                    box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
                }
                
                .bio-text {
                    color: #94a3b8;
                    line-height: 1.8;
                    font-size: 1.1rem;
                    margin-top: 2.5rem;
                    text-align: left;
                    padding: 0 1rem;
                }

                .vision-section {
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
                }

                .vision-icon {
                    font-size: 3rem;
                    color: #6366f1;
                    margin-bottom: 1.5rem;
                    text-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
                }

                .vision-title {
                    font-size: 2.2rem;
                    color: #fff;
                    margin-bottom: 1.5rem;
                    font-weight: 600;
                }

                .vision-text {
                    color: #94a3b8;
                    line-height: 1.8;
                    font-size: 1.1rem;
                    font-style: italic;
                    margin: 1.5rem 0;
                    text-align: left;
                    padding: 0 1rem;
                }

                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
                    gap: 2rem;
                    padding: 2rem;
                    max-width: 1800px;
                    margin: 0 auto;
                }

                .feature-card {
                    text-align: center;
                    padding: 3rem 4rem;
                    background: rgba(15, 23, 42, 0.95);
                    border-radius: 24px;
                    margin: 1rem auto;
                    max-width: none;
                    width: 100%;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 250px;
                }

                .feature-card i {
                    font-size: 3.2rem;
                    color: #6366f1;
                    margin-bottom: 1.5rem;
                    text-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
                }

                .feature-card h3 {
                    font-size: 2rem;
                    color: #fff;
                    margin: 1rem 0;
                    font-weight: 600;
                }

                .feature-card p {
                    color: #94a3b8;
                    line-height: 1.8;
                    font-size: 1.2rem;
                    margin: 0;
                    padding: 0 2rem;
                    max-width: 800px;
                }

                .hero-section {
                    text-align: center;
                    padding: 1.5rem 0;
                    margin: 1rem auto;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }

                .hero-title {
                    font-size: 3.2rem;
                    color: #fff;
                    margin-bottom: 0.8rem;
                    text-align: center;
                    font-weight: 700;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                .hero-subtitle {
                    font-size: 1.4rem;
                    color: #94a3b8;
                    margin: 0;
                    text-align: center;
                    max-width: 600px;
                    line-height: 1.6;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Hero Section
        st.markdown("""
            <div class="hero-section">
                <h1 class="hero-title">About AI Resume Builder & Analyzer</h1>
                <p class="hero-subtitle">A powerful AI-driven platform for optimizing your resume</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Profile Section
        st.markdown(f"""
            <div class="profile-section">
                <div class="team-grid">
                    <div class="team-member">
                        <img src="{image_base64s['amer'] if image_base64s['amer'] else 'https://avatars.githubusercontent.com/Hunterdii'}" 
                             alt="Team Member 1" 
                     class="profile-image"
                     onerror="this.onerror=null; this.src='https://github.com/amerthesavage';">
                        <h3 class="profile-name">Amer Ali Khan</h3>
                        <p class="profile-title">Team Leader<br>160722733014</p>
                <div class="social-links">
                            <a href="https://github.com/amerthesavage" class="social-link" target="_blank"><i class="fab fa-github"></i></a>
                            <a href="https://www.linkedin.com/in/amer-ali-khan/" class="social-link" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="mailto:albaik.khan99@gmail.com" class="social-link" target="_blank"><i class="fas fa-envelope"></i></a>
                        </div>
                    </div>
                    <div class="team-member">
                        <img src="{image_base64s['kushendra'] if image_base64s['kushendra'] else 'https://via.placeholder.com/200'}" 
                             alt="Team Member 2" 
                             class="profile-image">
                        <h3 class="profile-name">Yellam Kushendra</h3>
                        <p class="profile-title">Team Member<br>160722733011</p>
                        <div class="social-links">
                            <a href="ykushendra77@gmail.com" class="social-link" target="_blank"><i class="fab fa-github"></i></a>
                            <a href="https://www.linkedin.com/in/kushendra-5a6b7c8d/" class="social-link" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="mailto:kushendra@example.com" class="social-link" target="_blank"><i class="fas fa-envelope"></i></a>
                        </div>
                    </div>
                    <div class="team-member">
                        <img src="{image_base64s['shafi'] if image_base64s['shafi'] else 'https://via.placeholder.com/200'}" 
                             alt="Team Member 3" 
                             class="profile-image">
                        <h3 class="profile-name">Mohammed Shafi Omair</h3>
                        <p class="profile-title">Team Member<br>160722733004</p>
                        <div class="social-links">
                            <a href="https://github.com/mohammedshafi" class="social-link" target="_blank"><i class="fab fa-github"></i></a>
                            <a href="https://www.linkedin.com/in/mohamed-shafi-omair-986104295/" class="social-link" target="_blank"><i class="fab fa-linkedin"></i></a>
                            <a href="mailto:Ms.omair22@gmail.com" class="social-link" target="_blank"><i class="fas fa-envelope"></i></a>
                        </div>
                    </div>
                </div>
                <p class="bio-text">
                    Hello! We're a team of Computer Science students from Methodist College of Engineering and Technology, Hyderabad—Amer Ali Khan, Mohammed Shafi Omair, and Yellam Kushendra. We created Smart AI Resume Builder & Analyzer as part of our mini-project to help job seekers build and optimize their resumes using the power of AI.
With our shared interest in software development and machine learning, we built this platform to make resume creation smarter, faster, and more effective. Whether you're a fresher or a professional, our tool is designed to help you stand out and land better opportunities.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Vision Section
        st.markdown("""
            <div class="vision-section">
                <i class="fas fa-lightbulb vision-icon"></i>
                <h2 class="vision-title">Our Vision</h2>
                <p class="vision-text">
                    "AI Resume Builder & Analyzer represents my vision of democratizing career advancement through technology. 
                    By combining cutting-edge AI with intuitive design, this platform empowers job seekers at 
                    every career stage to showcase their true potential and stand out in today's competitive job market."
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Features Section
        st.markdown("""
            <div class="features-grid">
                <div class="feature-card">
                    <i class="fas fa-robot feature-icon"></i>
                    <h3 class="feature-title">AI-Powered Analysis</h3>
                    <p class="feature-description">
                        Advanced AI algorithms provide detailed insights and suggestions to optimize your resume for maximum impact.
                    </p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-chart-line feature-icon"></i>
                    <h3 class="feature-title">Data-Driven Insights</h3>
                    <p class="feature-description">
                        Make informed decisions with our analytics-based recommendations and industry insights.
                    </p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-shield-alt feature-icon"></i>
                    <h3 class="feature-title">Privacy First</h3>
                    <p class="feature-description">
                        Your data security is our priority. We ensure your information is always protected and private.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    def render_analyzer(self):
        """Render the resume analyzer page"""
        apply_modern_styles()
        
        # Page Header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(88, 28, 135, 0.95) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1.5rem auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: none;
            width: 100%;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, 
                    rgba(99, 102, 241, 0.15) 0%,
                    rgba(139, 92, 246, 0.15) 50%,
                    rgba(147, 51, 234, 0.15) 100%
                );
                z-index: 1;
            "></div>
            <div style="position: relative; z-index: 2;">
                <h1 style="
                    font-size: 3.2rem;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #9333ea 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 1rem;
                    font-weight: 700;
                ">Resume Analyzer</h1>
                <p style="
                    font-size: 1.4rem;
                    color: #94a3b8;
                    margin: 0;
                    line-height: 1.6;
                ">Get instant AI-powered feedback to optimize your resume</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Job Role Selection
        categories = list(self.job_roles.keys())
        selected_category = st.selectbox("Job Category", categories)
        
        roles = list(self.job_roles[selected_category].keys())
        selected_role = st.selectbox("Specific Role", roles)
        
        role_info = self.job_roles[selected_category][selected_role]
        
        # Display role information
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1.5rem auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            max-width: none;
            width: 100%;
        ">
            <h3 style="font-size: 2rem; color: #fff; margin-bottom: 1rem;">{selected_role}</h3>
            <p style="color: #94a3b8; font-size: 1.2rem; line-height: 1.8;">{role_info['description']}</p>
            <h4 style="color: #fff; margin-top: 1.5rem; font-size: 1.4rem;">Required Skills:</h4>
            <p style="color: #94a3b8; font-size: 1.2rem;">{', '.join(role_info['required_skills'])}</p>
        </div>
        """, unsafe_allow_html=True)

        # Empty state message with modern styling
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1.5rem auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: none;
            width: 100%;
        ">
            <i class="fas fa-cloud-upload-alt" style="font-size: 3rem; color: #6366f1; margin-bottom: 1.5rem;"></i>
            <p style="color: #94a3b8; font-size: 1.2rem;">Upload your resume to get started with AI-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File Upload
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'])
        
        if uploaded_file:
            with st.spinner("Analyzing your document..."):
                # Get file content
                text = ""
                try:
                    if uploaded_file.type == "application/pdf":
                        text = self.analyzer.extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = self.analyzer.extract_text_from_docx(uploaded_file)
                    else:
                        text = uploaded_file.getvalue().decode()
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    return

                
                # Analyze the document
                analysis = self.analyzer.analyze_resume({'raw_text': text}, role_info)
                
                # Save resume data to database
                resume_data = {
                    'personal_info': {
                        'name': analysis.get('name', ''),
                        'email': analysis.get('email', ''),
                        'phone': analysis.get('phone', ''),
                        'linkedin': analysis.get('linkedin', ''),
                        'github': analysis.get('github', ''),
                        'portfolio': analysis.get('portfolio', '')
                    },
                    'summary': analysis.get('summary', ''),
                    'target_role': selected_role,
                    'target_category': selected_category,
                    'education': analysis.get('education', []),
                    'experience': analysis.get('experience', []),
                    'projects': analysis.get('projects', []),
                    'skills': analysis.get('skills', []),
                    'template': ''
                }
                
                # Save to database
                try:
                    resume_id = save_resume_data(resume_data)
                    
                    # Save analysis data
                    analysis_data = {
                        'resume_id': resume_id,
                        'ats_score': analysis['ats_score'],
                        'keyword_match_score': analysis['keyword_match']['score'],
                        'format_score': analysis['format_score'],
                        'section_score': analysis['section_score'],
                        'missing_skills': ','.join(analysis['keyword_match']['missing_skills']),
                        'recommendations': ','.join(analysis['suggestions'])
                    }
                    save_analysis_data(resume_id, analysis_data)
                    st.success("Resume data saved successfully!")
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")
                    print(f"Database error: {e}")
                
                # Show results based on document type
                if analysis.get('document_type') != 'resume':
                    st.error(f"⚠️ This appears to be a {analysis['document_type']} document, not a resume!")
                    st.warning("Please upload a proper resume for ATS analysis.")
                    return                
                # Display results in a modern card layout
                col1, col2 = st.columns(2)
                
                with col1:
                    # ATS Score Card with circular progress
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        border-radius: 24px;
                        padding: 2rem;
                        margin: 1rem 0;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    ">
                        <h2>ATS Score</h2>
                        <div style="position: relative; width: 150px; height: 150px; margin: 0 auto;">
                            <div style="
                                position: absolute;
                                width: 150px;
                                height: 150px;
                                border-radius: 50%;
                                background: conic-gradient(
                                    #6366f1 0% {score}%,
                                    rgba(99, 102, 241, 0.1) {score}% 100%
                                );
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            ">
                                <div style="
                                    width: 120px;
                                    height: 120px;
                                    background: rgba(15, 23, 42, 0.95);
                                    border-radius: 50%;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 24px;
                                    font-weight: bold;
                                    color: {color};
                                ">
                                    {score}
                                </div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 10px;">
                            <span style="
                                font-size: 1.2em;
                                color: {color};
                                font-weight: bold;
                            ">
                                {status}
                            </span>
                        </div>
                    """.format(
                        score=analysis['ats_score'],
                        color='#6366f1' if analysis['ats_score'] >= 80 else '#8b5cf6' if analysis['ats_score'] >= 60 else '#ef4444',
                        status='Excellent' if analysis['ats_score'] >= 80 else 'Good' if analysis['ats_score'] >= 60 else 'Needs Improvement'
                    ), unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Skills Match Card
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        border-radius: 24px;
                        padding: 2rem;
                        margin: 1rem 0;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    ">
                        <h2>Skills Match</h2>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Keyword Match", f"{int(analysis.get('keyword_match', {}).get('score', 0))}%")
                    
                    if analysis['keyword_match']['missing_skills']:
                        st.markdown("#### Missing Skills:")
                        for skill in analysis['keyword_match']['missing_skills']:
                            st.markdown(f"- {skill}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    # Format Score Card
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        border-radius: 24px;
                        padding: 2rem;
                        margin: 1rem 0;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    ">
                        <h2>Format Analysis</h2>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Format Score", f"{int(analysis.get('format_score', 0))}%")
                    st.metric("Section Score", f"{int(analysis.get('section_score', 0))}%")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Suggestions Card with improved UI
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                        border: 1px solid rgba(99, 102, 241, 0.2);
                        border-radius: 24px;
                        padding: 2rem;
                        margin: 1rem 0;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                    ">
                        <h2>📋 Resume Improvement Suggestions</h2>
                    """, unsafe_allow_html=True)
                    
                    # Contact Section
                    if analysis.get('contact_suggestions'):
                        st.markdown("""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin-bottom: 10px;'>📞 Contact Information</h3>
                            <ul style='list-style-type: none; padding-left: 0;'>
                        """, unsafe_allow_html=True)
                        for suggestion in analysis.get('contact_suggestions', []):
                            st.markdown(f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                    
                    # Summary Section
                    if analysis.get('summary_suggestions'):
                        st.markdown("""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin-bottom: 10px;'>📝 Professional Summary</h3>
                            <ul style='list-style-type: none; padding-left: 0;'>
                        """, unsafe_allow_html=True)
                        for suggestion in analysis.get('summary_suggestions', []):
                            st.markdown(f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                    
                    # Skills Section
                    if analysis.get('skills_suggestions') or analysis['keyword_match']['missing_skills']:
                        st.markdown("""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin-bottom: 10px;'>🎯 Skills</h3>
                            <ul style='list-style-type: none; padding-left: 0;'>
                        """, unsafe_allow_html=True)
                        for suggestion in analysis.get('skills_suggestions', []):
                            st.markdown(f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>", unsafe_allow_html=True)
                        if analysis['keyword_match']['missing_skills']:
                            st.markdown("<li style='margin-bottom: 8px;'>✓ Consider adding these relevant skills:</li>", unsafe_allow_html=True)
                            for skill in analysis['keyword_match']['missing_skills']:
                                st.markdown(f"<li style='margin-left: 20px; margin-bottom: 4px;'>• {skill}</li>", unsafe_allow_html=True)
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                    
                    # Experience Section
                    if analysis.get('experience_suggestions'):
                        st.markdown("""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin-bottom: 10px;'>💼 Work Experience</h3>
                            <ul style='list-style-type: none; padding-left: 0;'>
                        """, unsafe_allow_html=True)
                        for suggestion in analysis.get('experience_suggestions', []):
                            st.markdown(f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                    
                    # Education Section
                    if analysis.get('education_suggestions'):
                        st.markdown("""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin-bottom: 10px;'>🎓 Education</h3>
                            <ul style='list-style-type: none; padding-left: 0;'>
                        """, unsafe_allow_html=True)
                        for suggestion in analysis.get('education_suggestions', []):
                            st.markdown(f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                    
                    # General Formatting Suggestions
                    if analysis.get('format_suggestions'):
                        st.markdown("""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin-bottom: 10px;'>📄 Formatting</h3>
                            <ul style='list-style-type: none; padding-left: 0;'>
                        """, unsafe_allow_html=True)
                        for suggestion in analysis.get('format_suggestions', []):
                            st.markdown(f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>", unsafe_allow_html=True)
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                

                
                # Course Recommendations
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 24px;
                    padding: 2rem;
                    margin: 1rem 0;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                ">
                    <h2>📚 Recommended Courses</h2>
                """, unsafe_allow_html=True)
                
                # Get courses based on role and category
                courses = get_courses_for_role(selected_role)
                if not courses:
                    category = get_category_for_role(selected_role)
                    courses = COURSES_BY_CATEGORY.get(category, {}).get(selected_role, [])
                
                # Display courses in a grid
                cols = st.columns(2)
                for i, course in enumerate(courses[:6]):  # Show top 6 courses
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                            <h4>{course[0]}</h4>
                            <a href='{course[1]}' target='_blank'>View Course</a>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Learning Resources
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 24px;
                    padding: 2rem;
                    margin: 1rem 0;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                ">
                    <h2>📺 Helpful Videos</h2>
                """, unsafe_allow_html=True)
                
                tab1, tab2 = st.tabs(["Resume Tips", "Interview Tips"])
                
                with tab1:
                    # Resume Videos
                    for category, videos in RESUME_VIDEOS.items():
                        st.subheader(category)
                        cols = st.columns(2)
                        for i, video in enumerate(videos):
                            with cols[i % 2]:
                                st.video(video[1])
                
                with tab2:
                    # Interview Videos
                    for category, videos in INTERVIEW_VIDEOS.items():
                        st.subheader(category)
                        cols = st.columns(2)
                        for i, video in enumerate(videos):
                            with cols[i % 2]:
                                st.video(video[1])
                
                st.markdown("</div>", unsafe_allow_html=True)
                
        # Close the page container
        st.markdown('</div>', unsafe_allow_html=True)

    def render_job_search(self):
        """Render the job search page with company listings"""
        # Apply modern styles
        apply_modern_styles()
        
        # Page Header with modern gradient
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(88, 28, 135, 0.95) 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 1.5rem auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: none;
            width: 100%;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, 
                    rgba(99, 102, 241, 0.15) 0%,
                    rgba(139, 92, 246, 0.15) 50%,
                    rgba(147, 51, 234, 0.15) 100%
                );
                z-index: 1;
            "></div>
            <div style="position: relative; z-index: 2;">
                <h1 style="
                    font-size: 3.2rem;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #9333ea 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 1rem;
                    font-weight: 700;
                ">Job Search</h1>
                <p style="
                    font-size: 1.4rem;
                    color: #94a3b8;
                    margin: 0;
                    line-height: 1.6;
                ">Explore career opportunities with top companies</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Add custom CSS for company cards
        st.markdown("""
        <style>
        .company-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2.5rem;
            padding: 2rem;
            max-width: 1800px;
            margin: 0 auto;
        }

        .company-card {
            background: rgba(15, 23, 42, 0.95);
            border-radius: 24px;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            min-height: 380px;
            margin-bottom: 1rem;
        }

        .company-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
            border-color: rgba(99, 102, 241, 0.3);
        }

        .company-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin: 0 auto 1.5rem;
        }

        .company-name {
            font-size: 1.6rem;
            color: #fff;
            margin: 0 0 1rem 0;
            font-weight: 600;
            line-height: 1.3;
        }

        .company-description {
            color: #94a3b8;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            flex-grow: 1;
        }

        .company-categories {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            justify-content: center;
            margin-bottom: 1.5rem;
            width: 100%;
        }

        .category-tag {
            background: rgba(99, 102, 241, 0.1);
            color: #6366f1;
            padding: 0.4rem 0.8rem;
            border-radius: 50px;
            font-size: 0.85rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .career-link {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white !important;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            text-decoration: none !important;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-block;
            margin-top: auto;
            font-size: 1rem;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .career-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(99, 102, 241, 0.4);
            filter: brightness(110%);
        }
        </style>
        """, unsafe_allow_html=True)

        # Create tabs for different company categories
        tab1, tab2, tab3 = st.tabs(["Tech Giants", "Indian Tech", "Global Corporations"])

        with tab1:
            st.markdown('<div class="company-grid">', unsafe_allow_html=True)
            for company in FEATURED_COMPANIES["tech"]:
                st.markdown(f"""
                <div class="company-card">
                    <i class="{company['icon']} company-icon" style="color: {company['color']}"></i>
                    <h2 class="company-name">{company['name']}</h2>
                    <p class="company-description">{company['description']}</p>
                    <div class="company-categories">
                        {''.join([f'<span class="category-tag">{cat}</span>' for cat in company['categories']])}
                    </div>
                    <a href="{company['careers_url']}" target="_blank" class="career-link">View Careers</a>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="company-grid">', unsafe_allow_html=True)
            for company in FEATURED_COMPANIES["indian_tech"]:
                st.markdown(f"""
                <div class="company-card">
                    <i class="{company['icon']} company-icon" style="color: {company['color']}"></i>
                    <h2 class="company-name">{company['name']}</h2>
                    <p class="company-description">{company['description']}</p>
                    <div class="company-categories">
                        {''.join([f'<span class="category-tag">{cat}</span>' for cat in company['categories']])}
                    </div>
                    <a href="{company['careers_url']}" target="_blank" class="career-link">View Careers</a>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="company-grid">', unsafe_allow_html=True)
            for company in FEATURED_COMPANIES["global_corps"]:
                st.markdown(f"""
                <div class="company-card">
                    <i class="{company['icon']} company-icon" style="color: {company['color']}"></i>
                    <h2 class="company-name">{company['name']}</h2>
                    <p class="company-description">{company['description']}</p>
                    <div class="company-categories">
                        {''.join([f'<span class="category-tag">{cat}</span>' for cat in company['categories']])}
                    </div>
                    <a href="{company['careers_url']}" target="_blank" class="career-link">View Careers</a>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    def render_feedback_page(self):
        """Render the feedback page"""
        st.markdown("""
            <style>
            .feedback-header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(90deg, rgba(76, 175, 80, 0.1), rgba(33, 150, 243, 0.1));
                border-radius: 10px;
                margin-bottom: 30px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feedback-header">
                <h1>📣 Your Voice Matters!</h1>
                <p>Help us improve AI Resume Builder & Analyzer with your valuable feedback</p>
            </div>
        """, unsafe_allow_html=True)

        # Initialize feedback manager
        feedback_manager = FeedbackManager()
        
        # Create tabs for form and statistics
        form_tab, stats_tab = st.tabs(["Share Feedback", "Feedback Overview"])
        
        with form_tab:
            feedback_manager.render_feedback_form()
            
        with stats_tab:
            feedback_manager.render_feedback_stats()

    def render_home(self):
        apply_modern_styles()
        
        # Hero Section
        hero_section(
            "AI Resume Builder & Analyzer",
            "Transform your career with AI-powered resume analysis and building. Get personalized insights and create professional resumes that stand out."
        )
        
        # Features Section
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        
        feature_card(
            "fas fa-robot",
            "AI-Powered Analysis",
            "Get instant feedback on your resume with advanced AI analysis that identifies strengths and areas for improvement."
        )
        
        feature_card(
            "fas fa-magic",
            "Smart Resume Builder",
            "Create professional resumes with our intelligent builder that suggests optimal content and formatting."
        )
        
        feature_card(
            "fas fa-chart-line",
            "Career Insights",
            "Access detailed analytics and personalized recommendations to enhance your career prospects."
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

    def render_chatbot(self):
        """Render the chatbot interface"""
        st.title("🤖 Resume Assistant Chatbot")
        st.markdown("---")
        
        # Predefined questions and answers
        faq = {
            "What should I include in my resume?": "Your resume should include: 1) Contact Information, 2) Professional Summary, 3) Work Experience, 4) Education, 5) Skills, 6) Projects, and 7) Certifications if relevant.",
            "How long should my resume be?": "For most professionals, a one-page resume is ideal. If you have extensive experience (10+ years), two pages may be acceptable. Focus on quality over quantity.",
            "What are the most important skills to list?": "Include a mix of technical skills (programming languages, tools) and soft skills (communication, leadership). Tailor them to the job you're applying for.",
            "How should I format my resume?": "Use a clean, professional layout with consistent formatting. Use bullet points for achievements, clear section headings, and a readable font (10-12pt).",
            "Should I include references?": "It's not necessary to include references on your resume. Instead, prepare a separate reference list to provide when requested.",
            "How can I make my resume stand out?": "1) Use action verbs, 2) Quantify achievements, 3) Tailor it to each job, 4) Use keywords from the job description, 5) Keep it visually appealing.",
            "What's the best way to describe my work experience?": "Use the STAR method: Situation, Task, Action, Result. Focus on achievements and impact rather than just responsibilities.",
            "Should I include a photo?": "In most cases, no. Unless specifically requested or common in your industry/country, it's best to avoid including a photo.",
            "How often should I update my resume?": "Update your resume every 6 months or whenever you achieve something significant. Keep it current even when not job searching.",
            "What's the best file format for my resume?": "PDF is generally the best format as it preserves formatting across different devices and operating systems."
        }
        
        # Create two columns
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Frequently Asked Questions")
            for question in faq.keys():
                if st.button(question, use_container_width=True):
                    st.session_state.selected_question = question
        
        with col2:
            st.subheader("Answer")
            if 'selected_question' in st.session_state:
                st.info(faq[st.session_state.selected_question])
            else:
                st.info("Select a question from the left to see the answer.")

    def main(self):
        """Main application entry point"""
        self.apply_global_styles()
        
        # Admin login/logout in sidebar
        with st.sidebar:
            st_lottie(self.load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_xyadoh9h.json"), height=200, key="sidebar_animation")
            st.title("AI Resume Builder & Analyzer")
            st.markdown("---")
            
            # Navigation buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    cleaned_name = page_name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip()
                    st.session_state.page = cleaned_name
                    st.rerun()
        
        # Force home page on first load
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()
        
        # Get current page and render it
        current_page = st.session_state.get('page', 'home')
        
        # Create a mapping of cleaned page names to original names
        page_mapping = {name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").strip(): name 
                       for name in self.pages.keys()}
        
        # Render the appropriate page
        if current_page in page_mapping:
            self.pages[page_mapping[current_page]]()
        else:
            # Default to home page if invalid page
            self.render_home()
    
if __name__ == "__main__":
    app = ResumeApp()
    app.main()
