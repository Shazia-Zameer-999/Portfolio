import os
import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    current_app,
    make_response,
    abort,
    send_from_directory,
)

main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Simple in-memory rate limiter (no Redis dependency for a single-server portfolio)
# ─────────────────────────────────────────────────────────────────────────────
from collections import defaultdict
import time

_rate_limit_store = defaultdict(list)
RATE_LIMIT_MAX = 5       # requests
RATE_LIMIT_WINDOW = 3600  # seconds (1 hour)


def rate_limit(f):
    """Decorator: max RATE_LIMIT_MAX calls per IP per RATE_LIMIT_WINDOW seconds."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW

        # Prune old timestamps
        _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > window_start]

        if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
            return jsonify({
                "success": False,
                "message": "Too many requests. Please wait before trying again.",
            }), 429

        _rate_limit_store[ip].append(now)
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio data — centralised here so Jinja gets it injected automatically.
# Swap this with a DB or JSON file as your portfolio grows.
# ─────────────────────────────────────────────────────────────────────────────

PORTFOLIO_DATA = {
    "projects": [
        {
            "id": "project-1",
            "title": "Project Alpha",
            "tagline": "A full-stack application that does X at scale",
            "description": (
                "Describe the problem you solved, why it mattered, "
                "and the engineering decisions that made it work."
            ),
            "tech": ["Python", "Flask", "PostgreSQL", "React", "Docker"],
            "challenges": [
                "Handling N concurrent users with < 200ms response time",
                "Designing a schema that could evolve without downtime",
            ],
            "decisions": [
                "Chose PostgreSQL over MongoDB for ACID guarantees",
                "Used Redis for session caching to reduce DB load by 40%",
            ],
            "image": "/static/assets/images/projects/project-1.jpg",
            "live_url": "https://example.com",
            "github_url": "https://github.com/yourusername/project-alpha",
            "featured": True,
        },
        {
            "id": "project-2",
            "title": "Project Beta",
            "tagline": "An open-source tool that developers actually use",
            "description": (
                "Built to scratch my own itch — a CLI tool that automates "
                "something every backend developer does manually."
            ),
            "tech": ["Python", "Click", "SQLite", "GitHub Actions"],
            "challenges": [
                "Cross-platform compatibility (Windows, macOS, Linux)",
                "Zero-config setup for first-time users",
            ],
            "decisions": [
                "Used Click over argparse for composable command trees",
                "Shipped a single binary via PyInstaller",
            ],
            "image": "/static/assets/images/projects/project-2.jpg",
            "live_url": None,
            "github_url": "https://github.com/yourusername/project-beta",
            "featured": True,
        },
        {
            "id": "project-3",
            "title": "Project Gamma",
            "tagline": "A data pipeline that processes X million records/day",
            "description": (
                "Built a real-time ETL pipeline for a freelance client, "
                "replacing a brittle spreadsheet workflow."
            ),
            "tech": ["Python", "Pandas", "Airflow", "GCP", "BigQuery"],
            "challenges": [
                "Data quality: 30% of source records were malformed",
                "Client's team had zero data engineering experience",
            ],
            "decisions": [
                "Used Airflow DAGs for visibility and retry logic",
                "Built a simple validation dashboard so the client could self-serve",
            ],
            "image": "/static/assets/images/projects/project-3.jpg",
            "live_url": None,
            "github_url": "https://github.com/yourusername/project-gamma",
            "featured": False,
        },
    ],

    "timeline": [
        {
            "year": "2021",
            "title": "First Line of Code",
            "description": "Wrote Hello World in Python. Didn't sleep for two days after.",
            "icon": "code",
            "type": "milestone",
        },
        {
            "year": "2022",
            "title": "Built First Real Project",
            "description": "A web scraper that actually solved a problem. Realized software could do real things.",
            "icon": "rocket",
            "type": "project",
        },
        {
            "year": "2022",
            "title": "Started Freelancing",
            "description": "First paid project. A small automation script for a local business. ₹3,000 and infinite confidence.",
            "icon": "briefcase",
            "type": "work",
        },
        {
            "year": "2023",
            "title": "Enrolled in BTech",
            "description": "Computer Science. Started taking algorithms seriously. Data Structures became a daily ritual.",
            "icon": "graduation",
            "type": "education",
        },
        {
            "year": "2023",
            "title": "Discovered Flask",
            "description": "Built my first backend API. Understood how the web actually works under the hood.",
            "icon": "server",
            "type": "learning",
        },
        {
            "year": "2024",
            "title": "Serious DSA Grind",
            "description": "300+ LeetCode problems. Not for the badge — to think in algorithms, not just code.",
            "icon": "chart",
            "type": "milestone",
        },
        {
            "year": "2024",
            "title": "Freelance Revenue Crossed ₹X Lakhs",
            "description": "Multiple clients. Real production systems. Learned more from this than any course.",
            "icon": "trending",
            "type": "work",
        },
        {
            "year": "2025",
            "title": "International Internship Prep Begins",
            "description": "Researching IAESTE, Google STEP, Microsoft Explore. Preparing OA, system design, and behaviorals.",
            "icon": "globe",
            "type": "goal",
        },
        {
            "year": "2025 →",
            "title": "The Goal",
            "description": "An internship at a company that builds things at scale. Anywhere in the world.",
            "icon": "star",
            "type": "future",
        },
    ],

    "skills": {
        "Languages": [
            {"name": "Python", "level": 90},
            {"name": "JavaScript", "level": 75},
            {"name": "C++", "level": 70},
            {"name": "SQL", "level": 80},
            {"name": "Bash", "level": 65},
        ],
        "Backend": [
            {"name": "Flask", "level": 88},
            {"name": "REST APIs", "level": 85},
            {"name": "PostgreSQL", "level": 78},
            {"name": "Redis", "level": 65},
            {"name": "Docker", "level": 70},
        ],
        "Frontend": [
            {"name": "HTML/CSS", "level": 82},
            {"name": "Vanilla JS", "level": 75},
            {"name": "React", "level": 60},
        ],
        "Tools & Platforms": [
            {"name": "Git / GitHub", "level": 88},
            {"name": "Linux", "level": 78},
            {"name": "GCP", "level": 60},
            {"name": "Nginx", "level": 65},
        ],
        "CS Fundamentals": [
            {"name": "Data Structures", "level": 85},
            {"name": "Algorithms", "level": 82},
            {"name": "System Design", "level": 68},
            {"name": "OOP", "level": 85},
        ],
    },

    "achievements": [
        {
            "title": "300+ LeetCode Problems",
            "description": "Consistent daily practice. Focus on patterns, not memorization.",
            "icon": "code",
        },
        {
            "title": "X Freelance Projects Delivered",
            "description": "Real clients, real deadlines, real production systems.",
            "icon": "briefcase",
        },
        {
            "title": "Open Source Contributor",
            "description": "N pull requests merged across M repositories.",
            "icon": "github",
        },
        {
            "title": "Hackathon — Top N%",
            "description": "Name of hackathon, what was built, what was learned.",
            "icon": "trophy",
        },
    ],

    "dsa_stats": {
        "total_solved": 300,
        "easy": 120,
        "medium": 145,
        "hard": 35,
        "streak": 47,
        "platforms": ["LeetCode", "Codeforces", "HackerRank"],
        "favorite_topics": [
            "Dynamic Programming",
            "Graph Algorithms",
            "Binary Search",
            "Tree Traversal",
            "Sliding Window",
        ],
    },

    "internship_prep": {
        "programs": [
            {
                "name": "Google STEP / SWE Intern",
                "status": "preparing",
                "notes": "Online assessment + behavioral + technical interviews",
            },
            {
                "name": "IAESTE",
                "status": "researching",
                "notes": "Technical work placement exchange — 50+ countries",
            },
            {
                "name": "Microsoft Explore",
                "status": "preparing",
                "notes": "PM + SWE hybrid program for pre-final year students",
            },
            {
                "name": "Outreachy",
                "status": "considering",
                "notes": "Open source internship — paid, remote, inclusive",
            },
        ],
        "preparation_areas": [
            "Data Structures & Algorithms (LeetCode Medium/Hard)",
            "System Design (Grokking, Donne Martin)",
            "Behavioral interviews (STAR method, leadership stories)",
            "Resume and application optimization",
            "Cold outreach and networking",
        ],
        "target_regions": ["USA", "Europe", "Singapore", "Remote"],
    },

    "currently": {
        "reading": "Designing Data-Intensive Applications — Martin Kleppmann",
        "building": "This portfolio",
        "learning": "System Design fundamentals",
        "open_to": "International internships for Summer 2026",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Context processor — injects site config into every template automatically
# ─────────────────────────────────────────────────────────────────────────────

@main.app_context_processor
def inject_site_config():
    return {
        "site": {
            "name": current_app.config["SITE_NAME"],
            "tagline": current_app.config["SITE_TAGLINE"],
            "email": current_app.config["SITE_EMAIL"],
            "github": current_app.config["SITE_GITHUB"],
            "linkedin": current_app.config["SITE_LINKEDIN"],
            "twitter": current_app.config["SITE_TWITTER"],
            "resume_url": current_app.config["SITE_RESUME_URL"],
            "year": datetime.now().year,
        },
        "data": PORTFOLIO_DATA,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main routes
# ─────────────────────────────────────────────────────────────────────────────

@main.route("/")
def index():
    """Main portfolio page — the single page application shell."""
    return render_template("index.html")


@main.route("/resume")
def resume():
    """Direct resume download / view."""
    resume_dir = os.path.join(current_app.static_folder, "assets")
    try:
        return send_from_directory(resume_dir, "resume.pdf", as_attachment=False)
    except FileNotFoundError:
        abort(404)


# ─────────────────────────────────────────────────────────────────────────────
# Contact form API endpoint
# ─────────────────────────────────────────────────────────────────────────────

@main.route("/api/contact", methods=["POST"])
@rate_limit
def contact():
    """
    Handles contact form submissions.
    Returns JSON — the frontend handles display.
    Validates, sanitizes, then sends email via SMTP.
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "message": "Invalid request format."}), 400

    # Validate fields
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    errors = {}

    if not name or len(name) < 2:
        errors["name"] = "Name must be at least 2 characters."
    if len(name) > 100:
        errors["name"] = "Name is too long."

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        errors["email"] = "Please enter a valid email address."
    if len(email) > 200:
        errors["email"] = "Email is too long."

    if not subject or len(subject) < 3:
        errors["subject"] = "Subject must be at least 3 characters."
    if len(subject) > 200:
        errors["subject"] = "Subject is too long."

    if not message or len(message) < 10:
        errors["message"] = "Message must be at least 10 characters."
    if len(message) > 5000:
        errors["message"] = "Message is too long (max 5000 characters)."

    if errors:
        return jsonify({"success": False, "errors": errors}), 422

    # Send email
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")

    if mail_username and mail_password:
        try:
            _send_email(
                mail_username=mail_username,
                mail_password=mail_password,
                mail_server=current_app.config["MAIL_SERVER"],
                mail_port=current_app.config["MAIL_PORT"],
                to_email=mail_username,
                from_name=name,
                from_email=email,
                subject=f"[Portfolio] {subject}",
                message=message,
            )
        except Exception as e:
            logger.error(f"Failed to send contact email: {e}")
            # Don't expose internal errors to the client
            return jsonify({
                "success": False,
                "message": "Failed to send your message. Please email me directly.",
            }), 500
    else:
        # Log in dev mode when email isn't configured
        logger.info(
            f"[DEV — no email configured] Contact from {name} <{email}>: {subject}"
        )

    return jsonify({
        "success": True,
        "message": "Message sent! I'll get back to you within 24 hours.",
    })


