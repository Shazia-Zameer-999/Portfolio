import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Shared settings across all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-production"
    SITE_NAME = os.environ.get("SITE_NAME", "Shazia Zameer")
    SITE_TAGLINE = os.environ.get("SITE_TAGLINE", "Building software that matters.")
    SITE_EMAIL = os.environ.get("SITE_EMAIL", "shaziazameer7867@gmail.com")
    SITE_GITHUB = os.environ.get("SITE_GITHUB", "https://github.com/Shazia-Zameer-999" \
    "")
    SITE_LINKEDIN = os.environ.get("SITE_LINKEDIN", "https://www.linkedin.com/in/shazia-zameer-59b149308/")
    SITE_TWITTER = os.environ.get("SITE_TWITTER", "https://twitter.com/yourusername")
    SITE_RESUME_URL = os.environ.get("SITE_RESUME_URL", "/static/assets/Shazia_Zameer_resume.pdf")

    # Mail settings (for contact form)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    # Rate limiting
    CONTACT_RATE_LIMIT = "5 per hour"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

    # Force HTTPS in production
    PREFERRED_URL_SCHEME = "https"

    # Tighter security headers in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
