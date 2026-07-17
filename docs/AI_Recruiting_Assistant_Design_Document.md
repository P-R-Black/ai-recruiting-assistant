# AI Recruiting Assistant

## Software Architecture & Design Document (Version 1.0)

## 1. Overview

### Goal

Build an AI-powered recruiting assistant that continuously monitors
incoming job opportunities, evaluates them against the user's
experience, recommends the best application strategy, and automates
repetitive application tasks while keeping the user in control of final
submission.

The system is intended to:

-   Reduce time spent reviewing job listings.
-   Increase application quality.
-   Demonstrate modern AI engineering techniques.
-   Serve as a portfolio-quality project.

## Primary Users

Initially: - Me

Future: - Any software engineer searching for jobs

## Design Principles

1.  AI is a service---not the application.
2.  Every AI decision must be explainable.
3.  Human approval before submitting applications.
4.  Modular architecture.
5.  Provider-agnostic AI integration.
6.  Strong typing everywhere.
7.  Background processing over synchronous APIs.
8.  Build features incrementally.

## High-Level Architecture

``` text
                    +----------------+
                    | Gmail API      |
                    +-------+--------+
                            |
                    Email Poll Worker
                            |
                    Job Extraction
                            |
                   AI Classification
                            |
                 Match & Resume Engine
                            |
                   PostgreSQL Database
                            |
                    +-------+--------+
                    |                |
              FastAPI API      Scheduler
                    |
               React Dashboard
                    |
             User Approval Queue
                    |
               Playwright Worker
                    |
             Job Application Site
```

## Technology Stack

### Frontend

-   React
-   Vite
-   TypeScript
-   TanStack Query
-   React Router
-   Tailwind CSS

### Backend

-   FastAPI
-   SQLAlchemy
-   Alembic
-   PostgreSQL

### AI

-   LiteLLM
-   Pydantic AI
-   OpenAI (initial provider)

Future: - Anthropic - Gemini - Local models

### Automation

-   Playwright

### Infrastructure

-   Docker
-   Docker Compose
-   Nginx
-   VPS
-   GitHub Actions

## Core Modules

### Gmail Service

Responsibilities: - Authenticate with Gmail - Poll inbox - Identify job
emails - Avoid duplicate imports

Output: Raw Email → Database

### Email Parser

Responsibilities: - Extract title - Company - Location - Job link -
Description - Salary (if present)

If description isn't present, visit the posting.

Output: ParsedJob

### AI Job Analyzer

**Input** - Job Description - Resume Summary

**Output**

``` json
{
  "role_type": "Frontend",
  "seniority": "Junior",
  "recommended_resume": "frontend",
  "match_score": 92,
  "confidence": 96,
  "should_apply": true,
  "strengths": [],
  "weaknesses": []
}
```

Performs: - Classification - Resume recommendation - Match scoring -
Skill extraction

### Resume Manager

Stores: - Frontend Resume - Backend Resume - Full Stack Resume

Future: - Generate optimized resumes

### Cover Letter Generator

Input: - Job - Resume

Output: - Markdown - PDF

### Dashboard API

Provides: - Jobs - Statistics - Recommendations - Application history -
Analytics

### Playwright Worker

Responsibilities: - Open application - Upload resume - Populate forms -
Pause for approval - Submit

## Database Design

### Job

-   id
-   title
-   company
-   location
-   salary
-   url
-   description
-   source
-   status
-   created_at

### Analysis

-   id
-   job_id
-   match_score
-   confidence
-   role_type
-   seniority
-   recommended_resume
-   strengths
-   weaknesses
-   summary
-   created_at

### Resume

-   id
-   type
-   file_path
-   active

### Application

-   id
-   job_id
-   status
-   submitted_at
-   resume_used
-   cover_letter_path

### Skill

-   id
-   name

### JobSkill

-   job_id
-   skill_id

## Suggested Folder Structure

### Backend

``` text
backend/
├── jobs/
│   ├── api.py
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   └── prompts.py
├── analysis/
├── applications/
├── gmail/
├── resumes/
├── analytics/
├── core/
└── database/
```

### Frontend

``` text
frontend/
├── components/
├── pages/
├── hooks/
├── api/
├── types/
├── layouts/
└── utils/
```

## API Endpoints

### Jobs

-   GET /jobs
-   GET /jobs/{id}
-   POST /jobs/import

### Analysis

-   POST /analysis/{jobId}
-   GET /analysis/{jobId}

### Resume

-   GET /resumes
-   POST /resume/upload

### Applications

-   POST /applications/start
-   POST /applications/submit
-   GET /applications

### Analytics

-   GET /stats

## AI Prompt Strategy

Each prompt should have exactly one responsibility.

Examples: - Extract skills - Recommend a resume - Score candidate fit

Avoid prompts that attempt to solve multiple unrelated tasks.

## Development Roadmap

### Milestone 1

-   Repository
-   Docker Compose
-   FastAPI
-   React
-   PostgreSQL
-   Authentication
-   CI

### Milestone 2

-   Gmail OAuth
-   Polling worker
-   Email storage
-   Duplicate detection
-   Parsing

### Milestone 3

-   Pydantic AI
-   Structured extraction
-   Classification
-   Match scoring
-   Resume recommendation

### Milestone 4

-   Resume management
-   Resume generation
-   Cover letters

### Milestone 5

-   Playwright automation
-   Human approval
-   Submission

### Milestone 6

-   Analytics
-   Outcome tracking
-   Success metrics
-   Dashboard

## Future Enhancements

-   pgvector semantic search
-   Multiple LLM providers
-   Calendar integration
-   Learning from outcomes
-   Multi-user SaaS
-   LangGraph orchestration

## Success Criteria

Version 1.0 should: - Import job emails automatically - Extract
structured job data - Analyze postings with typed AI outputs - Recommend
the best resume - Explain match decisions - Generate interview
preparation - Prepare browser-based applications - Require human
approval - Track outcomes and analytics
