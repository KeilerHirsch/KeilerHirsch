import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProfileSurfaceTests(unittest.TestCase):
    def test_readme_structure_and_public_safety(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        hero = "assets/profile-hero.webp"
        activity = "assets/activity-panel.svg"
        sections = [
            "## Activity",
            "## How I build",
            "## Engineering DNA",
            "## Security & forensics",
            "## MAYHEM Club",
        ]

        self.assertIn(hero, readme)
        self.assertIn(activity, readme)
        self.assertLess(readme.index(hero), readme.index(activity))

        positions = [readme.index(section) for section in sections]
        self.assertEqual(positions, sorted(positions))

        for canonical_link in (
            "https://myrank.dev/u/KeilerHirsch",
            "https://ko-fi.com/keilerhirsch",
            "https://www.reddit.com/r/MAYHEMClub/",
        ):
            self.assertIn(canonical_link, readme)

        self.assertRegex(
            readme,
            re.compile(
                r"13 of 24 full-time months completed; no qualification awarded",
                re.IGNORECASE,
            ),
        )
        self.assertRegex(
            readme,
            re.compile(
                r"23 months of voluntary military service.*Bundeswehr",
                re.IGNORECASE,
            ),
        )

        for stale in (
            "## Current signal",
            "assets/current-signal.svg",
            "## Selected work",
            "profile.json",
            "render_profile_signal.py",
            "Airbus",
        ):
            self.assertNotIn(stale, readme)

        self.assertNotIn("utm_", readme.lower())
        self.assertTrue((ROOT / "assets" / "profile-hero.webp").exists())
        self.assertTrue((ROOT / "assets" / "activity-panel.svg").exists())

    def test_activity_automation_contract(self):
        workflow_path = ROOT / ".github" / "workflows" / "profile-activity.yml"
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertFalse(
            (ROOT / ".github" / "workflows" / "profile-signal.yml").exists()
        )
        self.assertRegex(workflow, r"actions/checkout@[0-9a-f]{40}")

        for marker in (
            "name: Profile activity",
            "workflow_dispatch:",
            "pull_request:",
            "cron: '17 */6 * * *'",
            "contents: write",
            "python -m unittest discover -s tests -v",
            "GITHUB_TOKEN: ${{ github.token }}",
            "python tools/render_activity_panel.py --output assets/activity-panel.svg",
            "git diff --quiet -- assets/activity-panel.svg",
            'git commit -m "chore: refresh profile activity"',
            "git push",
        ):
            self.assertIn(marker, workflow)

    def test_internal_planning_material_is_not_published(self):
        self.assertFalse((ROOT / "docs" / "superpowers").exists())


if __name__ == "__main__":
    unittest.main()
