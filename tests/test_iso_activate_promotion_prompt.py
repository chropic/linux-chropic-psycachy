#!/usr/bin/env python3
"""Exercise the activation script's reviewed-promotion prompt without host writes."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
ACTIVATE = REPO / "iso/activate.sh"


class ActivationPromotionPromptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="activate-promotion-prompt-")
        self.root = Path(self.temp.name)
        self.calls = self.root / "trial-calls.txt"
        self.fake_trial = self.root / "fake-trial"
        self.fake_trial.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$@\" > \"$TRIAL_CALLS\"\n",
            encoding="utf-8",
        )
        self.fake_trial.chmod(0o755)

    def tearDown(self):
        self.temp.cleanup()

    def run_prompt(self, answer):
        env = os.environ.copy()
        env["ACTIVATE_SCRIPT"] = str(ACTIVATE)
        env["FAKE_TRIAL"] = str(self.fake_trial)
        env["TRIAL_CALLS"] = str(self.calls)
        return subprocess.run(
            [
                "bash",
                "-c",
                'source "$ACTIVATE_SCRIPT"; trial="$FAKE_TRIAL"; request_promotion',
            ],
            input=answer,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_blank_reviewed_path_stops_without_promote_invocation(self):
        result = self.run_prompt("\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists(), "blank input invoked the trial helper")

    def test_explicit_reviewed_path_is_forwarded_to_promote(self):
        path = str(self.root / "reviewed health attestation.json")
        result = self.run_prompt(path + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.calls.read_text(encoding="utf-8").splitlines(),
            ["promote", "--attestation", path],
        )


if __name__ == "__main__":
    unittest.main()
