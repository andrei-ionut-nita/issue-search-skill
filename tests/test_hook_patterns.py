#!/usr/bin/env python3
"""
Test suite for hook issue pattern matching.

Validates that the on_prompt_error hook correctly:
1. Detects issue-related prompts (128+ cases)
2. Avoids false positives (greetings, praise, neutral discussion)
3. Handles ambiguous cases appropriately

Run with: python3 -m pytest tests/test_hook_patterns.py -v
Or directly: python3 tests/test_hook_patterns.py
"""
import re
import sys


# Copy of pattern logic from on_prompt_error.py
ISSUE_PATTERNS = re.compile(
    r"(traceback|exception|error:|nameerror|typeerror|valueerror|"
    r"syntaxerror|importerror|filenotfounderror|exit code [1-9]|"
    r"failed|failing|crash|crashed|broken|doesn't work|doesn't|not working|"
    r"(?<!no\s)(?<!no\s)bug|(?<!no\s)problem|wrong|incorrect|undefined|can't|unable to|stopped|stopped working|"
    r"doesn't handle|not handling|not following|not respecting|inconsistent)",
    re.IGNORECASE
)

FALSE_POSITIVE_PATTERNS = [
    r"can't\s+wait",
    r"unable\s+to\s+contain",
    r"broken\s+(?:down|out)",
    r"break(?:ing)?\s+down",
    r"stopped\s+(?:raining|snowing|hailing)",
    r"for\s+maintenance",
    r"by\s+design",
    r"on\s+purpose",
    r"intentional",
    r"is\s+expected",
]


def should_match_prompt(prompt):
    """Determine if prompt describes a real issue."""
    if not ISSUE_PATTERNS.search(prompt):
        return False
    for fp_pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(fp_pattern, prompt, re.IGNORECASE):
            return False
    return True


