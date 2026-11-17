"""Behavioral invariants; all synthetic work/time is confined to temporary ledgers."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from store import Store
from metrics import summary
from forecast import forecast, calibration
from report import markdown_status


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="work-entropy-test-")
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.e("ledger.init", {})
        self.e("project.add", {"id": "p", "title": "Synthetic project", "unmodeled": ["runtime"]})

    def e(self, kind, data, at="2020-01-01T00:00:00Z", source="user_message", key=None, actor="assistant"):
        return self.store.append(kind, data, {"kind": source, "ref": "synthetic-test-only"},
                                 actor=actor, at=at, key=key)

    def state(self):
        return self.store.read()[0]

    def task(self, name="t", day="2020-01-01", baseline=True, receipt=True):
        data = dict(id=name, project_id="p", title="Design identity", work_type="design")
        if receipt:
            data["received_at"] = day + "T00:00:00Z"
        self.e("task.add", data, at=day + "T00:00:00Z")
        self.e("atom.add", dict(id="a-" + name, project_id="p", task_ids=[name],
            topic="identity", kind="decision", question="Who allocates the ID for " + name + "?",
            closure="Document and explain identity boundary", candidates=["source", "local"]),
            at=day + "T00:00:00Z")
        self.e("work.add", dict(id="w-" + name, task_id=name, title="Document choice",
            acceptance=["Identity origin and uniqueness are explicit"]), at=day + "T00:00:00Z")
        if baseline:
            self.baseline(name, "b-" + name, day)

    def baseline(self, task="t", name="b-t", day="2020-01-01"):
        self.e("baseline.add", dict(scope="task:" + task, id=name, reason="initial scope"),
               at=day + "T00:00:00Z")

    def focus(self, task="t", day="2020-01-01", start="00:00:00", end="01:00:00",
              topic="identity", atoms=None, confirmed=True, precision="second", phase="understand"):
        return self.e("focus.add", dict(task_id=task, topic=topic, phase=phase,
            atom_ids=atoms if atoms is not None else ["a-" + task], confirmed=confirmed,
            precision=precision, start=day + "T" + start + "Z", end=day + "T" + end + "Z"),
            at=day + "T" + end + "Z", source="manual_report", actor="user")

    def assess(self, task="t", day="2020-01-01", grade=1, when="01:00:00"):
        self.e("atom.assess", dict(id="a-" + task, grade=grade,
            reason="Synthetic user explains a new counterexample"),
            at=day + "T" + when + "Z")

    def coverage(self, task="t", day="2020-01-01"):
        self.e("task.coverage", dict(id=task, complete=True, reason="Synthetic timer coverage confirmed"),
               at=day + "T02:00:00Z")

    def finish(self, task="t", day="2020-01-01", when="02:00:00"):
        self.e("work.verify", dict(id="w-" + task, verified=True, reason="Synthetic artifact satisfies acceptance"),
               at=day + "T" + when + "Z", source="artifact")
        self.e("task.complete", {"id": task}, at=day + "T" + when + "Z", source="artifact")

    def report(self, task="t", now="2020-01-03T00:00:00Z"):
        return summary(self.state(), task_id=task, now=now)

    def test_replay_and_command_idempotency(self):
        data = {"id": "q", "title": "Other"}
        first, created = self.e("project.add", data, key="message-42")
        second, again = self.e("project.add", data, key="message-42")
        self.assertTrue(created)
        self.assertFalse(again)
        self.assertEqual(first, second)
        self.assertEqual(self.store.read(), self.store.read())
        with self.assertRaises(ValueError):
            self.e("project.add", {"id": "q2", "title": "Other"}, key="message-42")

    def test_model_resolution_does_not_imply_personal_or_delivery_completion(self):
        self.task()
        self.e("atom.resolve", {"id": "a-t", "remaining": ["local"], "reason": "Decision accepted"}, source="artifact")
        r = self.report()
        self.assertEqual(r["scope_model_entropy"]["model_bit_upper_sum"], 0)
        self.assertEqual(r["baseline_scope_model_bits"], 1)
        self.assertEqual(r["personal_remaining_load"], 1)
        self.assertEqual(r["personal_net_gain"], 0)
        self.assertEqual(r["baseline_delivery_fraction"], 0)
        self.assertEqual(r["unassessed_atoms"], ["a-t"])
        self.assertIn("数据不足", markdown_status(r))

    def test_ai_artifact_and_automatic_test_cannot_award_personal_mastery(self):
        self.task()
        before = self.store.path.read_bytes()
        for kind in ["artifact", "assistant_message", "test"]:
            with self.subTest(source=kind), self.assertRaises(ValueError):
                self.e("atom.assess", {"id": "a-t", "grade": 1, "reason": "AI said so"}, source=kind)
        self.assertEqual(before, self.store.path.read_bytes())

    def test_paired_gain_rates_and_unknown_calendar(self):
        self.task(receipt=False)
        self.focus()
        self.assess(grade=.75)
        self.coverage()
        r = self.report()
        self.assertEqual(r["personal_net_gain"], .75)
        self.assertEqual(r["narrow_rate"], .75)
        self.assertIsNone(r["broad_rate"])
        self.assertIsNone(r["calendar_days"])

    def test_elapsed_chat_span_does_not_become_focus_time(self):
        self.task()
        self.assess()
        self.coverage()
        r = self.report()
        self.assertEqual(r["confirmed_focus_hours"], 0)
        self.assertIsNone(r["narrow_rate"])
        self.assertIn("unpaired_gain:a-t", r["rate_blockers"])

    def test_estimated_time_not_exact_rate_denominator(self):
        self.task()
        self.focus(confirmed=False, precision="estimated")
        self.assess()
        self.coverage()
        r = self.report()
        self.assertEqual(r["uncertain_focus_hours"], 1)
        self.assertEqual(r["confirmed_focus_hours"], 0)
        self.assertIsNone(r["narrow_rate"])

    def test_overlap_union_and_conflicting_topics(self):
        self.task()
        self.focus()
        self.focus(start="00:30:00", end="01:30:00")
        self.assess(when="01:30:00")
        self.coverage()
        self.assertEqual(self.report()["confirmed_focus_hours"], 1.5)
        self.focus(topic="unrelated", atoms=[], start="00:30:00", end="01:00:00")
        r = self.report()
        self.assertEqual(r["confirmed_focus_hours"], 1)
        self.assertEqual(r["conflict_hours"], .5)
        self.assertIsNone(r["narrow_rate"])

    def test_one_active_focus_across_projects_and_switch(self):
        self.task()
        d = dict(task_id="t", topic="identity", phase="understand", atom_ids=["a-t"], confirmed=True, precision="second")
        self.e("focus.start", d, source="explicit_timer", actor="user")
        with self.assertRaises(ValueError):
            self.e("focus.start", d, source="explicit_timer", actor="user")
        self.e("focus.switch", dict(d, topic="other", atom_ids=[]), at="2020-01-01T00:30:00Z", source="explicit_timer", actor="user")
        r = self.report()
        self.assertEqual(r["confirmed_focus_hours"], .5)
        self.assertEqual(r["open_focus_intervals"], 1)

    def test_waiting_and_automation_are_not_human_focus(self):
        self.task()
        self.focus(phase="wait")
        r = self.report()
        self.assertEqual(r["confirmed_focus_hours"], 0)
        self.assertEqual(r["wait_hours"], 1)
        with self.assertRaises(ValueError):
            self.e("focus.start", dict(task_id="t", topic="identity", phase="understand", atom_ids=[],
                confirmed=True, precision="second"), actor="automation", source="explicit_timer")

    def test_scope_growth_preserves_original_gain_denominator(self):
        self.task()
        self.e("atom.add", dict(id="new", project_id="p", task_ids=["t"], topic="new",
            kind="competency", question="New skill?", closure="Apply it", budget=10))
        r = self.report()
        self.assertEqual(r["baseline_personal_load"], 1)
        self.assertEqual(r["personal_net_gain"], 0)
        self.assertEqual(r["personal_remaining_load"], 11)
        self.assertEqual(r["new_atoms_since_baseline"], ["new"])

    def test_retraction_can_make_net_progress_negative(self):
        self.task(baseline=False)
        self.assess(grade=.5)
        self.baseline()
        self.e("atom.reopen", {"id": "a-t", "reason": "Counterexample invalidates previous assessment"})
        self.assertEqual(self.report()["personal_net_gain"], -.5)

    def test_delivery_requires_real_acceptance_and_stops_focus(self):
        self.task()
        with self.assertRaises(ValueError):
            self.e("task.complete", {"id": "t"})
        self.finish()
        self.assertEqual(self.report()["baseline_delivery_fraction"], 1)
        self.assertEqual(self.report()["personal_remaining_load"], 1)

    def test_duplicate_question_shared_across_tasks_counted_once(self):
        self.task()
        self.e("task.add", dict(id="other", project_id="p", title="Other task", work_type="design"))
        self.e("atom.link", {"id": "a-t", "task_id": "other"})
        r = summary(self.state(), project_id="p")
        self.assertEqual(r["personal_budget"], 1)
        with self.assertRaises(ValueError):
            self.e("atom.add", dict(id="duplicate", project_id="p", task_ids=["other"], topic="identity",
                kind="decision", question="Who allocates the ID for t?", closure="Same question"))

    def test_invalid_events_and_corrupt_log_fail_closed(self):
        with self.assertRaises(ValueError):
            self.e("project.add", {"id": "bad", "title": "Bad"}, at="2020-01-01T00:00:00")
        with self.assertRaises(ValueError):
            self.e("unknown.type", {})
        self.store.path.write_bytes(self.store.path.read_bytes() + b'{"partial":')
        with self.assertRaises(ValueError):
            self.store.read()

    def test_cold_start_never_fabricates_quantiles(self):
        self.task()
        r = forecast(self.state(), "t")
        self.assertEqual(r["stage"], "data_insufficient")
        self.assertIsNone(r["focus_hours"])
        r = forecast(self.state(), "t", rate_range=[1, 2], known_execution_hours=2)
        self.assertEqual(r["stage"], "explicit_scenario")
        self.assertEqual(r["focus_hours"], {"optimistic": 2.5, "conservative": 3.0})
        self.assertIsNone(r["calendar_days"])

    def history(self, n=10):
        for i in range(n):
            task, day = "h" + str(i), f"2019-01-{i+1:02d}"
            self.task(task, day)
            self.focus(task, day)
            self.assess(task, day)
            self.coverage(task, day)
            self.finish(task, day)
            self.e("task.sample", {"id": task}, at=day + "T02:00:00Z")

    def test_empirical_forecast_is_reproducible_and_whole_mode_no_double_count(self):
        self.history()
        self.task()
        s = self.state()
        a = forecast(s, "t", seed=42)
        self.assertEqual(a, forecast(s, "t", seed=42))
        self.assertEqual(a["stage"], "empirical_uncalibrated")
        self.assertEqual(a["focus_hours"], {"p50": 1, "p85": 1})
        self.assertFalse(a["calibrated"])
        with self.assertRaises(ValueError):
            forecast(s, "t", mode="whole", known_execution_hours=1)

    def test_forecast_snapshot_has_no_future_leak_and_measures_only_remaining_time(self):
        self.history()
        self.task()
        options = dict(mode="decomposed", simulations=100)
        with patch("store.clock", return_value="2020-01-01T12:00:00Z"):
            event, _ = self.store.append("forecast.record", dict(task_id="t", options=options),
                {"kind": "system", "ref": "synthetic forecast before outcome"})
        self.focus(start="12:00:00", end="12:30:00")
        self.assess(when="12:30:00")
        self.coverage()
        self.finish(when="14:00:00")
        c = calibration(self.state(), "t")
        self.assertEqual(c["n"], 1)
        self.assertEqual(c["rows"][0]["actual_hours"], .5)
        self.assertEqual(c["p85_coverage"], 1)
        self.assertAlmostEqual(c["brier_at_p85"], .0225)
        self.assertEqual(self.state()["forecasts"][0]["id"], event["event_id"])

    def test_backdated_forecasts_rejected(self):
        self.task()
        with self.assertRaises(ValueError):
            self.e("forecast.record", dict(task_id="t", options={}))

    def test_late_mastery_cannot_be_counted_inside_an_already_finished_task(self):
        self.task()
        self.focus()
        self.coverage()
        self.finish()
        self.assess(day="2020-01-02")
        r = self.report()
        self.assertIsNone(r["narrow_rate"])
        self.assertIn("assessment_outside_task_window:a-t", r["rate_blockers"])
        with self.assertRaises(ValueError):
            self.e("focus.start", dict(task_id="t", topic="identity", phase="understand",
                atom_ids=["a-t"], confirmed=True, precision="second"),
                at="2020-01-02T00:00:00Z", source="explicit_timer", actor="user")

    def test_scope_changed_or_retracted_samples_are_not_reused_for_forecasting(self):
        self.history()
        self.task()
        self.e("atom.reopen", {"id": "a-h0", "reason": "Previous evidence invalidated"})
        r = forecast(self.state(), "t")
        self.assertEqual(r["sample_count"], 9)
        self.assertEqual(r["stage"], "data_insufficient")

    def test_cli_init_reuses_a_valid_ledger_created_by_another_entrypoint(self):
        script = Path(__file__).with_name("ledger.py")
        before = self.store.path.read_bytes()
        r = subprocess.run([sys.executable, "-B", str(script), "--store", self.temp.name, "init"],
                           capture_output=True, text=True, check=True)
        self.assertFalse(json.loads(r.stdout)["created"])
        self.assertEqual(before, self.store.path.read_bytes())


if __name__ == "__main__":
    unittest.main()
