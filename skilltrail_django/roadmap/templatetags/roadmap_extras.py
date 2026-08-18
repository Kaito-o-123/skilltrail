from django import template
from django.utils import timezone

register = template.Library()

BADGE_CLASS_MAP = {
    "not_started": "badge-ink",
    "in_progress": "badge-gold",
    "completed": "badge-moss",
    "suspended": "badge-danger",
}

PRIORITY_CLASS_MAP = {
    "high": "badge-danger",
    "medium": "badge-gold",
    "low": "badge-route",
}


@register.filter
def status_badge(value):
    return BADGE_CLASS_MAP.get(value, "badge-ink")


@register.filter
def priority_badge(value):
    return PRIORITY_CLASS_MAP.get(value, "badge-ink")


@register.filter
def minutes_display(value):
    if not value:
        return "0分"
    value = int(value)
    h, m = divmod(value, 60)
    if h and m:
        return f"{h}時間{m}分"
    if h:
        return f"{h}時間"
    return f"{m}分"


@register.filter
def days_left(value):
    """期限日までの残り日数（マイナスは超過）"""
    if not value:
        return None
    return (value - timezone.localdate()).days


@register.filter
def get_item(d, key):
    return d.get(key)