def _send_email(
    mail_username, mail_password, mail_server, mail_port,
    to_email, from_name, from_email, subject, message
):
    """Pure function: sends a plain-text email via SMTP TLS."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = mail_username
    msg["To"] = to_email
    msg["Reply-To"] = from_email

    body_text = f"From: {from_name} <{from_email}>\n\n{message}"
    body_html = f"""
    <html><body>
    <p><strong>From:</strong> {from_name} &lt;{from_email}&gt;</p>
    <hr>
    <p>{message.replace(chr(10), '<br>')}</p>
    </body></html>
    """

    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(mail_server, mail_port) as server:
        server.ehlo()
        server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(mail_username, to_email, msg.as_string())


# ─────────────────────────────────────────────────────────────────────────────
# SEO: Sitemap + Robots
# ─────────────────────────────────────────────────────────────────────────────

@main.route("/sitemap.xml")
def sitemap():
    """
    Auto-generated XML sitemap.
    Add your custom domain to SITE_URL in .env.
    """
    base_url = os.environ.get("SITE_URL", "https://yourname.dev")
    pages = [
        {"loc": base_url, "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{base_url}/#about", "priority": "0.8", "changefreq": "monthly"},
        {"loc": f"{base_url}/#projects", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{base_url}/#contact", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{base_url}/resume", "priority": "0.6", "changefreq": "monthly"},
    ]

    xml_items = "\n".join([
        f"""  <url>
    <loc>{p['loc']}</loc>
    <priority>{p['priority']}</priority>
    <changefreq>{p['changefreq']}</changefreq>
  </url>"""
        for p in pages
    ])

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_items}
</urlset>"""

    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@main.route("/robots.txt")
def robots():
    robots_txt = f"""User-agent: *
Allow: /
Sitemap: {os.environ.get('SITE_URL', 'https://yourname.dev')}/sitemap.xml
Disallow: /api/
"""
    response = make_response(robots_txt)
    response.headers["Content-Type"] = "text/plain"
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Health check — useful for uptime monitors and deployment pipelines
# ─────────────────────────────────────────────────────────────────────────────

@main.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────────────────────────────────────

@main.app_errorhandler(404)
def not_found(e):
    return render_template("index.html"), 200  # SPA: always serve index


@main.app_errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}")
    return jsonify({"error": "Internal server error"}), 500
