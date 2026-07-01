# Global Audit: Optuna Launch And Calibration (2026-06-02)

## 1. Current Truth
| Area | Current status | Source |
|---|---|---|
| Final launch status | `NO_GO` | `reports/qa_gate/p2017_optuna_strict_exec_cycle2_final_quality_decision_no_go_20260602T000048Z.json` |
| Forward stability | `FAIL / NOT_CONFIRMED` | `reports/qa_gate/p2016_optuna_strict_exec_cycle2_forward_stability_final_fail_20260602T000048Z.json` |
| Freeze | `project_ready=false`, `enforce_freeze=true` | `configs/readiness.yaml`, `reports/readiness/readiness_check_20260602T054925Z.json` |
| Historical GO | `P1792-P1795` are historical execution records only | `reports/qa_gate/p1792_optuna_production_unfreeze_decision_record_final_20260601T120607Z.json` |
| Next active track | `V3`: only new `feature/logic` hypotheses | `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md` |

## 2. What Is Already Assembled
1. The Optuna/APTuna runtime contour is technically assembled and usable:
   `APTuna/run_optuna_1d1d_stagec_process_pool.ps1`,
   `src/mlbotnav/adaptive_auto_train.py`,
   `src/mlbotnav/optuna_search_candidate.py`.
2. Long/short split, process-pool launcher, temporary unlock flow, preflight and artifact emission all work in real runs.
3. Strict Execution cycles were completed end-to-end:
   `Package A`, `Package B`, unified triage, post-audit, forward package, final decision package.
4. The full calibration matrix already exists and is available for wider battle-calibration:
   `configs/calibration_full_matrix_v1.yaml`.

## 3. Real Blockers Before Production
1. There is no portable candidate for launch.
   The only local candidate from cycle-2 (`long_only`, `R2`, `L2`) failed both mandatory forward windows.
2. Current final decision is `NO_GO`, so production unfreeze is not allowed.
3. Freeze is intentionally still on.
   Calibration is allowed only through the APTuna temporary unlock flow, not through normal production actions.
4. The operator contour had source-of-truth drift between the old unfreeze `GO` and the new forward-based `NO_GO`.
   The only active launch truth is now `P2017`.

## 4. What Is Not A Blocker Right Now
1. Re-running old `closeout-reconfirm` items is not launch work.
2. Post-audit after every micro-step is not required.
   Package-level triage plus one package-level post-audit is enough.
3. Replaying the old controlled unfreeze procedure is not useful until a new candidate survives forward validation.
4. Returning to historical single-window remediation loops and `+0.01` grid drift is not useful.
5. The old `sqlite -> postgres` blocker is no longer the main critical-path item for launch.
   Current runtime config already declares postgres as the required storage mode in `configs/optuna_engine.yaml`.

## 5. What We Stop Treating As Mandatory
1. No more micro-audit after each hypothesis tweak.
2. No more repeated reconfirm packages without a new experiment result.
3. No more reuse of superseded `GO` packages as if they were current launch permission.
4. No more package expansion without a new hypothesis class.

## 6. Strict Working Table
| Step | Current state | What we do | Exit artifact | Next |
|---|---|---|---|---|
| 1 | `DONE` | Freeze one active truth: only `P2017` is current launch status | `P2018` + synced registry | Step 2 |
| 2 | `DONE` | Open V3 Checkpoint A with only new `feature/logic` hypotheses | V3 checkpoint package | Step 3 |
| 3 | `DONE` | Run `Package A long_only` on 3 closed windows | `P2022` long-only run set | Step 4 |
| 4 | `DONE` | Run `Package A short_only` on 3 closed windows | `P2023` short-only run set | Step 5 |
| 5 | `DONE` | Publish one unified triage for `Package A` | `P2024` unified triage | Step 6 |
| 6 | `DONE` | Publish one post-audit for `Package A` | `P2025` package audit | Step 7 |
| 7 | branch resolved | `Package A` candidate branch not taken (`candidate_count=0`) | `NO_CANDIDATE` after Package A | Step 8 |
| 8 | `NEXT` | Run one final `Package B` after exact slot definition is fixed | Package B runs + triage + audit | Step 9 or Step 11 |
| 9 | branch | Run mandatory forward `F1` and `F2` on next closed windows | forward package | Step 10 |
| 10 | branch | If forward is `2/2 PASS`, publish new production decision-record and run controlled unfreeze | new launch `GO` package | BOEVOY START |
| 11 | branch | If forward fails or Package B gives no candidate, publish final `NO_GO` and stop the cycle | final bounded `NO_GO` | STOP / NEW TZ |

