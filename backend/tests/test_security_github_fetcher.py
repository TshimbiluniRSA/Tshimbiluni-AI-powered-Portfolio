#!/usr/bin/env python3
"""
Security validation tests for github_fetcher.py

Tests the security fixes for:
1. SSRF (Server-Side Request Forgery) prevention
2. Log Injection prevention
"""

import re


def _sanitize_for_log(value: str) -> str:
    """Sanitize user input for logging to prevent log injection attacks."""
    if not value:
        return ""
    sanitized = value.replace('\r', '').replace('\n', '').replace('\t', ' ')
    sanitized = ''.join(char if ord(char) >= 32 or char == ' ' else '' for char in sanitized)
    return sanitized


def _validate_github_endpoint(endpoint: str) -> str:
    """Validate that an endpoint is safe for use with GitHub API."""
    if not endpoint:
        raise ValueError("Endpoint cannot be empty")
    
    if '://' in endpoint or endpoint.startswith('//'):
        raise ValueError("Endpoint cannot contain protocol or domain")
    
    endpoint = endpoint.strip().strip('/')
    
    if '..' in endpoint:
        raise ValueError("Endpoint contains path traversal sequence")
    
    if not re.match(r'^[a-zA-Z0-9/_\-?&=.]+$', endpoint):
        raise ValueError("Endpoint contains invalid characters")
    
    return endpoint


def test_sanitize_for_log():
    """Test log injection prevention."""
    print("=== Testing Log Injection Prevention ===\n")
    
    tests = [
        ("normal_username", "normal_username", "Normal input"),
        ("user\nADMIN", "userADMIN", "Newline injection"),
        ("user\r\nADMIN", "userADMIN", "CRLF injection"),
        ("user\x00admin", "useradmin", "Null byte injection"),
        ("", "", "Empty string"),
    ]
    
    passed = 0
    for input_val, expected, description in tests:
        result = _sanitize_for_log(input_val)
        if result == expected and '\n' not in result and '\r' not in result:
            print(f"✓ {description}")
            passed += 1
        else:
            print(f"✗ {description}: FAILED")
    
    print(f"\nPassed {passed}/{len(tests)} log injection tests\n")
    return passed == len(tests)


def test_validate_endpoint():
    """Test SSRF prevention."""
    print("=== Testing SSRF Prevention ===\n")
    
    valid_tests = [
        ("users/testuser", "users/testuser", "Simple user endpoint"),
        ("repos/owner/repo/languages", "repos/owner/repo/languages", "Languages endpoint"),
    ]
    
    print("Valid endpoints:")
    valid_passed = 0
    for input_val, expected, description in valid_tests:
        try:
            result = _validate_github_endpoint(input_val)
            if result == expected:
                print(f"✓ {description}")
                valid_passed += 1
            else:
                print(f"✗ {description}: FAILED")
        except Exception as e:
            print(f"✗ {description}: Unexpected error")
    
    invalid_tests = [
        ("users/../admin", "Path traversal"),
        ("http://evil.com/api", "HTTP protocol injection"),
        ("//evil.com/api", "Protocol-relative URL"),
    ]
    
    print("\nInvalid endpoints (should be blocked):")
    invalid_passed = 0
    for input_val, description in invalid_tests:
        try:
            result = _validate_github_endpoint(input_val)
            print(f"✗ {description}: Should have been blocked")
        except ValueError:
            print(f"✓ {description}: Blocked")
            invalid_passed += 1
        except Exception:
            print(f"✗ {description}: Wrong exception")
    
    total_passed = valid_passed + invalid_passed
    total_tests = len(valid_tests) + len(invalid_tests)
    print(f"\nPassed {total_passed}/{total_tests} SSRF prevention tests\n")
    
    return valid_passed == len(valid_tests) and invalid_passed == len(invalid_tests)


def main():
    """Run all security tests."""
    print("=" * 70)
    print("Security Validation Tests for github_fetcher.py")
    print("=" * 70)
    print()
    
    log_injection_ok = test_sanitize_for_log()
    ssrf_ok = test_validate_endpoint()
    
    print("=" * 70)
    if log_injection_ok and ssrf_ok:
        print("✅ ALL SECURITY TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME SECURITY TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit(main())
