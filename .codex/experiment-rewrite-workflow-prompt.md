Use the experiment-rewrite-orchestrator custom agent and execute the staged experiment rewrite workflow.

Repository constraints:
- Use the project custom agents in `.codex/agents/`.
- Read authoritative stage prompts from `prompts/`.
- Write all generated workflow outputs under `workspace/experiment_rewrite/`.
- Do not write generated reports into `workspace/reports/`, `workspace/baselines/`, or unrelated project folders.
- Do not modify the original experiment repo unless Stage 0 explicitly locks `Rewrite Target: IN_PLACE`.
- Prefer `workspace/experiment_rewrite/rewritten_repo/` when the rewrite target is not explicitly in-place.
- Do not execute third-party baseline scripts.
- Do not install dependencies unless Stage 0 explicitly allows it.
- Do not ask the user to paste tokens, passwords, SSH keys, private keys, or other secrets into prompts or reports.

Required behavior:
1. Run Stage 0 requirement collection first with `experiment-requirement-collector`.
2. If required parameters are missing, ask the user the listed questions and stop. Do not inspect baselines, lock contracts, or rewrite code.
3. Continue only after `workspace/experiment_rewrite/reports/requirements.md` contains `STATUS: READY`.
4. Run Stage 1 experiment contract locking with `experiment-scope-contract-locker`.
5. If the original launch, dataset, split, metric, shape, runtime, or input contract is ambiguous, ask the user to clarify and stop. Do not inspect baselines or rewrite code.
6. Continue only after `workspace/experiment_rewrite/reports/experiment_contract.md` contains `STATUS: LOCKED`.
7. Run Stage 2 baseline triage and rewrite planning with `baseline-triage-planner`.
8. Stage 2 must classify every baseline directory and write `baseline_inventory.csv`, `rewrite_plan.csv`, and `input_adapter_plan.csv`.
9. Ignore empty, non-Python, non-PyTorch, and incompatible baselines only with explicit recorded reasons.
10. For input mismatch, plan input adapters before model architecture changes. For CNN-style baselines that require square input, prefer `pad_to_square` or another documented adapter before changing the model.
11. Run Stage 3 rewrite execution with `experiment-rewrite-executor` only after the Stage 2 plan files exist and are internally consistent.
12. Stage 3 must rewrite eligible baselines into one unified PyTorch experiment entry point. It must not preserve baseline-specific dataloaders, training loops, metrics, or launch scripts as the primary execution path.
13. Run Stage 4 minimal validation and profiling with `minimal-validation-profiler`.
14. Stage 4 must use the locked real repo data pipeline and must check original input shape, adapted input shape, forward pass, output shape, loss computation, finite values, backward pass, metric output, and short smoke training.
15. Stage 4 must record parameter count, trainable parameter count, FLOPs, and MACs when supported. If profiling fails, record a clear failure reason instead of marking success.
16. Do not run full paper-scale experiments, hyperparameter search, or publication-result comparisons.
17. Run Stage 5 report writing with `experiment-report-writer`.
18. Produce `final_model_summary.csv` with model status, rewrite files, adapter details, validation status, profiling results, and launch commands.
19. Run Stage 6 integrity review with `experiment-integrity-reviewer`.
20. If review rejects any stage, loop back to the specified stage and retry automatically unless user input is required.

Required workflow artifacts:
- `workspace/experiment_rewrite/reports/requirements.md`
- `workspace/experiment_rewrite/reports/experiment_contract.md`
- `workspace/experiment_rewrite/reports/baseline_inventory.csv`
- `workspace/experiment_rewrite/reports/rewrite_plan.csv`
- `workspace/experiment_rewrite/reports/input_adapter_plan.csv`
- `workspace/experiment_rewrite/reports/implementation_manifest.csv`
- `workspace/experiment_rewrite/reports/validation_results.csv`
- `workspace/experiment_rewrite/reports/model_profile.csv`
- `workspace/experiment_rewrite/reports/final_model_summary.csv`
- `workspace/experiment_rewrite/reports/final_summary.md`
- `workspace/experiment_rewrite/reports/integrity_report.md`
- `workspace/experiment_rewrite/reports/iteration_log.md` when any loopback occurs.

The final CSV must include at least:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

Allowed final model statuses:
- `DONE`
- `DONE_WITH_ADAPTER`
- `DONE_WITH_PREPROCESS`
- `DONE_WITH_PRETRAIN_REQUIRED`
- `SKIPPED_EMPTY`
- `SKIPPED_NON_PYTHON`
- `SKIPPED_NON_PYTORCH`
- `SKIPPED_INCOMPATIBLE`
- `BLOCKED_NEEDS_USER_INPUT`
- `FAILED_VALIDATION`
- `FAILED_REWRITE`

Loopback rules:
- If Stage 6 outputs `VERDICT: GO`, finalize and list generated report paths.
- If Stage 6 outputs `VERDICT: REJECT`, read the exact target stage, append a row to `workspace/experiment_rewrite/reports/iteration_log.md`, rerun that stage with the reviewer critique as a high-priority constraint, rerun all downstream affected stages, and return to Stage 6.
- If the rejected target stage requires user input, ask no more than 3 concise questions and stop.

Do not finalize unless the integrity reviewer returns `VERDICT: GO`.