## 6.1 Fixed Package A For Current Run
1. Windows:
   `W1 2026-05-29/2026-05-30`,
   `W2 2026-05-30/2026-05-31`,
   `W3 2026-05-31/2026-06-01`.
2. Hypotheses:
   `A-H1 = swing_structure_pair`,
   `A-H2 = value_area_rotation_vs_breakout`,
   `A-H3 = fib_extension_targets`.
3. Current execution pointer:
   Step 6 is done, Step 8 is next because `Package A` closed as `NO_CANDIDATE`.

## 6.2 Full Calibration Catalog Overlay
1. As of `2026-06-02T08:35:09Z`, active calibration work is broader than a launch-candidate fork.
2. The project must keep running the structured Optuna calibration catalog even when a local launch candidate is not found.
3. Each block/feature/hypothesis result is classified and stored:
   `positive`, `negative`, `neutral`, or `infra_fail`.
4. Positive catalog entries are not production permission.
   They are only `candidate_for_forward` until forward stability and a new production decision package pass.
5. Active catalog TZ:
   `docs/TZ_OPTUNA_FULL_CALIBRATION_CATALOG_2026-06-02_RU.md`
6. Checkpoint:
   `reports/qa_gate/p2026_optuna_full_calibration_catalog_checkpoint_20260602T083509Z.json`

## 6.3 P2028 First Catalog Smoke Stage
1. First practical catalog task is now fixed as `1d -> 1d` smoke/proof:
   calibrate parameters on one closed 1d train window, then apply those calibrated parameters on the next closed 1d test window.
2. Purpose:
   prove that feature/hypothesis wiring, parameter ranges, parameter transfer, classification, catalog index output, and 9-worker/`3x3` execution profile work штатно before wider medium/wide catalog runs.
3. Checkpoint:
   `reports/qa_gate/p2028_optuna_1d_to_1d_smoke_strategy_checkpoint_20260602T090943Z.json`
4. No runtime run was launched for this checkpoint; freeze/readiness were not changed.

## 6.4 P2030 Step 1 Wiring Inventory Result
1. Step 1 read-only wiring inventory completed with `PASS`.
2. Artifact:
   `reports/optuna_catalog/index/p2030_step1_wiring_inventory_20260602T092159Z.json`
3. Checkpoint:
   `reports/qa_gate/p2030_step1_wiring_inventory_checkpoint_20260602T092159Z.json`
4. Summary:
   6 enabled blocks, 68 matrix feature rows matched runtime columns, 56 tunable feature rows, 20 tunable hypothesis rows, 27/27 linked profiles, profile issues `0`.
5. Current pointer:
   Step 2 - exact `1d -> 1d` smoke matrix and command set.

## 6.5 P2032 Step 2 Smoke Command Set Result
1. Step 2 exact `1d -> 1d` smoke command set completed with `PASS`.
2. Artifact:
   `reports/optuna_catalog/index/p2032_step2_1d1d_smoke_command_set_20260602T092710Z.json`
3. Checkpoint:
   `reports/qa_gate/p2032_step2_1d1d_smoke_command_set_checkpoint_20260602T092710Z.json`
4. Fixed smoke profile:
   train `2026-05-31`, test `2026-06-01`, matrix `configs/calibration_full_matrix_v1.yaml`, `CalibrationGridPreset=narrow`, `ForceProfileEdgeCoverage=on`, `3x3`, 9 total workers.
5. Runtime was not launched; dry-runs confirmed child commands include the required Optuna preset flags.
6. Current pointer:
   Step 3 - smoke preflight.

## 6.6 P2034-P2037 1d-to-1d Smoke Execution Result
1. Step 3 preflight completed with `PASS`.
2. Step 4 long_only smoke completed with runtime `OK`, catalog `neutral`, best OOS `0.0%`, trades `0`.
3. Step 5 short_only smoke completed with runtime `OK`, best OOS `+0.2544%`, trades `1`, but `goal_pass=false`; stored as neutral/provisional-plus, not positive/top.
4. Step 6 triage decision: `GO_TO_MEDIUM_WORK`.
5. Accepted positive candidates remain `0`.
6. Artifacts:
   1. `reports/qa_gate/p2034_step3_smoke_preflight_20260602T093214Z.json`
   2. `reports/optuna_catalog/neutral/p2035_step4_long_only_1d1d_smoke_neutral_20260602T093324Z.json`
   3. `reports/optuna_catalog/neutral/p2036_step5_short_only_1d1d_smoke_provisional_plus_goal_fail_20260602T093604Z.json`
   4. `reports/qa_gate/p2037_step6_1d1d_smoke_triage_20260602T093704Z.json`
