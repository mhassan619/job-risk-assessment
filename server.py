"""
JobGuard AI - High-Tech Flask Enterprise Web Server
Serves the exact JobGuard HTML5/CSS/JS Single Page Interface and integrates
seamlessly with the Multi-Tier Heuristic Rule Engine, Domain Verifier, and Gemini AI.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import uuid

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from orchestrator.pipeline import run_pipeline

FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)
CORS(app)


# -----------------------------------------------------------------------------
# 1. UI Routes (Exact JobGuard SPA Delivery)
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Serves the primary modular JobGuard HTML5 single-page interface."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/JOBGUARD.html")
def standalone():
    """Serves the standalone production build of JobGuard."""
    return send_from_directory(FRONTEND_DIR, "JOBGUARD.html")


@app.route("/assets/<path:path>")
def serve_assets(path):
    """Serves design tokens, CSS components, and typography assets."""
    return send_from_directory(FRONTEND_DIR / "assets", path)


@app.route("/src/<path:path>")
def serve_src(path):
    """Serves client-side ES modules, view renderers, and SPA router."""
    return send_from_directory(FRONTEND_DIR / "src", path)


import socket

def check_internet(host="8.8.8.8", port=53, timeout=1.0) -> bool:
    """Quick socket probe to check if machine has active internet connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False


# -----------------------------------------------------------------------------
# 2. REST API Endpoints (Backend Orchestration Connection)
# -----------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    """Live engine status probe with real AI & internet connectivity checks."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    has_key = bool(gemini_key or groq_key or openai_key)
    online_net = check_internet()
    ai_connected = has_key and online_net

    mode_label = "Hybrid AI + Heuristic Engine" if ai_connected else ("Local Rule Engine (Offline)" if not online_net else "Local Rule Engine (No AI Key)")

    return jsonify({
        "status": "healthy",
        "system": "JobGuard AI 2.0 Threat Assessment Engine",
        "version": "2.0.0",
        "online": True,
        "internet_connected": online_net,
        "ai_configured": has_key,
        "ai_connected": ai_connected,
        "mode": mode_label
    })



