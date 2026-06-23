# A worked Lambda handler + IaC

Thin handler, init at module scope, structured logging, least-privilege role wired in IaC.

## Handler (Python)

```python
import json, logging, os
import boto3

# --- init once, at module scope: reused on warm invocations, runs during cold start ---
s3 = boto3.client("s3")
logger = logging.getLogger()
logger.setLevel("INFO")
RECEIPT_BUCKET = os.environ["RECEIPT_BUCKET"]   # config from env, set by IaC

def lambda_handler(event, context):
    """Thin: parse the event, delegate, shape the response."""
    try:
        order_id = event["order_id"]
        store_receipt(order_id, event["amount"], event["item"])
        logger.info(json.dumps({"msg": "receipt stored", "order_id": order_id}))
        return {"statusCode": 200}
    except KeyError as e:
        logger.error(json.dumps({"msg": "bad event", "missing": str(e)}))
        raise                                   # let Lambda record the failure + retry/DLQ

def store_receipt(order_id: str, amount: float, item: str) -> None:
    """Plain core - unit-testable without Lambda (inject a fake s3 client in tests)."""
    body = f"OrderID: {order_id}\nAmount: ${amount}\nItem: {item}"
    s3.put_object(Bucket=RECEIPT_BUCKET, Key=f"receipts/{order_id}.txt", Body=body)
```

Test `store_receipt` directly; the handler only wires `event -> core -> response`.

## IaC (AWS SAM) - role + env + timeout in one place

```yaml
Resources:
  ReceiptFn:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      Runtime: python3.12
      MemorySize: 512          # CPU scales with memory - measure, don't guess
      Timeout: 10              # near the p99, not the 15-minute max
      Environment:
        Variables:
          RECEIPT_BUCKET: !Ref ReceiptBucket
      Policies:                # SAM generates a scoped execution role from this
        - S3CrudPolicy:
            BucketName: !Ref ReceiptBucket
```

Prefer a scoped policy (`S3CrudPolicy` on one bucket) or an inline statement over a broad
managed policy - the function should reach only the resources it uses (see aws-iam).

## Structured logging with Powertools

In production, AWS Lambda Powertools gives a JSON `Logger`, `Tracer`, and `Metrics` (with a
cold-start metric) instead of hand-rolling `json.dumps`:

```python
from aws_lambda_powertools import Logger

logger = Logger()              # structured JSON + correlation id

@logger.inject_lambda_context
def lambda_handler(event, context):
    logger.info("processing", order_id=event["order_id"])
    ...
```
