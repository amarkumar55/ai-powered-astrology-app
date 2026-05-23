# 🔮 AI-Powered Astrology SaaS Platform
### Production-grade subscription SaaS · Django · FastAPI · BART NLP · AWS · Real-time Chat

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-REST_Framework-092E20?style=flat-square&logo=django)
![AWS](https://img.shields.io/badge/AWS-EC2_RDS_S3-FF9900?style=flat-square&logo=amazonaws)
![Redis](https://img.shields.io/badge/Redis-Caching_&_Queues-DC382D?style=flat-square&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-Restricted-red?style=flat-square)

> A full-lifecycle SaaS backend built from scratch — combining traditional astrology engines with AI-powered personalization, real-time chat, and production-grade subscription billing.

---

## 🎯 What This Platform Does

Most astrology apps are static content. This platform is a dynamic, AI-augmented SaaS — delivering personalized predictions, real-time interactions, and intelligent content generation, all backed by a modular, scalable backend I designed and owned end-to-end.

---

## ✨ Core Capabilities

### 🤖 AI & NLP
- Transformer-based text summarization using **BART** — powers horoscope reports, blog summaries, and personalized content
- AI-assisted **live chat** with intelligent conversational workflows
- Domain-specific content enhancement for astrology interpretations

### 🔭 Astrology Engine
- Kundli (Birth Chart) generation with AI-powered interpretation
- Dasha predictions, Panchang calculations, daily Horoscope
- Numerology & Loshu Grid analysis
- Compatibility matching and astrological reports

### 💳 Payments & Subscriptions
- Subscription state machine — trial → paid → cancellation with automated transitions
- Recurring billing, invoice generation, and transaction tracking
- Idempotent payment processing with webhook-driven sync and failure recovery
- Premium feature access control via subscription entitlements

### 💬 Communication & Engagement
- Real-time live chat system with AI-assisted workflows
- Blog and content publishing with AI summarization
- Personalized user dashboards and account-level views
- Live sessions, webinars, and recorded content delivery

### 🛡️ Security & Reliability
- Role-based access control (RBAC) with JWT authentication
- Payment-safe idempotent architecture
- Centralized logging, error monitoring, and audit trails
- Production-grade configuration and secret management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER (DRF)                          │
│   Authentication · Subscriptions · Astrology · Chat · Content   │
└────────────┬──────────────────────────────────────┬────────────┘
             │                                      │
    ┌────────▼────────┐                   ┌────────▼────────┐
    │   Core Services │                   │   AI / NLP      │
    │  Kundli · Dasha │                   │  BART · Chat    │
    │  Panchang · etc │                   │  Summarization  │
    └────────┬────────┘                   └────────┬────────┘
             │                                      │
    ┌────────▼──────────────────────────────────────▼────────┐
    │              Data & Infrastructure Layer                 │
    │   PostgreSQL · Redis (cache + queues) · Background Jobs  │
    │           AWS (EC2, RDS, S3) · Docker · CI/CD           │
    └─────────────────────────────────────────────────────────┘
```

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · Django · Django REST Framework |
| AI / NLP | BART Transformer · Hugging Face · AI chat workflows |
| Database | PostgreSQL · MySQL |
| Caching & Queues | Redis |
| Cloud | AWS (EC2, RDS, S3) |
| DevOps | Docker · CI/CD pipelines |
| Auth | JWT · RBAC |
| Frontend (supporting) | HTML5 · Tailwind CSS · JavaScript |

---

## 📁 Project Structure

```
astro/                          # Main project config
├── authentication/             # JWT auth, RBAC, session management
├── apis/                       # Unified RESTful API layer
├── kundli/                     # Birth chart generation + AI interpretation
├── dasha/                      # Dasha prediction engine
├── panchang/                   # Panchang & calendar calculations
├── horoscope/                  # Daily/weekly horoscope generation
├── compatibility/              # Compatibility matching & analysis
├── numberlogy/                 # Numerology & Loshu Grid
├── payment/                    # Payment processing & webhook handling
├── subscription/               # Subscription plans, billing, entitlements
├── invoice/                    # Invoice generation & transaction records
├── chat/                       # Real-time chat + AI-assisted workflows
├── blogs/                      # Content publishing & AI summarization
├── dashboard/                  # Personalized user dashboards
├── commands/                   # Background jobs & scheduled tasks
├── core/                       # Shared business logic & reusable utilities
├── admin_panel/                # System management & content moderation
├── utility/                    # Helper functions & shared utilities
└── manage.py
```

Each module is **loosely coupled and independently maintainable** — designed for scale from day one.

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/amarkumar55/ai-astrology-saas.git
cd ai-astrology-saas

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your DB, Redis, AWS, and API credentials

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

---

## 🚧 Deployment Notes

Docker configuration, AWS infrastructure, and CI/CD pipelines are managed separately and excluded from this public repository for security and compliance reasons.

The application is production-deployed on **AWS (EC2, RDS, S3)** with containerized environments via **Docker** and automated deployment via **CI/CD pipelines**.

---

## 🌍 Data Attribution

Country/state/city data sourced from the [Countries States Cities Database](https://github.com/dr5hn/countries-states-cities-database), licensed under [ODbL](https://opendatacommons.org/licenses/odbl/1-0/).

---

## 👤 Author

**Amar Kumar** — Senior Backend Engineer · IBM Certified AI Engineer  
Specializing in distributed systems, AI-powered SaaS backends, and production-scale Python architecture.

📌 [LinkedIn](https://www.linkedin.com/in/amarkumar241429017) ·  💻 [GitHub](https://github.com/amarkumar55)

---

## 📄 License

This project is licensed under a **restrictive license**.  
Commercial use, redistribution, or modification is not permitted without prior written authorization.

---

*Built to demonstrate full product lifecycle ownership — from system design to production deployment.*
