from . import data

REFUND_LIMIT = 50


def check_call(name, args):
    if name == "issue_refund":
        amount = args.get("amount", 0)
        if amount > REFUND_LIMIT:
            return ("DENY", f"issue_refund: amount {amount} exceeds limit {REFUND_LIMIT}")
        return ("ALLOW", None)
    if name == "send_email":
        to = args.get("to", "")
        if not to.endswith("@" + data.COMPANY_DOMAIN):
            return ("DENY", f"send_email: recipient {to} outside company domain")
        return ("ALLOW", None)
    return ("ALLOW", None)
