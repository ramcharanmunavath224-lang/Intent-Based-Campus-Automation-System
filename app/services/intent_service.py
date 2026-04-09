from datetime import datetime, timedelta
import re


def detect_intent(message):
    msg = message.lower()

    leave_keywords = [
        "leave",
        "absent",
        "permission",
        "not attend",
        "miss class",
        "miss classes",
        "time off",
        "won't come",
        "cannot attend",
    ]

    if any(keyword in msg for keyword in leave_keywords):
        return "leave"
    if "bonafide" in msg:
        return "bonafide"
    return "unknown"


def extract_leave_details(message):
    raw_message = message.strip()
    lowered = raw_message.lower()
    today = datetime.today()

    reason = "personal work"
    leave_category = "general"
    time_slot = "full_day"

    category_keywords = {
        "medical": ["fever", "sick", "ill", "headache", "doctor", "hospital", "checkup", "medical", "treatment", "clinic", "dental"],
        "family_function": [
            "family function", "wedding", "marriage", "ceremony", "engagement", "family event",
            "cousin wedding", "sister marriage", "brother marriage", "function at home", "family gathering"
        ],
        "academic_event": ["seminar", "workshop", "conference", "presentation", "technical event", "competition"],
        "personal_work": ["personal work", "bank", "document", "passport", "official work", "urgent work"],
        "travel": ["travel", "journey", "train", "bus", "flight", "hometown", "going home"],
        "emergency": ["emergency", "urgent", "immediate", "critical"],
    }

    for category, keywords in category_keywords.items():
        if any(keyword in lowered for keyword in keywords):
            leave_category = category
            reason = keywords[0] if category in {"medical", "family_function", "academic_event"} else category.replace("_", " ")
            break

    reason_patterns = [
        r"because of ([a-z0-9 ,'-]+)",
        r"due to ([a-z0-9 ,'-]+)",
        r"for ([a-z0-9 ,'-]+)",
    ]
    for pattern in reason_patterns:
        match = re.search(pattern, lowered)
        if match:
            extracted = match.group(1).strip(" .")
            if extracted:
                reason = extracted
                break

    if "first half" in lowered or "morning" in lowered:
        time_slot = "morning"
    elif "second half" in lowered or "afternoon" in lowered:
        time_slot = "afternoon"
    elif "evening" in lowered:
        time_slot = "evening"

    time_range_match = re.search(
        r"from\s+(\d{1,2}\s*(?:am|pm))\s+to\s+(\d{1,2}\s*(?:am|pm))",
        lowered
    )
    if not time_range_match:
        time_range_match = re.search(
            r"between\s+(\d{1,2}\s*(?:am|pm))\s+and\s+(\d{1,2}\s*(?:am|pm))",
            lowered
        )
    if time_range_match:
        start_time = time_range_match.group(1).upper().replace(" ", "")
        end_time = time_range_match.group(2).upper().replace(" ", "")
        time_slot = f"{start_time} to {end_time}"
    else:
        after_match = re.search(r"after\s+(\d{1,2}\s*(?:am|pm))", lowered)
        before_match = re.search(r"before\s+(\d{1,2}\s*(?:am|pm))", lowered)
        if after_match:
            time_slot = f"After {after_match.group(1).upper().replace(' ', '')}"
        elif before_match:
            time_slot = f"Before {before_match.group(1).upper().replace(' ', '')}"

    if "day after tomorrow" in lowered:
        start_date = today + timedelta(days=2)
    elif "tomorrow" in lowered:
        start_date = today + timedelta(days=1)
    else:
        weekday_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        start_date = today
        for weekday_name, weekday_number in weekday_map.items():
            if weekday_name in lowered:
                days_ahead = (weekday_number - today.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                start_date = today + timedelta(days=days_ahead)
                break

    duration_days = 1
    duration_match = re.search(r"\b(\d+)\s+days?\b", lowered)
    if duration_match:
        duration_days = max(1, int(duration_match.group(1)))

    end_date = start_date + timedelta(days=duration_days - 1)

    return {
        "raw_message": raw_message,
        "reason": reason.title() if reason.islower() else reason,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "leave_category": leave_category,
        "time_slot": time_slot,
    }
