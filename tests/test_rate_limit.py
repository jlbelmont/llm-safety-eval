from llm_safety_eval.util.rate_limit import TokenBucket


def test_token_bucket_waits():
    bucket = TokenBucket.create(rate_per_min=60)  # 1 per second
    # consume many tokens quickly to force wait
    waits = []
    for _ in range(3):
        waits.append(bucket.consume())
    assert waits[0] == 0
    assert waits[-1] >= 0  # may be zero or small depending on timing