7. Current pointer:
   Step 7 - medium work pass.

## 6.7 P2038 Smoke Triage Post-Sync Audit
1. Post-sync audit after P2034-P2037 passed.
2. Artifact:
   `reports/qa_gate/p2038_step6_smoke_triage_post_sync_audit_20260602T094006Z.json`
3. Freeze remains preserved:
   `project_ready=false`, `enforce_freeze=true`.
4. Current pointer:
   Step 7 - medium work pass.

## 6.8 P2039 Step 7 Medium Command Set
1. Step 7 medium command set completed with `PASS`.
2. Artifacts:
   1. `reports/optuna_catalog/index/p2039_step7_medium_command_set_20260602T095335Z.json`
   2. `reports/qa_gate/p2039_step7_medium_command_set_checkpoint_20260602T095335Z.json`
3. Medium profile is fixed for train `2026-05-31` -> test `2026-06-01`, `CalibrationGridPreset=medium`, `ForceProfileEdgeCoverage=on`.
4. Accepted resource profile remains `3x3`: `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`.
5. Current pointer:
   Step 7 runtime - run medium `long_only` first.

## 6.9 P2040-P2042 Step 7 Medium Runtime And Triage
1. Step 7 medium runtime completed for long_only and short_only.
2. Results:
   1. long_only `negative`, best OOS `-6.9497%`, trades `1`, `goal_pass=false`;
   2. short_only `negative`, best OOS `-0.6217%`, trades `1`, `goal_pass=false`.
3. Accepted positive candidates remain `0`.
4. Step 7 triage decision:
   `GO_TO_WIDE_BATTLE`.
5. Artifact:
   `reports/qa_gate/p2042_step7_medium_triage_20260602T100020Z.json`.
6. Current pointer:
   Step 8 - wide battle pass.

## 6.10 P2043 Step 7 Medium Post-Sync Audit
1. Step 7 medium post-sync audit status: `PASS`.
2. Artifact:
   `reports/qa_gate/p2043_step7_medium_post_sync_audit_20260602T100235Z.json`.
3. Freeze remains preserved:
   `project_ready=false`, `enforce_freeze=true`.
4. Current pointer:
   Step 8 - wide battle pass.

## 6.11 P2044 Step 8 Wide Command Set
1. Step 8 wide command set completed with `PASS`.
2. Artifact:
   `reports/optuna_catalog/index/p2044_step8_wide_command_set_20260602T100351Z.json`.
3. Wide profile is fixed for train `2026-05-31` -> test `2026-06-01`, `CalibrationGridPreset=wide`, `ForceProfileEdgeCoverage=on`.
4. Accepted resource profile remains `3x3`: `ProcessWorkers=3`, `SearchWorkersPerProcess=3`, total workers `9`.
5. Current pointer:
   Step 8 runtime - run wide `long_only` first.

## 6.12 P2045-P2049 Full Catalog Closeout
1. Current 1d->1d narrow/medium/wide catalog pass is structurally complete.
2. Catalog totals:
   positive `0`, neutral `2`, negative `4`, infra_fail `0`.
3. Forward stability:
   blocked because `candidate_for_forward=0`.
4. Production:
   still `NO_GO`; unfreeze is not allowed.
5. Boundary artifact:
   `reports/qa_gate/p2049_full_catalog_no_forward_boundary_20260602T100745Z.json`.

## 6.13 P2050 Full Catalog Closeout Post-Sync Audit
1. Closeout audit status: `PASS`.
2. Artifact:
   `reports/qa_gate/p2050_full_catalog_closeout_post_sync_audit_20260602T101019Z.json`.
3. Freeze remains preserved:
   `project_ready=false`, `enforce_freeze=true`.

## 6.14 P2051-P2052 Block-Level Catalog Cycle Setup
1. Because candidate_for_forward stayed `0`, the next allowed work is a block-level catalog cycle, not forward/prod.
2. Six block-isolated matrices were generated under:
   `configs/calibration_matrices/catalog_blocks/`.
