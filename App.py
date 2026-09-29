import streamlit as st
from dotenv import load_dotenv
import os
from google import genai
from urllib.parse import quote

# ============================================================
#  🌸 CUSTOM CSS SECTION — "Blossoms & Besties" theme
#  (Only styling lives here; app logic starts further below)
# ============================================================


def _svg(svg: str) -> str:
    """Turn an SVG string into a CSS-ready data URI."""
    return 'url("data:image/svg+xml;utf8,' + quote(svg) + '")'


# Daisy: 8 creamy petals + golden centre
_daisy_petals = "".join(
    f"<ellipse cx='50' cy='24' rx='8' ry='17' transform='rotate({a} 50 50)'/>"
    for a in range(0, 360, 45)
)
DAISY = _svg(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<g fill='#fffdf8' stroke='#f2c1cc' stroke-width='1.6'>" + _daisy_petals + "</g>"
    "<circle cx='50' cy='50' r='9' fill='#f6d68a'/></svg>"
)

# Rose: layered pink circles with curled petal strokes
ROSE = _svg(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<circle cx='50' cy='50' r='40' fill='#f4b6c2'/>"
    "<circle cx='50' cy='50' r='30' fill='#f8c9d3' stroke='#e79aab' stroke-width='2'/>"
    "<circle cx='50' cy='50' r='20' fill='#f4b6c2' stroke='#e79aab' stroke-width='2'/>"
    "<path d='M50 50 m-9 0 a9 9 0 1 1 9 9 a5 5 0 1 1 -5 -6' fill='none' "
    "stroke='#d9788f' stroke-width='2.5' stroke-linecap='round'/></svg>"
)

# Leafy vine running down an edge
VINE = _svg(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 400'>"
    "<path d='M60 0 C10 80 110 150 55 240 S 70 340 60 400' fill='none' "
    "stroke='#a9c3a4' stroke-width='3' stroke-linecap='round'/>"
    "<g fill='#bcd4b6' stroke='#93b08d' stroke-width='1'>"
    "<ellipse cx='30' cy='70' rx='20' ry='9' transform='rotate(-30 30 70)'/>"
    "<ellipse cx='92' cy='120' rx='20' ry='9' transform='rotate(30 92 120)'/>"
    "<ellipse cx='32' cy='190' rx='20' ry='9' transform='rotate(-25 32 190)'/>"
    "<ellipse cx='84' cy='262' rx='20' ry='9' transform='rotate(28 84 262)'/>"
    "<ellipse cx='36' cy='330' rx='20' ry='9' transform='rotate(-30 36 330)'/></g>"
    "<circle cx='92' cy='120' r='6' fill='#f4b6c2'/><circle cx='32' cy='190' r='6' fill='#fffdf8'/>"
    "</svg>"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Quicksand:wght@400;500;600;700&display=swap');

:root {
    --baby-pink: #fbe3ea;
    --blush: #f7cfda;
    --rose: #d9788f;
    --deep-rose: #b04a67;
    --sage: #a9c3a4;
    --mint: #dcefdc;
    --deep-green: #2f4a3a;
    --cream: #fffaf3;
    --brown: #4a3a34;
}

/* ---------- App background ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    color-scheme: light;
    font-family: 'Quicksand', sans-serif;
    color: var(--deep-green);
}
.stApp {
    background: linear-gradient(135deg, #fde7ee 0%, #fbeff0 40%, #e6f2e3 100%) fixed;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent; }

/* Floral corners (decorative, never blocks clicks) */
.stApp::before, .stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-repeat: no-repeat;
    opacity: 0.85;
}
.stApp::before {
    background-image: __VINE__, __ROSE__, __DAISY__, __DAISY__;
    background-position: -10px 0, 3% 6%, 9% 26%, 1% 52%;
    background-size: 120px 400px, 84px, 46px, 34px;
}
.stApp::after {
    background-image: __VINE__, __ROSE__, __DAISY__, __DAISY__;
    background-position: calc(100% + 10px) 100%, 96% 92%, 90% 70%, 99% 46%;
    background-size: 120px 400px, 92px, 50px, 34px;
    transform: rotate(0deg);
}
[data-testid="stAppViewContainer"] > .main, [data-testid="stMain"] { position: relative; z-index: 1; }

