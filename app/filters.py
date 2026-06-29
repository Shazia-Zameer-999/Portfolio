"""
Custom Jinja2 filters.
Registered via create_app() in __init__.py.
"""


def slugify(value):
    """Convert 'My Project Name' → 'my-project-name' for HTML IDs."""
    return value.lower().replace(" ", "-").replace("_", "-")


def skill_color(level):
    """Return a CSS class based on skill level for color-coded bars."""
    if level >= 85:
        return "skill--expert"
    elif level >= 70:
        return "skill--proficient"
    elif level >= 55:
        return "skill--comfortable"
    else:
        return "skill--learning"


def timeline_class(event_type):
    """Map timeline event types to CSS modifier classes."""
    mapping = {
        "milestone": "timeline__item--milestone",
        "project": "timeline__item--project",
        "work": "timeline__item--work",
        "education": "timeline__item--education",
        "learning": "timeline__item--learning",
        "goal": "timeline__item--goal",
        "future": "timeline__item--future",
    }
    return mapping.get(event_type, "")


def register_filters(app):
    """Register all custom filters with the Flask app."""
    app.jinja_env.filters["slugify"] = slugify
    app.jinja_env.filters["skill_color"] = skill_color
    app.jinja_env.filters["timeline_class"] = timeline_class
