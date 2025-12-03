# Discord AI Ticket Bot

A smart Discord bot that manages support tickets and uses AI to automatically respond to user inquiries.

## 🚀 Features

- **AI-Powered Responses**: Uses LLMs (via `litellm`) to provide intelligent answers to support queries.
- **Ticket Management**: Automated system for opening and managing support tickets.
- **Knowledge Base**: (In Development) Can use custom knowledge to answer questions.
- **Development Mode**: easy testing and debugging commands.

## 🛠️ Tech Stack

- **Python 3.12+**
- **Py-Cord**: For Discord API interactions.
- **LiteLLM**: For interfacing with various LLM providers.
- **Pydantic**: For robust settings management.

## 📦 Getting Started

1. **Clone the repository**

2. **Install dependencies**
   Using `uv` (recommended) or pip:

   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory:

   ```env
   DISCORD_BOT_TOKEN=your_token_here
   DEV_MODE=true # Optional
   ```

4. **Run the Bot**
   ```bash
   python main.py
   ```

## 📝 Usage

- Use `/button` (development command) to spawn the ticket creation panel.
- Users can click "Open Support Ticket" to start a private thread/channel.
- The AI agent will attempt to assist with the user's inquiry.
