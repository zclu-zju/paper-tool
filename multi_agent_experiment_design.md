# Experiment Rewrite Workflow Protocol

This document defines the Codex-style multi-agent workflow for rewriting paper experiment baselines into one unified PyTorch experiment framework.

The design follows the structure of the `baseline-research-workflows` plugin:

- one orchestrator controls the whole staged workflow;
- every worker has fixed inputs, outputs, status values, and strict rules;
- every stage writes auditable artifacts under `workspace/experiment_rewrite/`;
- the final reviewer returns `GO` or `REJECT`;
- a rejection routes back to exactly one target stage.

The workflow is not a software-development team split. The key question is whether Codex has enough validated information to migrate baseline model architectures into the user's original task, then prove each migrated model can build, run, train minimally, and be profiled.

## Agent List

The system uses 9 repo-local custom agents:

```text
1. experiment-rewrite-orchestrator
2. experiment-requirement-collector
3. experiment-scope-contract-locker
4. baseline-transfer-readiness-checker
5. baseline-triage-planner
6. experiment-rewrite-executor
7. minimal-validation-profiler
8. experiment-report-writer
9. experiment-integrity-reviewer
```

Only 8 worker stages exist because the orchestrator is the controller, not a worker stage.

## Output Layout

All generated workflow outputs must stay under:

```text
workspace/experiment_rewrite/
```

Required report artifacts:

```text
workspace/experiment_rewrite/reports/requirements.md
workspace/experiment_rewrite/reports/experiment_contract.md
workspace/experiment_rewrite/reports/transfer_readiness.md
workspace/experiment_rewrite/reports/baseline_inventory.csv
workspace/experiment_rewrite/reports/rewrite_plan.csv
workspace/experiment_rewrite/reports/input_adapter_plan.csv
workspace/experiment_rewrite/reports/baseline_triage_notes.md
workspace/experiment_rewrite/reports/implementation_manifest.csv
workspace/experiment_rewrite/reports/implementation_notes.md
workspace/experiment_rewrite/reports/validation_results.csv
workspace/experiment_rewrite/reports/model_profile.csv
workspace/experiment_rewrite/reports/validation_notes.md
workspace/experiment_rewrite/reports/final_model_summary.csv
workspace/experiment_rewrite/reports/final_summary.md
workspace/experiment_rewrite/reports/integrity_report.md
workspace/experiment_rewrite/reports/iteration_log.md
```

`iteration_log.md` is required only when loopback occurs.

## Stage 0: Requirement Collection

Agent:

```text
experiment-requirement-collector
```

Output:

```text
workspace/experiment_rewrite/reports/requirements.md
```

Stage 0 collects only the hard required inputs:

```text
1. Original repository root.
2. Original launch script path or original launch command.
3. Baseline root directory or directories.
```

All other values are workflow defaults unless the user explicitly says otherwise:

```text
Output Workspace: workspace/experiment_rewrite/
Rewrite Target: COPY_TO_REWRITTEN_REPO
Target Task Type: INFER_FROM_REPO
Data Policy: PRESERVE_ORIGINAL_DATALOADER
Split Policy: PRESERVE_ORIGINAL_SPLIT
Metric Policy: PRESERVE_ORIGINAL_METRICS
Training Policy: SHARED_TRAIN_LOOP
Allowed Language: PYTHON_ONLY
Allowed Framework: PYTORCH_ONLY
Baseline Handling: DROP_EMPTY / DROP_NON_PYTHON / DROP_NON_PYTORCH / DROP_INCOMPATIBLE / MARK_UNKNOWN_FOR_REVIEW
Input Adapter Policy: REQUIRED_WHEN_NEEDED
Preferred Input Adapters: pad_to_square, pad_to_multiple, resize, center_crop, channel_repeat, channel_project, flatten_to_sequence, sequence_to_grid, add_mask, custom
Model Architecture Change Policy: ALLOW_IF_ADAPTER_FAILS_WITH_RECORDED_REASON
Preprocessing Policy: ALLOW_EXPLICIT_PREPROCESS_STAGE
Pretrained Weight Policy: ASK_ONLY_WHEN_REQUIRED
Dependency Policy: USE_EXISTING_ENV_ONLY
Third-Party Code Execution: DO_NOT_EXECUTE_BASELINE_CODE
Smoke Epochs: 5
Max Validation Batches: 2
Profile Metrics: params, trainable_params, macs, flops
Device: auto
Output Format: CSV
Overwrite Policy: NO_OVERWRITE
```

Allowed status:

```text
STATUS: READY
STATUS: NEEDS_USER_INPUT
```

