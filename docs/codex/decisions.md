# Decisions

Last updated UTC: 2026-06-02T08:13:12Z

## Active Decisions
1. Project files are the source of truth; chat is secondary.
2. Active launch status is `NO_GO` from `P2017`.
3. Old `GO`/unfreeze records are historical and must not be used as current launch permission.
4. Freeze stays ON until a new candidate passes forward stability and a new production `GO` package is issued.
5. Calibration may run only through APTuna temporary unlock while freeze is ON.
6. V3 is bounded: maximum `Package A` and `Package B`, with one triage and one post-audit per package.
7. Candidate rule is unchanged:
   `goal_pass=true` + `oos_net_return_pct>0` + `oos_trades>0`.
8. Forward validation is mandatory after candidate discovery:
   `F1/F2 = 2/2 PASS`.

## Rejected Or Paused Paths
1. Repeating old closeout reconfirm packages without new experiment results.
2. Micro-audit after every hypothesis tweak.
3. Historical single-window remediation loops.
4. `+0.01` grid drift as a substitute for a new hypothesis.
5. Reusing old candidate from `P2013`.
6. Treating contour assembly as the blocker after runtime contour is already assembled.

## Why
1. Prior local candidate passed a narrow rule but failed transferability in forward windows.
2. The project needs quality calibration and forward stability, not more bookkeeping loops.
3. Strict package boundaries keep the work finite and understandable.
4. User explicitly requested no more left/right drift and no endless audit loops.

## Do Not Replay Without Reason
1. Do not replay old `GO` as current launch status.
2. Do not reopen `Package A` after it closed as `NO_CANDIDATE` unless a new TZ explicitly changes scope.
3. Do not run `Package B` until its exact slots are fixed in docs and artifacts.

