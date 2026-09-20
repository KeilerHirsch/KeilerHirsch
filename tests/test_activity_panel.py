import unittest
from datetime import datetime, timezone

from tools.render_activity_panel import (
    aggregate_months,
    language_breakdown,
    recent_repositories,
    render_svg,
    short_repo_name,
    window_metrics,
)


class ActivityPanelTests(unittest.TestCase):
    def test_language_breakdown_excludes_profile_and_archived_repos(self):
        repos = [
            {
                "name": "KeilerHirsch",
                "isArchived": False,
                "languages": {"edges": [{"size": 999, "node": {"name": "Python", "color": "#3572A5"}}]},
            },
            {
                "name": "Archived",
                "isArchived": True,
                "languages": {"edges": [{"size": 999, "node": {"name": "Rust", "color": "#dea584"}}]},
            },
            {
                "name": "A",
                "isArchived": False,
                "languages": {
                    "edges": [
                        {"size": 30, "node": {"name": "Ada", "color": "#02f88c"}},
                        {"size": 50, "node": {"name": "C#", "color": "#178600"}},
                    ]
                },
            },
            {
                "name": "B",
                "isArchived": False,
                "languages": {"edges": [{"size": 20, "node": {"name": "Ada", "color": "#02f88c"}}]},
            },
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

    def test_window_metrics_are_derived_from_recent_days(self):
        now = datetime(2026, 9, 20, tzinfo=timezone.utc)
        total, active, best = window_metrics(
            [
                {"date": "2026-08-01", "contributionCount": 99},
                {"date": "2026-09-10", "contributionCount": 3},
                {"date": "2026-09-20", "contributionCount": 7},
            ],
            now,
        )
        self.assertEqual((total, active), (10, 2))
        self.assertEqual(best, "best day 7 on 09-20")

    def test_recent_repositories_excludes_profile_and_archived(self):
        repos = [
            {"name": "KeilerHirsch", "isArchived": False, "pushedAt": "2026-09-20T10:00:00Z"},
            {"name": "Archived", "isArchived": True, "pushedAt": "2026-09-20T09:00:00Z"},
            {"name": "A", "isArchived": False, "pushedAt": "2026-09-19T10:00:00Z"},
            {"name": "B", "isArchived": False, "pushedAt": "2026-09-18T10:00:00Z"},
            {"name": "C", "isArchived": False, "pushedAt": "2026-09-17T10:00:00Z"},
            {"name": "D", "isArchived": False, "pushedAt": "2026-09-16T10:00:00Z"},
        ]
        self.assertEqual(
            [repo["name"] for repo in recent_repositories(repos, "KeilerHirsch")],
            ["A", "B", "C"],
        )

    def test_short_repo_name_is_bounded(self):
        self.assertEqual(short_repo_name("short"), "short")
        self.assertTrue(short_repo_name("x" * 40).endswith("…"))
        self.assertEqual(short_repo_name("x" * 40), "x" * 40)

    def test_svg_contains_expanded_live_metrics(self):
        now = datetime(2026, 9, 20, 10, 11, tzinfo=timezone.utc)
        data = {
            "user": {
                "login": "KeilerHirsch",
                "createdAt": "2026-02-03T18:45:21Z",
                "followers": {"totalCount": 29},
                "following": {"totalCount": 28},
                "publicRepos": {"totalCount": 6},
                "forkRepos": {"totalCount": 1},
                "originalRepos": {
                    "totalCount": 5,
                    "nodes": [
                        {
                            "name": "KeilerHirsch",
                            "isArchived": False,
                            "pushedAt": "2026-09-20T10:00:00Z",
                            "stargazerCount": 0,
                            "forkCount": 0,
                            "languages": {"edges": []},
                        },
                        {
                            "name": "WOLPERTINGER",
                            "isArchived": False,
                            "pushedAt": "2026-09-19T12:00:00Z",
                            "stargazerCount": 1,
                            "forkCount": 0,
                            "languages": {
                                "edges": [
                                    {"size": 100, "node": {"name": "Ada", "color": "#02f88c"}},
                                    {"size": 200, "node": {"name": "C#", "color": "#178600"}},
                                ]
                            },
                        },
                        {
                            "name": "PLLDN-Programming-Language-Licensing-Decision-Navigator",
                            "isArchived": False,
                            "pushedAt": "2026-09-18T12:00:00Z",
                            "stargazerCount": 0,
                            "forkCount": 0,
                            "languages": {
                                "edges": [{"size": 300, "node": {"name": "TypeScript", "color": "#3178c6"}}]
                            },
                        },
                    ],
                },
                "contributionsCollection": {
                    "totalCommitContributions": 10,
                    "totalPullRequestContributions": 2,
                    "contributionCalendar": {
                        "totalContributions": 14,
                        "weeks": [
                            {
                                "contributionDays": [
                                    {"date": "2026-09-10", "contributionCount": 3},
                                    {"date": "2026-09-20", "contributionCount": 7},
                                ]
                            }
                        ],
                    },
                },
            }
        }
        svg = render_svg(data, now)
        self.assertIn('height="540"', svg)
        self.assertIn("updated 2026-09-20 10:11 UTC", svg)
        self.assertIn("6 public repos", svg)
        self.assertIn("29 followers", svg)
        self.assertIn("Ada/SPARK", svg)
        self.assertIn("14 contributions · 10 commits · 2 PRs", svg)
        self.assertIn("10 contributions · 2 active days · best day 7 on 09-20", svg)
        self.assertIn("6 public · 5 original · 1 fork · 1 star · 0 downstream forks", svg)
        self.assertIn("WOLPERTINGER · pushed 2026-09-19", svg)
        for removed_label in ("ACCOUNT</text>", "LANGUAGES</text>", "12 MONTHS</text>", "30 DAYS</text>", "PORTFOLIO</text>", "RECENT WORK</text>"):
            self.assertNotIn(removed_label, svg)
        self.assertIn("PLLDN-Programming-Language-Licensing-Decision-Navigator", svg)


if __name__ == "__main__":
    unittest.main()
