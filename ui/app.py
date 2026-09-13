import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator.pipeline import run_pipeline

st.set_page_config(page_title="Job Risk Assessment", page_icon="🛡️", layout="centered")

# ---------- THEME TOGGLE ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

col_a, col_b = st.columns([5, 1])
with col_b:
    st.session_state.dark_mode = st.toggle("🌙", value=st.session_state.dark_mode, label_visibility="collapsed")

DARK = {
    "bg": "#0F1117", "card": "#1A1D27", "text": "#E8E9ED", "muted": "#9CA3AF",
    "border": "#2A2E3A", "accent": "#6366F1", "input_bg": "#1A1D27"
}
LIGHT = {
    "bg": "#F7F8FA", "card": "#FFFFFF", "text": "#1A1D27", "muted": "#6B7280",
    "border": "#E5E7EB", "accent": "#4F46E5", "input_bg": "#FFFFFF"
}
T = DARK if st.session_state.dark_mode else LIGHT

LEVEL_COLORS = {
    "Low": "#22C55E", "Medium": "#F59E0B", "High": "#F97316",
    "Critical": "#EF4444", "Unknown": "#6B7280"
}

st.markdown(f"""
<style>
    .stApp {{
        background-color: {T['bg']};
    }}
    /* Broad catch-all: forces every text element to the theme color first */
    .stApp, .stApp * {{
        color: {T['text']};
    }}
    [data-testid="stForm"] {{
        background-color: {T['card']};
        border: 1px solid {T['border']};
        border-radius: 16px;
        padding: 28px;
    }}
    .stTextArea textarea, .stTextInput input {{
        background-color: {T['input_bg']} !important;
        color: {T['text']} !important;
        border: 1px solid {T['border']} !important;
        border-radius: 10px !important;
    }}
    /* Button text always white, regardless of theme */
    .stButton button, .stButton button * {{
        color: #FFFFFF !important;
    }}
    .stButton button {{
        background: linear-gradient(135deg, {T['accent']}, #8B5CF6);
        border: none;
        border-radius: 10px;
        padding: 12px 0;
        font-weight: 600;
        font-size: 16px;
        transition: transform 0.15s ease;
    }}
    .stButton button:hover {{ transform: translateY(-2px); }}
    .title-wrap {{ text-align: center; margin-bottom: 6px; }}
    .subtitle {{ text-align: center; color: {T['muted']} !important; margin-bottom: 28px; font-size: 15px; }}
    .evidence-tag {{
        display: inline-block; background-color: {T['card']}; border: 1px solid {T['border']};
        border-radius: 8px; padding: 6px 12px; margin: 4px 6px 4px 0; font-size: 13.5px;
    }}
    .section-label {{
        font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em;
        color: {T['muted']} !important; font-weight: 600; margin: 18px 0 8px 0;
    }}
    div[data-testid="stExpander"] {{
        background-color: {T['card']}; border: 1px solid {T['border']}; border-radius: 12px;
    }}
    /* Alert boxes (st.info/st.warning/st.error) keep their own readable colors */
    .stAlert, .stAlert * {{
        color: inherit !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-wrap"><h1>🛡️ Job Risk Assessment</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-assisted scam detection for job postings</div>', unsafe_allow_html=True)

with st.form("risk_form"):
    job_text = st.text_area("Job posting text", height=180, placeholder="Paste the full job description here...")
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Recruiter email (optional)")
    with col2:
        url = st.text_input("Job/company URL (optional)")
    submitted = st.form_submit_button("🔍 Analyze Risk", use_container_width=True)

if submitted:
    if not job_text or not job_text.strip():
        st.error("Please paste a job posting to analyze.")
    else:
        with st.spinner("Analyzing... checking rules, running AI analysis, verifying details"):
            try:
                result = run_pipeline(job_text, email or None, url or None)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                result = None

        if result and not result["success"]:
            for err in result["errors"]:
                st.warning(err)
        elif result:
            level = result["risk_level"]
            color = LEVEL_COLORS.get(level, "#6B7280")

            if result.get("degraded"):
                st.info("⚠️ Some components didn't respond fully — this result may be partial.")

            st.markdown(f"""
            <div style="padding:24px;border-radius:16px;
                        background:linear-gradient(135deg, {color}22, {color}0D);
                        border:1.5px solid {color};margin:20px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:13px;color:{T['muted']};font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">Risk Level</div>
                        <div style="font-size:32px;font-weight:800;color:{color};">{level}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:13px;color:{T['muted']};font-weight:600;">SCORE</div>
                        <div style="font-size:28px;font-weight:800;color:{T['text']};">{result['risk_score']}<span style="font-size:16px;color:{T['muted']};">/100</span></div>
                    </div>
                </div>
                <div style="margin-top:10px;font-size:13.5px;color:{T['muted']};">
                    Confidence: <b style="color:{T['text']};">{result['confidence']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-label">Why this result</div>', unsafe_allow_html=True)
            st.write(result["explanation"])

            st.markdown('<div class="section-label">Recommendation</div>', unsafe_allow_html=True)
            st.info(result["recommendation"])

            with st.expander("📋 See detailed evidence"):
                st.markdown("**Rule-based flags**")
                if result["rule_flags"]:
                    tags = "".join([f'<span class="evidence-tag">🚩 {f["description"]}</span>' for f in result["rule_flags"]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("None found.")

                st.markdown("**AI contextual flags**")
                if result["llm_flags"]:
                    for f in result["llm_flags"]:
                        st.markdown(f'<span class="evidence-tag">🤖 <b>{f["flag"]}</b>: {f["reasoning"]}</span><br>', unsafe_allow_html=True)
                else:
                    st.caption("None found.")

                st.markdown("**Verification flags**")
                if result["verification_flags"]:
                    tags = "".join([f'<span class="evidence-tag">🔎 {f["description"]}</span>' for f in result["verification_flags"]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("None found.")

                st.markdown("**Score breakdown**")
                st.json(result["breakdown"])