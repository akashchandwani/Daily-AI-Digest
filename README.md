# Daily AI Digest 🤖📧

An open-source project that delivers the latest and greatest AI news, research papers, and videos directly to your inbox every day.

## Features
- **Research Papers**: Fetches latest papers from arXiv (cs.AI) with expandable abstracts.
- **Video Updates**: Tracks top AI channels like Two Minute Papers and AI Explained with thumbnails.
- **News**: Curates trending AI stories from Hacker News with preview images.
- **Daily Email**: Sends a beautifully formatted HTML email with rich visual content.
- **Automation**: Runs automatically via GitHub Actions (free for public repos).

## Setup Instructions

### 1. Google App Password (Required)
To send emails via Gmail, you need an **App Password**:
1. Go to your [Google Account](https://myaccount.google.com/).
2. Select **Security**.
3. Under "Signing in to Google," select **2-Step Verification**.
4. At the bottom of the page, select **App passwords**.
5. Enter a name (e.g., "Daily AI Digest") and click **Create**.
6. **Copy the 16-character password**. You will need this for `EMAIL_PASS`.

### 2. GitHub Secrets (For Automation)
To run this automatically on GitHub:
1. Go to your repository on GitHub.
2. Click **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret**.
4. Add the following secrets:
   - `EMAIL_USER`: Your Gmail address (e.g., `youremail@gmail.com`).
   - `EMAIL_PASS`: The 16-character App Password you generated above.
   - `RECIPIENT_EMAIL`: The email address where you want to receive the digest.

### 3. Local Development (Optional)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Daily-AI-Digest.git
   cd Daily-AI-Digest
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
- Add/Remove RSS feeds.

## Architecture
- `fetchers/`: Modules to scrape/fetch data from different sources.
- `emailer.py`: Handles HTML template rendering and SMTP transmission.
- `main.py`: Orchestrates the flow.

## License
MIT