Stage 0 must not inspect baseline code deeply, lock the experiment contract, rewrite code, run validation, run training, install dependencies, or execute third-party baseline scripts.

## Stage 1: Experiment Contract Lock

Agent:

```text
experiment-scope-contract-locker
```

Output:

```text
workspace/experiment_rewrite/reports/experiment_contract.md
```

Stage 1 reads the original repo and launch script to lock the task contract that every migrated baseline must obey.

It records:

```text
1. Original entry command and required arguments.
2. Dataset names, paths, dataloader, and split behavior.
3. Batch fields, input shape, label shape, dtype, and semantic meaning.
4. Loss, metrics, optimizer, scheduler, seed, and device behavior where discoverable.
5. Expected model input and output contract.
6. Minimal runnable command for the original model.
7. Input compatibility constraints such as non-square, irregular, masked, variable-length, graph-like, or multi-modal input.
```

Allowed status:

```text
STATUS: LOCKED
STATUS: NEEDS_USER_CLARIFICATION
```

Stage 1 may do a minimal original-repo shape probe when safe and allowed. It must not run third-party baseline code, full training, package managers, or dependency installation.

## Stage 2: Baseline Transfer Readiness Check

Agent:

```text
baseline-transfer-readiness-checker
```

Output:

```text
workspace/experiment_rewrite/reports/transfer_readiness.md
```

Stage 2 checks whether the locked original repo contract is sufficient to migrate baseline model architectures into the user's task.

Core assumptions:

```text
1. Baselines are model architectures to migrate.
2. Original baseline experiment protocols are not authoritative.
3. The original repo's shared dataloader, split, loss, metrics, training loop, and validation contract are authoritative.
4. Input adapters should bridge shape or format mismatch before model architecture changes.
```

Stage 2 must not require:

```text
baseline original optimizer
baseline original scheduler
baseline original training loop
baseline original dataloader
baseline original evaluation protocol
baseline original dataset split
baseline reported paper metrics
baseline original hyperparameter search
baseline original launch command
```

Allowed status:

```text
STATUS: READY
STATUS: NEEDS_CONTRACT_FIX
STATUS: NEEDS_USER_INPUT
STATUS: BLOCKED
```

`NEEDS_CONTRACT_FIX` loops back to Stage 1. `NEEDS_USER_INPUT` stops for no more than 3 concise user questions.

## Stage 3: Baseline Triage And Rewrite Planning

Agent:

```text
baseline-triage-planner
```

Outputs:

```text
workspace/experiment_rewrite/reports/baseline_inventory.csv
workspace/experiment_rewrite/reports/rewrite_plan.csv
workspace/experiment_rewrite/reports/input_adapter_plan.csv
workspace/experiment_rewrite/reports/baseline_triage_notes.md
```

Stage 3 classifies every baseline directory and plans adapters. It does not rewrite code.

Allowed baseline status values:

```text
REWRITE_READY
NEEDS_INPUT_ADAPTER
NEEDS_PREPROCESS
NEEDS_PRETRAIN
DROP_EMPTY
DROP_NON_PYTHON
DROP_NON_PYTORCH
DROP_INCOMPATIBLE
UNKNOWN
```

Input mismatch policy:

```text
1. Preserve original dataset and split.
2. Preserve shared dataloader, train loop, loss, and metrics.
3. Preserve baseline architecture as much as possible.
4. Add a documented input adapter before model forward when needed.
5. Prefer padding, masking, resizing, channel conversion, or reshaping before model architecture changes.
6. Use architecture changes only when adaptation cannot make the baseline valid and the reason is recorded.
```

For CNN-style baselines that require square image tensors while the original task uses non-square image-like tensors, prefer `pad_to_square` before changing the model.

## Stage 4: Rewrite Execution

Agent:

```text
experiment-rewrite-executor
```

Outputs:

```text
workspace/experiment_rewrite/reports/implementation_manifest.csv
workspace/experiment_rewrite/reports/implementation_notes.md
```

Stage 4 is the only stage allowed to rewrite code. It rewrites eligible Python/PyTorch model structures into one unified experiment framework.

Required shared framework:

```text
1. One entry point.
2. One model registry.
3. One dataset builder or wrapper using the original repo data contract.
4. One shared train loop.
5. One shared evaluation loop.
6. One shared metric implementation based on the original metric contract.
7. One input adapter layer used before model forward when required.
8. One profiling path for params, trainable params, FLOPs, and MACs.
```

Required entry behavior:

```bash
python run.py --model MODEL --dataset DATASET --mode validate_shape
python run.py --model MODEL --dataset DATASET --mode smoke_train --epochs 5
python run.py --model MODEL --dataset DATASET --mode profile
```

