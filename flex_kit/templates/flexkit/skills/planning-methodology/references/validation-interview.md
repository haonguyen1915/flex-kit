# Validation Interview

Five questions to ask after drafting a plan, before the first implementation step.

1. **What breaks if this assumption is wrong?** Find the most load-bearing assumption
   and its blast radius.
2. **Which step depends on something outside our control?** External APIs, other teams,
   third-party services. What is the contingency?
3. **Where is the rollback hardest?** Which completed step is most difficult to undo - a
   migration, a published API, a deployed service?
4. **What is the first signal this is going wrong?** The earliest observable failure - a
   failing test, a build error, a regression?
5. **Who needs to know before we start?** Stakeholders, dependent teams, reviewers.

If any answer reveals a blocking risk, address it before proceeding. Record the answers
in the plan's `decisions.md` or `## Open Questions`.
