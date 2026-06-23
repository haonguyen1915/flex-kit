---
name: aws-iam
description: AWS IAM done securely - least-privilege policies, roles over users, short-lived role tokens over long-lived access keys, policy structure (Effect/Action/Resource/Condition), execution roles for Lambda/EC2, and scoping by resource ARN. Use when writing IAM policies/roles, granting a service access on AWS, or reviewing AWS permissions. Not for app-level authn/authz (see fastapi-auth) or agnostic threat modeling (see the security- pack).
---

# AWS IAM

IAM is where most AWS breaches start. The rule that prevents them: **grant the least
privilege that works, to a role, with short-lived tokens** - never a broad policy on a
long-lived access key.

## Prefer roles + short-lived tokens

- Give a **workload a role**, not an IAM user with static keys: a Lambda/ECS/EC2 **execution
  role** hands the code short-lived tokens automatically, rotated by AWS. Nothing to leak.
- Humans federate via an identity provider (IAM Identity Center / SSO) for short-lived access;
  reserve IAM users for the rare programmatic case, always with MFA.
- **Never put a long-lived access key in code, an env var, or a repo.** The execution-role
  path removes the key entirely; if a static key must exist, scope it hard and rotate it.

## Least privilege

- Start from an AWS **managed policy** to move fast, then **narrow to a customer policy** scoped
  to your use case - grant only the actions a task needs.
- Scope to the **resource ARN**, not `"Resource": "*"`: `s3:GetObject` on
  `arn:aws:s3:::my-bucket/*`, not all of S3.
- Use **IAM Access Analyzer** to generate a least-privilege policy from real CloudTrail
  activity, validate policies, and flag public / cross-account access.

## Policy structure

A policy is JSON statements of `Effect` + `Action` + `Resource` (+ optional `Condition`):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::my-bucket/*",
    "Condition": { "Bool": { "aws:SecureTransport": "true" } }
  }]
}
```

- **Condition** tightens further: require TLS (`aws:SecureTransport`), MFA
  (`aws:MultiFactorAuthPresent`), a source VPC, an account, or a tag.
- An explicit **`Deny` always wins** over an `Allow` - use it for hard guardrails.

## Roles & assume-role

- A **role** has a *trust policy* (who may assume it) + *permission policies* (what it can do).
  A service assumes its execution role; cross-account access is `sts:AssumeRole` with the
  target account as principal plus an MFA / `ExternalId` condition.
- **Permission boundaries** cap the maximum a delegated role/user can be granted - use them to
  let a team self-manage within a ceiling.

## Review checklist

- [ ] workloads use an execution **role**, not a static access key
- [ ] no long-lived key in code / env / repo; humans use federated short-lived access
- [ ] every statement scoped to a resource ARN, not `"*"`
- [ ] actions limited to what the task needs (started managed, then narrowed)
- [ ] conditions enforce TLS / MFA / account where they apply
- [ ] Access Analyzer validates the policy; unused users/roles/keys removed

## Red Flags

- a long-lived access key committed, in an env var, or baked into an image
- `"Resource": "*"` or `"Action": "*"` (or `s3:*`) on anything but a deliberate admin role
- an IAM user with static keys where an execution role would work
- the root user used for daily work, or any principal without MFA
- a policy never narrowed from the broad AWS managed one it started at
