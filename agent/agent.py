from . import data, guardrails, model, policy, screening, tools

PROFILES = {
    1: "no_defenses",
    2: "guardrails",
    3: "isolation",
    4: "gateway_policy",
}


class RunResult:
    def __init__(self, profile, message, reply, events, sink):
        self.profile = profile
        self.message = message
        self.reply = reply
        self.events = events
        self.sink = sink


def _wants_kb(message):
    import re

    return re.search(r"\breturn|policy|broken|how\b", message, re.IGNORECASE) is not None


def run(profile, message):
    events = []
    sink = tools.Sink()

    if profile >= 2:
        decision, detail = guardrails.screen_input(message)
        events.append({"layer": "guardrail_input", "decision": decision, "detail": detail})
        if decision == "BLOCK":
            return RunResult(
                profile,
                message,
                "I can't process that request. Please contact human support.",
                events,
                sink,
            )

    kb_results = []
    if _wants_kb(message):
        articles = tools.search_kb(message)
        if profile >= 3:
            kept, screen_events = screening.screen_articles(articles)
            for decision, detail in screen_events:
                events.append({"layer": "tool_result_screen", "decision": decision, "detail": detail})
            kb_results = kept
        else:
            kb_results = articles

    calls, refusal = model.decide_calls(message, kb_results)
    if refusal:
        return RunResult(profile, message, refusal, events, sink)

    results = []
    customer = None
    for call in calls:
        name = call["name"]
        args = call["args"]
        if profile >= 4:
            decision, detail = policy.check_call(name, args)
            events.append({"layer": "gateway_policy", "decision": decision, "detail": detail})
            if decision == "DENY":
                results.append({"status": "denied"})
                continue
        if name == "lookup_customer":
            customer = tools.lookup_customer(args["customer_id"])
            results.append({"status": "allowed", "customer": customer})
        elif name == "search_kb":
            articles = tools.search_kb(args["query"])
            if profile >= 3:
                articles, _ = screening.screen_articles(articles)
            results.append({"status": "allowed", "articles": articles})
        elif name == "send_email":
            tools.send_email(sink, args["to"], args["body"])
            results.append({"status": "allowed"})
        elif name == "issue_refund":
            tools.issue_refund(sink, args["order_id"], args["amount"])
            results.append({"status": "allowed"})

    reply = model.compose_reply(message, calls, results, customer)

    if profile >= 2:
        decision, payload = guardrails.screen_output(reply)
        if decision == "MASKED":
            reply, detail = payload
            events.append({"layer": "guardrail_output", "decision": "MASKED", "detail": detail})
        else:
            events.append({"layer": "guardrail_output", "decision": "ALLOW", "detail": None})

    return RunResult(profile, message, reply, events, sink)
