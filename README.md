# ChainIntel - AI-Powered Analytics for DePIN Infrastructure

![ChainIntel Banner](https://img.shields.io/badge/DePIN-Analytics-blue) ![Wave 1](https://img.shields.io/badge/Wave-1-green) ![Polygon](https://img.shields.io/badge/Built%20on-Polygon-purple)

**ChainIntel** is the first AI-powered analytics marketplace specifically designed for DePIN (Decentralized Physical Infrastructure) networks. We aggregate data from DIMO, GEODNET, IoTeX, and other networks, apply machine learning models, and deliver actionable insights.

## 🎯 Wave 1 Deliverables (Polygon Buildathon)

This repository contains our **Wave 1 MVP** demonstrating technical feasibility:

✅ **Working data pipeline** - Fetches live data from DIMO Network (140K+ connected vehicles)
✅ **ML forecasting model** - Prophet-based time-series forecasting with 90% confidence intervals
✅ **Interactive dashboard** - Real-time visualization of network metrics and growth predictions
✅ **Professional documentation** - Complete setup instructions and architecture docs
✅ **Demo video** - 3-minute walkthrough (link below)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (optional for Wave 1)

# Run the server
python main.py
```

The backend API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## 📊 Features

### Current (Wave 1)

- **Live DIMO Network Data**: Real-time metrics from 140K+ connected vehicles
- **Historical Analytics**: 90-day network growth visualization
- **ML Forecasting**: 180-day growth predictions using Facebook Prophet
- **Growth Rate Analysis**: Daily, weekly, and monthly growth metrics
- **Interactive Charts**: Beautiful visualizations with Chart.js
- **REST API**: FastAPI backend with auto-generated OpenAPI docs

### Coming Soon (Wave 2+)

- Multi-network support (GEODNET, IoTeX)
- Smart contract marketplace on Polygon
- Geographic distribution maps
- Anomaly detection
- Real-time alerts
- White-label analytics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              ChainIntel Wave 1                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  Data Source: DIMO API (GraphQL)                │
│       ↓                                          │
│  Backend: Python FastAPI + PostgreSQL           │
│       ↓                                          │
│  ML Engine: Prophet (time-series forecasting)   │
│       ↓                                          │
│  Frontend: Next.js 14 + Chart.js + Tailwind     │
│       ↓                                          │
│  Dashboard: Real-time analytics visualization   │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Prophet** - Facebook's time-series forecasting library
- **Supabase** - PostgreSQL database (managed)
- **DIMO Python SDK** - Official SDK for DIMO Network data

### Frontend
- **Next.js 14** - React framework with TypeScript
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Interactive data visualization
- **Axios** - HTTP client

### Infrastructure
- **Polygon Network** - DIMO runs on Polygon for scalability
- **Vercel** - Frontend deployment (planned)
- **Render** - Backend deployment (planned)

## 📁 Project Structure

```
chainintel/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── requirements.txt     # Python dependencies
│   ├── data/
│   │   ├── dimo_client.py   # DIMO API client
│   │   └── database.py      # Supabase database client
│   ├── models/
│   │   └── forecaster.py    # Prophet ML model
│   └── routes/
│       ├── dimo.py          # DIMO endpoints
│       └── analytics.py     # Analytics endpoints
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── index.tsx    # Main dashboard
│   │   ├── components/
│   │   │   ├── StatCard.tsx
│   │   │   ├── LineChart.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── lib/
│   │   │   └── api.ts       # API client
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   └── tsconfig.json
└── docs/
    ├── ARCHITECTURE.md
    ├── API.md
    └── DEPLOYMENT.md
```

## 🔑 API Endpoints

### DIMO Data
- `GET /api/dimo/metrics` - Current network statistics
- `GET /api/dimo/historical?days=90` - Historical data
- `GET /api/dimo/health` - API health check

### Analytics
- `POST /api/analytics/forecast?days_ahead=180` - Generate ML forecast
- `GET /api/analytics/forecast/latest` - Get latest forecast
- `GET /api/analytics/growth-rate` - Growth rate analysis
- `GET /api/analytics/summary` - Comprehensive summary

Full API documentation available at `/docs` when running the backend.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest  # Coming soon
```

### Frontend Tests
```bash
cd frontend
npm test  # Coming soon
```

## 📈 ML Model Details

**Prophet Time-Series Forecasting**

- **Training Data**: 90 days of historical DIMO network metrics
- **Forecast Horizon**: 180 days (configurable)
- **Confidence Level**: 90% intervals
- **Seasonality**: Weekly and yearly patterns detected
- **Validation**: 14-day test set with MAE, RMSE, MAPE metrics

**Key Predictions**:
- 30-day growth forecast
- 90-day growth forecast
- 180-day growth forecast
- Average daily growth rate
- Trend acceleration/deceleration

## 🎥 Demo Video

[Watch the 3-minute demo video](link-to-loom-video)

--- 

## 🗺️ Roadmap (Tentative)


### **Wave 1 (Weeks 1–2) ✅ – Foundation & Proof of Concept**

- [x] Connect to **DIMO API** and fetch live network metrics
- [x] Build backend (FastAPI + Supabase) for data ingestion
* [x] Train **Prophet ML model** for time-series growth forecasting
* [x] Develop **Next.js dashboard** to visualize metrics and forecasts
* [x] Publish GitHub repo with documentation and architecture notes
* [x] Record 3-minute Loom demo (data → ML → dashboard flow)

---

### **Wave 2 (Weeks 3–4) 🚧 – Multi-Network Integration + Marketplace MVP**

* [ ] Add **GEODNET** and **IoTeX** integrations (multi-network data)
* [ ] Implement three ML analytics: growth forecast, anomaly detection, geo-clustering
* [ ] Deploy **Marketplace Smart Contract** on **Polygon testnet** (buy/access logic)
* [ ] Upgrade dashboard for comparative analytics across networks
* [ ] Publish first purchasable analytics demo product

---

### **Wave 3 (Weeks 5–6) 🔒 – Verifiable Analytics (Alpha)**

* [ ] Deploy **AnalyticsRegistry.sol** to store hashed proofs of analytics results on Polygon
* [ ] Prototype **DataStake.sol** for staking verified data providers
* [ ] Add “**Verified on Polygon**” badge to analytics dashboard
* [ ] Automate daily analytics generation (cron/Airflow)
* [ ] Onboard 3–5 DePIN operators for closed beta testing

---

### **Wave 4 (Weeks 7–8) 💼 – Monetization & User Growth**

* [ ] Acquire first paying customer ($500–$2K MRR)
* [ ] Launch **10+ analytics products** (ROI optimizer, churn prediction, etc.)
* [ ] Release API + SDK for developer integrations
* [ ] Publish case study: “How [Network] saved $X using ChainIntel”
* [ ] Prototype **white-label dashboards** for operators

---

### **Wave 5 (Weeks 9–10) 🎤 – Pitch & Fundraise**

* [ ] Prepare investor **pitch deck** with traction metrics
* [ ] Create **demo video** featuring real customer impact
* [ ] Announce partnership with 1 major DePIN network
* [ ] Draft **tokenomics + staking whitepaper**
* [ ] Present at **Polygon Buildathon Demo Day**

---

### **Wave 6 (Weeks 11–12) 🚀 – Post-Funding Scale**

* [ ] Hire backend engineer + BD lead
* [ ] Integrate **10+ DePIN networks** (Helium, Render, Filecoin, Akash)
* [ ] Migrate `AnalyticsRegistry.sol` + `DataStake.sol` to **Polygon mainnet**
* [ ] Expand staking mechanics and verification incentives
* [ ] Reach **10+ paying customers**

---

### **Wave 7 (Weeks 13–14) 🏢 – Enterprise & Compliance**

* [ ] Launch **white-label platform** for enterprise clients
* [ ] Add **custom analytics builder** (self-serve reports)
* [ ] Implement **SOC2 / GDPR** compliance features
* [ ] Establish **enterprise SLA (99.9% uptime)**
* [ ] Secure first enterprise customer ($10K+/month)

---

### **Wave 8 (Weeks 15–16) 🌐 – Cross-Chain Expansion**

* [ ] Add support for **Solana, Base, Arbitrum, Ethereum**
* [ ] Build **cross-chain analytics dashboard**
* [ ] Develop blockchain-agnostic data layer
* [ ] Integrate **20+ DePIN networks**
* [ ] Reach **$50K+ MRR**

---

### **Wave 9 (Weeks 17–18) 🤖 – AI-Powered Optimization**

* [ ] Launch **AI assistant chatbot** (“Ask ChainIntel anything”)
* [ ] Deploy **automated optimization recommendations**
* [ ] Implement **predictive alerts** for maintenance and churn
* [ ] Add **benchmark comparisons** vs competitors
* [ ] Grow to **30+ paying customers**

---

### **Wave 10 (Weeks 19–20) 💰 – Series A Readiness**

* [ ] Achieve **$100K+ MRR** and **40+ customers**
* [ ] Form **5+ strategic partnerships** with major DePIN networks
* [ ] Finalize **Series A pitch deck + financial projections**
* [ ] Expand into **RWA / supply-chain analytics** verticals
* [ ] Demo at **TOKEN2049 / global Polygon stage**

---



## 🤝 Contributing

We're currently in stealth mode for the buildathon, but contributions will be welcome post-Wave 1!

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

Solo developer project for Polygon Buildathon: From Launch to Fundraising

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **Documentation**: [docs/](./docs)
- **DIMO Network**: https://dimo.org
- **Polygon**: https://polygon.technology

## 💡 Vision

ChainIntel aims to become the **Bloomberg Terminal for DePIN infrastructure**. Every network operator will use our analytics to make data-driven decisions about network expansion, node optimization, and infrastructure planning.

**Built on Polygon** for scalability and deep integration with the DePIN ecosystem.

---

**Questions?** Create an issue or contact us at [your-email]

**Building the future of DePIN analytics, one wave at a time.** 🌊