3. First executable block is `price_volatility`; command set `P2052` is `PASS`.
4. Current pointer:
   block01 narrow runtime.

## 6.15 P2053-P2064 Block01 Price Volatility Closeout
1. Block01 `price_volatility` completed across narrow, medium, and wide grids.
2. Totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`.
3. No forward candidate emerged.
4. Current pointer:
   block02 `trend_momentum` narrow command set.

## 6.16 P2065-P2068 Block02 Trend Momentum Narrow
1. Block02 `trend_momentum` narrow completed with runtime OK.
2. Totals:
   positive `0`, neutral `1`, negative `1`, infra_fail `0`.
3. No forward candidate emerged.
4. Current pointer:
   block02 `trend_momentum` medium command set.

## 6.17 P2069-P2077 Block02 Trend Momentum Closeout
1. Block02 `trend_momentum` completed across narrow, medium, and wide grids with runtime `OK` in all 6 runs.
2. Catalog totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
3. Full triage:
   `reports/qa_gate/p2076_block02_trend_momentum_full_triage_20260602T103215Z.json`.
4. Post-sync audit:
   `reports/qa_gate/p2077_block02_trend_momentum_post_sync_audit_20260602T103526Z.json`, status `PASS`.
5. Freeze remains preserved:
   `project_ready=false`, `enforce_freeze=true`.
6. Current pointer:
   block03 `volume_flow` narrow command set.

## 6.18 P2078-P2081 Block03 Volume Flow Narrow
1. Block03 `volume_flow` narrow completed with runtime `OK` for long_only and short_only.
2. Catalog totals:
   positive `1`, neutral `0`, negative `1`, infra_fail `0`, candidate_for_forward `1`.
3. Positive candidate:
   long_only best OOS `+1.9186%`, trades `1`, artifact `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
4. Triage:
   `reports/qa_gate/p2081_block03_volume_flow_narrow_triage_20260602T104055Z.json`.
5. Launch boundary:
   production/unfreeze remains blocked until full validation path passes.
6. Current pointer:
   block03 `volume_flow` medium command set.

## 6.19 P2082-P2090 Block03 Volume Flow Closeout
1. Block03 `volume_flow` completed across narrow, medium, and wide grids.
2. Catalog totals:
   positive `1`, neutral `2`, negative `3`, infra_fail `0`, candidate_for_forward `1`.
3. Positive candidate preserved:
   `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
4. Full triage:
   `reports/qa_gate/p2089_block03_volume_flow_full_triage_20260602T104655Z.json`.
5. Post-sync audit:
   `reports/qa_gate/p2090_block03_volume_flow_post_sync_audit_20260602T104830Z.json`, status `PASS`, freeze preserved.
6. Current pointer:
   block04 `density_profile` narrow command set.

## 6.20 P2091-P2103 Block04 Density Profile Closeout
1. Block04 `density_profile` completed across narrow, medium, and wide grids.
2. Catalog totals:
   positive `0`, neutral `4`, negative `2`, infra_fail `0`, candidate_for_forward `0`.
3. Prior positive candidate preserved:
   `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
4. Full triage:
   `reports/qa_gate/p2102_block04_density_profile_full_triage_20260602T105800Z.json`.
5. Post-sync audit:
   `reports/qa_gate/p2103_block04_density_profile_post_sync_audit_20260602T105853Z.json`, status `PASS`, freeze preserved.
6. Current pointer:
   block05 `structure_ta` narrow command set.

## 6.21 P2104-P2116 Block05 Structure TA Closeout
1. Block05 `structure_ta` completed across narrow, medium, and wide grids.
2. Catalog totals:
   positive `0`, neutral `3`, negative `3`, infra_fail `0`, candidate_for_forward `0`.
3. Prior positive candidate preserved:
   `reports/optuna_catalog/positive/p2079_block03_volume_flow_narrow_long_only_positive_20260602T103932Z.json`.
4. Full triage:
   `reports/qa_gate/p2115_block05_structure_ta_full_triage_20260602T110710Z.json`.
5. Post-sync audit:
   `reports/qa_gate/p2116_block05_structure_ta_post_sync_audit_20260602T110808Z.json`, status `PASS`, freeze preserved.
6. Current pointer:
   block06 `pattern` narrow command set.

## 6.22 P2117-P2132 Block-Level Catalog Closeout
1. Block06 `pattern` completed across narrow, medium, and wide grids.
2. Full block-level catalog totals:
   positive `1`, neutral `18`, negative `17`, infra_fail `0`, candidate_for_forward `1`.
