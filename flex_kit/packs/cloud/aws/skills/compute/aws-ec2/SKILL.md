---
name: aws-ec2
description: Running AWS EC2 instances well - when to choose EC2 over serverless, the launch/stop/start/terminate lifecycle (stop-vs-terminate + EBS persistence), right-sizing instance types, security groups, SSM Session Manager over SSH, an instance profile + IMDSv2 instead of static keys, and cost (stop when idle, spot). Use when launching/managing an EC2 instance, checking create/stop/terminate, choosing an instance type, or securing instance access. Not for serverless compute (see aws-lambda) or IAM policy detail (see aws-iam).
---

# AWS EC2

EC2 is a virtual server you run and operate. Reach for it only when you need a long-running
host, full OS control, or a stateful/legacy workload - otherwise Lambda (see aws-lambda) or
containers are less to manage. Once you do, the lifecycle and a few secure defaults are what
matter.

## Lifecycle: launch -> stop/start -> terminate

| Action | What happens | Use for |
|---|---|---|
| **launch** (`run-instances`) | a new instance from an AMI + type + security group | create |
| **stop** | halts compute (stops compute billing); **EBS persists**, public IP changes | pause idle |
| **start** | boots a stopped instance again (same EBS) | resume |
| **terminate** | deletes the instance; root EBS removed if `DeleteOnTermination` | dispose |

- **stop ≠ terminate.** Stop keeps the disk and identity (resume later; you still pay for EBS).
  Terminate is permanent - the root volume is gone unless you snapshot it or cleared
  `DeleteOnTermination`.
- A stopped instance's **public IP changes** on restart; attach an **Elastic IP** for a stable
  address.
- Treat instances as **cattle, not pets**: bootstrap via user data / a baked AMI so any
  instance is reproducible, not hand-configured.

## Right-size & cost

- Pick the smallest instance type/family that fits - start small, measure, resize (resizing the
  type needs a stop/start, so design for it).
- **Stop instances when idle** (dev/test) to cut compute cost; **spot** for interruptible batch
  (big discount, can be reclaimed); reserved / savings plans for a steady baseline.

## Access: SSM over SSH

- Prefer **SSM Session Manager** for a shell - no open SSH port, no key file to manage, every
  session logged. Give the instance the SSM role + agent, then `aws ssm start-session`.
- If you must use SSH, use a **key pair** (AWS keeps the public key; you hold the private key
  file - never commit it) and open port 22 only to your own IP, never `0.0.0.0/0`.

## Security defaults

- **Security groups** are stateful allow-lists - open only the ports/sources needed; never
  `0.0.0.0/0` on SSH/RDP/database ports. Reference another security group instead of an IP
  range where you can.
- Give the instance an **instance profile (IAM role)** for AWS access - never put static access
  keys on the box (see aws-iam).
- Require **IMDSv2** (`--metadata-options HttpTokens=required`) - it blocks the SSRF trick that
  steals the instance role's temporary tokens from the metadata endpoint.
- Put instances in **private subnets** where possible; reach them via SSM / a load balancer / a
  bastion, not a public IP.

CLI lifecycle (create / stop / start / terminate / describe): [references/lifecycle.md](references/lifecycle.md).

## Review checklist

- [ ] EC2 is justified over Lambda/containers (long-running, OS control, stateful)
- [ ] stop vs terminate chosen deliberately; root volume snapshotted before terminate if needed
- [ ] instance type right-sized; idle dev instances stopped; spot for interruptible work
- [ ] access via SSM Session Manager; if SSH, port 22 limited to your IP + a privately held key
- [ ] security group opens only needed ports/sources, no `0.0.0.0/0` on admin ports
- [ ] instance profile (role) for AWS access; no static keys on the host; IMDSv2 required

## Red Flags

- a security group with `0.0.0.0/0` on port 22 / 3389 / a database port
- static access keys copied onto the instance instead of an instance profile
- IMDSv1 left enabled (metadata tokens stealable via SSRF)
- terminating an instance with unsnapshotted data on the root volume
- a long-lived pet instance configured by hand, impossible to reproduce
- an idle dev instance left running 24/7, billing for nothing
