import os
import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
import resend
from email_validator import validate_email, EmailNotValidError
import requests
import json
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

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
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY
# ─────────────────────────────────────────────────────────────────────────────
# Simple in-memory rate limiter (no Redis dependency for a single-server portfolio)
# ─────────────────────────────────────────────────────────────────────────────
from collections import defaultdict
import time

_rate_limit_store = defaultdict(list)
RATE_LIMIT_MAX = 5  # requests
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
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Too many requests. Please wait before trying again.",
                    }
                ),
                429,
            )

        _rate_limit_store[ip].append(now)
        return f(*args, **kwargs)

    return decorated


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio data — centralised here so Jinja gets it injected automatically.
# ─────────────────────────────────────────────────────────────────────────────

PORTFOLIO_DATA = {
    "projects": [
        {
            "id": "project-1",
            "title": "BitLinks",
            "tagline": "A full-stack URL shortener with custom aliases, dynamic redirects, and integrated contact workflow.",
            "description": (
                "BitLinks is a modern full-stack URL shortening application built with "
                "Next.js, MongoDB, and Resend. Users can generate memorable short links "
                "using custom aliases, while the application validates duplicate aliases, "
                "stores mappings in MongoDB Atlas, and performs dynamic server-side redirects. "
                "The project also includes a secure contact form that persists messages to "
                "MongoDB and sends email notifications through Resend, demonstrating "
                "full-stack API development, database integration, and responsive UI design."
            ),
            "tech": [
                "Next.js",
                "React",
                "JavaScript",
                "MongoDB Atlas",
                "Mongoose",
                "Resend",
                "Tailwind CSS",
                "Framer Motion",
                "Vercel",
            ],
            "challenges": [
                "Implementing dynamic routing for seamless short URL redirection using the Next.js App Router.",
                "Preventing duplicate custom aliases while maintaining consistent database integrity.",
                "Designing reusable API routes for URL generation, validation, storage, and email handling.",
                "Integrating MongoDB Atlas and Resend into a secure server-side workflow.",
            ],
            "decisions": [
                "Used MongoDB Atlas with Mongoose to efficiently store and query URL mappings.",
                "Leveraged Next.js API Routes instead of a separate backend to simplify deployment and architecture.",
                "Integrated Resend for reliable transactional email delivery from the contact form.",
                "Deployed the application on Vercel for seamless CI/CD and production hosting.",
            ],
            "image": "/static/assets/images/projects/bitlinks.png",
            "live_url": "https://bitlinks.datendiva.me",
            "github_url": "https://github.com/Shazia-Zameer-999/BitLinks",
            "featured": True,
        },
        {
            "id": "project-2",
            "title": "Linktree Clone",
            "tagline": "A full-stack link-in-bio platform with custom profiles, dynamic routing, and MongoDB persistence.",
            "description": (
                "Developed a full-stack Linktree-inspired web application that enables users "
                "to create personalized public profile pages using unique handles. The platform "
                "supports profile customization with bios, profile images, and multiple external "
                "links while persisting user data in MongoDB. Built using the Next.js App Router, "
                "the application includes secure server-side validation, dynamic routing, responsive "
                "design, and modern animations to deliver a polished user experience."
            ),
            "tech": [
                "Next.js",
                "React",
                "JavaScript",
                "MongoDB",
                "Tailwind CSS",
                "GSAP",
                "Typed.js",
                "React Toastify",
                "React Icons",
                "Vercel",
            ],
            "challenges": [
                "Implementing dynamic public profile pages using unique handles with the Next.js App Router.",
                "Preventing duplicate usernames while validating user input on the server.",
                "Supporting both remote profile image URLs and local image uploads while maintaining input constraints.",
                "Designing a responsive UI that provides a consistent experience across desktop and mobile devices.",
            ],
            "decisions": [
                "Used MongoDB to persist user profiles and link collections for scalable data storage.",
                "Leveraged Next.js Route Handlers instead of a separate backend to simplify deployment and application architecture.",
                "Implemented reusable server-side validation utilities to sanitize profile data before database insertion.",
                "Integrated GSAP and Typed.js to enhance the landing page with smooth animations while keeping the builder experience lightweight.",
            ],
            "image": "/static/assets/images/projects/linktree-clone.png",
            "live_url": "https://linktree.datendiva.me",
            "github_url": "https://github.com/Shazia-Zameer-999/Linktree",
            "featured": True,
        },
        {
            "id": "project-3",
            "title": "Get Me a Chai",
            "tagline": "A full-stack creator funding platform with OAuth authentication, Razorpay payments, and personalized creator pages.",
            "description": (
                "Get Me a Chai is a full-stack creator support platform built with "
                "Next.js, MongoDB, NextAuth, and Razorpay. The application enables "
                "creators to build personalized public pages where supporters can send "
                "one-time payments through Razorpay Test Mode. It features OAuth "
                "authentication, creator profile management, secure payment verification, "
                "dynamic public routes, supporter history, and MongoDB-backed data "
                "persistence, demonstrating modern full-stack architecture, authentication "
                "workflows, payment gateway integration, and responsive UI development."
            ),
            "tech": [
                "Next.js",
                "React",
                "JavaScript",
                "MongoDB",
                "Mongoose",
                "NextAuth.js",
                "Razorpay",
                "Tailwind CSS",
                "Framer Motion",
                "React Toastify",
                "Vercel",
            ],
            "challenges": [
                "Implementing secure OAuth authentication with multiple providers using NextAuth.js.",
                "Integrating Razorpay Test Mode with server-side order creation and payment signature verification.",
                "Managing dynamic creator pages while maintaining consistent supporter records after username changes.",
                "Designing a responsive dashboard for profile management, payment settings, and live creator page updates.",
            ],
            "decisions": [
                "Used Next.js App Router with Server Actions to simplify the full-stack architecture and reduce API boilerplate.",
                "Stored creator profiles and payment records in MongoDB using Mongoose for efficient querying and data consistency.",
                "Integrated NextAuth.js to provide secure OAuth authentication and session management across the application.",
                "Implemented server-side Razorpay signature verification to ensure payment authenticity before updating transaction records.",
            ],
            "image": "/static/assets/images/projects/getmeachai.png",
            "live_url": "https://buymeachai.datendiva.me",
            "github_url": "https://github.com/Shazia-Zameer-999/get-me-a-chai",
            "featured": True,
        },
        {
            "id": "project-4",
            "title": "Headless Shopify Store",
            "tagline": "A modern headless e-commerce storefront powered by Shopify, Sanity CMS, Next.js, and MongoDB with authentication, wishlist, and persistent carts.",
            "description": (
                "Headless Shopify Store is a full-stack e-commerce application built with "
                "Next.js App Router, Shopify Storefront API, Sanity CMS, MongoDB, and NextAuth. "
                "The application separates content management, commerce, and authentication into "
                "independent services to deliver a fast, scalable shopping experience. Customers "
                "can browse products, search the catalog, manage authenticated or guest carts, "
                "maintain wishlists, securely sign in using multiple authentication providers, "
                "view order history, and complete purchases through Shopify's hosted checkout. "
                "Sanity powers dynamic homepage content while MongoDB persists user accounts, "
                "wishlists, and cart synchronization for authenticated users."
            ),
            "tech": [
                "Next.js",
                "React",
                "JavaScript",
                "Shopify Storefront API",
                "Shopify Admin API",
                "NextAuth",
                "MongoDB Atlas",
                "Mongoose",
                "Sanity CMS",
                "Tailwind CSS",
                "Framer Motion",
                "Vercel",
            ],
            "challenges": [
                "Building a fully headless storefront while seamlessly integrating Shopify's Storefront and Admin APIs.",
                "Synchronizing guest carts with authenticated user accounts using MongoDB without losing cart state.",
                "Implementing secure authentication with Google, GitHub, and credentials using NextAuth.",
                "Managing product search, wishlist persistence, order retrieval, and dynamic homepage content across multiple services.",
            ],
            "decisions": [
                "Used the Shopify Storefront API for product catalog, search, cart operations, and checkout while leveraging the Admin API for customer order retrieval.",
                "Integrated Sanity CMS to decouple marketing content from commerce, enabling independent content management.",
                "Persisted authenticated carts and wishlists in MongoDB while maintaining cookie-based storage for guest users.",
                "Deployed the storefront on Vercel and configured Shopify checkout on a dedicated subdomain for a scalable headless architecture.",
            ],
            "image": "/static/assets/images/projects/headless-shopify.png",
            "live_url": "https://shop.datendiva.me",
            "github_url": "https://github.com/Shazia-Zameer-999/shopify_demo",
            "featured": True,
        },
        {
            "id": "project-5",
            "title": "ShazBlog",
            "tagline": "A production-ready blogging platform with OAuth authentication, article publishing, and secure content management.",
            "description": (
                "ShazBlog is a full-stack publishing platform built with Flask, MongoDB, "
                "and Bootstrap. Users can authenticate using local accounts or Google, "
                "GitHub, LinkedIn, and Facebook OAuth, publish and manage articles, "
                "upload cover images and profile avatars, participate in discussions "
                "through authenticated comments, and manage personalized profiles. "
                "The application stores uploaded media in MongoDB GridFS, implements "
                "role-based authorization, CSRF protection, secure session handling, "
                "search, category filtering, pagination, and a persistent contact system, "
                "demonstrating production-ready backend architecture, authentication, "
                "database design, and responsive user experience."
            ),
            "tech": [
                "Flask",
                "Python",
                "MongoDB Atlas",
                "PyMongo",
                "GridFS",
                "Jinja2",
                "Bootstrap 5",
                "JavaScript",
                "OAuth 2.0",
                "Google OAuth",
                "GitHub OAuth",
                "LinkedIn OAuth",
                "Facebook OAuth",
                "Gunicorn",
                "Render",
            ],
            "challenges": [
                "Implementing secure authentication with local login alongside multiple OAuth providers.",
                "Designing role-based authorization to ensure users can only manage their own content.",
                "Persisting uploaded images using MongoDB GridFS instead of the local filesystem for deployment compatibility.",
                "Building scalable article management with search, category filters, pagination, and draft/publish workflows.",
            ],
            "decisions": [
                "Used Flask with Jinja2 to create a lightweight, server-rendered architecture with minimal client-side complexity.",
                "Stored application data and uploaded media in MongoDB Atlas using GridFS for persistent cloud storage.",
                "Implemented OAuth authentication alongside traditional login to improve user accessibility and flexibility.",
                "Applied CSRF protection, secure session management, validation, and ownership-based authorization to strengthen application security.",
            ],
            "image": "/static/assets/images/projects/shazblog.png",
            "live_url": "https://shazblog.datendiva.me/",
            "github_url": "https://github.com/Shazia-Zameer-999/flask-blog",
            "featured": True,
        },
    ],
    "timeline": [
        {
            "year": "2023",
            "title": "A Curious Beginning",
            "description": "Started exploring programming with one simple question: ‘How does software actually work?’ That curiosity eventually became a habit.",
            "icon": "code",
            "type": "milestone",
        },
        {
            "year": "2023",
            "title": "Learning by Building",
            "description": "Built small projects, broke them countless times, and slowly realized that debugging teaches more than tutorials ever can.",
            "icon": "rocket",
            "type": "project",
        },
        {
            "year": "2024",
            "title": "First Freelance Clients",
            "description": "Worked with real clients, delivered production projects, and learned what it means to write software that other people depend on.",
            "icon": "briefcase",
            "type": "work",
        },
        {
            "year": "2025",
            "title": "Choosing Flask Over Convenience",
            "description": "Moved away from frameworks that hid too much behind abstractions. Chose Flask to understand authentication, routing, databases, sessions, and the web from the ground up.",
            "icon": "server",
            "type": "learning",
        },
        {
            "year": "2026",
            "title": "Thinking Like an Engineer",
            "description": "Started focusing on Data Structures & Algorithms—not to solve interview questions, but to learn how experienced engineers approach problems.",
            "icon": "chart",
            "type": "education",
        },
        {
            "year": "2026",
            "title": "Building with Purpose",
            "description": "Every new project became an opportunity to learn architecture, deployment, scalability, and writing cleaner code instead of simply adding another repository.",
            "icon": "trending",
            "type": "project",
        },
        {
            "year": "Today",
            "title": "Always Learning",
            "description": "Currently building backend applications with Flask, improving problem-solving skills through DSA, and exploring system design one concept at a time.",
            "icon": "globe",
            "type": "goal",
        },
        {
            "year": "Next",
            "title": "Building Software That Matters",
            "description": "My goal isn’t just to work at a great company—it’s to become the kind of engineer who can build reliable systems that make a real difference.",
            "icon": "star",
            "type": "future",
        },
    ],
    "freelancer": {
        "profile_url": "https://www.freelancer.com/u/shaziaz17",
        "rating": 5.0,
        "review_count": 3,
        # Verified from the public Freelancer profile. Keep this local fallback
        # available even if a future API sync is unavailable.
        "reviews": [
            {
                "reviewer": "Gary G.",
                "country": "Canada",
                "country_code": "CA",
                "rating": 5.0,
                "project": "Email Account Setup via SSH on VPS Linux Server",
                "review": (
                    "Shazia is very knowledgeable and professional worker. She "
                    "completed the project very quickly and provided extra support "
                    "that was needed. I would highly recommend her to anyone using "
                    "freelancer.com. She is an asset to this website. Looking forward "
                    "to working again in the future!"
                ),
                "date_label": "5 months ago",
            },
            {
                "reviewer": "Siva S.",
                "country": "India",
                "country_code": "IN",
                "rating": 5.0,
                "project": "React Scrollytelling Timeline Component",
                "review": "Awesome work!!! Delivered within time.",
                "date_label": "7 months ago",
            },
            {
                "reviewer": "Maria M.",
                "country": "Austria",
                "country_code": "AT",
                "rating": 5.0,
                "project": "Solve Undergraduate Math Problems Mathematica -- 2",
                "review": (
                    "She’s the sweetest person ever, highly recommend to work with! "
                    "I had many questions and she answered them all, my project was a "
                    "pretty long request and it only took about 2 hours, no regrets at all! <3"
                ),
                "date_label": "7 months ago",
            },
        ],
    },
    "skills": {
        "Languages": [
            {"name": "Python", "level": 92},
            {"name": "JavaScript", "level": 78},
            {"name": "SQL", "level": 80},
        ],
        "Backend": [
            {"name": "Flask", "level": 92},
            {"name": "REST APIs", "level": 88},
            {"name": "MongoDB", "level": 90},
            {"name": "Mongoose", "level": 78},
            {"name": "PostgreSQL", "level": 65},
        ],
        "Frontend": [
            {"name": "HTML/CSS", "level": 85},
            {"name": "Vanilla JavaScript", "level": 78},
            {"name": "React", "level": 78},
            {"name": "Next.js", "level": 78},
            {"name": "Tailwind CSS", "level": 82},
            {"name": "Jinja Templates", "level": 90},
        ],
        "Project Stacks": [
            {"name": "Next.js App Router", "level": 78},
            {"name": "Server Actions", "level": 72},
            {"name": "NextAuth.js", "level": 75},
            {"name": "Shopify Storefront API", "level": 70},
            {"name": "Shopify Admin API", "level": 65},
            {"name": "Sanity CMS", "level": 68},
            {"name": "Razorpay", "level": 66},
            {"name": "Resend", "level": 72},
            {"name": "Framer Motion", "level": 70},
            {"name": "GSAP", "level": 68},
        ],
        "Tools & Platforms": [
            {"name": "Git / GitHub", "level": 88},
            {"name": "Linux", "level": 75},
            {"name": "Render", "level": 80},
            {"name": "Vercel", "level": 82},
            {"name": "OAuth", "level": 75},
        ],
        "CS Fundamentals": [
            {"name": "Data Structures", "level": 82},
            {"name": "Algorithms", "level": 75},
            {"name": "OOP", "level": 88},
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
        "total_solved": 50,
        "easy": 15,
        "medium": 25,
        "hard": 10,
        "streak": 20,
        "platforms": ["LeetCode", "Codeforces", "HackerRank"],
        "favorite_topics": [
            "Dynamic Programming",
            "Linked Lists",
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
        "reading": "Designing Data-Intensive Applications",
        "building": "Full-stack web applications with Flask and Next.js",
        "learning": "Data Structures & Algorithms",
        "open_to": "Backend & Full-Stack Internships",
    },
}


def _unique_technologies(*technology_groups):
    """Return technologies in display order without duplicate labels."""
    return list(dict.fromkeys(tech for group in technology_groups for tech in group))


# Keep portfolio-wide technology displays in sync with both the skills grid and
# every project. Adding a technology to a future project automatically includes
# it in the Skills section and technology marquee.
PORTFOLIO_DATA["project_techs"] = _unique_technologies(
    *(project["tech"] for project in PORTFOLIO_DATA["projects"])
)
PORTFOLIO_DATA["portfolio_techs"] = _unique_technologies(
    *(
        [skill["name"] for skill in skills]
        for skills in PORTFOLIO_DATA["skills"].values()
    )
)
PORTFOLIO_DATA["portfolio_techs"] = _unique_technologies(
    PORTFOLIO_DATA["portfolio_techs"], PORTFOLIO_DATA["project_techs"]
)


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
        return send_from_directory(resume_dir, "Shazia_Zameer.pdf", as_attachment=False)
    except FileNotFoundError:
        abort(404)



def update_all_leetcode_stats(username="shazia-zameer-999", top_n=5):
    url = "https://leetcode.com/graphql"
    
    # 1. ONE combined GraphQL query asking for solved counts, streaks, and topics
    payload = {
        "query": """
        query getCombinedLeetCodeStats($username: String!) {
            matchedUser(username: $username) {
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
                userCalendar {
                    streak
                }
                tagProblemCounts {
                    advanced { tagName problemsSolved }
                    intermediate { tagName problemsSolved }
                    fundamental { tagName problemsSolved }
                }
            }
        }
        """,
        "variables": {
            "username": username
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # 2. Extract all the data from the single response
        user_data = data.get("data", {}).get("matchedUser", {})
        if not user_data:
            print("User data not found")
            return

        stats = user_data.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        streak = user_data.get("userCalendar", {}).get("streak", 0)
        tag_counts = user_data.get("tagProblemCounts", {})
        
        # 3. Process the top topics
        all_topics = (
            tag_counts.get("advanced", []) + 
            tag_counts.get("intermediate", []) + 
            tag_counts.get("fundamental", [])
        )
        sorted_topics = sorted(all_topics, key=lambda x: x["problemsSolved"], reverse=True)
        top_topics_list = [item['tagName'] for item in sorted_topics[:top_n]]
        
        # 4. Update the dictionary all at once
        if len(stats) >= 4:
            PORTFOLIO_DATA["dsa_stats"]["total_solved"] = stats[0]["count"]
            PORTFOLIO_DATA["dsa_stats"]["easy"] = stats[1]["count"]
            PORTFOLIO_DATA["dsa_stats"]["medium"] = stats[2]["count"]
            PORTFOLIO_DATA["dsa_stats"]["hard"] = stats[3]["count"]
            
        PORTFOLIO_DATA["dsa_stats"]["streak"] = streak
        PORTFOLIO_DATA["dsa_stats"]["favorite_topics"] = top_topics_list
        
        print(f"Background Update Success! Total: {stats[0]['count']}, Streak: {streak}")
        
    except Exception as e:
        print(f"Failed to update LeetCode stats in background: {e}")


# 5. Create ONLY ONE scheduler instance
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_leetcode_stats, trigger="interval", minutes=15)
scheduler.start()

# Shut down the scheduler cleanly on exit
atexit.register(lambda: scheduler.shutdown())

# Run it once immediately so the data is ready on startup
update_all_leetcode_stats()


# 6. Provide a single unified endpoint
@main.route("/api/leetcode-stats")
def leetcode_stats():
    # Since both of your previous endpoints returned PORTFOLIO_DATA["dsa_stats"],
    # you only need one route to serve everything to your frontend.
    return PORTFOLIO_DATA["dsa_stats"]
# def update_leetcode_stats_job():
#     url = "https://leetcode.com/graphql"
#     payload = "{\"query\":\"query userProblemsSolved($username: String!) {\\r\\n    allQuestionsCount {    \\r\\n        difficulty    \\r\\n        count  \\r\\n        }\\r\\n        matchedUser(username: $username) {\\r\\n            problemsSolvedBeatsStats { \\r\\n                difficulty\\r\\n                percentage    \\r\\n                }\\r\\n        submitStatsGlobal {\\r\\n            acSubmissionNum {        \\r\\n                difficulty        \\r\\n                count      \\r\\n                    }    \\r\\n                }  \\r\\n            }             \\r\\n        }\\r\\n\",\"variables\":{\"username\":\"shazia-zameer-999\"}}"
#     headers = {'Content-Type': 'application/json'}
    
#     try:
#         response = requests.post(url, headers=headers, data=payload)
#         data = response.json()
        
#         stats = data["data"]["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
        
#         PORTFOLIO_DATA["dsa_stats"]["total_solved"] = stats[0]["count"]
#         PORTFOLIO_DATA["dsa_stats"]["easy"] = stats[1]["count"]
#         PORTFOLIO_DATA["dsa_stats"]["medium"] = stats[2]["count"]
#         PORTFOLIO_DATA["dsa_stats"]["hard"] = stats[3]["count"]
        
#         print(f"Background Update: LeetCode stats synced! Total: {stats[0]['count']}")
#     except Exception as e:
#         print(f"Failed to update LeetCode stats in background: {e}")

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=update_leetcode_stats_job, trigger="interval", minutes=15)
# scheduler.start()

# atexit.register(lambda: scheduler.shutdown())

# update_leetcode_stats_job()

# @main.route("/api/leetcode-stats")
# def leetcode_stats():

#     return PORTFOLIO_DATA["dsa_stats"]


# def leecode_streaks():
#     url="https://leetcode.com/graphql"
#     payload = "{\"query\":\"query \\r\\nuserProfileCalendar($username: String!, $year: Int) {\\r\\n    matchedUser(username: $username) {    \\r\\n        userCalendar(year: $year) {\\r\\n            activeYears\\r\\n            streak      \\r\\n            totalActiveDays      \\r\\n            dccBadges {        \\r\\n                timestamp        \\r\\n                badge {          \\r\\n                    name          \\r\\n                    icon\\r\\n                    }\\r\\n                }\\r\\n            submissionCalendar \\r\\n            }\\r\\n        }\\r\\n    } \",\"variables\":{\"username\":\"shazia-zameer-999\"}}"
#     headers = {
#     'Content-Type': 'application/json'
#     }
#     try:
#         response = requests.post(url, headers=headers, data=payload)
#         data = response.json()
        
#         stats = data["data"]["matchedUser"]["userCalendar"]["streak"]
#         print(stats)
#         PORTFOLIO_DATA["dsa_stats"]["streak"] = stats
#         print(f"Background Update: LeetCode stats synced! Total: {stats}")
#     except Exception as e:
#         print(f"Failed to update LeetCode stats in background: {e}")

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=leecode_streaks, trigger="interval", minutes=15)
# scheduler.start()

# atexit.register(lambda: scheduler.shutdown())

# leecode_streaks()

# @main.route("/api/leetcode_streaks")
# def leetcode_stats2():
#     return PORTFOLIO_DATA["dsa_stats"]


# def get_top_leetcode_topics(username="shazia-zameer-999", top_n=5):
#     url = "https://leetcode.com/graphql"
    
#     # The GraphQL query to fetch tag problem counts
#     payload = {
#         "query": """
#         query skillStats($username: String!) {
#             matchedUser(username: $username) {
#                 tagProblemCounts {
#                     advanced {
#                         tagName
#                         problemsSolved
#                     }
#                     intermediate {
#                         tagName
#                         problemsSolved
#                     }
#                     fundamental {
#                         tagName
#                         problemsSolved
#                     }
#                 }
#             }
#         }
#         """,
#         "variables": {
#             "username": username
#         }
#     }
    
#     headers = {
#         'Content-Type': 'application/json'
#     }
    
#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()
#         data = response.json()
        
#         tag_counts = data.get("data", {}).get("matchedUser", {}).get("tagProblemCounts", {})
        
#         if not tag_counts:
#             return {"error": "User data not found"}
        
#         all_topics = (
#             tag_counts.get("advanced", []) + 
#             tag_counts.get("intermediate", []) + 
#             tag_counts.get("fundamental", [])
#         )
        
#         sorted_topics = sorted(all_topics, key=lambda x: x["problemsSolved"], reverse=True)

#         data=sorted_topics[:top_n]
#         topics_list=[]
#         for item in data:
#             topics_list.append(item['tagName'])
#         PORTFOLIO_DATA["dsa_stats"]["favorite_topics"] = topics_list

#         return sorted_topics[:top_n]
        
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return []
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=get_top_leetcode_topics, trigger="interval", minutes=15)
# scheduler.start()

