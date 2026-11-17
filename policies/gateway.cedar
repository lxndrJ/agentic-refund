// Cedar policy for the AgentCore Gateway in front of the refund agent.
// This is the layer-4 rule set; agent/policy.py mirrors it for the offline demo.
// Any tool call not matched by a permit clause is denied by default.

permit (
  principal == AgentCore::Agent::"refund-agent",
  action == AgentCore::Action::"search_kb",
  resource
);

permit (
  principal == AgentCore::Agent::"refund-agent",
  action == AgentCore::Action::"lookup_customer",
  resource
);

permit (
  principal == AgentCore::Agent::"refund-agent",
  action == AgentCore::Action::"issue_refund",
  resource
)
when {
  context.refund.amount <= 50
};

permit (
  principal == AgentCore::Agent::"refund-agent",
  action == AgentCore::Action::"send_email",
  resource
)
when {
  context.email.recipient.endsWith("@acme-shop.example")
};
