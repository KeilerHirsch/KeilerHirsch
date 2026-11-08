import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from tools.render_activity_panel import (
    aggregate_months,
    build_panel_model,
    language_breakdown,
    recent_repositories,
    render_svg,
    format_percentage,
    total_language_bytes,
    WORKING_LANGUAGES,
    WEB_TECHNOLOGIES,
    short_repo_name,
    validated_repositories,
    window_metrics,
)


def sample_data() -> dict:
    return {
        "user": {
            "login": "KeilerHirsch",
            "createdAt": "2026-02-03T18:45:21Z",
            "followers": {"totalCount": 29},
            "following": {"totalCount": 28},
            "publicRepos": {"totalCount": 6},
            "forkRepos": {"totalCount": 1},
            "originalRepos": {
                "totalCount": 3,
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
                            "edges": [
                                {"size": 300, "node": {"name": "TypeScript", "color": "#3178c6"}}
                            ]
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
        },
        "organization": {
            "login": "KeilerHirschLabs",
            "publicRepos": {"totalCount": 0},
            "forkRepos": {"totalCount": 0},
            "originalRepos": {"totalCount": 0, "nodes": []},
        },
    }


class ActivityPanelTests(unittest.TestCase):
    def test_khl_projects_are_counted_without_organization_metadata(self):
        data = sample_data()
        data["organization"]["publicRepos"]["totalCount"] = 2
        data["organization"]["originalRepos"] = {
            "totalCount": 2,
            "nodes": [
                {
                    "name": ".github", "nameWithOwner": "KeilerHirschLabs/.github",
                    "isFork": False, "isEmpty": False, "isArchived": False,
                    "pushedAt": "2026-11-08T14:34:48Z",
                    "stargazerCount": 0, "forkCount": 0,
                    "languages": {"edges": [{"size": 5000, "node": {"name": "Markdown", "color": ""}}]},
                },
                {
                    "name": "SCUM-SENF", "nameWithOwner": "KeilerHirschLabs/SCUM-SENF",
                    "isFork": False, "isEmpty": False, "isArchived": False,
                    "pushedAt": "2026-11-08T14:10:17Z",
                    "stargazerCount": 2, "forkCount": 0,
                    "languages": {"edges": [{"size": 123, "node": {"name": "Python", "color": "#3572A5"}}]},
                },
            ],
        }
        model = build_panel_model(data, datetime(2026, 11, 8, tzinfo=timezone.utc))
        self.assertIn("8 public (6 personal + 2 KHL)", model["portfolio"])
        self.assertIn("3 active originals", model["portfolio"])
        self.assertEqual(
            model["languages"],
            [
                ("TypeScript", 300, "#3178c6"),
                ("C#", 200, "#178600"),
                ("Python", 123, "#3572A5"),
                ("Ada", 100, "#02f88c"),
            ],
        )
        self.assertNotIn("Markdown", {name for name, _, _ in model["languages"]})
        self.assertEqual(model["recent"][0]["nameWithOwner"], "KeilerHirschLabs/SCUM-SENF")
        self.assertIn("KeilerHirschLabs/SCUM-SENF", render_svg(model))

    def test_missing_organization_fails_closed(self):
        data = sample_data()
        del data["organization"]
        with self.assertRaises(KeyError):
            build_panel_model(data, datetime(2026, 11, 8, tzinfo=timezone.utc))

    def test_repository_query_fails_closed_when_truncated(self):
        user = sample_data()["user"]
        user["originalRepos"]["totalCount"] = 101

        with self.assertRaisesRegex(RuntimeError, "query incomplete"):
            validated_repositories(user)

    def test_language_breakdown_excludes_profile_and_archived_repos(self):
        repos = [
            {
                "name": "KeilerHirsch",
                "isArchived": False,
                "languages": {
                    "edges": [
                        {"size": 999, "node": {"name": "Python", "color": "#3572A5"}}
                    ]
                },
            },
            {
                "name": "Archived",
                "isArchived": True,
                "languages": {
                    "edges": [
                        {"size": 999, "node": {"name": "Rust", "color": "#dea584"}}
                    ]
                },
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
                "languages": {
                    "edges": [
                        {"size": 20, "node": {"name": "Ada", "color": "#02f88c"}}
                    ]
                },
            },
        ]

        self.assertEqual(
            language_breakdown(repos, "KeilerHirsch"),
            [("Ada", 50, "#02f88c"), ("C#", 50, "#178600")],
        )

    def test_month_aggregation_keeps_empty_months(self):
        now = datetime(2026, 9, 19, tzinfo=timezone.utc)
        result = aggregate_months(
            [
                {"date": "2026-08-01", "contributionCount": 3},
                {"date": "2026-09-01", "contributionCount": 5},
            ],
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
        self.assertEqual(best, "best day 7 on 2026-09-20")

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

    def test_all_original_languages_appear_and_fill_visual_bar(self):
        names = [
            "TypeScript", "C#", "JavaScript", "Ada", "Python",
            "Lua", "CSS", "PowerShell", "HTML",
        ]
        repo = {
            "name": "ActualProject",
            "isArchived": False,
            "isEmpty": False,
            "languages": {
                "edges": [
                    {
                        "size": (1000 if i == 0 else 30 - i),
                        "node": {"name": name, "color": "#123456"},
                    }
                    for i, name in enumerate(names)
                ]
            },
        }
        ignored_empty = {
            "name": "EmptyProject",
            "isArchived": False,
            "isEmpty": True,
            "languages": {
                "edges": [{"size": 999999, "node": {"name": "Rust", "color": "#123456"}}]
            },
        }
        ignored_fork = {
            "name": "UpstreamFork",
            "isFork": True,
            "isArchived": False,
            "languages": {
                "edges": [{"size": 777777, "node": {"name": "Go", "color": "#123456"}}]
            },
        }
        repos = [repo, ignored_empty, ignored_fork]
        languages = language_breakdown(repos, "KeilerHirsch")
        total = total_language_bytes(repos, "KeilerHirsch")
        self.assertEqual(len(languages), len(names))
        self.assertEqual({name for name, _, _ in languages}, set(names))
        self.assertEqual(total, sum(size for _, size, _ in languages))
        self.assertNotIn("Rust", {name for name, _, _ in languages})
        self.assertNotIn("Go", {name for name, _, _ in languages})

        model = build_panel_model(sample_data(), datetime(2026, 9, 20, tzinfo=timezone.utc))
        model["languages"] = languages
        model["language_bytes"] = total
        output = render_svg(model)
        root = ET.fromstring(output)
        self.assertIn("ALL 9 DETECTED", output)
        for name in names:
            self.assertIn(name + " ", output)
        self.assertIn("NOT SKILL LEVEL", output)
        self.assertIn("Linguist code-size shares; profile, archived, empty repos and forks excluded.", output)
        self.assertIn("LANGUAGES · ACTIVE ORIGINAL PROJECT CODE", output)
        self.assertNotIn("all public original repositories", output.lower())
        self.assertIn("LANGUAGES I WORK WITH", output)
        self.assertIn("OWNER-CONFIRMED", output)
        for name in WORKING_LANGUAGES:
            self.assertIn(name, output)
        for name in WEB_TECHNOLOGIES:
            self.assertIn(name, output)
        self.assertEqual(len(WORKING_LANGUAGES), 13)
        self.assertEqual(WEB_TECHNOLOGIES, ("HTML", "CSS"))

        svg_ns = "{http://www.w3.org/2000/svg}"
        group = root.find(f"{svg_ns}g")
        segments = group.findall(f"{svg_ns}rect")
        self.assertEqual(len(segments), 9)
        self.assertAlmostEqual(
            sum(float(segment.attrib["width"]) for segment in segments),
            1120,
            delta=0.02,
        )
        self.assertGreater(int(root.attrib["height"]), 540)

    def test_missing_and_small_language_shares_are_readable(self):
        self.assertEqual(format_percentage(0, 0), "0%")
        self.assertEqual(format_percentage(1, 50000), "<0.1%")
        self.assertEqual(format_percentage(1, 1000), "0.1%")
        self.assertEqual(format_percentage(1, 4), "25%")

    def test_recent_repositories_ignore_empty_newly_created_repo(self):
        repos = [
            {
                "name": "FS25_SmartVRAM", "isArchived": False,
                "isEmpty": True, "pushedAt": "2026-11-07T18:43:26Z",
            },
            {
                "name": "PLLDN", "isArchived": False,
                "isEmpty": False, "pushedAt": "2026-11-07T02:13:00Z",
            },
            {
                "name": "KeilerHirsch", "isArchived": False,
                "isEmpty": False, "pushedAt": "2026-11-08T00:00:00Z",
            },
        ]
        self.assertEqual(
            [repo["name"] for repo in recent_repositories(repos, "KeilerHirsch")],
            ["PLLDN"],
        )

    def test_language_colors_are_restricted_to_valid_hex(self):
        repo = {
            "name": "Project",
            "isArchived": False,
            "languages": {
                "edges": [{"size": 12, "node": {
                    "name": "C#", "color": '" onmouseover="alert(1)'
                }}]
            },
        }
        self.assertEqual(language_breakdown([repo], "KeilerHirsch")[0][2], "#7f8a99")

    def test_short_repo_name_is_bounded(self):
        self.assertEqual(short_repo_name("short"), "short")
        self.assertTrue(short_repo_name("x" * 80).endswith("…"))
        self.assertLessEqual(len(short_repo_name("x" * 80)), 70)

    def test_rendered_panel_is_deterministic_and_evidence_honest(self):
        now = datetime(2026, 9, 20, 10, 11, tzinfo=timezone.utc)
        model = build_panel_model(sample_data(), now)
        first = render_svg(model)
        second = render_svg(model)

        self.assertEqual(first, second)
        ET.fromstring(first)
        self.assertIn("AUTO · GitHub GraphQL", first)
        self.assertIn("active, nonempty public original projects", first)
        self.assertIn("excluding the profile repo, forks and archived projects", first)
        self.assertNotIn("updated ", first)
        self.assertIn("Ada 17%", first)
        self.assertNotIn("Ada/SPARK", first.split("LANGUAGES I WORK WITH", 1)[0])
        self.assertIn("Ada/SPARK", first)
        self.assertIn("14 contributions · 10 commits · 2 PRs", first)
        self.assertIn("10 contributions · 2 active days", first)
        self.assertIn(
            "PLLDN-Programming-Language-Licensing-Decision-Navigator",
            first,
        )


if __name__ == "__main__":
    unittest.main()
