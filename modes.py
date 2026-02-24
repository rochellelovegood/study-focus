def get_message(mode, status):
    messages = {
        "asian_mom": {
            "phone": "PUT THAT PHONE DOWN! You want to be a failure?!",
            "away": "I don't see you studying! Where did you go?!",
            "multiple_people": "WHO IS THAT?! Why are you talking?! NO TALKING, ONLY STUDYING!",
            "focus": "Good. Keep your eyes on the book."
        }
    }
    return messages[mode].get(status, "Keep working!")