3. Accepted candidate:
   block03 `volume_flow`, checkpoint `P2079`, OOS `+1.9186%`, trades `1`.
4. Ranking and boundary artifacts:
   1. `reports/optuna_catalog/index/p2130_block_level_catalog_ranking_20260602T111745Z.json`
   2. `reports/qa_gate/p2131_block_level_forward_boundary_20260602T111745Z.json`
   3. `reports/qa_gate/p2132_block_level_catalog_closeout_post_sync_audit_20260602T111822Z.json`
5. Freeze remains preserved:
   `project_ready=false`, `enforce_freeze=true`.
6. Current pointer:
   `P2133` exact F1/F2 forward stability command set.

## 7. Exact Execution Steps
1. Step 1. Do not touch old `GO` packages as launch permission.
   Active source of truth is only `p2017`.
2. Step 2. Build `V3 Package A`.
   Rule: only new `feature/logic` hypotheses.
   Rule: no `+0.01` grid drift, no replay of old candidate.
3. Step 3. Run `Package A long_only` on 3 closed windows.
   Output: 9 long slot-window runs.
4. Step 4. Run `Package A short_only` on 3 closed windows.
   Output: 9 short slot-window runs.
5. Step 5. Publish one unified `Package A triage`.
   Candidate rule stays unchanged:
   `goal_pass=true` + `oos_net_return_pct>0` + `oos_trades>0`.
6. Step 6. Publish one `Package A post-audit`.
   Only package-level audit, no micro-audit between hypothesis tweaks.
7. Step 7. Decision fork after Package A.
   If `candidate_count>0` -> go directly to forward-stability.
   If `candidate_count=0` -> open one last `Package B`.
8. Step 8. If Package B is needed:
   run long + short on the same 3-window scheme,
   then publish one unified triage,
   then publish one post-audit,
   then stop branching.
9. Step 9. If candidate exists after A or B:
   run forward `F1` and `F2` on next closed windows.
10. Step 10. Only if forward result is `2/2 PASS`:
    publish a new production decision-record,
    confirm approvals,
    execute controlled unfreeze,
    run post-unfreeze verification.
11. Step 11. If forward fails or Package B gives no candidate:
    publish final `NO_GO`,
    do not launch,
    open a new TZ only after a new hypothesis class is defined.

## 8. When Launch Is Allowed
1. Not after Package A.
2. Not after Package B.
3. Not after local candidate discovery.
4. Only after all three conditions are true together:
   new candidate exists,
   forward `F1` and `F2` both PASS,
   new production decision-record says `GO`.

## 9. Bounded Path Length
1. Shortest path to launch:
   Step 2 -> Step 3 -> Step 4 -> Step 5 -> Step 6 -> Step 9 -> Step 10.
2. Longest bounded path before final answer:
   Step 2 -> Step 3 -> Step 4 -> Step 5 -> Step 7 -> Step 8 -> Step 9 -> Step 10 or Step 11.
3. There is no allowed infinite loop inside this table.

## 10. Working Conclusion
1. The project is not blocked by contour assembly anymore.
2. The project is blocked by candidate quality and transferability.
3. The correct next phase is adult calibration under V3, not more journal-like micro-audits.

## 8. Hard Structural Audit Addendum
1. Hard audit completed UTC `2026-06-02T19:16:09Z`, local `2026-06-03 00:16:09 +05:00`.
2. Artifact:
   `reports/qa_gate/hard_structural_audit_features_hypotheses_20260602T191609Z.md`.
3. Status:
   `PASS_WITH_FINDINGS`.
4. Structural conclusion:
   Optuna/APTuna feature, hypothesis, grid, and block catalog framework is assembled and proven for the current catalog contour: 68/68 runtime features mapped, 20 hypotheses, 27/27 profiles linked, narrow/medium/wide min/max anchors preserved, block catalog `36/36 runtime OK`.
5. Finding:
   block-level results are feature-row isolated, but not proven as pure strategy-block isolated because hypothesis/trend-filter rows can require out-of-block columns. `P2079` is a valid working catalog candidate, but not proven as pure `volume_flow` only.
6. Boundary:
   `P2079` is a catalog `candidate_for_forward`, not a production candidate. Production remains `NO_GO` until forward F1/F2 is `2/2 PASS` and a new production GO package is created.
