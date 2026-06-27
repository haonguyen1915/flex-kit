# EC2 lifecycle - CLI

Create, inspect, pause, and dispose an instance. The same calls exist in boto3
(`ec2.run_instances`, `stop_instances`, ...).

## Launch (with secure defaults)

```bash
aws ec2 run-instances \
  --image-id ami-0abc... \                 # an AMI (e.g. latest Amazon Linux via an SSM param)
  --instance-type t3.micro \               # start small, resize after measuring
  --security-group-ids sg-0abc... \        # opens only needed ports (no 0.0.0.0/0 on 22)
  --subnet-id subnet-0abc... \             # a private subnet where possible
  --iam-instance-profile Name=app-role \   # role for AWS access - no static keys on the box
  --metadata-options HttpTokens=required \ # IMDSv2 only (blocks SSRF token theft)
  --user-data file://bootstrap.sh \        # reproducible setup at first boot
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=app}]' \
  --query 'Instances[0].InstanceId' --output text
```

## Inspect state

```bash
aws ec2 describe-instances \
  --instance-ids i-0abc... \
  --query 'Reservations[].Instances[].State.Name' --output text
# pending | running | stopping | stopped | shutting-down | terminated
```

## Stop / start (keeps EBS; resume later)

```bash
aws ec2 stop-instances  --instance-ids i-0abc...
aws ec2 start-instances --instance-ids i-0abc...

# block until the transition completes:
aws ec2 wait instance-stopped --instance-ids i-0abc...
aws ec2 wait instance-running --instance-ids i-0abc...
```

## Terminate (permanent)

```bash
# snapshot the volume first if the data matters:
aws ec2 create-snapshot --volume-id vol-0abc... --description "pre-terminate"
aws ec2 terminate-instances --instance-ids i-0abc...
```

## Shell without SSH - SSM Session Manager

```bash
# instance has the SSM role + agent; no open port 22, no key file, session is logged
aws ssm start-session --target i-0abc...
```

Stop an instance when idle (dev/test) to stop compute billing; terminate only ephemeral
instances whose data is reproducible or already snapshotted.
