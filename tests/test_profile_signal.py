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


def make_repo_payload(default_branch="main"):
    return {"default_branch": default_branch}


def make_branch_payload(sha):
    return {"commit": {"sha": sha}}


def make_run(sha, conclusion="success", run_id=1, updated_at="2026-09-15T12:00:00Z"):
    return {
        "id": run_id,
        "head_sha": sha,
        "conclusion": conclusion,
        "html_url": f"https://example.invalid/actions/runs/{run_id}",
        "updated_at": updated_at,
    }


class BaseProfileTest(unittest.TestCase):
    def setUp(self):
        self.renderer = load_renderer()
        self.config = {
            "current_focus": "WOLPERTINGER — Presentation subsystem",
            "projects": [
                {"key": "WOLPERTINGER", "repo": "KeilerHirsch/WOLPERTINGER", "status": "BUILDING", "workflow": "ci.yml"},
                {"key": "PLLDN", "repo": "KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator", "status": "BETA 1", "workflow": "verify.yml"},
            ],
        }


class ProfileSignalTests(BaseProfileTest):
    def setUp(self):
        super().setUp()
        self.snapshot = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_render_is_deterministic_and_valid_svg(self):
        first = self.renderer.render_svg(self.config, self.snapshot)
        second = self.renderer.render_svg(self.config, self.snapshot)
        self.assertEqual(first, second)
        ET.fromstring(first)
        for marker in ("CURRENT SIGNAL", "WOLPERTINGER", "BUILDING", "HEAD VERIFIED", "RELEASE SHIPPED", "main@1111111", "PLLDN v0.0.1 Beta 1", "RELEASE VERIFIED", "exact-HEAD · GitHub Actions"):
            self.assertIn(marker, first)
        self.assertNotIn("CI PASS", first)

    def test_render_escapes_untrusted_text(self):
        config = dict(self.config)
        config["current_focus"] = "A < B & C"
        svg = self.renderer.render_svg(config, self.snapshot)
        self.assertIn("A &lt; B &amp; C", svg)
        ET.fromstring(svg)

    def test_render_shows_fail_and_unknown(self):
        snapshot = json.loads(json.dumps(self.snapshot))
        snapshot["projects"]["WOLPERTINGER"]["verification"]["state"] = "FAIL"
        snapshot["projects"]["PLLDN"]["verification"]["state"] = "UNKNOWN"
        svg = self.renderer.render_svg(self.config, snapshot)
        self.assertIn("FAIL", svg)
        self.assertIn("HEAD UNKNOWN · RELEASE SHIPPED", svg)
        ET.fromstring(svg)

    def test_latest_release_prefers_newest_valid_shipped_release(self):
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

    def test_normalize_verification_maps_only_known_conclusions(self):
        self.assertEqual(self.renderer.normalize_verification("success"), "VERIFIED")
        self.assertEqual(self.renderer.normalize_verification("failure"), "FAIL")
        self.assertEqual(self.renderer.normalize_verification("cancelled"), "FAIL")
        self.assertEqual(self.renderer.normalize_verification(None), "UNKNOWN")
        self.assertEqual(self.renderer.normalize_verification("neutral"), "UNKNOWN")


