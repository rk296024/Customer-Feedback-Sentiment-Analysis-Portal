Here's a properly formatted `README.md` file for direct copy-pasting:

```markdown
# Customer Feedback Sentiment Analysis Application

This project is a FastAPI-based application for analyzing user feedback sentiments using the Hugging Face Transformers library and OpenAI API. It integrates with Supabase for data storage and offers an admin interface for sentiment analysis.

## Features
- **Sentiment Analysis**: Analyze feedback sentiments with OpenAI GPT-3.5 API and a local fallback model from Hugging Face.
- **Feedback Storage**: Save user feedback in Supabase and retrieve it for analysis.
- **Admin Panel**: Restricted access to a sentiment analysis dashboard for authorized users.
- **Environment Variables**: Secure API keys with a `.env` file.

## Prerequisites
- Python 3.8+
- [Supabase Account and API Key](https://supabase.com/)
- [OpenAI API Key](https://platform.openai.com/)
- A `.env` file with the required API keys and Supabase URL.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the root directory with the following variables:
   ```plaintext
   OPENAI_API_KEY="your_openai_api_key"
   SUPABASE_URL="your_supabase_url"
   SUPABASE_API_KEY="your_supabase_api_key"
   ```

## Project Structure

```
├── main.py                    # Main FastAPI application
├── templates                  # HTML templates for FastAPI responses
│   ├── index.html             # User feedback submission page
│   ├── admin_analysis.html    # Admin login page
│   └── analysis.html          # Admin analysis dashboard
├── .env                       # Environment variables (not tracked in Git)
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Usage

1. **Run the FastAPI application**:
   ```bash
   uvicorn main:app --reload
   ```
   The application will be available at `http://127.0.0.1:8000`.

2. **Access the feedback submission form**:
   Go to `http://127.0.0.1:8000/` to submit feedback and view stored feedback data.

3. **Admin Analysis**:
   - Go to `http://127.0.0.1:8000/admin_analysis` to log in.
   - The default admin credentials are:
     - **User ID**: `admin`
     - **Password**: `password`

4. **Submit Feedback**:
   - Enter feedback and a user ID on the main page.
   - The feedback will be analyzed, and the sentiment will be stored in Supabase.

## Updating Requirements
To update `requirements.txt` after adding new dependencies:
```bash
pip freeze > requirements.txt
```

