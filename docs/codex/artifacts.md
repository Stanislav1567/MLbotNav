# Artifacts

Last updated UTC: 2026-06-02T08:13:12Z

## Source Of Truth Docs
| Path | Purpose |
|---|---|
| `docs/OPTUNA_GLOBAL_LAUNCH_AUDIT_2026-06-02_RU.md` | Current strict execution table and launch truth. |
| `docs/TZ_OPTUNA_LAUNCH_RECOVERY_V3_2026-06-02_RU.md` | Active V3 technical assignment. |
| `docs/ACTIVE_WORK_ITEMS_RU.md` | Active work registry. |
| `docs/CHANGELOG_CHRONOLOGY_RU.md` | Chronological project log. |
| `configs/readiness.yaml` | Freeze/readiness state. |

## Current Decision Artifacts
| Path | Purpose |
|---|---|
| `reports/qa_gate/p2016_optuna_strict_exec_cycle2_forward_stability_final_fail_20260602T000048Z.json` | Shows forward stability failed. |
| `reports/qa_gate/p2017_optuna_strict_exec_cycle2_final_quality_decision_no_go_20260602T000048Z.json` | Current final launch decision: `NO_GO`. |

## V3 Package A Artifacts
| Path | Purpose |
|---|---|
| `reports/qa_gate/p2021_optuna_launch_recovery_v3_checkpoint_a_20260602T060358Z.json` | V3 Package A checkpoint. |
| `reports/qa_gate/p2022_optuna_v3_package_a_long_only_summary_20260602T064116Z.json` | Long-only Package A summary. |
| `reports/qa_gate/p2022_optuna_v3_package_a_long_only_runs_20260602T064116Z.jsonl` | Long-only Package A run ledger. |
| `reports/qa_gate/p2023_optuna_v3_package_a_short_only_summary_20260602T064841Z.json` | Short-only Package A summary. |
| `reports/qa_gate/p2023_optuna_v3_package_a_short_only_runs_20260602T064841Z.jsonl` | Short-only Package A run ledger. |
| `reports/qa_gate/p2024_optuna_v3_package_a_unified_triage_20260602T065019Z.json` | Unified Package A verdict: `NO_CANDIDATE`. |
| `reports/qa_gate/p2025_optuna_v3_package_a_post_audit_20260602T065250Z.json` | Package A post-audit: `PASS`. |
| `reports/qa_gate/p2025_text_encoding_audit_20260602T065227Z.json` | UTF-8 / krakozyabr audit for Package A post-audit. |

## Runtime And Config
| Path | Purpose |
|---|---|
| `APTuna/run_optuna_1d1d_stagec_process_pool.ps1` | Main process-pool APTuna runner. |
| `run_optuna_v3_package_a.ps1` | Repeatable V3 Package A slot-window runner. |
| `configs/calibration_full_matrix_v1.yaml` | Full calibration matrix. |
| `configs/calibration_matrices/optuna_v3_package_a_ah1_long.yaml` | Isolated Package A long A-H1 matrix. |
| `configs/calibration_matrices/optuna_v3_package_a_ah1_short.yaml` | Isolated Package A short A-H1 matrix. |
| `configs/calibration_matrices/optuna_v3_package_a_ah2.yaml` | Isolated Package A A-H2 matrix. |
| `configs/calibration_matrices/optuna_v3_package_a_ah3.yaml` | Isolated Package A A-H3 matrix. |

## Health Reports
| Path | Purpose |
|---|---|
| `reports/qa_gate/recovery_r5_text_guard_20260602T065118Z.json` | Text integrity guard, `PASS`. |
| `reports/readiness/readiness_check_20260602T065117Z.json` | Readiness report after Package A, freeze unchanged. |