class ProfileSignalCollectionTests(BaseProfileTest):
    def _api(self, *, wolper_head="a"*40, wolper_run=None, wolper_releases=None, pll_head="b"*40, pll_run=None, pll_releases=None, default_branch="main"):
        wolper_run = make_run(wolper_head, run_id=11) if wolper_run is None else wolper_run
        pll_run = make_run(pll_head, run_id=12) if pll_run is None else pll_run
        wolper_releases = [] if wolper_releases is None else wolper_releases
        pll_releases = [] if pll_releases is None else pll_releases
        def get_json(path):
            if path == "/repos/KeilerHirsch/WOLPERTINGER":
                return make_repo_payload(default_branch)
            if path == f"/repos/KeilerHirsch/WOLPERTINGER/branches/{default_branch}":
                return make_branch_payload(wolper_head)
            if "WOLPERTINGER/actions/workflows/ci.yml/runs" in path:
                return {"workflow_runs": [] if wolper_run == [] else [wolper_run]}
            if path == "/repos/KeilerHirsch/WOLPERTINGER/releases?per_page=10":
                return wolper_releases
            if path == "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator":
                return make_repo_payload(default_branch)
            if path == f"/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/branches/{default_branch}":
                return make_branch_payload(pll_head)
            if "PLLDN-Programming-Language-Licensing-Decision-Navigator/actions/workflows/verify.yml/runs" in path:
                return {"workflow_runs": [] if pll_run == [] else [pll_run]}
            if path == "/repos/KeilerHirsch/PLLDN-Programming-Language-Licensing-Decision-Navigator/releases?per_page=10":
                return pll_releases
            raise AssertionError(path)
        return get_json

    def test_collect_snapshot_verifies_exact_default_branch_head(self):
        head = "a" * 40
        calls = []
        base = self._api(wolper_head=head)
        def get_json(path):
            calls.append(path)
            return base(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        project = snapshot["projects"]["WOLPERTINGER"]
        self.assertEqual(project["head"], {"branch": "main", "sha": head})
        self.assertEqual(project["verification"]["state"], "VERIFIED")
        self.assertTrue(any(f"head_sha={head}" in call for call in calls))

    def test_stale_success_never_verifies_current_head(self):
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_head="a"*40, wolper_run=make_run("c"*40, "success", 99)))
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["verification"]["state"], "UNKNOWN")

    def test_current_head_failure_maps_to_fail(self):
        head = "a" * 40
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_head=head, wolper_run=make_run(head, "failure", 13)))
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["verification"]["state"], "FAIL")

    def test_missing_current_head_run_maps_to_unknown(self):
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_run=[]))
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["verification"]["state"], "UNKNOWN")

    def test_naive_timestamp_fails_closed(self):
        head = "a" * 40
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_head=head, wolper_run=make_run(head, updated_at="2026-09-15T12:00:00")))
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["verification"]["state"], "UNKNOWN")

    def test_malformed_branch_payload_fails_closed(self):
        base = self._api()
        def get_json(path):
            if path == "/repos/KeilerHirsch/WOLPERTINGER/branches/main":
                return {"commit": {}}
            return base(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        project = snapshot["projects"]["WOLPERTINGER"]
        self.assertIsNone(project["head"]["sha"])
        self.assertEqual(project["verification"]["state"], "UNKNOWN")

    def test_default_branch_is_not_hardcoded_to_main(self):
        calls = []
        base = self._api(default_branch="develop")
        def get_json(path):
            calls.append(path)
            return base(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["head"]["branch"], "develop")
        self.assertIn("/repos/KeilerHirsch/WOLPERTINGER/branches/develop", calls)

    def test_valid_empty_release_list_means_none(self):
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_releases=[]))
        project = snapshot["projects"]["WOLPERTINGER"]
        self.assertEqual(project["release_state"], "NONE")
        self.assertIsNone(project["release"])

    def test_malformed_release_response_is_unknown(self):
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_releases={"message": "bad"}))
        project = snapshot["projects"]["WOLPERTINGER"]
        self.assertEqual(project["release_state"], "UNKNOWN")
        self.assertIsNone(project["release"])

    def test_release_with_naive_timestamp_is_unknown(self):
        release = {"draft": False, "name": "Bad time", "tag_name": "v1", "published_at": "2026-09-07T17:21:54", "html_url": "https://example.invalid/release"}
        snapshot = self.renderer.collect_snapshot(self.config, self._api(wolper_releases=[release]))
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["release_state"], "UNKNOWN")

    def test_public_release_is_shipped_and_resolves_tag_to_commit(self):
        head = "a" * 40
        release = {"draft": False, "name": "v1", "tag_name": "v1", "published_at": "2026-09-07T17:21:54Z", "html_url": "https://example.invalid/release"}
        base = self._api(wolper_head=head, wolper_releases=[release])
        def get_json(path):
            if path == "/repos/KeilerHirsch/WOLPERTINGER/commits/v1":
                return {"sha": head}
            return base(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        project = snapshot["projects"]["WOLPERTINGER"]
        self.assertEqual(project["release_state"], "SHIPPED")
        self.assertEqual(project["release"]["sha"], head)
        self.assertEqual(project["release"]["verification"]["state"], "VERIFIED")

    def test_release_does_not_inherit_head_verification_for_different_sha(self):
        head, release_sha = "a"*40, "d"*40
        release = {"draft": False, "name": "v1", "tag_name": "v1", "published_at": "2026-09-07T17:21:54Z", "html_url": "https://example.invalid/release"}
        base = self._api(wolper_head=head, wolper_releases=[release])
        def get_json(path):
            if path == "/repos/KeilerHirsch/WOLPERTINGER/commits/v1":
                return {"sha": release_sha}
            if "WOLPERTINGER/actions/workflows/ci.yml/runs" in path and f"head_sha={release_sha}" in path:
                return {"workflow_runs": []}
            return base(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        project = snapshot["projects"]["WOLPERTINGER"]
        self.assertEqual(project["verification"]["state"], "VERIFIED")
        self.assertEqual(project["release"]["verification"]["state"], "UNKNOWN")

    def test_release_endpoint_failure_is_unknown(self):
        base = self._api()
        def get_json(path):
            if path == "/repos/KeilerHirsch/WOLPERTINGER/releases?per_page=10":
                raise OSError("network")
            return base(path)
        snapshot = self.renderer.collect_snapshot(self.config, get_json)
        self.assertEqual(snapshot["projects"]["WOLPERTINGER"]["release_state"], "UNKNOWN")

    def test_main_fixture_mode_writes_svg_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "profile.json"
            output_path = Path(tmp) / "signal.svg"
            config_path.write_text(json.dumps(self.config), encoding="utf-8")
            exit_code = self.renderer.main(["--config", str(config_path), "--snapshot", str(FIXTURE_PATH), "--output", str(output_path)])
            self.assertEqual(exit_code, 0)
            self.assertIn("VERIFIED", output_path.read_text(encoding="utf-8"))

    def test_main_live_mode_uses_github_token(self):
        class FakeResponse:
            def __init__(self, payload): self.payload = json.dumps(payload).encode("utf-8")
            def __enter__(self): return self
            def __exit__(self, exc_type, exc, tb): return False
            def read(self): return self.payload
        def fake_urlopen(request, timeout=0):
            self.assertEqual(request.headers.get("Authorization"), "Bearer test-token")
            url = request.full_url
            if "/branches/" in url: return FakeResponse({"commit": {"sha": "a"*40}})
            if "/actions/workflows/" in url: return FakeResponse({"workflow_runs": [make_run("a"*40)]})
            if "/releases?" in url: return FakeResponse([])
            return FakeResponse({"default_branch": "main"})
        with tempfile.TemporaryDirectory() as tmp:
            config_path, output_path = Path(tmp)/"profile.json", Path(tmp)/"signal.svg"
            config_path.write_text(json.dumps(self.config), encoding="utf-8")
            with mock.patch.object(self.renderer.urllib.request, "urlopen", fake_urlopen):
                with mock.patch.dict(self.renderer.os.environ, {"GITHUB_TOKEN": "test-token"}):
                    exit_code = self.renderer.main(["--config", str(config_path), "--output", str(output_path)])
            self.assertEqual(exit_code, 0)
            self.assertIn("VERIFIED", output_path.read_text(encoding="utf-8"))


class ProfileSurfaceContractTests(unittest.TestCase):
    def test_workflow_contract(self):
        text = (ROOT / ".github" / "workflows" / "profile-signal.yml").read_text(encoding="utf-8")
        for marker in ("workflow_dispatch:", "pull_request:", "cron: '17 */6 * * *'", "contents: write", "persist-credentials: true", "python -m unittest discover -s tests -v", "GITHUB_TOKEN: ${{ github.token }}", "python tools/render_profile_signal.py --config profile.json --output assets/current-signal.svg", "git diff --quiet -- assets/current-signal.svg", 'git commit -m "chore: refresh profile signal"', "git push"):
            self.assertIn(marker, text)

    def test_readme_contract(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        hero, signal = "assets/profile-hero.webp", "assets/current-signal.svg"
        required_sections = ["## Current signal", "## How I build", "## Engineering DNA", "## Security & forensics", "## MAYHEM Club"]
        self.assertIn(hero, readme)
        self.assertIn(signal, readme)
        self.assertLess(readme.index(hero), readme.index(signal))
        self.assertEqual([readme.index(s) for s in required_sections], sorted(readme.index(s) for s in required_sections))
        required_markers = ["Simple products. Uncomfortably serious engineering underneath.", "High-assurance software", "Evidence before claims.", "Over State of the Art by default.", "I would rather prove an invariant than explain later why", "Precision Mechanic", "Feinwerkmechaniker", "13 of 24 full-time months completed", "no qualification awarded", "Electronics Technician for Industrial Engineering", "Elektroniker für Betriebstechnik", "23 months of voluntary military service", "Autodidact by habit", "Polish", "German", "English", "GitHub is where the workshop became software", "Build cool shit. Share it. Get real feedback.", "Simple outside. Technically unpleasant to copy inside.", "The Man, The Myth, The Legend.", "https://myrank.dev/u/KeilerHirsch", "https://ko-fi.com/keilerhirsch", "https://www.reddit.com/r/MAYHEMClub/"]
        for marker in required_markers: self.assertIn(marker, readme)
        self.assertNotIn("Airbus", readme)
        self.assertNotIn("utm_", readme.lower())
        self.assertGreaterEqual(len(readme.split()), 300)
        self.assertLessEqual(len(readme.split()), 650)
        section = readme.split("## How I build", 1)[1].split("## Engineering DNA", 1)[0]
        self.assertEqual(len([line for line in section.splitlines() if line.startswith("- **")]), 4)
        self.assertTrue((ROOT / "assets" / "profile-hero.webp").exists())


class PublicApiFallbackTests(BaseProfileTest):
    def test_live_mode_works_without_github_token_for_public_repos(self):
        renderer = load_renderer()
        class FakeResponse:
            def __init__(self, payload): self.payload = payload
            def __enter__(self): return self
            def __exit__(self, exc_type, exc, tb): return False
            def read(self): return json.dumps(self.payload).encode("utf-8")
        def fake_urlopen(request, timeout=0):
            self.assertIsNone(request.headers.get("Authorization"))
            url = request.full_url
            if "/branches/" in url: return FakeResponse({"commit": {"sha": "a"*40}})
            if "/actions/workflows/" in url: return FakeResponse({"workflow_runs": []})
            if "/releases?" in url: return FakeResponse([])
            return FakeResponse({"default_branch": "main"})
        with tempfile.TemporaryDirectory() as tmp:
            config_path, output_path = Path(tmp)/"profile.json", Path(tmp)/"signal.svg"
            config_path.write_text((ROOT/"profile.json").read_text(encoding="utf-8"), encoding="utf-8")
            with mock.patch.object(renderer.urllib.request, "urlopen", fake_urlopen):
                with mock.patch.dict(renderer.os.environ, {}, clear=True):
                    exit_code = renderer.main(["--config", str(config_path), "--output", str(output_path)])
            self.assertEqual(exit_code, 0)
            self.assertIn("UNKNOWN", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
