# Red-Team Personas

Four adversarial lenses for a drafted plan. Apply each in sequence; write 2-3 specific
challenges per lens. Fix the critical ones before implementing; record the rest under
`## Risks`.

### Security Adversary
- What is the attack surface? Any secrets, credentials, or tokens that could leak?
- Does any step grant broader access than necessary?

### Assumption Destroyer
- What untested beliefs does the plan rely on?
- Which implicit dependencies could break silently? Which "obvious" facts are unverified?

### Failure-Mode Analyst
- What cascade failures could this trigger?
- If a step fails halfway, what state is left behind? Is there a clean rollback?

### Scope Critic
- Any gold-plating (features beyond the goal) or premature abstraction?
- Does the plan deliver the minimum viable scope, or over-engineer?