# atexit.register(lambda: scheduler.shutdown())
# get_top_leetcode_topics()

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

    data = request.get_json()
    if not data:

        return (
            jsonify(
                {"success": False, "message": "Invalid request. JSON data is required."}
            ),
            400,
        )
    required_fields = ["name", "email", "subject", "message"]
    for field in required_fields:

        if field not in data:

            return (
                jsonify(
                    {"success": False, "message": f"{field.capitalize()} is missing."}
                ),
                400,
            )
    name = data["name"].strip()

    email = data["email"].strip()

    subject = data["subject"].strip()

    message = data["message"].strip()
    if not name:
        return jsonify({"success": False, "message": "Name cannot be empty."}), 400

    if not email:
        return jsonify({"success": False, "message": "Email cannot be empty."}), 400

    if not subject:
        return jsonify({"success": False, "message": "Subject cannot be empty."}), 400

    if not message:
        return jsonify({"success": False, "message": "Message cannot be empty."}), 400
    if len(name) < 2 or len(name) > 100:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Name must be between 2 and 100 characters.",
                }
            ),
            400,
        )

    if len(subject) > 150:
        return (
            jsonify(
                {"success": False, "message": "Subject must not exceed 150 characters."}
            ),
            400,
        )

    if len(message) < 10:
        return jsonify({"success": False, "message": "Message is too short."}), 400

    if len(message) > 3000:
        return jsonify({"success": False, "message": "Message is too long."}), 400

    try:

        valid = validate_email(email)

        email = valid.normalized

    except EmailNotValidError:

        return (
            jsonify(
                {"success": False, "message": "Please enter a valid email address."}
            ),
            400,
        )
    try:
        resend.Emails.send(
            {
                "from": "Shazia's Portfolio <onboarding@resend.dev>",
                "to": "shaziazameer7867@gmail.com",
                "reply_to": email,
                "subject": f"Portfolio Contact: {subject}",
                "html": f"""
            <h2>New Portfolio Contact</h2>

            <p><strong>Name:</strong> {name}</p>

            <p><strong>Email:</strong> {email}</p>

            <p><strong>Subject:</strong> {subject}</p>

            <p><strong>Message:</strong></p>

            <p>{message}</p>
        """,
            }
        )
        return jsonify({"success": True, "message": "Email sent successfully."}), 200

    except Exception as e:

        return jsonify({"success": False, "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# SEO: Sitemap + Robots
# ─────────────────────────────────────────────────────────────────────────────


@main.route("/sitemap.xml")
def sitemap():
    """
    Generates a simple XML sitemap for SEO purposes.
    This is a static sitemap based on the main portfolio sections.
    """
    base_url = os.environ.get("SITE_URL", "https://shaziazameer.dev")
    pages = [
        {"loc": base_url, "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{base_url}/#about", "priority": "0.8", "changefreq": "monthly"},
        {"loc": f"{base_url}/#projects", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{base_url}/#contact", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{base_url}/resume", "priority": "0.6", "changefreq": "monthly"},
    ]

    xml_items = "\n".join([f"""  <url>
    <loc>{p['loc']}</loc>
    <priority>{p['priority']}</priority>
    <changefreq>{p['changefreq']}</changefreq>
  </url>""" for p in pages])

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
Sitemap: {os.environ.get('SITE_URL', 'https://shaziazameer.dev')}/sitemap.xml
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
    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }
    )


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
