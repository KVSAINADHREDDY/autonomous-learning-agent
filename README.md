# 🎓 Autonomous Learning Agent

An AI-powered learning assistant that uses **Checkpoint Verification** and **Feynman Pedagogy** to help you master any topic.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📚 **Smart Context Gathering** | Automatically searches and aggregates learning materials |
| 🎯 **Quiz Generator** | Creates MCQ quizzes to test your understanding |
| 📝 **Flashcard Creator** | Generates study flashcards from key concepts |
| 🧠 **Feynman Explanations** | Simplifies complex topics using Feynman technique |
| 💬 **Chat with Summary** | Ask questions about generated summaries |
| 📥 **Export Options** | Download summaries as Markdown |
| 🌙 **Modern UI** | Premium dark/light dashboard interface |

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/springboardmentor123455-maker/Designing-an-Autonomous-Learning-Agent-with-Checkpoint-Verification-and-Feynman-Pedagogy-.git
   cd Designing-an-Autonomous-Learning-Agent-with-Checkpoint-Verification-and-Feynman-Pedagogy-
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

### Required API Keys

| Key | Provider | Purpose |
|-----|----------|---------|
| `GROQ_API_KEY` | [Groq](https://console.groq.com) | LLM for quiz/flashcard generation (Free tier) |
| `SERPAPI_API_KEY` | [SerpAPI](https://serpapi.com) | Web search for context gathering |
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com) | Alternative LLM provider (optional) |

## ☁️ Deploy to Streamlit Cloud

1. **Push your code to GitHub** (already done ✅)

2. **Go to [Streamlit Cloud](https://share.streamlit.io)**

3. **Click "New app"** and select your repository

4. **Configure app settings:**
   - Main file path: `streamlit_app.py`
   - Python version: 3.9+

5. **Add Secrets** (in app settings → Secrets):
   ```toml
   MODEL_PROVIDER = "groq"
   GROQ_API_KEY = "your_groq_api_key"
   SERPAPI_API_KEY = "your_serpapi_key"
   SEARCH_PROVIDER = "serpapi"
   ```

6. **Deploy!** 🚀

## 📁 Project Structure

```
├── streamlit_app.py      # Main Streamlit application
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── .streamlit/           # Streamlit configuration
│   └── config.toml       # Theme and server settings
├── src/
│   ├── models/           # Data models (Checkpoint, State)
│   ├── graph/            # LangGraph workflow
│   ├── nodes/            # Workflow nodes
│   └── services/         # External services (LLM, Search)
└── tests/                # Test files
```

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Workflow:** LangGraph
- **LLM:** Groq (Llama 3.3 70B) / OpenAI GPT-4
- **Search:** SerpAPI / DuckDuckGo
- **Language:** Python 3.9+

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ using LangGraph and Streamlit</p>
