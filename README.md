# 🎙️ EchoStudy — Multimodal AI Study Pack Generator

<div align="center">

```
███████╗ ██████╗██╗  ██╗ ██████╗ ███████╗████████╗██╗   ██╗██████╗ ██╗   ██╗
██╔════╝██╔════╝██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗╚██╗ ██╔╝
█████╗  ██║     ███████║██║   ██║███████╗   ██║   ██║   ██║██║  ██║ ╚████╔╝
██╔══╝  ██║     ██╔══██║██║   ██║╚════██║   ██║   ██║   ██║██║  ██║  ╚██╔╝
███████╗╚██████╗██║  ██║╚██████╔╝███████║   ██║   ╚██████╔╝██████╔╝   ██║
╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝    ╚═╝
```

**Convert Lecture Voice, YouTube Videos, PDF Notes, and Transcripts into Complete Interactive Study Packs in Seconds**

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google GenAI](https://img.shields.io/badge/Google%20GenAI-2.5%20Flash%20%7C%20Pro-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com/)
[![Multimodal](https://img.shields.io/badge/Multimodal-Audio%20%7C%20Video%20%7C%20PDF%20%7C%20Text-6366F1?style=for-the-badge)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-059669?style=for-the-badge)](LICENSE)

### 🌐 [Live Demo → Click Here to Try EchoStudy](https://YOUR-APP-URL.streamlit.app)

> 🔗 **Deployment Link:** `https://YOUR-APP-URL.streamlit.app`
> *(Update this link after deploying on Streamlit Community Cloud)*

---

[✨ Key Features](#-key-features) • [🏗️ Architecture](#️-system-architecture) • [🚀 Quickstart](#-quickstart) • [📖 User Guide](#-user-guide) • [⚙️ Tech Specs](#️-technical-specifications)

</div>

---

## 📌 Executive Summary

**EchoStudy** is an elite academic intelligence platform that bridges the gap between raw, unstructured learning materials and high-yield active recall studying. Built on top of Google's **Gemini Multimodal AI**, EchoStudy digests multi-format academic inputs — including **YouTube video lectures**, **multi-page PDF slides & notes**, **live microphone recordings**, **audio files**, and **raw text** — and instantly transforms them into an integrated, interactive **Study Pack**.

Each generated Study Pack contains:

1. 📖 **A Structured Study Guide** — executive overview, key concept definitions, real-world examples, mathematical formulas, misconceptions to avoid, and high-yield exam tips.
2. 🃏 **8 Active Recall Flashcards** — categorized by difficulty and topic tags, with flip/reveal views, random shuffle, and interactive table editing.
3. 🧠 **An Interactive 5-Question MCQ Quiz** — live scoring, instant feedback, rationale explanations, and comprehensive performance analytics.
4. 📤 **Universal Export Engine** — Anki/Quizlet CSV, full JSON packages, and formatted Markdown for Notion & Obsidian.

---

## ✨ Key Features

### 🎛️ 5 Multi-Modal Ingestion Pipelines

| Mode | Description |
|------|-------------|
| 🎥 **YouTube Link** | Paste any lecture URL — EchoStudy fetches the transcript automatically via captions API |
| 📄 **PDF Notes** | Upload `.pdf` lecture slides or notes — multi-page text extraction via `pypdf` |
| 🎙️ **Live Mic Recording** | Record your voice directly in the browser — transcribed via Gemini Multimodal |
| 📁 **Audio File Upload** | Upload `.mp3`, `.wav`, `.m4a`, `.ogg`, `.webm` audio lectures |
| ✏️ **Type / Paste Notes** | Paste raw notes, textbook summaries, or lecture transcripts directly |

### 🤖 Gemini Resilience & Dynamic Model Discovery
- **Live Model Discovery** — queries Google AI Studio to detect models active on your key
- **Multi-Model Fallback Cascade** — `gemini-2.5-flash → 2.0-flash → 1.5-flash → pro`
- **Auto-Recovery JSON Parser** — cleans and normalizes model output for schema compliance
- **Dual SDK Support** — modern `google-genai` SDK with `google-generativeai` legacy fallback

### 🎨 Professional Light Design System
- Clean white cards, slate-white background (`#f8fafc`), Electric Indigo accents (`#6366f1`)
- Inter + DM Mono typography with strict weight hierarchy
- Animated waveform loader, difficulty pills, metric cards, and responsive layout

### 🧪 1-Click Quick Demos
- ⚡ **Load Sample Notes (OS)** — Process Scheduling: FCFS, SJF, Round Robin, Priority
- 📄 **Load Sample PDF (DBMS ACID)** — Transactions, ACID, Serializability, 2PL, WAL
- 🎥 **Load Sample YouTube (Neural Nets)** — 3Blue1Brown Deep Learning Chapter 1

---

## 🏗️ System Architecture

```
📥 INPUT LAYER
  YouTube URL → Video ID + oEmbed + Captions API
  PDF File    → pypdf Multi-Page Text Extraction
  Mic/Audio   → Browser Audio Capture → Raw Bytes
  Text/Notes  → Direct Text Editor

        ↓

🔄 NORMALIZATION LAYER
  Audio Bytes → MIME Detection → Gemini Transcription
  All Sources → Transcript Text → Session State

        ↓

🧠 GEMINI AI ENGINE
  Dynamic Model Discovery → Best Available Model
  Structured JSON Prompt  → Study Pack Schema
  Fallback Cascade        → Guaranteed Output

        ↓

🛡️ SANITIZATION LAYER
  Markdown Fence Stripper → JSON Parser → Schema Validator

        ↓

📱 OUTPUT TABS
  📖 Study Guide  |  🃏 Flashcards  |  🧠 Quiz  |  📤 Export
```

---

## 🚀 Quickstart

### Prerequisites
- **Python 3.10, 3.11, or 3.12**
- A **Google Gemini API Key** — free from [Google AI Studio](https://aistudio.google.com)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/echostudy-app.git
cd echostudy-app
```

### 2. Create a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
streamlit run app.py
```

Open **`http://localhost:8501`** in your browser.

---

## 📖 User Guide

**Step 1 — API Key:** Enter your Gemini API key in the sidebar under ⚙ Configuration. Models are auto-discovered.

**Step 2 — Choose Input:** Go to the 📥 Input & Generation tab and pick one of the 5 input modes.

**Step 3 — Generate:** Click **⚡ Generate Study Pack**. Full pack generated in ~3–5 seconds.

**Step 4 — Study:**
- **📖 Study Guide** — Overview, concepts, formulas, exam tips
- **🃏 Flashcards** — Flip cards, difficulty filter, shuffle, editable table
- **🧠 Quiz** — 5 MCQ questions with instant scoring and explanations
- **📤 Export** — Download as CSV (Anki/Quizlet), JSON, or Markdown (Notion/Obsidian)

---

## 🗂️ Project Structure

```
echostudy-app/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── DESIGN.md               # Technical design document
└── .streamlit/
    └── config.toml         # Theme & server configuration
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|:--------|:--------|:--------|
| `streamlit` | `>=1.35.0` | Reactive frontend framework |
| `google-genai` | `>=1.0.0` | Google GenAI SDK (Gemini 2.5/2.0/1.5) |
| `google-generativeai` | `>=0.8.3` | Legacy SDK fallback |
| `pypdf` | `>=4.0.0` | PDF text extraction |
| `youtube-transcript-api` | `>=0.6.2` | YouTube caption extraction |
| `requests` | `>=2.31.0` | HTTP & oEmbed metadata |
| `pandas` | `>=2.2.2` | Data manipulation & CSV export |

---

## ⚙️ Technical Specifications

| Capability | Spec |
|:-----------|:-----|
| YouTube | Any video with English captions (auto or manual) |
| PDF | Multi-page standard PDFs up to 50MB |
| Audio | `.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm` up to 200MB |
| Generation Speed | ~2.5–4.5 seconds per Study Pack |
| Output | 8 Flashcards + 5 Quiz Questions + Full Study Guide (guaranteed) |
| Python | 3.10, 3.11, 3.12 |

---

## ☁️ Deployment

This app is deployed on **Streamlit Community Cloud**.

🔗 **Live URL:** [https://YOUR-APP-URL.streamlit.app](https://YOUR-APP-URL.streamlit.app)

To deploy your own instance:
1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → set main file to `app.py`
4. Add `GEMINI_API_KEY` in **Settings → Secrets**
5. Click Deploy ✅

---

## 🛡️ License

Distributed under the **MIT License**.

---

<div align="center">
  <b>EchoStudy AI</b> — Built with ❤️ for Students & Educators Worldwide<br>
  <i>MirAI Capstone Project 2026</i>
</div>
