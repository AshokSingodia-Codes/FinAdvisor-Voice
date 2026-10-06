# 💹 FinAdvisor Voice — Frontend

> AI-powered financial advisor with voice input, conversational memory, and hybrid RAG-backed answers. Built with **React 19 + TypeScript + Vite + Tailwind CSS v4**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running Locally](#running-locally)
- [Available Scripts](#available-scripts)
- [Components](#components)
- [Context & State Management](#context--state-management)
- [API Integration](#api-integration)
- [Deployment](#deployment)
  - [Vercel (Recommended)](#vercel-recommended)
  - [Manual Build](#manual-build)
- [Linting](#linting)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **FinAdvisor Voice** frontend is a single-page chat application that connects to a FastAPI backend powered by a **Hybrid Graph-RAG** pipeline. Users can:

- 🔐 **Sign up / Log in** with JWT-authenticated sessions
- 💬 **Chat** with an AI financial advisor using Markdown-rendered responses
- 🎙️ **Use voice input** via the Web Speech API
- 🗂️ **Browse conversation history** through a persistent sidebar
- 📊 Get answers grounded in real financial documents (10-K filings, transaction data)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 19 |
| Language | TypeScript ~6.0 |
| Build Tool | Vite 8 |
| Styling | Tailwind CSS v4 (via `@tailwindcss/vite` plugin) |
| Icons | Lucide React |
| Markdown | `react-markdown` + `remark-gfm` |
| Linter | OxLint |
| Deployment | Vercel |

---

## Project Structure

```
frontend/
├── public/                         # Static assets
├── src/
│   ├── assets/                     # Images, SVGs
│   ├── components/
│   │   ├── AuthModal.tsx           # Sign-up / Login modal
│   │   ├── ChatMessageItem.tsx     # Individual chat bubble (Markdown rendered)
│   │   ├── ConversationSidebarItem.tsx  # Sidebar conversation list item
│   │   ├── LoginPage.tsx           # Full landing / login page
│   │   └── VoiceInputButton.tsx    # Microphone button (Web Speech API)
│   ├── context/
│   │   └── AuthContext.tsx         # Global auth state (JWT token, user info)
│   ├── App.tsx                     # Root component — routing & main chat UI
│   ├── App.css                     # App-level styles
│   ├── config.ts                   # API base URL configuration
│   ├── index.css                   # Global Tailwind entry
│   └── main.tsx                    # React DOM entry point
├── .env.development                # Dev environment variables
├── .env.production                 # Production environment variables
├── .oxlintrc.json                  # OxLint configuration
├── vercel.json                     # Vercel SPA rewrite rules
├── vite.config.ts                  # Vite + Tailwind plugin config
├── tsconfig.json                   # TypeScript project references
├── tsconfig.app.json               # App TypeScript config
└── package.json
```

---

## Getting Started

### Prerequisites

| Tool | Minimum Version |
|---|---|
| Node.js | 18.x or later |
| npm | 9.x or later |
| Backend API | Running on `http://localhost:8000` |

> **Backend required:** This frontend is a thin client; all AI/RAG logic lives in the FastAPI backend. Clone and run the backend before starting the frontend.

---

### Installation

```bash
# Clone the repository (if not already done)
git clone <repo-url>
cd frontend

# Install dependencies
npm install
```

---

### Environment Variables

The app uses Vite's built-in env system. Variables **must** be prefixed with `VITE_`.

| Variable | Description | Default (dev) |
|---|---|---|
| `VITE_API_BASE` | Base URL of the FastAPI backend | `http://localhost:8000` |

**`.env.development`** (local dev):
```env
VITE_API_BASE=http://localhost:8000
```

**`.env.production`** (production build):
```env
VITE_API_BASE=https://finadvisor-voice.onrender.com
```

> ℹ️ If `VITE_API_BASE` is not set, `src/config.ts` auto-detects `localhost` and falls back to `http://127.0.0.1:8000`, or uses the production Render URL otherwise.

---

### Running Locally

```bash
# Step 1: Start the backend (from the repo root)
cd ..
uvicorn main:app --reload --port 8000

# Step 2: Start the frontend dev server
cd frontend
npm run dev
```

The app will be available at **http://localhost:5173** with Hot Module Replacement (HMR) enabled.

---

## Available Scripts

```bash
npm run dev        # Start Vite dev server (HMR enabled)
npm run build      # Type-check + production build → /dist
npm run preview    # Serve the production /dist build locally
npm run lint       # Run OxLint static analysis
```

---

## Components

### `LoginPage.tsx`
Full-page landing screen shown to unauthenticated users. Contains branding, feature highlights, and entry points to the auth modal.

### `AuthModal.tsx`
Handles both **Sign Up** and **Log In** flows. Calls the backend `/auth/register` and `/auth/login` endpoints, stores the JWT in `AuthContext`.

### `ChatMessageItem.tsx`
Renders a single message bubble in the chat thread. Supports:
- `user` and `assistant` roles with distinct styling
- Full **GitHub Flavored Markdown** via `react-markdown` + `remark-gfm`
- Code block syntax highlighting
- Tables, blockquotes, lists

### `ConversationSidebarItem.tsx`
A clickable sidebar entry for a past conversation. Shows the conversation title/preview and supports rename/delete actions.

### `VoiceInputButton.tsx`
Microphone button that uses the browser's **Web Speech API** (`webkitSpeechRecognition`). Transcribed text is injected into the chat input.

> ⚠️ Voice input requires a modern Chromium-based browser (Chrome, Edge). Firefox is not supported.

---

## Context & State Management

### `AuthContext.tsx`

Provides global authentication state throughout the app tree.

```tsx
// Available values from useAuth()
const { user, token, login, logout, isLoading } = useAuth();
```

| Value | Type | Description |
|---|---|---|
| `user` | `User \| null` | Logged-in user object |
| `token` | `string \| null` | JWT access token |
| `login(token, user)` | `function` | Persist auth state |
| `logout()` | `function` | Clear auth state |
| `isLoading` | `boolean` | Initial auth check in progress |

The token is persisted to `localStorage` and rehydrated on page load.

---

## API Integration

All API calls use the base URL from `src/config.ts`.

```ts
// src/config.ts
export const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000'
    : 'https://finadvisor-voice.onrender.com');
```

### Key Endpoints Used

| Endpoint | Method | Auth Required | Description |
|---|---|---|---|
| `/auth/register` | `POST` | No | Create new user account |
| `/auth/login` | `POST` | No | Login, receive JWT |
| `/chat` | `POST` | Yes | Send message, receive AI response |
| `/conversations` | `GET` | Yes | List all user conversations |
| `/conversations/:id` | `GET` | Yes | Load a specific conversation |
| `/conversations/:id` | `DELETE` | Yes | Delete a conversation |

All protected endpoints require:
```
Authorization: Bearer <JWT_TOKEN>
```

---

## Deployment

### Vercel (Recommended)

The `vercel.json` configures SPA fallback routing so React Router handles all paths:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Steps:**

1. Push your code to GitHub
2. Import the repository in [Vercel](https://vercel.com)
3. Set **Root Directory** to `frontend`
4. Add environment variable: `VITE_API_BASE = https://your-backend.onrender.com`
5. Deploy — Vercel auto-runs `npm run build`

---

### Manual Build

```bash
npm run build
# Output is in /dist — serve with any static host (Nginx, S3, etc.)
```

For Nginx, add SPA fallback:
```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

---

## Linting

This project uses [OxLint](https://oxc.rs/docs/guide/usage/linter) — a fast Rust-based linter.

```bash
npm run lint
```

Configuration in `.oxlintrc.json`:
```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": { "typeAware": true },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `CORS error` in browser console | Ensure backend has `http://localhost:5173` in its `CORS_ORIGINS` env var |
| Blank page after `npm run build` | Check `vercel.json` rewrites are in place for SPA routing |
| Voice input not working | Use Chrome or Edge — Firefox lacks `webkitSpeechRecognition` |
| `401 Unauthorized` on API calls | JWT token expired — log out and log back in |
| Backend not reachable | Confirm FastAPI is running on port `8000` and `VITE_API_BASE` is set correctly |
| Type errors during build | Run `npm run lint` first; ensure TypeScript version matches `~6.0.2` |

---

## Related

- 📦 **Backend README** — [`../README.md`](../README.md)
- 🐳 **Docker Compose** — [`../docker-compose.yml`](../docker-compose.yml)
- 🚀 **Render Deployment** — [`../render.yaml`](../render.yaml)
- 📊 **System Health Report** — [`../reports/SYSTEM_HEALTH_AND_IMPROVEMENT_PLAN.md`](../reports/SYSTEM_HEALTH_AND_IMPROVEMENT_PLAN.md)

---

<p align="center">Made with ❤️ &nbsp;·&nbsp; FinAdvisor Voice &nbsp;·&nbsp; React 19 + Vite + Tailwind CSS v4</p>