# Test cases: (prompt, should_match, category, description)
TEST_CASES = [
    # ============================================================
    # POSITIVE CASES — Code Errors (10)
    # ============================================================
    ("Traceback (most recent call last):", True, "code_error", "Python traceback"),
    ("NameError: name 'foo' is not defined", True, "code_error", "NameError"),
    ("TypeError: expected string, got int", True, "code_error", "TypeError"),
    ("ValueError: invalid literal", True, "code_error", "ValueError"),
    ("SyntaxError: invalid syntax", True, "code_error", "SyntaxError"),
    ("ImportError: cannot import module", True, "code_error", "ImportError"),
    ("FileNotFoundError: file not found", True, "code_error", "FileNotFoundError"),
    ("Exception: something went wrong", True, "code_error", "Generic Exception"),
    ("error: something failed", True, "code_error", "Generic error:"),
    ("Exit code 1 returned", True, "code_error", "Exit code"),

    # ============================================================
    # POSITIVE CASES — Functional Issues (20)
    # ============================================================
    ("The button is broken", True, "functional", "broken"),
    ("This feature is completely broken", True, "functional", "broken (emphatic)"),
    ("The app crashed on startup", True, "functional", "crashed"),
    ("The server crashed", True, "functional", "crashed (server)"),
    ("It failed to connect", True, "functional", "failed"),
    ("The login failed", True, "functional", "failed (action)"),
    ("Tests are failing", True, "functional", "failing (tests)"),
    ("It crashed with a segfault", True, "functional", "crashed (specific)"),
    ("Build failed", True, "functional", "failed (build)"),
    ("The deployment crashed", True, "functional", "crashed (deployment)"),
    ("The search doesn't work", True, "functional", "doesn't work"),
    ("Why doesn't the dark mode work?", True, "functional", "doesn't work (question)"),
    ("It doesn't work on Firefox", True, "functional", "doesn't work (conditional)"),
    ("Not working as expected", True, "functional", "not working"),
    ("Dark mode is not working", True, "functional", "not working (feature)"),
    ("The API doesn't work", True, "functional", "doesn't work (API)"),
    ("It doesn't work at all", True, "functional", "doesn't work (emphatic)"),
    ("Login doesn't work anymore", True, "functional", "doesn't work (regression)"),
    ("The plugin doesn't work", True, "functional", "doesn't work (plugin)"),
    ("Not working correctly", True, "functional", "not working (quality)"),

    # ============================================================
    # POSITIVE CASES — Bug Reports (10)
    # ============================================================
    ("There's a bug in the search", True, "bug", "bug (straightforward)"),
    ("Found a bug with dates", True, "bug", "bug (with context)"),
    ("Critical bug in production", True, "bug", "bug (severity)"),
    ("I found a problem", True, "bug", "problem (vague)"),
    ("There's a problem with the form", True, "bug", "problem (specific)"),
    ("Memory problem detected", True, "bug", "problem (type)"),
    ("Database problem", True, "bug", "problem (system)"),
    ("The problem is in the config", True, "bug", "problem (location)"),
    ("Security problem found", True, "bug", "problem (category)"),
    ("UI problem on mobile", True, "bug", "problem (platform)"),

    # ============================================================
    # POSITIVE CASES — Styling / Frontend (10)
    # ============================================================
    ("The search bar is not following dark mode styling", True, "ui", "not following (styling)"),
    ("The header is not respecting the theme", True, "ui", "not respecting (theme)"),
    ("Styling is inconsistent", True, "ui", "inconsistent (styling)"),
    ("The colors are inconsistent across pages", True, "ui", "inconsistent (color)"),
    ("Button styling is broken on mobile", True, "ui", "broken (styling)"),
    ("The layout doesn't follow the design system", True, "ui", "doesn't follow (design)"),
    ("Navbar not following responsive guidelines", True, "ui", "not following (responsive)"),
    ("Icons are inconsistent", True, "ui", "inconsistent (icons)"),
    ("The theme doesn't handle dark mode correctly", True, "ui", "doesn't handle (theme)"),
    ("Fonts are not respecting the CSS rules", True, "ui", "not respecting (CSS)"),

    # ============================================================
    # POSITIVE CASES — Action Failures (10)
    # ============================================================
    ("Can't connect to the database", True, "action", "can't (connect)"),
    ("Can't authenticate", True, "action", "can't (auth)"),
    ("Unable to parse the response", True, "action", "unable to (parse)"),
    ("Can't find the file", True, "action", "can't (find)"),
    ("Unable to read the config", True, "action", "unable to (read)"),
    ("Can't load the module", True, "action", "can't (load)"),
    ("Unable to execute the query", True, "action", "unable to (execute)"),
    ("Can't serialize the object", True, "action", "can't (serialize)"),
    ("Unable to start the service", True, "action", "unable to (start)"),
    ("Can't decode the message", True, "action", "can't (decode)"),

    # ============================================================
    # POSITIVE CASES — Process/State Issues (8)
    # ============================================================
    ("The service stopped", True, "functional", "stopped"),
    ("It stopped working after the update", True, "functional", "stopped working"),
    ("The job stopped unexpectedly", True, "functional", "stopped (unexpected)"),
    ("The process stopped responding", True, "functional", "stopped (responding)"),
    ("Cache stopped working", True, "functional", "stopped working (cache)"),
    ("The scheduler stopped", True, "functional", "stopped (scheduler)"),
    ("Worker stopped processing", True, "functional", "stopped (worker)"),
    ("Queue stopped accepting messages", True, "functional", "stopped (queue)"),

    # ============================================================
    # POSITIVE CASES — Logic/Data Issues (12)
    # ============================================================
    ("The results are wrong", True, "logic", "wrong (results)"),
    ("The calculation is incorrect", True, "logic", "incorrect (calculation)"),
    ("Data is incorrect", True, "logic", "incorrect (data)"),
    ("The output is wrong", True, "logic", "wrong (output)"),
    ("Results are inconsistent", True, "logic", "inconsistent (results)"),
    ("The behavior is wrong", True, "logic", "wrong (behavior)"),
    ("Undefined behavior detected", True, "logic", "undefined (behavior)"),
    ("Variable is undefined", True, "logic", "undefined (variable)"),
    ("Response handling not working", True, "logic", "not working (handling)"),
    ("The logic doesn't handle edge cases", True, "logic", "doesn't handle (edge cases)"),
    ("Not handling null values correctly", True, "logic", "not handling (null)"),
    ("Not handling concurrent requests", True, "logic", "not handling (concurrent)"),

    # ============================================================
    # NEGATIVE CASES — Positive Contexts (13)
    # ============================================================
    ("I don't see any issues with this code", False, "false_positive", "issue in positive context"),
    ("No problem, everything looks good", False, "false_positive", "problem in positive context"),
    ("There are no bugs here", False, "false_positive", "bugs in positive context"),
    ("Undefined behavior is expected in this case", False, "false_positive", "undefined in expected context"),
    ("The undefined is intentional", False, "false_positive", "undefined intentional"),
    ("This works fine, no issues", False, "false_positive", "works fine"),
    ("No problems detected in the logs", False, "false_positive", "problems positive"),
    ("We can't wait to ship this", False, "false_positive", "can't (positive)"),
    ("Unable to contain my excitement", False, "false_positive", "unable (excited)"),
    ("The system is stopped for maintenance", False, "false_positive", "stopped (intentional)"),
    ("It stopped raining", False, "false_positive", "stopped (weather)"),
    ("I failed the test on purpose", False, "false_positive", "failed (intentional)"),
    ("These examples are broken down nicely", False, "false_positive", "broken (positive)"),

    # ============================================================
    # NEGATIVE CASES — Neutral Conversation (15)
    # ============================================================
    ("How are you doing today?", False, "conversation", "greeting"),
    ("Let me explain how this works", False, "conversation", "explanation"),
    ("What's the best approach?", False, "conversation", "question"),
    ("Here's the plan for next sprint", False, "conversation", "plan"),
    ("This is a great feature", False, "conversation", "praise"),
    ("Can you help me understand this?", False, "conversation", "request"),
    ("I'd love to collaborate", False, "conversation", "sentiment"),
    ("Let's review the documentation", False, "conversation", "action"),
    ("This looks correct to me", False, "conversation", "assessment"),
    ("The code is well-structured", False, "conversation", "praise (code)"),
    ("I think this is ready", False, "conversation", "readiness"),
    ("What should we do next?", False, "conversation", "question (planning)"),
    ("Can we discuss this further?", False, "conversation", "discussion"),
    ("This is interesting", False, "conversation", "observation"),
    ("Let's move forward with this", False, "conversation", "decision"),

    # ============================================================
    # NEGATIVE CASES — Code Discussion (10)
    # ============================================================
    ("This function is well-written", False, "code_discussion", "function (positive)"),
    ("The API design is clean", False, "code_discussion", "API (positive)"),
    ("I like the approach here", False, "code_discussion", "approach (positive)"),
    ("The error handling is good", False, "code_discussion", "error handling (positive)"),
    ("The tests are comprehensive", False, "code_discussion", "tests (positive)"),
    ("This pattern is elegant", False, "code_discussion", "pattern (positive)"),
    ("The refactoring is complete", False, "code_discussion", "refactoring (positive)"),
    ("The implementation is solid", False, "code_discussion", "implementation (positive)"),
    ("The performance is acceptable", False, "code_discussion", "performance (positive)"),
    ("The documentation is thorough", False, "code_discussion", "documentation (positive)"),

    # ============================================================
    # NEGATIVE CASES — Technical Discussion (10)
    # ============================================================
    ("Let me trace through the execution", False, "technical", "trace (neutral)"),
    ("How does the cache work?", False, "technical", "question (cache)"),
    ("Explain the error handling strategy", False, "technical", "question (strategy)"),
    ("What happens on timeout?", False, "technical", "question (timeout)"),
    ("The system handles retries internally", False, "technical", "handles (positive)"),
    ("When does the cleanup happen?", False, "technical", "question (timing)"),
    ("How do we manage state?", False, "technical", "question (state)"),
    ("The framework handles this automatically", False, "technical", "handles (neutral)"),
    ("What's the expected behavior?", False, "technical", "question (behavior)"),
    ("The service manages connections well", False, "technical", "manages (positive)"),
]


def run_tests():
    """Run all test cases and report results."""
    passed = 0
    failed = 0
    failures = []

    for prompt, should_match, category, description in TEST_CASES:
        matches = should_match_prompt(prompt)

        if matches == should_match:
            passed += 1
        else:
            failed += 1
            expected = "should match" if should_match else "should NOT match"
            failures.append({
                "prompt": prompt,
                "expected": expected,
                "got": "matched" if matches else "no match",
                "category": category,
                "description": description
            })

    print(f"Results: {passed} passed, {failed} failed out of {len(TEST_CASES)} total")
    print(f"Pass rate: {100 * passed / len(TEST_CASES):.1f}%")
    print()

    if failures:
        print("FAILURES:")
        for i, failure in enumerate(failures, 1):
            print(f"\n{i}. {failure['category']} — {failure['description']}")
            print(f"   Prompt: {failure['prompt']}")
            print(f"   Expected: {failure['expected']}")
            print(f"   Got: {failure['got']}")
        return 1
    else:
        print("✓ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
