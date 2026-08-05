# Multi-Agent Financial Equity Research Analyst

An AI-driven multi-agent system designed to automate financial equity research. This project leverages **LangGraph** to coordinate specialized AI agents that ingest financial data, analyze market sentiment, evaluate ratios, and perform DCF (Discounted Cash Flow) valuations. The results are synthesized into a comprehensive equity research report.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for data ingestion, ratio analysis, market sentiment, valuation, and red flag detection.
- **Human-in-the-Loop (HITL)**: Support for a "verified" run mode where human review is required before the final synthesis.
- **Automated Valuation Models**: Computes Discounted Cash Flow (DCF) with sensitivity analysis.
- **Fact-checking & Citation**: Built-in guardrails to verify claims and ensure citations are supported by SEC filings and news.
- **Export Options**: Automatically generates beautifully formatted PDF and Markdown reports.
- **Modern Web Interface**: React + Vite + TailwindCSS frontend with Server-Sent Events (SSE) for real-time node execution tracking.

## 🧠 LangGraph Architecture

The backend utilizes LangGraph to orchestrate the research process:

1. **Ingestion Node**: Fetches historical data, financials, SEC filings (via EDGAR), and news (via Alpha Vantage).
2. **Parallel Analysis**:
   - `Ratio Agent`: Calculates and analyzes key financial ratios.
   - `Sentiment Agent`: Analyzes recent news and filings for market sentiment.
   - `Valuation Agent`: Performs DCF valuation based on base, bull, and bear scenarios.
3. **Fan-In & Red Flag Detection**: Aggregates parallel results and flags potential investment risks.
4. **Human Review (Optional)**: Halts execution to allow analysts to review or override red flags.
5. **Synthesis**: Compiles the findings into a structured report and verifies claims against sources.

## 💻 Tech Stack

**Backend**
- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) (REST API & SSE)
- [LangGraph](https://python.langchain.com/docs/langgraph) (Agent Orchestration)
- [OpenRouter](https://openrouter.ai/) / Llama 3 (LLM routing)
- yfinance & Alpha Vantage (Financial Data)

**Frontend**
- [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- [Tailwind CSS 4](https://tailwindcss.com/)
- Recharts (Data Visualization)
- Lucide React (Icons)

## 📸 Screenshots

*(Replace with actual screenshots of the application)*

- **Dashboard:** `![Dashboard Screenshot](./docs/images/dashboard.png)`
- **Node Execution Trace:** `![Execution Trace](./docs/images/execution.png)`
- **Exported PDF Report:** `![PDF Report](./docs/images/pdf-report.png)`

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose (Recommended)
- [Node.js 18+](https://nodejs.org/) (for local frontend development)
- [Python 3.10+](https://www.python.org/) (for local backend development)

### Environment Variables

Create a `.env` file in the `equity-research-backend` directory based on `.env.example`:

```env
OPENROUTER_API_KEY="your_openrouter_api_key_here"
LLM_MODEL="meta-llama/llama-3.3-70b-instruct:free"
ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key_here"
LANGSMITH_API_KEY="your_langsmith_api_key_here"
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=equity-research-analyst
SEC_EDGAR_USER_AGENT="Your Name your.email@example.com"
```

### 🐳 Running with Docker (Recommended)

From the project root directory, run:

```bash
docker-compose up --build
```
- The **Frontend** will be available at [http://localhost:5173](http://localhost:5173)
- The **Backend API** will be available at [http://localhost:8000](http://localhost:8000)

### 💻 Running Locally (Without Docker)

#### 1. Backend Setup
```bash
cd equity-research-backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

#### 2. Frontend Setup
```bash
cd equity-research-frontend
npm install
npm run dev
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
