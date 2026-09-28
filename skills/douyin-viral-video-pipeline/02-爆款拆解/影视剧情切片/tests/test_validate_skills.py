#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for validate_skills.py (publish-time checks)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import validate_skills  # noqa: E402


def make_skill(tmp, with_frontmatter=True, leak=None):
    os.makedirs(tmp, exist_ok=True)
    fm = "---\nname: test-skill\ndescription: a test skill\n---\n\n# Test\n" if with_frontmatter else "# Test\n"
    with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(fm)
    if leak:
        with open(os.path.join(tmp, "leak.txt"), "w", encoding="utf-8") as f:
            f.write(leak)
    return tmp


class TestValidator(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp)
            errors = validate_skills.check_frontmatter(os.path.join(tmp, "SKILL.md"))
            self.assertEqual(errors, [])

    def test_missing_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, with_frontmatter=False)
            errors = validate_skills.check_frontmatter(os.path.join(tmp, "SKILL.md"))
            self.assertTrue(any("frontmatter" in e for e in errors))

    def test_missing_description_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: x\n---\n")
            errors = validate_skills.check_frontmatter(os.path.join(tmp, "SKILL.md"))
            self.assertTrue(any("description" in e for e in errors))

    def test_local_path_leak_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, leak=r"config at C:\Users\someone\app\config.yaml")
            errors = validate_skills.check_leaks(tmp)
            self.assertTrue(any("leak" in e for e in errors))

    def test_api_key_leak_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, leak="api_key: sk-abcdefghijklmnopqrstuvwxyz123456")
            errors = validate_skills.check_leaks(tmp)
            self.assertTrue(any("leak" in e for e in errors))

    def test_contact_info_not_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_skill(tmp, leak="Email: test@example.com  WeChat: abc12345")
            errors = validate_skills.check_leaks(tmp)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
