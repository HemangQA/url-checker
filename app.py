import streamlit as st
import requests
import pandas as pd
import time
from docx import Document

st.set_page_config(page_title="URL Status Checker", layout="wide")

st.title("🔗 URL Status Checker")

st.write("Paste URLs or upload a file (CSV, TXT, DOCX).")

# -----------------------
# Helpers
# -----------------------
def extract_urls_from_text(text):
    lines = text.splitlines()
    return [l.strip() for l in lines if l.strip()]

def extract_urls_from_docx(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return extract_urls_from_text(text)

def extract_urls_from_csv(file):
    df = pd.read_csv(file)
    urls = []
    for col in df.columns:
        urls += df[col].dropna().astype(str).tolist()
    return urls

# -----------------------
# Inputs
# -----------------------
uploaded_file = st.file_uploader(
    "Upload file (CSV / TXT / DOCX)",
    type=["csv", "txt", "docx"]
)

urls_input = st.text_area("Or paste URLs (one per line)")

urls = []

# From text box
if urls_input:
    urls += extract_urls_from_text(urls_input)

# From file
if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "csv":
        urls += extract_urls_from_csv(uploaded_file)

    elif file_type == "txt":
        text = uploaded_file.read().decode("utf-8")
        urls += extract_urls_from_text(text)

    elif file_type == "docx":
        urls += extract_urls_from_docx(uploaded_file)

# Remove duplicates
urls = list(set(urls))

st.write(f"Total URLs detected: **{len(urls)}**")

# -----------------------
# Check URLs
# -----------------------
if st.button("Check URLs"):

    if not urls:
        st.warning("No URLs found.")
    else:
        results = []
        progress = st.progress(0)

        for i, url in enumerate(urls):

            if not url.startswith("http"):
                url = "https://" + url

            try:
                start = time.time()

                r = requests.get(
                    url,
                    timeout=10,
                    allow_redirects=True
                )

                duration = round((time.time() - start) * 1000, 2)

                results.append({
                    "URL": url,
                    "Status": r.status_code,
                    "Response Time (ms)": duration,
                    "Final URL": r.url
                })

            except Exception as e:
                results.append({
                    "URL": url,
                    "Status": "ERROR",
                    "Response Time (ms)": None,
                    "Final URL": str(e)
                })

            progress.progress((i + 1) / len(urls))

        df = pd.DataFrame(results)

        st.success("Done!")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Results CSV",
            data=csv,
            file_name="url_results.csv",
            mime="text/csv"
        )