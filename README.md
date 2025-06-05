# Investment Progress Update Generator

This project generates fresh, motivational, and text-friendly monthly progress updates for clients about their investment goals. It uses in-memory data and AI-powered (or template-based) message generation.

## Features
- In-memory mock database (no setup required)
- Progress calculation and change detection
- Fresh, friendly, and emoji-rich messages
- JSON output, ready for SMS or other delivery

## How to Run
1. Install requirements (none needed for basic version)
2. Run `python main.py`

## Extending to Real AI
- To use OpenAI or another LLM for message generation, install the `openai` package and update `message_generator.py` to call the API. 