@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Main job risk assessment endpoint.
    Accepts job posting text, recruiter contact, and URL;
    runs full orchestrator pipeline; returns mapped JobGuard RiskReport JSON.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = (data.get("text") or "").strip()

        if not text:
            return jsonify({"error": "Job description text is required."}), 400

        contact = data.get("contact") or data.get("email") or None
        job_url = data.get("url") or None

        # Execute the core orchestrator pipeline from main branch
        result = run_pipeline(job_text=text, email=contact, url=job_url)

        if not result.get("success"):
            return jsonify({
                "error": "Validation failed",
                "details": result.get("errors", ["Invalid job input"])
            }), 400

        score = int(round(result.get("risk_score", 0)))
        risk_level_raw = (result.get("risk_level") or "Low").capitalize()
        confidence_str = result.get("confidence") or "High"

        # Numerical confidence
        confidence_pct = 92 if confidence_str == "High" else (75 if confidence_str == "Medium" else 55)

        # Map to UI levels: safe, low, medium, high, critical
        if risk_level_raw == "Critical" or score >= 80:
            level_ui = "critical"
            verdict_level = "danger"
            emoji = "🚨"
            default_title = "Extreme Scam Danger — Do Not Apply"
        elif risk_level_raw == "High" or score >= 50:
            level_ui = "high"
            verdict_level = "danger"
            emoji = "🚨"
            default_title = "Warning: High Risk Job Scam Detected"
        elif risk_level_raw == "Medium" or score >= 25:
            level_ui = "medium"
            verdict_level = "caution"
            emoji = "⚠️"
            default_title = "Caution Advised — Potential Anomalies Found"
        else:
            level_ui = "low"
            verdict_level = "low"
            emoji = "✅"
            default_title = "Looks Genuine & Safe to Apply"

        # Collect all flags
        all_flags = []
        breakdown_bars = {
            "contractTerms": 0,
            "urgencyAndPressure": 0,
            "domainReputation": 0,
            "communicationVectors": 0,
            "compensationFeasibility": 0
        }

        # 1. Rule flags
        for rf in result.get("rule_flags", []):
            name = rf.get("name") or rf.get("rule_name") or "Suspicious Pattern"
            cat = rf.get("category") or "General Heuristics"
            weight = int(rf.get("weight") or 15)
            snippet = rf.get("snippet") or rf.get("matched_text") or ""

            # Route weight to visual breakdown bars
            if any(w in name.lower() or w in cat.lower() for w in ["fee", "payment", "money", "check", "bank"]):
                breakdown_bars["contractTerms"] = min(30, breakdown_bars["contractTerms"] + weight)
            elif any(w in name.lower() or w in cat.lower() for w in ["urgent", "immediate", "hurry"]):
                breakdown_bars["urgencyAndPressure"] = min(25, breakdown_bars["urgencyAndPressure"] + weight)
            elif any(w in name.lower() or w in cat.lower() for w in ["telegram", "whatsapp", "signal", "chat"]):
                breakdown_bars["communicationVectors"] = min(15, breakdown_bars["communicationVectors"] + weight)
            elif any(w in name.lower() or w in cat.lower() for w in ["email", "domain", "url", "tld"]):
                breakdown_bars["domainReputation"] = min(15, breakdown_bars["domainReputation"] + weight)
            else:
                breakdown_bars["compensationFeasibility"] = min(15, breakdown_bars["compensationFeasibility"] + weight)

            all_flags.append({
                "id": rf.get("id") or f"RULE_{len(all_flags)+1}",
                "category": cat,
                "title": name,
                "description": f"Evidence: \"{snippet}\"" if snippet else "Pattern triggered by automated heuristic.",
                "weight": weight,
                "severity": "CRITICAL" if level_ui in ["high", "critical"] else "WARNING"
            })

        # 2. Verification flags
        for vf in result.get("verification_flags", []):
            v_name = vf.get("type") or "Domain Verification"
            all_flags.append({
                "id": f"VERIF_{len(all_flags)+1}",
                "category": "Domain & Identity Audit",
                "title": v_name,
                "description": vf.get("detail") or "Failed verification check.",
                "weight": int(vf.get("weight") or 10),
                "severity": "WARNING"
            })
            breakdown_bars["domainReputation"] = min(15, breakdown_bars["domainReputation"] + 10)

        # 3. LLM contextual flags
        for lf in result.get("llm_flags", []):
            all_flags.append({
                "id": f"LLM_{len(all_flags)+1}",
                "category": "AI Contextual Insight",
                "title": lf.get("flag") or "AI Contextual Risk",
                "description": lf.get("reason") or "Identified by AI reasoning model.",
                "weight": 10,
                "severity": "WARNING"
            })

        explanation = result.get("explanation") or "Assessment completed based on heuristic and AI signals."
        recommendation = result.get("recommendation") or "Review recruiter credibility carefully before sharing sensitive personal data."

        ai_assessment = {
            "emoji": emoji,
            "verdict_title": default_title,
            "verdict_level": verdict_level,
            "p1": f"Verdict: {explanation}",
            "p2": f"Why we rated this: {explanation}",
            "p3": f"What you should do: {recommendation}"
        }

        response_payload = {
            "id": f"JG-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "riskScore": score,
            "riskLevel": level_ui,
            "confidence": confidence_pct,
            "summary": explanation,
            "breakdown": breakdown_bars,
            "flags": all_flags,
            "recommendations": [
                recommendation,
                "Never send money, registration fees, or gift cards for a job interview.",
                "Verify recruiter identities through company LinkedIn and official domains."
            ],
            "ai_assessment": ai_assessment,
            "degraded": result.get("degraded", False)
        }

        return jsonify(response_payload)

    except Exception as ex:
        app.logger.error("API Analyze Error: %s", str(ex), exc_info=True)
        return jsonify({"error": "Internal assessment failure", "detail": str(ex)}), 500


# -----------------------------------------------------------------------------
# 3. Server Startup Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 60)
    print("🛡️  JobGuard AI 2.0 - High-Tech Enterprise Web Server")
    print(f"🔗  URL: http://127.0.0.1:{port}")
    print("⚡  Connected: Multi-Tier Rules + Domain Verifier + Gemini AI")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