Baseline-specific dataloaders, training loops, and metrics must not remain the primary execution path.

## Stage 5: Minimal Validation And Profiling

Agent:

```text
minimal-validation-profiler
```

Outputs:

```text
workspace/experiment_rewrite/reports/validation_results.csv
workspace/experiment_rewrite/reports/model_profile.csv
workspace/experiment_rewrite/reports/validation_notes.md
```

Stage 5 runs minimal validation only, not paper-scale experiments.

Required checks:

```text
1. Build dataset through the locked original repo data contract.
2. Build model from registry.
3. Check original input shape.
4. Check adapted input shape.
5. Run forward pass.
6. Check output shape.
7. Compute loss.
8. Check finite output and finite loss.
9. Run short smoke training, normally 5 epochs.
10. Check backward pass and optimizer step.
11. Check metric output.
12. Record total parameters.
13. Record trainable parameters.
14. Record FLOPs and MACs when supported.
```

If FLOPs or MACs tooling fails, the failure reason must be recorded and profiling must not be marked complete.

## Stage 6: Final CSV And Summary

Agent:

```text
experiment-report-writer
```

Outputs:

```text
workspace/experiment_rewrite/reports/final_model_summary.csv
workspace/experiment_rewrite/reports/final_summary.md
```

Required final CSV header:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

Allowed final status values:

```text
DONE
DONE_WITH_ADAPTER
DONE_WITH_PREPROCESS
DONE_WITH_PRETRAIN_REQUIRED
SKIPPED_EMPTY
SKIPPED_NON_PYTHON
SKIPPED_NON_PYTORCH
SKIPPED_INCOMPATIBLE
BLOCKED_NEEDS_USER_INPUT
FAILED_VALIDATION
FAILED_REWRITE
UNKNOWN
```

Stage 6 must not invent validation, profiling, rewrite, adapter, preprocessing, or pretrained-weight results.

## Stage 7: Integrity Review

Agent:

```text
experiment-integrity-reviewer
```

Output:

```text
workspace/experiment_rewrite/reports/integrity_report.md
```

Allowed verdict:

```text
VERDICT: GO
VERDICT: REJECT
```

Allowed rejection targets:

```text
Stage 0 Requirement Collector
Stage 1 Scope Contract Locker
Stage 2 Baseline Transfer Readiness Checker
Stage 3 Baseline Triage Planner
Stage 4 Rewrite Executor
Stage 5 Minimal Validation Profiler
Stage 6 Report Writer
```

The reviewer checks hard requirements, workflow defaults, original contract lock, transfer readiness, baseline triage coverage, adapter planning, rewrite discipline, real-data minimal validation, profiling completeness, final CSV schema, launch commands, and status honesty.

## Orchestrator Protocol

Agent:

```text
experiment-rewrite-orchestrator
```

Workflow:

```text
0. Create workspace/experiment_rewrite/reports/ if missing.
1. Run Stage 0 Requirement Collector.
2. Stop for user input if requirements.md says NEEDS_USER_INPUT.
3. Run Stage 1 Scope Contract Locker after requirements.md says READY.
4. Stop for user input if experiment_contract.md says NEEDS_USER_CLARIFICATION.
5. Run Stage 2 Baseline Transfer Readiness Checker after experiment_contract.md says LOCKED.
6. If transfer_readiness.md says NEEDS_CONTRACT_FIX, loop back to Stage 1.
7. If transfer_readiness.md says NEEDS_USER_INPUT, ask the user and stop.
8. Run Stage 3 Baseline Triage Planner after transfer_readiness.md says READY.
9. Run Stage 4 Rewrite Executor after Stage 3 plan files exist.
10. Run Stage 5 Minimal Validation Profiler after implementation_manifest.csv exists.
11. Run Stage 6 Report Writer.
12. Run Stage 7 Integrity Reviewer.
13. If VERDICT is GO, finalize and list artifact paths.
14. If VERDICT is REJECT, log the retry in iteration_log.md, rerun the target stage, rerun downstream affected stages, and return to Stage 7.
```

Loopback log format:

```text
Iteration # | Target Stage | Reason for Rejection | Action Taken | User Input Required
```

## Non-Goals

This workflow does not:

- reproduce every baseline's original experiment protocol;
- preserve baseline-specific dataloaders as primary paths;
- preserve baseline-specific training loops as primary paths;
- preserve baseline-specific metrics as primary paths;
- run full paper-scale experiments;
- tune hyperparameters;
- search for publication results;
- execute third-party baseline scripts during triage.