/* Drifting hearts & petals (very subtle) */
.floaties { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.floaties span {
    position: absolute; bottom: -30px; color: var(--rose); opacity: 0;
    animation: floatUp 16s ease-in infinite;
}
.floaties span:nth-child(1) { left: 12%; animation-delay: 0s;  font-size: 16px; }
.floaties span:nth-child(2) { left: 30%; animation-delay: 4s;  font-size: 12px; color: var(--sage); }
.floaties span:nth-child(3) { left: 55%; animation-delay: 8s;  font-size: 18px; }
.floaties span:nth-child(4) { left: 74%; animation-delay: 2s;  font-size: 13px; color: #e9a3b5; }
.floaties span:nth-child(5) { left: 88%; animation-delay: 10s; font-size: 15px; color: var(--sage); }
@keyframes floatUp {
    0%   { transform: translateY(0) rotate(0deg); opacity: 0; }
    12%  { opacity: 0.55; }
    85%  { opacity: 0.35; }
    100% { transform: translateY(-105vh) rotate(40deg); opacity: 0; }
}

/* ---------- Main chatbot card ---------- */
.block-container {
    position: relative;
    max-width: 760px;
    margin: 2.5rem auto;
    padding: 3rem 2.6rem 2.6rem !important;
    background: var(--cream);
    border: 1.5px solid var(--sage);
    border-radius: 32px;
    box-shadow: 0 18px 50px rgba(217, 120, 143, 0.22), 0 2px 8px rgba(217, 120, 143, 0.12);
}
.block-container::before {
    content: "🌼  🌿";
    position: absolute; top: 14px; left: 22px; font-size: 20px; letter-spacing: 4px;
}
.block-container::after {
    content: "🌿  ♡  🌼";
    position: absolute; bottom: 12px; right: 24px; font-size: 18px; letter-spacing: 4px; opacity: 0.9;
}

/* ---------- Title & subtitle ---------- */
h1, [data-testid="stHeading"] h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    color: var(--deep-rose) !important;
    text-align: center;
    letter-spacing: 0.3px;
    padding-bottom: 0.2rem !important;
}
h1::before { content: "🌸 "; font-size: 0.8em; }
h1::after  { content: " 🌷"; font-size: 0.8em; }
.subtitle {
    text-align: center;
    color: #5f7f68;
    font-size: 1.02rem;
    font-weight: 500;
    margin: 0 0 1.6rem;
}
h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: var(--deep-rose) !important; }

/* ---------- Text area ---------- */
[data-testid="stWidgetLabel"] p, label p {
    color: var(--deep-green) !important;
    font-weight: 600;
    font-size: 1rem;
}
[data-baseweb="textarea"], [data-baseweb="base-input"] {
    background: #fffdf8 !important;
    border: 1.5px solid #f2bccb !important;
    border-radius: 18px !important;
    transition: box-shadow .3s ease, border-color .3s ease;
}
[data-baseweb="textarea"]:focus-within {
    border-color: var(--rose) !important;
    box-shadow: 0 0 0 4px rgba(247, 207, 218, 0.7), 0 0 18px rgba(217, 120, 143, 0.35);
}
.stTextArea textarea {
    background: #fffdf8 !important;
    color: var(--deep-green) !important;
    -webkit-text-fill-color: var(--deep-green) !important;
    caret-color: var(--rose);
    font-family: 'Quicksand', sans-serif;
    font-size: 1.02rem;
    line-height: 1.65;
    min-height: 150px;
    padding: 14px 16px;
    border-radius: 18px;
}
.stTextArea textarea::placeholder {
    color: #c98a9b !important;
    -webkit-text-fill-color: #c98a9b !important;
    opacity: 1;
}

/* ---------- Generate button ---------- */
.stButton > button {
    background: linear-gradient(120deg, #f8c8d4 0%, #cfe3c8 100%) !important;
    color: var(--deep-green) !important;
    border: 1.5px solid #ecb5c3 !important;
    border-radius: 999px !important;
    padding: 0.65rem 2rem !important;
    font-family: 'Quicksand', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    box-shadow: 0 6px 16px rgba(217, 120, 143, 0.22);
    transition: transform .25s ease, box-shadow .25s ease, filter .25s ease;
}
.stButton > button p { color: var(--deep-green) !important; font-weight: 700; }
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 24px rgba(217, 120, 143, 0.32);
    filter: brightness(1.03);
    border-color: var(--rose) !important;
}
.stButton > button:active { transform: translateY(-1px); }
.stButton > button:focus-visible { outline: 3px solid rgba(169, 195, 164, 0.8); outline-offset: 2px; }

