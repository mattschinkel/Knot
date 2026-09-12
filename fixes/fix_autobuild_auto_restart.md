# fix_autobuild_auto_restart — retry failed tasks instead of stopping the phase

## Problem
`autobuild.py` stopped the entire phase on the first crew task failure
(`FAILED … STOPPING PHASE`). With a 4B model that often needs several
attempts (or a later manual land), the driver exited and waited for a human
to relaunch `--from=TN`.

## Fix
- Per-task retry loop: `GOLEM_TASK_RETRIES` (default 8) with `GOLEM_RETRY_SLEEP_SEC`.
- Outer **auto-restart** (`GOLEM_AUTO_RESTART=1` default): after retries are
  exhausted, start the same task again from scratch until it goes green
  (no phase stop). Set `GOLEM_AUTO_RESTART=0` to restore old stop-on-fail.
- `--watch`: process supervisor re-execs autobuild if the child crashes or
  exits non-zero (covers LLM server blips / uncaught exceptions).
- Refuse to declare a phase done when `parse_tasks` returns 0 tasks.

## Continue
Phase 2 is done; resume with Phase 3 under watch:
`.venv/bin/python autobuild.py --watch --phase 3`
