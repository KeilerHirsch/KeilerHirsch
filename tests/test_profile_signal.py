import importlib.util
import json
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "render_profile_signal.py"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "signal-snapshot.json"


def load_renderer():
    spec = importlib.util.spec_from_file_location("profile_signal", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ProfileSignalTests(unittest.TestCase):
    def setUp(self):
        self.renderer = load_renderer()
        self.config = {
            "current_focus": "WOLPERTINGER Ã¢â‚¬â€ Presentation subsystem",
            "projects": [
                {
                    "key": "WOLPERTINGER",
                    "repo": "KeilerHirsch/WOLPERTINGER",
                    "status": "BUILDING",
                    "workflow": "ci.yml",
                },
                {
                    "key": "PLLDN",
                    "repo": "KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator",
                    "status": "BETA 1",
                    "workflow": "verify.yml",
                },
            ],
        }
        self.snapshot = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_render_is_deterministic_and_valid_svg(self):
        first = self.renderer.render_svg(self.config, self.snapshot)
        second = self.renderer.render_svg(self.config, self.snapshot)
        self.assertEqual(first, second)
        ET.fromstring(first)
        self.assertIn("CURRENT SIGNAL", first)
        self.assertIn("WOLPERTINGER", first)
        self.assertIn("PLLDN", first)
        self.assertIn("PLLDN v0.0.1 Beta 1", first)

    def test_render_escapes_untrusted_text(self):
        config = dict(self.config)
        config["current_focus"] = "A < B & C"
        svg = self.renderer.render_svg(config, self.snapshot)
        self.assertIn("A &lt; B &amp; C", svg)
        ET.fromstring(svg)

    def test_latest_release_prefers_newest_published_release(self):
        newest = self.renderer.latest_release(self.snapshot)
        self.assertEqual(newest["tag"], "v0.0.1-beta.1")

    def test_atomic_write_preserves_existing_file_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "current-signal.svg"
            target.write_text("old", encoding="utf-8")

            def broken_writer(_path, _text):
                raise RuntimeError("boom")

            with self.assertRaises(RuntimeError):
                self.renderer.atomic_write_text(target, "new", writer=broken_writer)
            self.assertEqual(target.read_text(encoding="utf-8"), "old")

    def test_validate_config_rejects_duplicate_project_keys(self):
        config = dict(self.config)
        config["projects"] = [self.config["projects"][0], self.config["projects"][0]]
        with self.assertRaises(ValueError):
            self.renderer.validate_config(config)

    def test_normalize_ci_maps_only_known_conclusions(self):
        self.assertEqual(self.renderer.normalize_ci("success"), "PASS")
        self.assertEqual(self.renderer.normalize_ci("failure"), "FAIL")
        self.assertEqual(self.renderer.normalize_ci("cancelled"), "FAIL")
        self.assertEqual(self.renderer.normalize_ci(None), "UNKNOWN")
        self.assertEqual(self.renderer.normalize_ci("neutral"), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()


class ProfileSignalCollectionTests(unittest.TestCase):
    def setUp(self):
        self.renderer = load_renderer()
        self.config = {
            "current_focus": "WOLPERTINGER Ã¢â‚¬â€ Presentation subsystem",
            "projects": [
                {
                    "key": "WOLPERTINGER",
                    "repo": "KeilerHirsch/WOLPERTINGER",
                    "status": "BUILDING",
                    "workflow": "ci.yml",
                },
                {
                    "key": "PLLDN",
                    "repo": "KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator",
                    "status": "BETA 1",
                    "workflow": "verify.yml",
                },
            ],
        }

    def test_collect_snapshot_reads_ci_and_prerelease(self):
        calls = []

        def get_json(path):
            calls.append(path)
            if "WOLPERTINGER/actions/workflows/ci.yml" in path:
                return {"workflow_runs": [{"conclusion": "success"}]}
            if "WOLPERTINGER/releases" in path:
                return []
            if "PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/workflows/verify.yml" in path:
                return {"workflow_runs": [{"conclusion": "success"}]}
            if "PLLDN-Programming-Language-Licensing-Decision-Navigator/releases" in path:
                return [
                    {
                        "draft": False,
                        "name": "PLLDN v0.0.1 Beta 1",
                        "tag_name": "v0.0.1-beta.1",
                        "published_at": "2026-09-07T17:21:54Z",
                        "html_url": "https://example.invalid/release",
                    }
                ]
            raise AssertionError(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["ci"], "PASS")
        self.assertIsNone(snapshot["projects"]["WOLPERTINGER"]["release"])
        self.assertEqual(snapshot["projects"]["PLLDN"]["ci"], "PASS")
        self.assertEqual(
            snapshot["projects"]["PLLDN"]["release"]["tag"],
            "v0.0.1-beta.1",
        )
        self.assertEqual(len(calls), 4)

    def test_collect_snapshot_maps_missing_runs_to_unknown(self):
        def get_json(path):
            if "/actions/workflows/" in path:
                return {"workflow_runs": []}
            return []

        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["ci"], "UNKNOWN")
        self.assertEqual(snapshot["projects"]["PLLDN"]["ci"], "UNKNOWN")

    def test_main_fixture_mode_writes_svg_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / "profile.json"
            output_path = tmp_path / "signal.svg"
            config_path.write_text(json.dumps(self.config), encoding="utf-8")
            exit_code = self.renderer.main(
                [
                    "--config",
                    str(config_path),
                    "--snapshot",
                    str(FIXTURE_PATH),
                    "--output",
                    str(output_path),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertIn("CURRENT SIGNAL", output_path.read_text(encoding="utf-8"))

    def test_main_live_mode_uses_github_token_and_api(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = json.dumps(payload).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return self.payload

        def fake_urlopen(request, timeout=0):
            self.assertEqual(request.headers.get("Authorization"), "Bearer test-token")
            url = request.full_url
            if "/actions/workflows/" in url:
                return FakeResponse({"workflow_runs": [{"conclusion": "success"}]})
            return FakeResponse([])

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_path = tmp_path / "profile.json"
            output_path = tmp_path / "signal.svg"
            config_path.write_text(json.dumps(self.config), encoding="utf-8")
            with mock.patch.object(self.renderer.urllib.request, "urlopen", fake_urlopen):
                with mock.patch.dict(self.renderer.os.environ, {"GITHUB_TOKEN": "test-token"}):
                    exit_code = self.renderer.main(
                        ["--config", str(config_path), "--output", str(output_path)]
                    )
            self.assertEqual(exit_code, 0)
            self.assertIn("CI PASS", output_path.read_text(encoding="utf-8"))


class ProfileSurfaceContractTests(unittest.TestCase):
    def test_workflow_contract(self):
        workflow = ROOT / ".github" / "workflows" / "profile-signal.yml"
        self.assertTrue(workflow.exists(), "profile signal workflow must exist")
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("cron: '17 */6 * * *'", text)
        self.assertIn("contents: write", text)
        self.assertIn("persist-credentials: true", text)
        self.assertIn("python tools/render_profile_signal.py --config profile.json --output assets/current-signal.svg", text)
        self.assertIn("git diff --quiet -- assets/current-signal.svg", text)
        self.assertIn("git add -- assets/current-signal.svg", text)
        self.assertIn("git commit -m \"chore: refresh profile signal\"", text)
        self.assertIn("git push", text)

    def test_readme_contract(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        hero = "assets/profile-hero.webp"
        signal = "assets/current-signal.svg"
        selected = "## Selected work"
        self.assertIn(hero, readme)
        self.assertIn(signal, readme)
        self.assertLess(readme.index(hero), readme.index(signal))
        self.assertLess(readme.index(signal), readme.index(selected))
        required = [
            "https://github.com/KeilerHirsch/WOLPERTINGER",
            "https://github.com/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator",
            "https://myrank.dev/u/KeilerHirsch",
            "https://ko-fi.com/keilerhirsch",
            "https://www.reddit.com/r/MAYHEMClub/",
            "Founder & Mod",
            "Build cool shit. Share it. Get real feedback.",
        ]
        for marker in required:
            self.assertIn(marker, readme)
        self.assertNotIn("## Clean-slate policy", readme)
        words = readme.split()
        self.assertGreaterEqual(len(words), 250)
        self.assertLessEqual(len(words), 350)

        section = readme.split("## How I build", 1)[1].split("## MAYHEM Club", 1)[0]
        principles = [line for line in section.splitlines() if line.startswith("- **")]
        self.assertEqual(len(principles), 3)
        self.assertTrue((ROOT / "assets" / "profile-hero.webp").exists())


class PublicApiFallbackTests(unittest.TestCase):
    def test_live_mode_works_without_github_token_for_public_repos(self):
        renderer = load_renderer()

        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def read(self):
                return b'{"workflow_runs": []}'

        def fake_urlopen(request, timeout=0):
            self.assertIsNone(request.headers.get("Authorization"))
            if "/releases?" in request.full_url:
                return type("R", (), {
                    "__enter__": lambda self: self,
                    "__exit__": lambda self, *args: False,
                    "read": lambda self: b"[]",
                })()
            return FakeResponse()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "profile.json"
            output_path = Path(tmp) / "signal.svg"
            config_path.write_text((ROOT / "profile.json").read_text(encoding="utf-8"), encoding="utf-8")
            with mock.patch.object(renderer.urllib.request, "urlopen", fake_urlopen):
                with mock.patch.dict(renderer.os.environ, {}, clear=True):
                    exit_code = renderer.main([
                        "--config", str(config_path),
                        "--output", str(output_path),
                    ])
            self.assertEqual(exit_code, 0)
            self.assertIn("CI UNKNOWN", output_path.read_text(encoding="utf-8"))
