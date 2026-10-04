"""Tests for scripts/examples-section.py.

The generator writes the Examples gallery of the README from
examples/manifest.json. What must hold: every entry carries its provenance
(request, mode, version and commit, model, selection, cost) and its receipt;
a missing field, a missing media or receipt file, a media file over 720 KB and
U+2014 (em dash) are refused instead of published; a conversation links its
transcript, the brief of the agent playing the client and the first message it
sent, and is refused without the last two; a recorded run that is not
featured is listed after the gallery with its reason and receipt; --write
replaces only its region and --check fails when the region is out of date.
"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "examples-section.py"
REAL_MANIFEST = Path(__file__).resolve().parents[2] / "examples" / "manifest.json"
DASH = "\u2014"

ENTRY = {
    "id": "pottery-firing",
    "title": "Pottery studio firing stages",
    "skill": "cast",
    "modules": ["gsap", "tells"],
    "kind": "cast",
    "run": {
        "mode": "headless",
        "harness": "claude plugin eval, Claude Code 2.1.289",
        "plugin_version": "4.1.0",
        "plugin_commit": "09c177b",
        "model": "claude-opus-5-5",
        "date": "2026-10-04",
        "cost_usd": 1.5256,
        "turns": 23,
        "selected_from": 1,
        "human_edits": 0,
    },
    "prompt": "/genjutsu:cast pin the four firing stages",
    "caption": "The page is the starting fixture; the pin is the run's work.",
    "media": {
        "cover": {"src": "assets/examples/pottery-firing/still.png", "alt": "the pinned section"},
        "clip": {"src": "assets/examples/pottery-firing/clip.webp", "alt": "scrolling the pinned section"},
        "stills": [],
    },
    "receipt": "examples/pottery-firing/receipt.md",
    "notes": "First pass, built unchanged.",
}


class ExamplesSectionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "examples" / "pottery-firing").mkdir(parents=True)
        (self.tmp / "examples" / "pottery-firing" / "receipt.md").write_text("receipt\n")
        media = self.tmp / "assets" / "examples" / "pottery-firing"
        media.mkdir(parents=True)
        (media / "still.png").write_bytes(b"png")
        (media / "clip.webp").write_bytes(b"webp")
        self.manifest = self.tmp / "examples" / "manifest.json"
        self.write_manifest([copy.deepcopy(ENTRY)])

    def write_manifest(self, entries):
        self.manifest.write_text(json.dumps({"examples": entries}, ensure_ascii=False))

    def run_gen(self, *extra):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--manifest", str(self.manifest), *extra],
            capture_output=True, text=True,
        )

    def refused(self, entry, needle):
        self.write_manifest([entry])
        r = self.run_gen()
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn(needle, r.stderr)

    def test_block_is_wrapped_in_its_markers(self):
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.strip().splitlines()
        self.assertEqual(out[0], "<!-- genjutsu:examples:start -->")
        self.assertEqual(out[-1], "<!-- genjutsu:examples:end -->")

    def test_block_carries_the_request_the_provenance_and_the_receipt(self):
        out = self.run_gen().stdout
        self.assertIn("`/genjutsu:cast pin the four firing stages`", out)
        for fact in ("`cast`", "one-shot headless run", "genjutsu 4.1.0 at `09c177b`",
                     "`claude-opus-5-5`", "first pass", "$1.53", "23 turns", "0 human edits"):
            self.assertIn(fact, out)
        self.assertIn("[Receipt](./examples/pottery-firing/receipt.md)", out)
        self.assertIn("No transcript", out)
        self.assertIn("The page is the starting fixture", out)

    def test_clip_is_shown_width_limited_and_cover_without_a_clip(self):
        out = self.run_gen().stdout
        self.assertIn('src="./assets/examples/pottery-firing/clip.webp"', out)
        self.assertIn('width="720"', out)
        entry = copy.deepcopy(ENTRY)
        del entry["media"]["clip"]
        self.write_manifest([entry])
        out = self.run_gen().stdout
        self.assertIn('src="./assets/examples/pottery-firing/still.png"', out)

    def conversation(self, entry):
        """Turn an entry into a conversation, with its transcript, brief and opening on disk."""
        ex = self.tmp / "examples" / entry["id"]
        ex.mkdir(parents=True, exist_ok=True)
        for name in ("transcript.md", "client.md", "opening.txt"):
            (ex / name).write_text("t\n")
        entry["run"]["mode"] = "conversation"
        entry["transcript"] = f"examples/{entry['id']}/transcript.md"
        entry["client"] = f"examples/{entry['id']}/client.md"
        entry["opening"] = f"examples/{entry['id']}/opening.txt"
        return entry

    def test_selection_and_conversation_are_said(self):
        entry = self.conversation(copy.deepcopy(ENTRY))
        entry["run"]["selected_from"] = 3
        self.write_manifest([entry])
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("selected from 3 runs", r.stdout)
        self.assertIn("conversation with an agent playing the client", r.stdout)
        self.assertIn("[Transcript](./examples/pottery-firing/transcript.md)", r.stdout)
        self.assertIn("[Client brief](./examples/pottery-firing/client.md)", r.stdout)
        self.assertIn("[First message](./examples/pottery-firing/opening.txt)", r.stdout)
        self.assertNotIn("one-shot headless run is", r.stdout)

    def test_a_conversation_without_its_transcript_is_refused(self):
        entry = self.conversation(copy.deepcopy(ENTRY))
        del entry["transcript"]
        self.refused(entry, "transcript")

    def test_a_conversation_without_its_client_brief_or_opening_is_refused(self):
        for key in ("client", "opening"):
            with self.subTest(key=key):
                entry = self.conversation(copy.deepcopy(ENTRY))
                del entry[key]
                self.refused(entry, key)
            with self.subTest(key=key, missing_file=True):
                entry = self.conversation(copy.deepcopy(ENTRY))
                entry[key] = "examples/pottery-firing/gone.txt"
                self.refused(entry, "gone.txt")
            with self.subTest(key=key, unfeatured=True):
                hidden = self.conversation(self.unfeatured())
                del hidden[key]
                self.write_manifest([copy.deepcopy(ENTRY), hidden])
                r = self.run_gen()
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assertIn(key, r.stderr)

    def test_a_client_brief_on_a_headless_run_is_refused(self):
        entry = copy.deepcopy(ENTRY)
        entry["client"] = "examples/pottery-firing/receipt.md"
        self.refused(entry, "only for a conversation")

    def test_an_unfeatured_conversation_lists_its_brief_and_opening(self):
        hidden = self.conversation(self.unfeatured())
        self.write_manifest([copy.deepcopy(ENTRY), hidden])
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(
            "[Receipt](./examples/old-run/receipt.md) · [Transcript](./examples/old-run/transcript.md)"
            " · [Client brief](./examples/old-run/client.md) · [First message](./examples/old-run/opening.txt)",
            r.stdout,
        )

    def test_a_missing_required_field_is_refused(self):
        for key in ("prompt", "caption", "receipt", "notes", "media"):
            with self.subTest(key=key):
                entry = copy.deepcopy(ENTRY)
                del entry[key]
                self.refused(entry, key)
        for key in ("plugin_commit", "model", "cost_usd", "selected_from", "mode"):
            with self.subTest(run_key=key):
                entry = copy.deepcopy(ENTRY)
                del entry["run"][key]
                self.refused(entry, key)

    def test_a_media_path_that_does_not_exist_is_refused(self):
        entry = copy.deepcopy(ENTRY)
        entry["media"]["clip"]["src"] = "assets/examples/pottery-firing/nope.webp"
        self.refused(entry, "nope.webp")
        entry = copy.deepcopy(ENTRY)
        entry["media"]["stills"] = [{"src": "assets/examples/pottery-firing/gone.png", "alt": "x"}]
        self.refused(entry, "gone.png")

    def test_a_receipt_that_does_not_exist_is_refused(self):
        entry = copy.deepcopy(ENTRY)
        entry["receipt"] = "examples/pottery-firing/missing.md"
        self.refused(entry, "missing.md")

    def test_media_over_720_kb_is_refused(self):
        clip = self.tmp / "assets" / "examples" / "pottery-firing" / "clip.webp"
        clip.write_bytes(b"0" * 720_000)
        self.write_manifest([copy.deepcopy(ENTRY)])
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        clip.write_bytes(b"0" * 720_001)
        self.refused(copy.deepcopy(ENTRY), "over the")

    def test_an_unreleased_build_and_the_client_cost_are_said(self):
        entry = copy.deepcopy(ENTRY)
        entry["run"].update(plugin_source="fix/skill-arguments on 09c177b (4.1.1 candidate)",
                            client_cost_usd=0.8589, exchanges=8)
        self.write_manifest([entry])
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("genjutsu fix/skill-arguments on 09c177b (4.1.1 candidate)", r.stdout)
        self.assertNotIn("genjutsu 4.1.0 at", r.stdout)
        self.assertIn("$1.53 (plus $0.86 for the agent playing the client)", r.stdout)
        self.assertIn("8 exchanges", r.stdout)
        self.assertIn("names the branch and commit", r.stdout)

    def test_a_plugin_source_that_does_not_name_the_commit_is_refused(self):
        entry = copy.deepcopy(ENTRY)
        entry["run"]["plugin_source"] = "fix/skill-arguments (4.1.1 candidate)"
        self.refused(entry, "plugin_source")

    def unfeatured(self):
        (self.tmp / "examples" / "old-run").mkdir(exist_ok=True)
        (self.tmp / "examples" / "old-run" / "receipt.md").write_text("receipt\n")
        return {
            "id": "old-run", "featured": False, "title": "First headless run",
            "skill": "paint", "kind": "paint-new",
            "run": {"mode": "headless", "plugin_version": "4.1.0", "plugin_commit": "09c177b",
                    "date": "2026-10-04"},
            "reason": "Plain: a correct page with nothing past a tidy default.",
            "receipt": "examples/old-run/receipt.md",
        }

    def test_an_unfeatured_run_is_listed_after_the_gallery_with_its_reason(self):
        self.write_manifest([copy.deepcopy(ENTRY), self.unfeatured()])
        r = self.run_gen()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        self.assertIn("### Recorded, not featured", out)
        self.assertLess(out.index("### Pottery studio firing stages"), out.index("### Recorded, not featured"))
        self.assertIn(
            "- **First headless run**: `paint`, one-shot headless run, genjutsu 4.1.0 at `09c177b`, "
            "2026-10-04. Plain: a correct page with nothing past a tidy default. "
            "[Receipt](./examples/old-run/receipt.md)",
            out,
        )
        self.assertNotIn("### First headless run", out)
        self.write_manifest([copy.deepcopy(ENTRY)])
        self.assertNotIn("Recorded, not featured", self.run_gen().stdout)

    def test_an_unfeatured_run_needs_its_reason_and_its_receipt(self):
        entry = self.unfeatured()
        del entry["reason"]
        self.write_manifest([copy.deepcopy(ENTRY), entry])
        r = self.run_gen()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("reason", r.stderr)
        entry = self.unfeatured()
        entry["receipt"] = "examples/old-run/gone.md"
        self.write_manifest([copy.deepcopy(ENTRY), entry])
        r = self.run_gen()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("gone.md", r.stderr)

    def test_a_manifest_with_nothing_featured_is_refused(self):
        self.refused(self.unfeatured(), "featured")

    def test_an_em_dash_anywhere_is_refused(self):
        for path in (("caption",), ("run", "harness"), ("media", "cover", "alt")):
            with self.subTest(path=path):
                entry = copy.deepcopy(ENTRY)
                node = entry
                for k in path[:-1]:
                    node = node[k]
                node[path[-1]] = f"one {DASH} two"
                self.refused(entry, "em dash")

    def test_unknown_kind_mode_and_multiline_prompt_are_refused(self):
        entry = copy.deepcopy(ENTRY)
        entry["kind"] = "sketch"
        self.refused(entry, "kind")
        entry = copy.deepcopy(ENTRY)
        entry["run"]["mode"] = "batch"
        self.refused(entry, "mode")
        entry = copy.deepcopy(ENTRY)
        entry["prompt"] = "/genjutsu:cast one\nsecond line"
        self.refused(entry, "first line")

    def test_duplicate_ids_are_refused(self):
        self.write_manifest([copy.deepcopy(ENTRY), copy.deepcopy(ENTRY)])
        r = self.run_gen()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("duplicate", r.stderr)

    def test_a_backtick_in_the_prompt_stays_one_code_span(self):
        entry = copy.deepcopy(ENTRY)
        entry["prompt"] = "/genjutsu:cast animate the `Card` hover"
        self.write_manifest([entry])
        out = self.run_gen().stdout
        self.assertIn("`` /genjutsu:cast animate the `Card` hover ``", out)

    def test_write_replaces_only_the_region_and_check_follows(self):
        target = self.tmp / "README.md"
        target.write_text("before\n<!-- genjutsu:examples:start -->\nold\n<!-- genjutsu:examples:end -->\nafter\n")
        self.assertNotEqual(self.run_gen("--check", str(target)).returncode, 0)
        r = self.run_gen("--write", str(target))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = target.read_text()
        self.assertTrue(text.startswith("before\n<!-- genjutsu:examples:start -->\n"))
        self.assertTrue(text.endswith("<!-- genjutsu:examples:end -->\nafter\n"))
        self.assertNotIn("\nold\n", text)
        self.assertEqual(self.run_gen("--check", str(target)).returncode, 0)
        entry = copy.deepcopy(ENTRY)
        entry["run"]["cost_usd"] = 2.5
        self.write_manifest([entry])
        self.assertNotEqual(self.run_gen("--check", str(target)).returncode, 0)

    def test_write_refuses_a_file_without_exactly_one_region(self):
        target = self.tmp / "README.md"
        target.write_text("no markers here\n")
        r = self.run_gen("--write", str(target))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(target.read_text(), "no markers here\n")

    def test_the_real_manifest_is_valid(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(REAL_MANIFEST)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
