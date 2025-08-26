import os
import json
from datetime import datetime

def log_usage(user_msg, bot_msg):
    os.makedirs("logs", exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_msg,
        "bot": bot_msg
    }
    with open("logs/usage_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def save_feedback(user_msg, bot_msg, feedback_type):
    os.makedirs("feedback", exist_ok=True)
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_msg,
        "bot": bot_msg,
        "feedback": feedback_type
    }
    with open("feedback/feedback_log.json", "a") as f:
        f.write(json.dumps(feedback_entry) + "\n")
