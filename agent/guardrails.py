from . import data


def screen_input(message):
    if data.INJECTION_RE.search(message):
        return ("BLOCK", "prompt attack pattern in customer message")
    if data.EXFIL_RE.search(message) and data.EXFIL_DATA_RE.search(message):
        external = [
            e for e in data.EMAIL_RE.findall(message)
            if not e.endswith("@" + data.COMPANY_DOMAIN)
        ]
        if external:
            return ("BLOCK", "exfiltration pattern: send customer data to external address")
    return ("ALLOW", None)


def screen_output(reply):
    masked = reply
    events = []
    if data.SSN_RE.search(masked):
        masked = data.SSN_RE.sub("***-**-****", masked)
        events.append("masked SSN")
    if data.INTERNAL_NOTE_RE.search(masked):
        masked = data.INTERNAL_NOTE_RE.sub("[internal note withheld]", masked)
        events.append("withheld internal note")
    if events:
        return ("MASKED", (masked, ", ".join(events)))
    return ("ALLOW", None)
