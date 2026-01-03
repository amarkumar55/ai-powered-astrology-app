# 🔮 AI-Powered Astrology SaaS Platform

A **production-grade SaaS platform** combining traditional astrology systems with **modern AI capabilities**, built to support subscriptions, payments, live chat, and intelligent content generation at scale.

This platform is designed to serve users with personalized astrological insights, real-time interactions, and AI-powered summaries, while maintaining performance, security, and scalability.

---

## 🚀 Key Features

### 🧠 AI & NLP Capabilities
- **AI-powered text transformation** for astrology interpretations
- **NLP-based summarization** using the **BART model** for concise horoscope, report, and content summaries
- Intelligent content enhancement for blogs, notes, and astrology reports
- AI-assisted **live chat** for user interactions and guidance

---

### 🔭 Astrology Modules
- **Kundli (Birth Chart) Generation**
- **Dasha & Panchang Calculations**
- **Horoscope & Daily Predictions**
- **Numerology & Loshu Grid**
- **Compatibility Analysis**
- **Astrological Reports**

---

### 💬 Communication & Engagement
- **Live Chat System** with real-time messaging
- Blog & content publishing system
- Personalized dashboards for users
- Event-based features (live sessions, recordings)

---

### 💳 Payments & Subscriptions
- Subscription-based access model
- Secure **payment processing**
- Invoice generation and transaction tracking
- Support for recurring plans and premium features

---

### 🛠️ Backend Architecture

- Modular backend structure with clearly separated domains:
  - Authentication & Authorization
  - Payments & Subscriptions
  - AI & NLP services
  - Astrology engines
  - Content & Media handling
- Background jobs for async processing
- Centralized logging and monitoring
- RESTful APIs for frontend and integrations

---

## 🧩 Tech Stack

### Backend
- **Python** (Django)
- **Django REST Framework**
- REST APIs

### AI / NLP
- **Transformer-based models**
- **BART (NLP Summarization)**
- AI-driven text processing & chat workflows

### Database & Caching
- PostgreSQL / MySQL
- Redis (caching & background tasks)

### Frontend
- HTML5, Tailwind CSS
- JavaScript

### Cloud & DevOps
- AWS (EC2, RDS, S3) – Production deployment
- Docker – Containerized application environments
- CI/CD – Automated build and deployment workflows
  
---

## 🚧 Deployment & Infrastructure Notes

This repository focuses on the **application-level implementation**.  
Docker configuration, cloud infrastructure (AWS), and deployment pipelines are managed separately and are not included in this public repository for security and compliance reasons.


## 📂 Project Structure (High-Level) 

## 📂 Project Structure

The project is organized into modular Django apps and directories to ensure scalability, maintainability, and clear separation of concerns.

- **admin_panel/**  
  Handles administrative functionalities such as system management, content moderation, and operational controls.

- **apis/**  
  Exposes RESTful APIs for core application features and third-party integrations.

- **astro/**  
  Main project container and configuration directory for the Astrology SaaS platform.

- **authentication/**  
  Manages user authentication, authorization, and role-based access control (RBAC).

- **blogs/**  
  Handles blog content creation, management, and publishing workflows.

- **chat/**  
  Implements real-time chat functionality, including AI-assisted user interactions.

- **commands/**  
  Contains background jobs and scheduled tasks for automated and asynchronous processing.

- **compatibility/**  
  Manages astrology-based compatibility matching and analysis features.

- **dasha/**  
  Handles Dasha calculation and prediction logic.

- **home/**  
  Manages public-facing landing pages and entry points of the application.

- **horoscope/**  
  Provides daily, weekly, and personalized horoscope generation.

- **payment/**  
  Handles payment processing and transaction workflows.

- **subscription/**  
  Manages subscription plans, recurring billing, and access entitlements.

- **invoice/**  
  Responsible for invoice generation, storage, and transaction records.

- **dashboard/**  
  Implements user dashboards, personalized insights, and account-level views.

- **core/**  
  Contains shared business logic and core components reused across multiple apps.

- **kundli/**  
  Manages Kundli (birth chart) generation along with AI-powered interpretation and summarization.

- **loshugrid/**  
  Handles Loshu Grid generation and numerological analysis.

- **media/**  
  Stores and serves user-uploaded media files.

- **numberlogy/**  
  Manages numerology-related features and calculations.

- **panchang/**  
  Provides Panchang calculations and calendar-based astrological predictions.

- **logs/**  
  Stores application logs for monitoring, debugging, and auditing.

- **static/**  
  Contains static assets used during development.

- **staticfiles/**  
  Holds collected static assets for production deployment.

- **templates/**  
  Manages HTML templates used for server-side rendering.

- **utility/**  
  Contains reusable helper functions and shared utilities.

- **manage.py**  
  Entry point for Django management commands and administrative tasks.


Each module is designed to be **loosely coupled and independently maintainable**, enabling future scalability and feature expansion.

---

## 🔐 Security & Reliability
- Role-based access control (RBAC)
- Secure authentication flows
- Payment-safe architecture
- Centralized error logging
- Production-grade configuration handling

---

## 🎯 Use Cases
- Astrology SaaS platforms
- Subscription-based content services
- AI-assisted knowledge platforms
- Event & webinar-driven applications

---

## 🧑‍💻 Author

**Amar Kumar**  
Senior Backend Engineer  
Specializing in **Laravel, Python, AWS, SaaS systems, and AI-powered backend integrations**

📌 LinkedIn: https://www.linkedin.com/in/amarinfo  
📌 Portfolio: https://www.amaraiverse.com/

---


### 🌍 Data Source Attribution

This project uses data from the [Countries States Cities Database](https://github.com/dr5hn/countries-states-cities-database),  
which is licensed under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/1-0/).  
Individual contents are under the [Database Contents License (DbCL)](https://opendatacommons.org/licenses/dbcl/1-0/).


## 📄 License
This project is licensed under the MIT License.