/* ---------- Spinner ---------- */
[data-testid="stSpinner"], [data-testid="stSpinner"] * { color: var(--deep-rose) !important; }

/* ---------- Success & warning messages ---------- */
[data-testid="stAlert"], [data-testid="stAlertContainer"] {
    border-radius: 18px !important;
    font-weight: 600;
}
[data-testid="stAlert"] {
    border: 1.5px solid var(--sage) !important;
    background: var(--mint) !important;
    color: var(--deep-green) !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] svg { color: var(--deep-green) !important; fill: var(--deep-green); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
div[data-testid="stAlert"]:has(svg[data-testid="stAlertWarningIcon"]) {
    background: #fdeaee !important;
    border-color: #ecb5c3 !important;
}
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) p { color: var(--deep-rose) !important; }

/* ---------- AI response card ---------- */
.st-key-response-card {
    background: var(--cream);
    border: 1.5px solid var(--sage);
    border-radius: 26px;
    padding: 1.6rem 1.8rem;
    margin-top: 1.4rem;
    box-shadow: 0 10px 30px rgba(217, 120, 143, 0.2);
    animation: fadeIn .9s ease both;
}
.st-key-response-card h3 { margin-top: 0; }
.st-key-response-card, .st-key-response-card p, .st-key-response-card li,
.st-key-response-card span, .st-key-response-card td, .st-key-response-card th {
    color: var(--brown);
    line-height: 1.85;
    font-size: 1.02rem;
}
.st-key-response-card h1, .st-key-response-card h2, .st-key-response-card h3, .st-key-response-card h4 { color: var(--deep-rose) !important; }
.st-key-response-card strong { color: var(--deep-green); }
.st-key-response-card a { color: var(--deep-rose); }
.st-key-response-card code {
    background: #fdeef2 !important; color: var(--deep-green) !important; border-radius: 8px; padding: 2px 6px;
}
.st-key-response-card pre { background: #f1f7ef !important; border: 1px solid var(--sage); border-radius: 14px; }
.st-key-response-card pre code { background: transparent !important; }
.st-key-response-card table { border-collapse: collapse; }
.st-key-response-card th, .st-key-response-card td { border: 1px solid #e6c9d1; padding: 6px 10px; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

/* ---------- Responsive ---------- */
@media (max-width: 640px) {
    .block-container { margin: 1rem 0.5rem; padding: 2.6rem 1.1rem 2.4rem !important; border-radius: 24px; }
    h1 { font-size: 1.7rem !important; }
    .subtitle { font-size: 0.92rem; }
    .stButton > button { width: 100%; }
    .st-key-response-card { padding: 1.2rem 1rem; }
    .stApp::before, .stApp::after { opacity: 0.45; }
}
@media (prefers-reduced-motion: reduce) {
    .floaties span, .st-key-response-card { animation: none; }
    .stButton > button { transition: none; }
}
</style>
"""

for _token, _uri in (("__VINE__", VINE), ("__ROSE__", ROSE), ("__DAISY__", DAISY)):
    CUSTOM_CSS = CUSTOM_CSS.replace(_token, _uri)

# ============================================================
#  APP LOGIC (unchanged)
# ============================================================

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)
st.set_page_config(
    page_title="ROSELLE AI",
    layout="centered",
)

# Inject theme
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown(
    '<div class="floaties"><span>♡</span><span>❀</span><span>♡</span><span>✿</span><span>♡</span></div>',
    unsafe_allow_html=True,
)

st.title("ROSELLE AI")
st.markdown(
    '<p class="subtitle">A little garden of thoughts, ideas &amp; endless possibilities ♡</p>',
    unsafe_allow_html=True,
)
prompt=st.text_area(
    "enter your prompt:",
    placeholder="Explain Aritificial Intelligence"
)
if st.button("Generate Response ♡"):
    if prompt:
        with st.spinner("Gemini is thinking....."):
            response=client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
        st.success("Response Generated!")
        with st.container(key="response-card"):
            st.markdown("### A little something for you 🌷")
            st.write(response.text)
    else:
        st.warning("Please enter a prompt.")