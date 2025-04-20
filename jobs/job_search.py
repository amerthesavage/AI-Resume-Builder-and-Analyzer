import streamlit as st
import requests
from datetime import datetime
import json
import pandas as pd
from .companies import get_featured_companies

# Job Search API Configuration
JOB_SEARCH_API = "https://api.linkedin.com/v2/jobs/search"
JOBSDB_API = "https://api.jobsdb.com/v1/jobs/search"
INDEED_API = "https://api.indeed.com/v2/jobs/search"

def get_job_platforms():
    """Return list of job platforms with their icons and colors"""
    return [
        {
            "name": "LinkedIn",
            "icon": "fab fa-linkedin",
            "color": "#0077B5",
            "api": JOB_SEARCH_API
        },
        {
            "name": "Indeed",
            "icon": "fas fa-search",
            "color": "#2164F3",
            "api": INDEED_API
        },
        {
            "name": "JobsDB",
            "icon": "fas fa-database",
            "color": "#FF6B6B",
            "api": JOBSDB_API
        }
    ]

def render_job_search():
    """Render modern job list interface"""
    st.markdown("""
        <div class="job-list-header">
            <h1>🌟 Featured Jobs</h1>
            <p class="subtitle">Discover exciting opportunities</p>
        </div>
    """, unsafe_allow_html=True)

    # Sample job data
    jobs = [
        {
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "type": "Full-time",
            "posted": "2 days ago",
            "description": "Looking for an experienced software engineer to join our team...",
            "salary": "$120,000 - $150,000",
            "platform": "LinkedIn"
        },
        {
            "title": "Product Manager",
            "company": "InnovateX",
            "location": "New York, NY",
            "type": "Full-time",
            "posted": "1 day ago",
            "description": "Lead product development and strategy for our new platform...",
            "salary": "$130,000 - $160,000",
            "platform": "Indeed"
        },
        {
            "title": "Data Scientist",
            "company": "DataFlow",
            "location": "Remote",
            "type": "Full-time",
            "posted": "3 days ago",
            "description": "Join our data science team to build innovative ML models...",
            "salary": "$110,000 - $140,000",
            "platform": "LinkedIn"
        }
    ]

    # Display jobs in a modern list
    for job in jobs:
        st.markdown(f"""
            <div class="job-box">
                <div class="job-box-content">
                    <div class="job-box-header">
                        <h3>{job['title']}</h3>
                        <span class="job-type">{job['type']}</span>
                    </div>
                    <div class="job-box-company">
                        <i class="fas fa-building"></i>
                        {job['company']}
                    </div>
                    <div class="job-box-details">
                        <span><i class="fas fa-map-marker-alt"></i> {job['location']}</span>
                        <span><i class="fas fa-dollar-sign"></i> {job['salary']}</span>
                        <span><i class="fas fa-clock"></i> {job['posted']}</span>
                    </div>
                    <p class="job-box-description">{job['description']}</p>
                    <div class="job-box-footer">
                        <span class="platform-badge">{job['platform']}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def perform_job_search(job_title, location, experience_level, job_types):
    """Perform job search across multiple platforms"""
    # This is a placeholder for actual API integration
    # In a real implementation, you would call the respective APIs
    return [
        {
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "type": "Full-time",
            "posted": "2 days ago",
            "description": "Looking for an experienced software engineer...",
            "salary": "$120,000 - $150,000",
            "platform": "LinkedIn",
            "url": "https://linkedin.com/jobs/view/123456"
        },
        # Add more sample jobs
    ]

def display_job_results(jobs):
    """Display job search results in a modern card layout"""
    for job in jobs:
        st.markdown(f"""
            <div class="job-card">
                <div class="job-header">
                    <h3>{job['title']}</h3>
                    <span class="job-type">{job['type']}</span>
                </div>
                <div class="job-company">
                    <i class="fas fa-building"></i>
                    {job['company']}
                </div>
                <div class="job-details">
                    <span><i class="fas fa-map-marker-alt"></i> {job['location']}</span>
                    <span><i class="fas fa-dollar-sign"></i> {job['salary']}</span>
                    <span><i class="fas fa-clock"></i> {job['posted']}</span>
                </div>
                <p class="job-description">{job['description']}</p>
                <div class="job-footer">
                    <span class="platform-badge">{job['platform']}</span>
                    <a href="{job['url']}" target="_blank" class="apply-button">Apply Now</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

def display_featured_companies():
    """Display featured companies in a modern grid layout"""
    companies = [
        {
            "name": "Google",
            "logo": "https://logo.clearbit.com/google.com",
            "description": "World's leading technology company",
            "openings": "150+",
            "website": "https://careers.google.com"
        },
        {
            "name": "Microsoft",
            "logo": "https://logo.clearbit.com/microsoft.com",
            "description": "Global technology leader",
            "openings": "200+",
            "website": "https://careers.microsoft.com"
        },
        # Add more companies
    ]

    cols = st.columns(3)
    for idx, company in enumerate(companies):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="company-card">
                    <img src="{company['logo']}" alt="{company['name']}" class="company-logo">
                    <h3>{company['name']}</h3>
                    <p>{company['description']}</p>
                    <div class="company-stats">
                        <span><i class="fas fa-briefcase"></i> {company['openings']} Openings</span>
                    </div>
                    <a href="{company['website']}" target="_blank" class="company-link">View Careers</a>
                </div>
            """, unsafe_allow_html=True)
