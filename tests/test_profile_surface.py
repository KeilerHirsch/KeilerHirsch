import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProfileSurfaceTests(unittest.TestCase):
    def test_readme_contract(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        hero = "assets/profile-hero.webp"
        activity = "assets/activity-panel.svg"

        required_sections = [
            "## Activity",
            "## How I build",
            "## Engineering DNA",
            "## Security & forensics",
            "## MAYHEM Club",
        ]
        self.assertIn(hero, readme)
        self.assertIn(activity, readme)
        self.assertLess(readme.index(hero), readme.index(activity))
        self.assertEqual(
            [readme.index(section) for section in required_sections],
            sorted(readme.index(section) for section in required_sections),
        )

        required_markers = [
            "Simple products. Uncomfortably serious engineering underneath.",
            "High-assurance software",
            "The workshop moves; this panel follows it automatically",
            "Evidence before claims.",
            "Over State of the Art by default.",
            "Ada/SPARK is my primary engineering language.",
            "I would rather prove an invariant than explain later why",
            "Precision Mechanic",
            "Feinwerkmechaniker",
            "13 of 24 full-time months completed",
            "no qualification awarded",
            "Electronics Technician for Industrial Engineering",
            "Elektroniker für Betriebstechnik",
            "23 months of voluntary military service",
            "Autodidact by habit",
            "Polish",
            "German",
            "English",
            "GitHub is where the workshop became software",
            "Build cool shit. Share it. Get real feedback.",
            "Simple outside. Technically unpleasant to copy inside.",
            "The Man, The Myth, The Legend.",
            "https://myrank.dev/u/KeilerHirsch",
            "https://ko-fi.com/keilerhirsch",
            "https://www.reddit.com/r/MAYHEMClub/",
        ]
        for marker in required_markers:
            self.assertIn(marker, readme)

        self.assertNotIn("## Current signal", readme)
        self.assertNotIn("assets/current-signal.svg", readme)
        self.assertNotIn("## Selected work", readme)
        self.assertNotIn("Airbus", readme)
        self.assertNotIn("utm_", readme.lower())

        self.assertGreaterEqual(len(readme.split()), 300)
        self.assertLessEqual(len(readme.split()), 600)

        how_i_build = readme.split("## How I build", 1)[1].split("## Engineering DNA", 1)[0]
        self.assertEqual(len([line for line in how_i_build.splitlines() if line.startswith("- **")]), 4)

        self.assertTrue((ROOT / "assets" / "profile-hero.webp").exists())
        self.assertTrue((ROOT / "assets" / "activity-panel.svg").exists())

    def test_activity_only_automation_contract(self):
        workflow = (ROOT / ".github" / "workflows" / "profile-signal.yml").read_text(encoding="utf-8")

        for marker in (
            "name: Profile activity",
            "workflow_dispatch:",
            "pull_request:",
            "cron: '17 */6 * * *'",
            "contents: write",
            "persist-credentials: true",
            "python -m unittest discover -s tests -v",
            "GITHUB_TOKEN: ${{ github.token }}",
            "python tools/render_activity_panel.py --output assets/activity-panel.svg",
            "git diff --quiet -- assets/activity-panel.svg",
            'git commit -m "chore: refresh profile activity"',
            "git push",
        ):
            self.assertIn(marker, workflow)

        for stale in (
            "render_profile_signal.py",
            "profile.json",
            "assets/current-signal.svg",
        ):
            self.assertNotIn(stale, workflow)

        self.assertFalse((ROOT / "profile.json").exists())
        self.assertFalse((ROOT / "tools" / "render_profile_signal.py").exists())
        self.assertFalse((ROOT / "assets" / "current-signal.svg").exists())
        self.assertFalse((ROOT / "tests" / "fixtures" / "signal-snapshot.json").exists())


if __name__ == "__main__":
    unittest.main()
