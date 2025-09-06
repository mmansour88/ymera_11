
import os, json, base64, hmac, hashlib
from datetime import datetime, timedelta

def sign_post_policy(bucket: str, key_prefix: str, content_type: str, max_mb: int):
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    region = os.getenv("S3_REGION","us-east-1")
    endpoint = os.getenv("S3_ENDPOINT", f"https://{bucket}.s3.{region}.amazonaws.com")
    if not access_key or not secret_key:
        raise RuntimeError("S3 credentials not set")
    expiration = (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    policy_dict = {
        "expiration": expiration,
        "conditions": [
            {"bucket": bucket},
            ["starts-with", "$key", key_prefix],
            {"acl": "private"},
            {"success_action_status": "201"},
            ["starts-with", "$Content-Type", content_type.split('/')[0]],
            ["content-length-range", 1, max_mb*1024*1024],
        ]
    }
    policy = base64.b64encode(json.dumps(policy_dict).encode()).decode()
    signature = base64.b64encode(hmac.new(secret_key.encode(), policy.encode(), hashlib.sha1).digest()).decode()
    return {
        "url": endpoint,
        "fields": {
            "key": f"{key_prefix}${{filename}}",
            "acl": "private",
            "Content-Type": content_type,
            "AWSAccessKeyId": access_key,
            "policy": policy,
            "signature": signature,
            "success_action_status": "201"
        }
    }

def sign_put_url(bucket: str, key: str):
    endpoint = os.getenv("S3_ENDPOINT", f"https://{bucket}.s3.amazonaws.com")
    return f"{endpoint}/{key}"
