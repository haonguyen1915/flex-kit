---
name: aws-s3
description: Using AWS S3 safely - block public access by default, default server-side encryption, enforce TLS, least-privilege bucket policies, presigned URLs for temporary access, key/prefix design, versioning, and lifecycle/storage classes. Use when creating or reviewing an S3 bucket, storing/serving objects, or sharing a file. Not for IAM policy basics (see aws-iam) or DynamoDB (see aws-dynamodb).
---

# AWS S3

S3 is durable object storage that goes *public-by-mistake* more than any other service. Lock
it down first - block public access, encrypt, force TLS - then design keys and lifecycle.

## Secure defaults (every bucket)

- **Block Public Access** - turn on all four (`BlockPublicAcls`, `IgnorePublicAcls`,
  `BlockPublicPolicy`, `RestrictPublicBuckets`). A bucket is private unless there's a real
  reason; serve public content through CloudFront, not a public bucket.
- **Encryption** - S3 now applies default encryption (`SSE-S3`/AES256) to new objects
  automatically; keep it on and verify it isn't disabled. Choose `SSE-KMS` when you need key
  control + an audit trail.
- **Enforce TLS** - a bucket policy that `Deny`s `s3:*` when `aws:SecureTransport` is false.
- **Versioning** - enable for recovery from overwrite/delete; pair with lifecycle to expire
  old versions.
- **Disable ACLs** - set Object Ownership to *Bucket owner enforced*; control access with the
  bucket policy + IAM, not per-object ACLs.

## Access: least privilege + presigned URLs

- Grant access via a **bucket policy / IAM** scoped to a prefix
  (`arn:aws:s3:::bucket/uploads/*`) and only the actions needed, not bucket-wide.
- For temporary client up/download, **don't make the object public** - issue a **presigned
  URL** that expires. Generate it server-side with the app's role.

```python
url = s3.generate_presigned_url(
    "get_object",
    Params={"Bucket": "my-bucket", "Key": key},
    ExpiresIn=300,                              # short - minutes, not days
)
```

## Key & prefix design

- The **key** is the path; design prefixes for how you list and scope
  (`tenant/123/invoices/...`). S3 scales per-prefix automatically; prefixes still matter for
  organization and policy scoping.
- Don't store data you'd query in the key and then `list` to find it - that's a database's job
  (see aws-dynamodb).

## Lifecycle & cost

- Add **lifecycle rules** to transition cold objects (Standard -> IA -> Glacier) and to expire
  temp data and old versions. Storage class is the main S3 cost lever.

## Review checklist

- [ ] Block Public Access on (all four); no public bucket for app data
- [ ] default server-side encryption enabled
- [ ] bucket policy denies non-TLS requests (`aws:SecureTransport=false`)
- [ ] versioning on; lifecycle expires old versions / temp data
- [ ] ACLs disabled (bucket-owner-enforced); access via policy + IAM
- [ ] object access scoped to a prefix; sharing via short-lived presigned URLs

## Red Flags

- a bucket made public (or a `"Principal": "*"` policy) to "make it work"
- an object URL handed out as if permanent instead of a presigned, expiring one
- no default encryption, or no TLS-enforcing bucket policy
- `s3:*` on `arn:aws:s3:::*` in an app role (see aws-iam)
- `ListObjects` + key parsing used as a query engine instead of a database
- versioning off on a bucket holding anything you'd hate to lose to an overwrite
