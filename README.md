# Daily AI Digest 🤖📧

An open-source project that delivers the latest and greatest AI news, research papers, and videos directly to your inbox every day.

## Features
- **Research Papers**: Fetches latest papers from arXiv (cs.AI) with expandable abstracts.
- **Video Updates**: Tracks top AI channels like Two Minute Papers and AI Explained with thumbnails.
- **News**: Curates trending AI stories from Hacker News with preview images.
- **Daily Email**: Sends a beautifully formatted HTML email with rich visual content.
- **Automation**: Runs automatically via GitHub Actions (free for public repos).

## Setup Instructions

### Prerequisites
1. **Gmail App Password**: Enable 2FA on your Google Account and generate an App Password for SMTP access.

### Local Development
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Agent-Sending-Reads-on-AI.git
   cd Agent-Sending-Reads-on-AI
   ```

2. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

4. **Run the script**:
   ```bash
   # Dry run (no email sent, prints to console)
   python main.py --dry-run

   # Send email
   python main.py
   ```

### Configuration
The content sources are defined in `config.yaml`. You can edit this file to:
- Add/Remove arXiv topics (e.g., `cs.LG`, `cs.CV`).
- Add/Remove YouTube channels (Name: ID).
- Add/Remove News keywords.

### GitHub Actions Automation
1. Go to your repository **Settings** -> **Secrets and variables** -> **Actions**.
2. Add the following **Repository secrets**:
   - `EMAIL_USER` (Your Gmail address)
   - `EMAIL_PASS` (Your App Password)
   - `RECIPIENT_EMAIL` (Where to send the digest)
3. The workflow is scheduled to run daily at 8:00 AM UTC. You can also trigger it manually from the "Actions" tab.

## Architecture
- `fetchers/`: Modules to scrape/fetch data from different sources.
- `emailer.py`: Handles HTML template rendering and SMTP transmission.
- `main.py`: Orchestrates the flow.

## License
MIT
