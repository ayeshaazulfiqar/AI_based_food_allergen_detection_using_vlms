import streamlit as st
from google import genai
from PIL import Image
import json
import re
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AllergenAI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Righteous&family=DM+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050810 !important;
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 15% 10%, rgba(0,255,180,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 80%, rgba(0,120,255,0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

#MainMenu, footer { visibility: hidden; }

[data-testid="stHeader"] {
    background: rgba(5,8,16,0.95) !important;
    border-bottom: 1px solid rgba(0,255,180,0.08) !important;
}

[data-testid="stSidebar"] {
    background: rgba(8,12,22,0.98) !important;
    border-right: 1px solid rgba(0,255,180,0.08) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #050810; }
::-webkit-scrollbar-thumb { background: rgba(0,255,180,0.3); border-radius: 2px; }

[data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #4a5568 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] { color: #00ffb4 !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: #00ffb4 !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { background: rgba(255,255,255,0.05) !important; }

.stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid rgba(0,255,180,0.15) !important;
    border-radius: 12px !important;
    color: #111111 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    caret-color: #111111 !important;
}
.stTextArea textarea:focus { border-color: rgba(0,255,180,0.4) !important; }
.stTextArea textarea::placeholder { color: #999999 !important; }

[data-testid="stFileUploader"] {
    background: rgba(0,255,180,0.02) !important;
    border: 1px dashed rgba(0,255,180,0.2) !important;
    border-radius: 12px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00ffb4 0%, #00b4ff 100%) !important;
    color: #050810 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border: none !important;
    border-radius: 10px !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(0,255,180,0.2) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,255,180,0.35) !important;
}

.stTextInput input {
    background: #ffffff !important;
    border: 1px solid rgba(0,255,180,0.15) !important;
    border-radius: 10px !important;
    color: #111111 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    caret-color: #111111 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
ALLERGEN_ICONS = {
    'Milk': '🥛', 'Egg': '🥚', 'Peanut': '🥜', 'Tree_Nuts': '🌰',
    'Wheat_Gluten': '🌾', 'Soy': '🫘', 'Fish': '🐟', 'Shellfish': '🦐',
    'Sesame': '🌿', 'Mustard': '🌼', 'Celery': '🥬', 'Molluscs': '🦪'
}
ALLERGEN_LABELS = list(ALLERGEN_ICONS.keys())

# ─────────────────────────────────────────────
# GEMINI
# ─────────────────────────────────────────────
@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)

def detect_allergens(client, image=None, ingredients_text=None):
    prompt = """
You are an expert food allergen detection system.
Analyze the provided food information and return ONLY a JSON response in this exact format:
{
    "dish_name": "Name of the dish",
    "description": "Brief one line description",
    "detected_allergens": ["Milk", "Egg"],
    "allergen_risk": {
        "Milk": 85, "Egg": 90, "Peanut": 0, "Tree_Nuts": 0,
        "Wheat_Gluten": 75, "Soy": 0, "Fish": 0, "Shellfish": 0,
        "Sesame": 0, "Mustard": 10, "Celery": 0, "Molluscs": 0
    },
    "confidence": "High",
    "warning": "Any important allergen warning or null"
}
Rules:
- allergen_risk values are 0-100
- detected_allergens only lists allergens with risk > 50
- Consider hidden allergens (e.g. soy in sauces, milk in butter)
- Return ONLY the JSON, no markdown, no extra text
"""
    contents = []
    if image:
        contents.append(image)
    if ingredients_text:
        contents.append(f"Ingredients: {ingredients_text}")
    contents.append(prompt)

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=contents
    )
    raw = re.sub(r'^```json\s*|^```\s*|\s*```$', '', response.text.strip())
    return json.loads(raw)

# ─────────────────────────────────────────────
# RENDER RESULTS
# ─────────────────────────────────────────────
def render_results(data):
    risk = data.get("allergen_risk", {})
    detected = data.get("detected_allergens", [])
    confidence = data.get("confidence", "Medium")
    warning = data.get("warning")
    conf_color = {"High": "#00ffb4", "Medium": "#ffb020", "Low": "#ff5050"}.get(confidence, "#ffb020")

    # Dish card
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(0,255,180,0.12);
                border-radius:16px; padding:1.4rem 1.6rem; margin-bottom:1rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
            <div>
                <div style="font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.3em;
                            text-transform:uppercase; color:#00ffb4; margin-bottom:0.35rem;">● Identified Dish</div>
                <div style="font-family:'Righteous',cursive; font-size:1.55rem; color:#ffffff; margin-bottom:0.3rem;">
                    {data.get("dish_name", "Unknown")}
                </div>
                <div style="color:#d4dce8; font-size:0.8rem;">{data.get("description", "")}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'DM Mono',monospace; font-size:0.55rem; letter-spacing:0.2em;
                            text-transform:uppercase; color:#c0ccd8; margin-bottom:0.3rem;">Confidence</div>
                <div style="font-family:'Righteous',cursive; font-size:1.1rem; color:{conf_color};
                            text-shadow:0 0 10px {conf_color}50;">{confidence}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    if detected:
        st.markdown(f"""
        <div style="display:inline-flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;
                    padding:0.45rem 1.1rem; border-radius:50px;
                    background:rgba(255,80,80,0.1); border:1px solid rgba(255,80,80,0.3);
                    color:#ff6060; font-size:0.85rem; font-weight:600;">
            ⚠️ &nbsp;{len(detected)} Allergen{"s" if len(detected)>1 else ""} Detected
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:inline-flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem;
                    padding:0.45rem 1.1rem; border-radius:50px;
                    background:rgba(0,255,180,0.07); border:1px solid rgba(0,255,180,0.22);
                    color:#00ffb4; font-size:0.85rem; font-weight:600;">
            ✅ &nbsp;No Allergens Detected
        </div>""", unsafe_allow_html=True)

    # Gauges
    st.markdown("""<div style="font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.25em;
                text-transform:uppercase; color:#d4dce8; margin-bottom:0.7rem;">● Allergen Risk Scores</div>
    """, unsafe_allow_html=True)

    for row in [ALLERGEN_LABELS[i:i+3] for i in range(0, 12, 3)]:
        cols = st.columns(3)
        for col, label in zip(cols, row):
            score = risk.get(label, 0)
            is_det = label in detected
            icon = ALLERGEN_ICONS[label]
            disp = label.replace("_", " ")

            if score >= 70:
                c, b, bg = "#ff5050", "linear-gradient(90deg,#ff5050,#ff2020)", "rgba(255,80,80,0.08)"
                border = "rgba(255,80,80,0.45)" if is_det else "rgba(255,80,80,0.12)"
            elif score >= 40:
                c, b, bg = "#ffb020", "linear-gradient(90deg,#ffb020,#ff8c00)", "rgba(255,176,32,0.06)"
                border = "rgba(255,176,32,0.45)" if is_det else "rgba(255,176,32,0.12)"
            else:
                c, b, bg = "#00ffb4", "linear-gradient(90deg,#00ffb4,#00b4ff)", "rgba(0,255,180,0.03)"
                border = "rgba(0,255,180,0.25)" if is_det else "rgba(255,255,255,0.04)"

            with col:
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid {border}; border-radius:14px;
                            padding:0.9rem 0.7rem; text-align:center; margin-bottom:0.5rem;">
                    <div style="font-family:'DM Mono',monospace; font-size:0.52rem; letter-spacing:0.15em;
                                text-transform:uppercase; color:#d4dce8; margin-bottom:0.4rem;">{disp}</div>
                    <div style="font-size:1.4rem; margin-bottom:0.35rem; line-height:1;">{icon}</div>
                    <div style="font-family:'Righteous',cursive; font-size:1.3rem; color:{c};
                                text-shadow:0 0 12px {c}45; margin-bottom:0.4rem;">{score}%</div>
                    <div style="height:3px; background:rgba(255,255,255,0.04); border-radius:2px; overflow:hidden;">
                        <div style="height:100%; width:{score}%; background:{b}; border-radius:2px;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

    if warning:
        st.markdown(f"""
        <div style="margin-top:0.7rem; padding:0.9rem 1.1rem;
                    background:rgba(255,176,32,0.05); border:1px solid rgba(255,176,32,0.18);
                    border-left:3px solid #ffb020; border-radius:10px;">
            <div style="font-family:'DM Mono',monospace; font-size:0.57rem; letter-spacing:0.18em;
                        text-transform:uppercase; color:#ffb020; margin-bottom:0.35rem;">⚠ Allergen Note</div>
            <div style="color:#b8943b; font-size:0.78rem; line-height:1.6;">{warning}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:0.8rem; padding:0.6rem 0.9rem; background:rgba(255,255,255,0.015);
                border:1px solid rgba(255,255,255,0.04); border-radius:8px;">
        <p style="color:#c0ccd8; font-size:0.65rem; margin:0; font-family:'DM Mono',monospace; line-height:1.5;">
        ⚕ AI-generated analysis for informational purposes only.
        Always verify with a certified food specialist or medical professional before consumption.
        </p>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Righteous',cursive; font-size:1.3rem; color:#fff; margin-bottom:0.2rem;">
        Allergen<span style="background:linear-gradient(135deg,#00ffb4,#00b4ff);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">AI</span>
    </div>
    <div style="font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.2em;
                text-transform:uppercase; color:#d4dce8; margin-bottom:1.5rem;">
        Gemini Vision · v2.0
    </div>
    <div style="font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.2em;
                text-transform:uppercase; color:#00ffb4; margin-bottom:0.6rem;">● API Key</div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("", type="password", placeholder="AIza...", label_visibility="collapsed")

    st.markdown("""
    <div style="color:#c0ccd8; font-size:0.65rem; font-family:'DM Mono',monospace;
                line-height:1.6; margin-top:0.4rem; margin-bottom:1.5rem;">
        Get free key at<br>
        <span style="color:#00ffb460;">aistudio.google.com</span>
    </div>
    <div style="height:1px; background:rgba(0,255,180,0.08); margin-bottom:1.5rem;"></div>
    <div style="font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.2em;
                text-transform:uppercase; color:#00ffb4; margin-bottom:0.8rem;">● How It Works</div>
    <div style="color:#d4dce8; font-size:0.72rem; font-family:'DM Mono',monospace; line-height:1.8;">
        1. Add your API key<br>
        2. Upload food image<br>
        &nbsp;&nbsp;&nbsp;or enter ingredients<br>
        3. Get instant allergen<br>
        &nbsp;&nbsp;&nbsp;risk assessment
    </div>
    <div style="height:1px; background:rgba(0,255,180,0.08); margin:1.5rem 0;"></div>
    <div style="font-family:'DM Mono',monospace; font-size:0.6rem; letter-spacing:0.2em;
                text-transform:uppercase; color:#00ffb4; margin-bottom:0.8rem;">● Detects</div>
    <div style="color:#d4dce8; font-size:0.7rem; font-family:'DM Mono',monospace; line-height:1.9;">
        🥛 Milk &nbsp;&nbsp; 🥚 Egg<br>
        🥜 Peanut &nbsp;&nbsp; 🌰 Tree Nuts<br>
        🌾 Wheat &nbsp;&nbsp; 🫘 Soy<br>
        🐟 Fish &nbsp;&nbsp; 🦐 Shellfish<br>
        🌿 Sesame &nbsp;&nbsp; 🌼 Mustard<br>
        🥬 Celery &nbsp;&nbsp; 🦪 Molluscs
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2rem 0 1.5rem;">
    <div style="font-family:'DM Mono',monospace; font-size:0.62rem; letter-spacing:0.35em;
                text-transform:uppercase; color:#00ffb4; margin-bottom:0.9rem; opacity:0.8;">
        🧬 &nbsp; AI-Powered Allergen Detection
    </div>
    <div style="font-family:'Righteous',cursive; font-size:clamp(2.8rem,5.5vw,5rem);
                color:#ffffff; line-height:1; margin-bottom:0.7rem; letter-spacing:0.04em;">
        Allergen<span style="background:linear-gradient(135deg,#00ffb4,#00b4ff);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">AI</span>
    </div>
    <div style="color:#d4dce8; font-size:0.85rem; letter-spacing:0.03em; margin-bottom:0.5rem;">
        Multi-label risk assessment for unpackaged foods · Powered by Gemini Vision
    </div>
    <div style="color:#ff9f43; font-size:0.68rem; font-family:'DM Mono',monospace;">
        ⚠️ Informational use only — always consult a medical professional
    </div>
</div>
<div style="height:1px; background:linear-gradient(90deg,transparent,rgba(0,255,180,0.25),transparent); margin-bottom:1.8rem;"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.5], gap="large")

with left_col:
    st.markdown("""<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
                border-radius:16px; padding:1.4rem; backdrop-filter:blur(10px);">
    <div style="font-family:'DM Mono',monospace; font-size:0.58rem; letter-spacing:0.25em;
                text-transform:uppercase; color:#00ffb4; margin-bottom:1rem;">● Input</div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖼️  Image", "📝  Ingredients", "⚡  Both"])

    with tab1:
        st.markdown('<p style="color:#d4dce8; font-size:0.75rem; margin-bottom:0.7rem; font-family:DM Mono,monospace;">Upload food photo — AI identifies dish and detects allergens.</p>', unsafe_allow_html=True)
        img_file = st.file_uploader("", type=["jpg","jpeg","png","webp"], key="img_only", label_visibility="collapsed")
        if img_file:
            st.image(img_file, use_container_width=True)
        run_img = st.button("🔍 Analyse Image", key="btn_img")

    with tab2:
        st.markdown('<p style="color:#d4dce8; font-size:0.75rem; margin-bottom:0.7rem; font-family:DM Mono,monospace;">Enter ingredients separated by commas.</p>', unsafe_allow_html=True)
        text_input = st.text_area("", placeholder="e.g. whole milk, eggs, flour, butter, sesame oil...", height=150, key="text_only", label_visibility="collapsed")
        run_text = st.button("🔬 Analyse Ingredients", key="btn_text")

    with tab3:
        st.markdown('<p style="color:#d4dce8; font-size:0.75rem; margin-bottom:0.7rem; font-family:DM Mono,monospace;">Combine image + ingredients for maximum accuracy.</p>', unsafe_allow_html=True)
        img_both = st.file_uploader("", type=["jpg","jpeg","png","webp"], key="img_both", label_visibility="collapsed")
        if img_both:
            st.image(img_both, use_container_width=True)
        text_both = st.text_area("", placeholder="e.g. chicken, butter, garlic, cream...", height=90, key="text_both", label_visibility="collapsed")
        run_both = st.button("⚡ Analyse Both", key="btn_both")

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
with right_col:
    if not api_key:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
                    border-radius:16px; padding:3rem 2rem; text-align:center;">
            <div style="font-size:2.5rem; margin-bottom:1rem;">🔑</div>
            <div style="font-family:'Righteous',cursive; font-size:1rem; color:#e2e8f0; margin-bottom:0.5rem;">Add API Key First</div>
            <div style="color:#c0ccd8; font-size:0.75rem; font-family:'DM Mono',monospace; line-height:1.7;">
                Enter your Gemini API key in the sidebar ←
            </div>
        </div>""", unsafe_allow_html=True)

    elif not (run_img or run_text or run_both):
        st.markdown("""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
                    border-radius:16px; padding:3rem 2rem; text-align:center;">
            <div style="font-size:2.5rem; margin-bottom:1rem;">🧬</div>
            <div style="font-family:'Righteous',cursive; font-size:1rem; color:#e2e8f0; margin-bottom:0.5rem;">Ready to Scan</div>
            <div style="color:#c0ccd8; font-size:0.75rem; font-family:'DM Mono',monospace; line-height:1.8;">
                Upload a food image or enter ingredients<br>
                then click Analyse.<br><br>
                <span style="color:#00ffb430;">Powered by Gemini Vision AI</span>
            </div>
        </div>""", unsafe_allow_html=True)

    else:
        try:
            client = get_client(api_key)

            if run_img and img_file:
                with st.spinner("🔍 Analysing image..."):
                    result = detect_allergens(client, image=Image.open(img_file))
                render_results(result)

            elif run_text and text_input.strip():
                with st.spinner("🔬 Analysing ingredients..."):
                    result = detect_allergens(client, ingredients_text=text_input)
                render_results(result)

            elif run_both:
                with st.spinner("⚡ Analysing..."):
                    img = Image.open(img_both) if img_both else None
                    result = detect_allergens(client, image=img, ingredients_text=text_both or None)
                render_results(result)

            else:
                st.warning("Please provide an image or ingredients.")

        except Exception as e:
            st.markdown(f"""
            <div style="padding:1rem; background:rgba(255,80,80,0.08);
                        border:1px solid rgba(255,80,80,0.25); border-radius:10px;
                        color:#ff8080; font-family:'DM Mono',monospace; font-size:0.78rem;">
                ❌ {str(e)}
            </div>""", unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div style="height:1px; background:linear-gradient(90deg,transparent,rgba(0,255,180,0.12),transparent); margin-top:3rem;"></div>
<div style="text-align:center; padding:1rem 0 2rem; font-family:'DM Mono',monospace;
            font-size:0.6rem; letter-spacing:0.15em; color:#a8b8cc;">
    ALLERGENAI · GEMINI VISION · MULTI-LABEL ALLERGEN RISK ASSESSMENT
</div>
""", unsafe_allow_html=True)
