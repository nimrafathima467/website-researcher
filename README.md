# Website Researcher

A website research and summarization tool built with Python and Streamlit.

## Features
- Extract readable text from public webpages.
- Generate basic summaries using rule-based text processing.
- View and download summaries.
- Download extracted webpage text.
- View research history during the current session.
- Use a clean, user-friendly interface.

## Technologies
- Python
- Streamlit
- Requests
- BeautifulSoup4

## Installation

Install the required packages:

```bash
python -m pip install streamlit requests beautifulsoup4
```

## Run the App

```bash
python -m streamlit run app.py
```

## How It Works

The app retrieves publicly accessible webpage content, extracts readable text, and generates a summary using rule-based sentence processing.

## Limitations
Some websites may block automated requests or require JavaScript. Summary quality depends on the extracted webpage text.

## Future Improvements
- Keyword extraction
- Additional download formats
- Improved webpage compatibility
- Optional AI-powered summarization
