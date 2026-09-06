"""Offline structural/provenance checks, not a substitute for a GPU render."""

import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_reference_shoot as build


class ReferenceShootTests(unittest.TestCase):
    def setUp(self):
        self.pack = build.load_pack()
        self.runs = json.loads((build.PACK / "runs.json").read_text())["runs"]

    def test_four_independent_deterministic_graphs(self):
        self.assertEqual({s["id"] for s in self.pack["shots"]},
                         {"front", "profile", "full-body", "close-up"})
        for shot in self.pack["shots"]:
            graph = build.workflow(self.pack, shot)
            self.assertEqual(graph, build.workflow(self.pack, shot))
            source = next(n for n in graph["nodes"] if n["type"] == "LoadImage")
            self.assertEqual(source["widgets_values"][0], self.pack["reference"]["filename"])
            sampler = next(n for n in graph["nodes"] if n["type"] == "KSampler")
            self.assertEqual(sampler["widgets_values"][:4], [shot["seed"], "fixed", 10, 1.0])
            self.assertEqual(sum(n["type"] == "SaveImage" for n in graph["nodes"]), 1)
            self.assertEqual(sum(n["type"] == "LoadImage" for n in graph["nodes"]), 1)

    def test_workflow_ids_match_comfyui_uuid_contract(self):
        # ComfyUI_frontend workflowSchema.ts, revision c25e8cb: id is UUID, not a slug.
        ids = []
        for shot in self.pack["shots"]:
            workflow_id = build.workflow(self.pack, shot)["id"]
            with self.subTest(shot=shot["id"]):
                self.assertEqual(str(UUID(workflow_id)), workflow_id)
            ids.append(workflow_id)
        self.assertEqual(len(set(ids)), len(self.pack["shots"]))

    def test_primary_action_opens_inline_setup_not_a_markdown_download(self):
        rendered = build.render_page(self.pack, self.runs)
        self.assertIn('class="button" href="#make-it-yours"', rendered)
        self.assertIn('id="make-it-yours"', rendered)
        self.assertIn(f'href="{self.pack["dependency"]["space"]}"', rendered)
        self.assertIn("random seed off", rendered)

    def test_links_have_matching_sockets_and_acyclic_dependencies(self):
        for shot in self.pack["shots"]:
            graph = build.workflow(self.pack, shot)
            nodes = {n["id"]: n for n in graph["nodes"]}
            self.assertEqual(len(nodes), len(graph["nodes"]))
            self.assertEqual(len({link[0] for link in graph["links"]}), len(graph["links"]))
            edges = {node_id: set() for node_id in nodes}
            for link_id, src, src_slot, dst, dst_slot, kind in graph["links"]:
                outgoing = nodes[src]["outputs"][src_slot]
                incoming = nodes[dst]["inputs"][dst_slot]
                self.assertIn(link_id, outgoing["links"])
                self.assertEqual(incoming["link"], link_id)
                self.assertEqual(incoming["type"], kind)
                self.assertEqual(outgoing["type"], kind)
                edges[dst].add(src)
            while edges:
                ready = {node_id for node_id, dependencies in edges.items() if not dependencies}
                self.assertTrue(ready, "Cycle in graph")
                edges = {node_id: dependencies - ready for node_id, dependencies in edges.items()
                         if node_id not in ready}

    def test_dual_reference_conditioning_and_preencode_target(self):
        graph = build.workflow(self.pack, self.pack["shots"][0])
        nodes = graph["nodes"]
        links = {link[0]: link for link in graph["links"]}
        source = next(n for n in nodes if n["type"] == "LoadImage")
        target = next(n for n in nodes if n["type"] == "EmptySD3LatentImage")
        patch = next(n for n in nodes if n["type"] == "Krea2EditModelPatch")
        for name, expected in (("source_image", source), ("target_latent", target)):
            incoming = next(i for i in patch["inputs"] if i["name"] == name)
            self.assertEqual(links[incoming["link"]][1], expected["id"])
        grounded = [n for n in nodes if n["type"] == "Krea2EditGroundedEncode"]
        self.assertEqual(len(grounded), 2)
        self.assertEqual(grounded[1]["widgets_values"][0], "")
        for node in grounded:
            incoming = next(i for i in node["inputs"] if i["name"] == "image")
            self.assertEqual(links[incoming["link"]][1], source["id"])
        sampler = next(n for n in nodes if n["type"] == "KSampler")
        latent = next(i for i in sampler["inputs"] if i["name"] == "latent_image")
        self.assertEqual(links[latent["link"]][1], target["id"])
        self.assertEqual(patch["widgets_values"][2], "fit")

    def test_only_reviewed_outputs_are_shown(self):
        accepted = build.accepted_runs(self.pack, self.runs)
        self.assertEqual(set(accepted), {s["id"] for s in self.pack["shots"]})
        rendered = build.render_page(self.pack, self.runs)
        for run in accepted.values():
            self.assertIn(f'src="{run["output"]}"', rendered)
        self.assertIn("structural checks only", rendered)
        self.assertNotIn("Not visually accepted yet", rendered)
        pending = copy.deepcopy(self.runs)
        for run in pending:
            if run["shot"] == "front":
                run["review"]["status"] = "pending"
        partial = build.render_page(self.pack, pending)
        self.assertNotIn('src="examples/front.webp"', partial)
        self.assertIn("Not visually accepted yet", partial)

    def test_per_shot_setting_reaches_graph_and_receipt_validation(self):
        front = next(s for s in self.pack["shots"] if s["id"] == "front")
        profile = next(s for s in self.pack["shots"] if s["id"] == "profile")
        self.assertEqual(build.settings_for(self.pack, front)["ref_boost"], 1.0)
        self.assertEqual(build.settings_for(self.pack, profile)["ref_boost"], 2.5)
        for shot in (front, profile):
            graph = build.workflow(self.pack, shot)
            patch = next(n for n in graph["nodes"] if n["type"] == "Krea2EditModelPatch")
            self.assertEqual(patch["widgets_values"][0], build.settings_for(self.pack, shot)["ref_boost"])
        run = copy.deepcopy(build.accepted_runs(self.pack, self.runs)["front"])
        run["settings"]["ref_boost"] = 2.5
        with self.assertRaisesRegex(ValueError, "Setting mismatch"):
            build.accepted_runs(self.pack, [run])

    def test_browser_asset_and_actual_input_are_required_and_verified(self):
        original = next(r for r in self.runs
                        if r["review"]["status"] == "accepted" and r.get("provider_asset_id"))
        self.assertIsNone(original["event_id"])
        self.assertIn(original["shot"], build.accepted_runs(self.pack, [original]))
        mutations = (("provider_asset_id", "wrong"), ("provider_asset_id", "0" * 64),
                     ("provider_asset_id", None), ("output_url", "https://example.com/image.webp"),
                     ("reference_input", None))
        for key, value in mutations:
            run = copy.deepcopy(original)
            run[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                build.accepted_runs(self.pack, [run])
        for key, value in (("sha256", "0" * 64), ("transport", ""),
                           ("path", "../../images/portrait-001.webp")):
            run = copy.deepcopy(original)
            run["reference_input"][key] = value
            with self.subTest(input_key=key), self.assertRaises(ValueError):
                build.accepted_runs(self.pack, [run])

    def test_api_event_id_cannot_be_replaced_with_arbitrary_text(self):
        run = copy.deepcopy(next(r for r in self.runs
                                 if r["review"]["status"] == "accepted" and r.get("event_id")))
        run["event_id"] = "made up"
        with self.assertRaisesRegex(ValueError, "Missing provider provenance"):
            build.accepted_runs(self.pack, [run])

    def test_missing_review_never_passes(self):
        run = copy.deepcopy(next(r for r in self.runs if r["review"]["status"] == "accepted"))
        run["review"]["anatomy"] = "pending"
        with self.assertRaisesRegex(ValueError, "Incomplete visual review"):
            build.accepted_runs(self.pack, [run])

    def test_mutated_recipe_and_bytes_are_rejected(self):
        original = next(r for r in self.runs if r["review"]["status"] == "accepted")
        for key, value in (("instruction", "a different prompt"), ("seed", 123),
                           ("reference_sha256", "0" * 64), ("sha256", "0" * 64),
                           ("status", "quota_blocked"), ("randomize_seed", True),
                           ("output", "../../images/portrait-001.webp")):
            run = copy.deepcopy(original)
            run[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                build.accepted_runs(self.pack, [run])
        run = copy.deepcopy(original)
        run["settings"]["ref_boost"] = 4
        with self.assertRaisesRegex(ValueError, "Setting mismatch"):
            build.accepted_runs(self.pack, [run])

    def test_duplicate_accepted_shot_is_rejected(self):
        run = next(r for r in self.runs if r["review"]["status"] == "accepted")
        with self.assertRaisesRegex(ValueError, "More than one accepted run"):
            build.accepted_runs(self.pack, [run, run])

    def test_catalog_is_not_inflated_by_adapter_results(self):
        catalog = json.loads((build.ROOT / "prompts.json").read_text())
        self.assertFalse(any(e["image"].startswith("workflows/reference-shoot/")
                             for e in catalog["entries"]))

    def test_preview_local_links_resolve(self):
        refs = []

        class Links(HTMLParser):
            def handle_starttag(self, tag, attrs):
                refs.extend(value for key, value in attrs if key in ("src", "href"))

        Links().feed(build.render_page(self.pack, self.runs))
        for ref in refs:
            if not ref.startswith(("https://", "http://", "#")):
                with self.subTest(ref=ref):
                    self.assertTrue((build.PACK / ref).resolve().exists())


if __name__ == "__main__":
    unittest.main()
