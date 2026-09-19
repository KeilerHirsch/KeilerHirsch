import unittest
from datetime import datetime, timezone

from tools.render_activity_panel import aggregate_months, language_breakdown, render_svg


class ActivityPanelTests(unittest.TestCase):
    def test_language_breakdown_excludes_profile_repo_and_sorts(self):
        repos = [
            {"name": "KeilerHirsch", "languages": {"edges": [{"size": 999, "node": {"name": "Python", "color": "#3572A5"}}]}},
            {"name": "A", "languages": {"edges": [{"size": 30, "node": {"name": "Ada", "color": "#02f88c"}}, {"size": 50, "node": {"name": "C#", "color": "#178600"}}]}},
            {"name": "B", "languages": {"edges": [{"size": 20, "node": {"name": "Ada", "color": "#02f88c"}}]}},
        ]
        self.assertEqual(
            language_breakdown(repos, "KeilerHirsch"),
            [("Ada", 50, "#02f88c"), ("C#", 50, "#178600")],
        )

    def test_month_aggregation_keeps_empty_months(self):
        now = datetime(2026, 9, 19, tzinfo=timezone.utc)
        result = aggregate_months(
            [{"date": "2026-08-01", "contributionCount": 3}, {"date": "2026-09-01", "contributionCount": 5}],
            now,
        )
        self.assertEqual(len(result), 12)
        self.assertEqual(result[-2:], [("2026-08", 3), ("2026-09", 5)])

    def test_svg_contains_compact_metrics_and_ada_label(self):
        now = datetime(2026, 9, 19, tzinfo=timezone.utc)
        data = {
            "user": {
                "login": "KeilerHirsch",
                "createdAt": "2026-02-03T18:45:21Z",
                "followers": {"totalCount": 29},
                "following": {"totalCount": 33},
                "publicRepos": {"totalCount": 6},
                "languageRepos": {"nodes": [
                    {"name": "WOLPERTINGER", "languages": {"edges": [{"size": 100, "node": {"name": "Ada", "color": "#02f88c"}}]}}
                ]},
                "contributionsCollection": {
                    "totalCommitContributions": 10,
                    "totalPullRequestContributions": 2,
                    "contributionCalendar": {
                        "totalContributions": 14,
                        "weeks": [{"contributionDays": [{"date": "2026-09-19", "contributionCount": 4}]}],
                    },
                },
            }
        }
        svg = render_svg(data, now)
        self.assertIn("GitHub since 2026", svg)
        self.assertIn("29 followers", svg)
        self.assertIn("Ada/SPARK 100%", svg)
        self.assertIn("14 contributions · 10 commits · 2 PRs", svg)


if __name__ == "__main__":
    unittest.main()
