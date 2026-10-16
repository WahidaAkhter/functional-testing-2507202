"""Smoke test script for live deployment verification.

Waits for the expected commit SHA on the live site and performs live API checks:
1. Health endpoint and deployed commit SHA match
2. Function execution: is_adult(20) -> True
3. Function execution: celsius_to_fahrenheit(100) -> 212.0
4. Exception execution: divide(10, 0) -> ZeroDivisionError
"""

import argparse
import sys
import time
from typing import Optional
import urllib.error
import urllib.parse
import urllib.request
import json


def http_request(
    url: str,
    method: str = "GET",
    data: Optional[dict] = None,
    timeout: int = 10,
):
    """Execute standard HTTP request without third-party dependencies."""
    headers = {"User-Agent": "SmokeTestRunner/1.0"}
    encoded_data = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        encoded_data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=encoded_data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            try:
                parsed_json = json.loads(body)
            except Exception:
                parsed_json = None
            return status_code, parsed_json, body
    except urllib.error.HTTPError as exc:
        status_code = exc.code
        body = exc.read().decode("utf-8")
        try:
            parsed_json = json.loads(body)
        except Exception:
            parsed_json = None
        return status_code, parsed_json, body
    except Exception as exc:
        return None, None, str(exc)


def wait_for_deployment(base_url: str, expected_sha: Optional[str], timeout: int = 180) -> bool:
    """Polls /health until the service is live and matches expected_sha (if provided)."""
    health_url = f"{base_url.rstrip('/')}/health"
    start_time = time.time()
    print(f"[*] Polling health endpoint: {health_url}")
    if expected_sha:
        print(f"[*] Waiting for commit SHA: {expected_sha}")

    while time.time() - start_time < timeout:
        status, json_data, _ = http_request(health_url)
        if status == 200 and json_data and json_data.get("status") == "ok":
            current_sha = json_data.get("commit_sha")
            print(f"[*] Response 200 OK. Current live SHA: {current_sha}")
            if not expected_sha or current_sha == expected_sha:
                print(f"[+] Deployment verified! Matching SHA: {current_sha}")
                return True
        else:
            print(f"[-] Waiting for live server... (status: {status})")

        time.sleep(5)

    print(f"[!] Timed out after {timeout} seconds waiting for deployment.")
    return False


def run_smoke_tests(base_url: str, expected_sha: Optional[str] = None) -> bool:
    """Run all required live smoke test checks."""
    base = base_url.rstrip("/")
    passed = 0
    total = 3

    print("\n" + "=" * 60)
    print("STARTING LIVE SMOKE TESTS (3 Requests Required)")
    print("=" * 60)

    # Check 1: Health & SHA Check
    print("\n[Check 1/3] GET /health")
    status, data, body = http_request(f"{base}/health")
    if status == 200 and data and data.get("status") == "ok":
        live_sha = data.get("commit_sha")
        print(f"  PASS: /health returned 200 OK with commit_sha='{live_sha}'")
        passed += 1
    else:
        print(f"  FAIL: /health returned status={status}, body={body}")

    # Check 2: Execute Valid Function (is_adult)
    print("\n[Check 2/3] POST /api/run -> is_adult(age=20)")
    status, data, body = http_request(
        f"{base}/api/run",
        method="POST",
        data={"function_name": "is_adult", "arguments": {"age": 20}},
    )
    if status == 200 and data and data.get("success") is True and data.get("result") is True:
        print("  PASS: /api/run returned 200 OK with result=True")
        passed += 1
    else:
        print(f"  FAIL: /api/run returned status={status}, body={body}")

    # Check 3: Execute Mathematical Function (celsius_to_fahrenheit)
    print("\n[Check 3/3] POST /api/run -> celsius_to_fahrenheit(celsius=100)")
    status, data, body = http_request(
        f"{base}/api/run",
        method="POST",
        data={"function_name": "celsius_to_fahrenheit", "arguments": {"celsius": 100}},
    )
    if status == 200 and data and data.get("success") is True and data.get("result") == 212.0:
        print("  PASS: /api/run returned 200 OK with result=212.0")
        passed += 1
    else:
        print(f"  FAIL: /api/run returned status={status}, body={body}")

    # Extra Check: Exception handling boundary (divide by zero)
    print("\n[Bonus Check] POST /api/run -> divide(a=10, b=0)")
    status, data, body = http_request(
        f"{base}/api/run",
        method="POST",
        data={"function_name": "divide", "arguments": {"a": 10, "b": 0}},
    )
    if status == 400 and data and data.get("error_type") == "ZeroDivisionError":
        print("  PASS: Live error handling properly returned 400 ZeroDivisionError")
    else:
        print(f"  WARN: /api/run error handling returned status={status}")

    print("\n" + "=" * 60)
    print(f"SMOKE TEST SUMMARY: {passed}/{total} Passed")
    print("=" * 60)

    return passed == total


def main():
    parser = argparse.ArgumentParser(description="Live Deployment Smoke Test")
    parser.add_argument("--url", default="http://localhost:8000", help="Live deployment base URL")
    parser.add_argument("--sha", default=None, help="Expected Git commit SHA to wait for")
    parser.add_argument("--timeout", type=int, default=180, help="Polling timeout in seconds")
    parser.add_argument(
        "--skip-wait", action="store_true", help="Skip polling and run checks immediately"
    )
    args = parser.parse_args()

    if not args.skip_wait and args.sha:
        is_ready = wait_for_deployment(args.url, args.sha, args.timeout)
        if not is_ready:
            print("[ERROR] Deployment was not ready in time.")
            sys.exit(1)

    success = run_smoke_tests(args.url, args.sha)
    if not success:
        print("[ERROR] Smoke tests failed!")
        sys.exit(1)

    print("[SUCCESS] All live smoke tests passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
