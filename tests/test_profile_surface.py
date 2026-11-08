import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = (
    "Ada/SPARK", "C", "C++", "C#", "Python", "Lua", "JavaScript",
    "TypeScript", "PowerShell", "Go", "Rust", "Kotlin", "Dart",
)


class ProfileSurfaceTests(unittest.TestCase):
    def test_rich_profile_sections_and_background(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sections = (
            "## About", "## Activity", "## How I build",
            "## Engineering DNA", "## Security & forensics",
            "## MAYHEM Club", "## Licence",
        )
        self.assertEqual(
            [readme.index(x) for x in sections],
            sorted(readme.index(x) for x in sections),
        )
        self.assertIn("assets/profile-hero.webp", readme)
        self.assertIn("assets/activity-panel.svg", readme)
        self.assertLess(readme.index("assets/profile-hero.webp"), readme.index("assets/activity-panel.svg"))
        for marker in (
            "reproducible evidence", "root causes", "Background & qualifications",
            "13 of 24 full-time months completed; no qualification awarded",
            "23 months of voluntary military service",
            "Polish", "German", "English",
            "preserve evidence", "Build cool shit.",
        ):
            self.assertIn(marker, readme)
        self.assertTrue((ROOT / "assets/profile-hero.webp").exists())
        self.assertTrue((ROOT / "LICENSE").exists())
        self.assertTrue((ROOT / ".github/FUNDING.yml").exists())

    def test_no_hand_maintained_project_catalog(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for old in (
            "## Projects", "### Featured", "### Research & experiments",
            "Forks & upstream projects", "https://github.com/KeilerHirsch/SCUM-SENF",
            "FS25_Advanced_RealismSuite", "PLLDN-Programming-Language", "wolpertinger",
        ):
            self.assertNotIn(old, readme)
        for url in (
            "https://github.com/orgs/KeilerHirschLabs/repositories",
            "https://github.com/KeilerHirsch?tab=repositories",
            "https://www.reddit.com/r/MAYHEMClub/",
            "https://myrank.dev/u/KeilerHirsch",
            "https://ko-fi.com/keilerhirsch",
        ):
            self.assertIn(url, readme)

    def test_dynamic_languages_and_graphic(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        svg = (ROOT / "assets/activity-panel.svg").read_text(encoding="utf-8")
        self.assertIn("![GitHub activity", readme)
        self.assertIn("both KeilerHirsch and KeilerHirschLabs", readme)
        self.assertIn("13 working languages", readme)
        self.assertIn("LANGUAGES · ACTIVE ORIGINAL PROJECT CODE", svg)
        self.assertIn("LANGUAGES I WORK WITH · OWNER-CONFIRMED", svg)
        self.assertIn("KeilerHirschLabs/SCUM-SENF", svg)
        for language in LANGUAGES:
            self.assertIn(language, svg)
        self.assertIn("HTML", svg)
        self.assertIn("CSS", svg)
        ET.fromstring(svg)

    def test_public_safety_and_links(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for secret in ("Operation Roland", "Oxycodon", "utm_", "E:\\", "C:\\", "\ufffd"):
            self.assertNotIn(secret, readme)
        for link in re.findall(r"\]\(([^)]+)\)", readme):
            if link.startswith(("http://", "https://", "#")):
                continue
            self.assertTrue((ROOT / link).exists(), link)
        self.assertFalse((ROOT / "docs/superpowers").exists())

    def test_activity_workflow_is_pinned_and_scheduled(self):
        workflow = (ROOT / ".github/workflows/profile-activity.yml").read_text(encoding="utf-8")
        for marker in (
            "name: Profile activity", "cron: '17 */6 * * *'",
            "workflow_dispatch:", "pull_request:", "contents: write",
            "python -m unittest discover -s tests -v",
            "tools/render_activity_panel.py",
            'git commit -m "chore: refresh profile activity"',
        ):
            self.assertIn(marker, workflow)
        self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40}")

    def test_pull_request_checks_have_no_write_token(self):
        workflow = (ROOT / ".github/workflows/profile-activity.yml").read_text(encoding="utf-8")
        self.assertIn("\npermissions:\n  contents: read\n", workflow)
        validate = workflow.split("\n  validate:\n", 1)[1].split("\n  refresh:\n", 1)[0]
        refresh = workflow.split("\n  refresh:\n", 1)[1]
        for marker in ("if: github.event_name == 'pull_request'", "contents: read", "persist-credentials: false"):
            self.assertIn(marker, validate)
        self.assertNotIn("contents: write", validate)
        self.assertNotIn("git push", validate)
        self.assertIn("if: github.event_name != 'pull_request'", refresh)
        self.assertIn("contents: write", refresh)
        self.assertIn("ref: $" + "{{ github.event.repository.default_branch }}", refresh)
        self.assertIn("git push", refresh)


if __name__ == "__main__":
    unittest.main()
