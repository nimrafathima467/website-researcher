
import re
from urllib.parse import urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Website Research Assistant",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "research_history" not in st.session_state:
    st.session_state.research_history = []

if "research_result" not in st.session_state:
    st.session_state.research_result = None


# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F7FC;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E4EAF3;
    }

    .hero {
        background: linear-gradient(120deg, #10213A, #2457A7);
        padding: 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
    }

    .hero .eyebrow {
        color: #BFD7FF;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .hero h1 {
        color: white;
        font-size: 36px;
        margin: 12px 0;
    }

    .hero p {
        color: #E3ECFA;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-label {
        color: #2457A7;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }

    div.stButton > button {
        background: #2457A7;
        color: white;
        border: 1px solid #2457A7;
        border-radius: 10px;
        min-height: 44px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background: #183F80;
        border-color: #183F80;
        color: white;
    }

    div.stDownloadButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 10px;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 10px;
    }

    .footer-note {
        color: #64748B;
        font-size: 12px;
        text-align: center;
        padding: 24px 0 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">YOUR PERSONAL RESEARCH WORKSPACE</div>
        <h1>🔎 Website Research Assistant</h1>
        <p>
            Turn public webpages into readable summaries.
            Extract content, organize your research, and download results.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SUMMARY FUNCTION
# --------------------------------------------------

def summarize_text(text, sentence_limit=5):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip().split()) >= 5
    ]

    if not sentences:
        return "Not enough text to summarize."

    stop_words = {
        "the", "and", "for", "are", "was", "were", "with",
        "that", "this", "from", "you", "your", "has", "have",
        "had", "but", "not", "can", "will", "into", "its",
        "a", "an", "of", "to", "in", "on", "is", "it", "as",
        "at", "by", "or", "be", "we", "our", "they", "their",
        "which", "who", "what", "when", "where", "how",
    }

    frequencies = {}

    for word in re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()):
        if word not in stop_words:
            frequencies[word] = frequencies.get(word, 0) + 1

    scored = []

    for index, sentence in enumerate(sentences):
        words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
        useful_words = [
            word for word in words if word not in stop_words
        ]

        score = (
            sum(frequencies.get(word, 0) for word in useful_words)
            / len(useful_words)
            if useful_words
            else 0
        )

        scored.append((score, index, sentence))

    best = sorted(scored, key=lambda item: item[0], reverse=True)
    best = best[:sentence_limit]
    best.sort(key=lambda item: item[1])

    return " ".join(item[2] for item in best)


# --------------------------------------------------
# WEBSITE RESEARCH HELPER
# --------------------------------------------------

def research_website(url):
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()

    if "text/html" not in content_type:
        raise ValueError("This link does not contain an HTML webpage.")

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup([
        "script", "style", "nav", "footer", "header",
        "noscript", "svg", "form", "iframe",
    ]):
        element.decompose()

    title = (
        soup.title.get_text(" ", strip=True)
        if soup.title
        else "Untitled webpage"
    )

    content = (
        soup.find("article")
        or soup.find("main")
        or soup.body
        or soup
    )

    page_text = content.get_text(" ", strip=True)
    page_text = re.sub(r"\s+", " ", page_text).strip()

    if not page_text:
        raise ValueError("No readable text was found on this webpage.")

    summary = summarize_text(page_text)

    return {
        "url": url,
        "title": title,
        "summary": summary,
        "text": page_text,
    }


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🔎 Research Assistant")
    st.caption("Your simple website research workspace")

    st.divider()

    st.markdown("### ✨ Features")
    st.write("🌐 Extract public webpage text")
    st.write("📝 Create quick rule-based summaries")
    st.write("📥 Download summaries")
    st.write("📚 Keep session research history")

    st.divider()

    st.markdown("### 📚 Research History")

    if st.session_state.research_history:
        for index, item in enumerate(
            reversed(st.session_state.research_history),
            start=1,
        ):
            with st.expander(item["title"][:45]):
                st.caption(item["url"])
                st.write(item["summary"])

                st.download_button(
                    "Download this summary",
                    data=item["summary"],
                    file_name=f"research_summary_{index}.txt",
                    mime="text/plain",
                    key=f"history_download_{index}",
                )
    else:
        st.caption("Your researched websites will appear here.")

    st.divider()

    st.caption(
        "Free to use. No AI API key required. "
        "History is stored for the current session."
    )


# --------------------------------------------------
# MAIN RESEARCH INPUT
# --------------------------------------------------

st.markdown(
    '<div class="section-label">STEP 1 · ENTER A WEBSITE</div>',
    unsafe_allow_html=True,
)

st.subheader("🌐 Research a Website")
st.write("Enter a public webpage URL to extract its text and create a summary.")

with st.form("research_form"):
    url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        help="Enter a full public webpage address starting with http:// or https://.",
    )

    submitted = st.form_submit_button(
        "🔍 Research Website",
        use_container_width=True,
    )


# --------------------------------------------------
# PROCESS WEBSITE
# --------------------------------------------------

if submitted:
    clean_url = url.strip()
    parsed = urlparse(clean_url)

    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        st.error("Please enter a valid URL starting with https:// or http://.")

    else:
        try:
            with st.spinner("Reading and analyzing the webpage..."):
                result = research_website(clean_url)

            st.session_state.research_result = result

            existing_urls = {
                item["url"]
                for item in st.session_state.research_history
            }

            if clean_url not in existing_urls:
                st.session_state.research_history.append(result)

            st.success("Website researched successfully!")

        except requests.exceptions.Timeout:
            st.error("The website took too long to respond. Try again.")

        except requests.exceptions.RequestException:
            st.error(
                "Could not retrieve this webpage. Check the URL "
                "or try another public website."
            )

        except ValueError as error:
            st.error(str(error))

        except Exception as error:
            st.error(
                f"An unexpected error occurred: "
                f"{type(error).__name__}: {error}"
            )


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

result = st.session_state.research_result

if result:
    st.divider()

    st.markdown(
        '<div class="section-label">STEP 2 · REVIEW YOUR RESULTS</div>',
        unsafe_allow_html=True,
    )

    st.subheader("📄 Website Overview")

    st.markdown(f"### {result['title']}")
    st.caption(result["url"])

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "Characters extracted",
            f"{len(result['text']):,}",
        )

    with metric2:
        st.metric(
            "Words extracted",
            f"{len(result['text'].split()):,}",
        )

    st.divider()

    st.subheader("📝 Research Summary")

    with st.container(border=True):
        st.write(result["summary"])

        st.download_button(
            label="📥 Download Summary",
            data=(
                f"Website: {result['title']}\n"
                f"URL: {result['url']}\n\n"
                f"Summary:\n{result['summary']}\n"
            ),
            file_name="website_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="main_summary_download",
        )

    st.caption(
        "This summary is generated using word-frequency scoring. "
        "It is not an AI-generated analysis and may miss important context."
    )

    with st.expander("📖 View Extracted Website Text"):
        st.text_area(
            "Extracted content",
            value=result["text"][:20000],
            height=300,
            key="extracted_page_text",
        )

        st.download_button(
            "📥 Download Extracted Text",
            data=result["text"],
            file_name="extracted_website_text.txt",
            mime="text/plain",
            key="download_extracted_text",
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer-note">
        Website Research Assistant · Built with Python and Streamlit
        <br>
        Free rule-based summaries · No API key required
    </div>
    """,
    unsafe_allow_html=True,
)
