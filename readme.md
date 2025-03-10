# PubSub Emulator UI with AI Features

A Streamlit-based UI for Google Cloud Pub/Sub emulator with AI-powered message analysis capabilities.

## Features

- Project and Topic Management
- Subscription Creation and Management
- Message Publishing and Viewing
- AI-Enhanced Features:
  - Message content type detection
  - Structure validation
  - Sentiment analysis
  - Pattern recognition across messages

## Setup

### Using Docker Compose

1. Start the services:
```bash
docker-compose up -d
```

This will start:
- PubSub Emulator on port 8681
- Streamlit UI on port 8501

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the PubSub emulator:
```bash
docker run -p 8681:8681 messagebird/gcloud-pubsub-emulator:latest
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

### Using uvx

Run directly from GitHub:
```bash
uvx --from git+https://github.com/yourusername/pubsub-emulator-ui pubsub-emulator-ui
```

Or after cloning:
```bash
uvx pubsub-emulator-ui
```

## Usage

1. Enter a project ID in the sidebar
2. Create or select a topic
3. Create subscriptions for your topics
4. Publish messages and view them with AI-powered analysis

## Project Structure

- `app.py`: Main Streamlit application
- `pubsub_client.py`: PubSub emulator client
- `message_analyzer.py`: AI-powered message analysis
- `storage.py`: Local storage for project persistence

## Environment Variables

- `PUBSUB_EMULATOR_HOST`: PubSub emulator host (default: localhost:8681)

## Development

The project uses:
- Streamlit for UI
- google-cloud-pubsub for PubSub operations
- Transformers for NLP tasks
- Pandas & Plotly for visualizations
