# Experiment Rewrite Workflow Protocol

This document redesigns the multi-agent system as a Codex-style staged workflow, following the structure of the `baseline-research-workflows` plugin:

- a main orchestrator controls the whole workflow;
- Stage 0 collects and validates required parameters before any code rewrite;
- Stage 1 locks the experiment scope and repository contract;
- every stage writes auditable artifacts;
- the final reviewer returns `GO` or `REJECT`;
- when rejected, the orchestrator loops back to exactly one target stage.

This is not primarily a development-team split. The main concern is whether Codex has enough validated information to safely perform the rewrite and whether each stage produced verifiable artifacts.

## 1. Target Shape

The future implementation should look like a project-local Codex workflow:

```text
.codex/
  agents/
    experiment_rewrite_orchestrator.toml
    experiment_requirement_collector.toml
    experiment_scope_contract_locker.toml
    baseline_triage_planner.toml
    experiment_rewrite_executor.toml
    minimal_validation_profiler.toml
    experiment_report_writer.toml
    experiment_integrity_reviewer.toml
  experiment-rewrite-workflow-prompt.md

prompts/
  experiment_rewrite_orchestrator.md
  experiment_requirement_collector.md
  experiment_scope_contract_locker.md
  baseline_triage_planner.md
  experiment_rewrite_executor.md
  minimal_validation_profiler.md
  experiment_report_writer.md
  experiment_integrity_reviewer.md
```

All workflow outputs should be isolated under:

```text
workspace/experiment_rewrite/
```

Recommended output layout:

```text
workspace/experiment_rewrite/
  reports/
    requirements.md
    experiment_contract.md
    baseline_inventory.csv
    rewrite_plan.csv
    input_adapter_plan.csv
    implementation_manifest.csv
    validation_results.csv
    model_profile.csv
    final_model_summary.csv
    final_summary.md
    integrity_report.md
    iteration_log.md
  rewritten_repo/
  logs/
```

## 2. Agent List

The system uses 8 agents:

```text
1. experiment-rewrite-orchestrator
2. experiment-requirement-collector
3. experiment-scope-contract-locker
4. baseline-triage-planner
5. experiment-rewrite-executor
6. minimal-validation-profiler
7. experiment-report-writer
8. experiment-integrity-reviewer
```

The important design point is that agents are stage workers, not independent developers. Each agent has a narrow protocol, fixed inputs, fixed outputs, and status values.

## 3. Stage 0: Requirement Collection And Parameter Validation

Agent:

```text
experiment-requirement-collector
```

Output:

```text
workspace/experiment_rewrite/reports/requirements.md
```

Allowed status:

```text
STATUS: READY
STATUS: NEEDS_USER_INPUT
```

The orchestrator must not run Stage 1 unless `requirements.md` says:

```text
STATUS: READY
```

If required parameters are missing, the collector asks no more than 3 concise questions and stops.

This is the stage that validates whether Codex has enough information to start. It is more important than listing every possible `run.py` argument.

### Required Parameters

Stage 0 must collect or confirm:

```text
1. Original repository root.
2. Original launch script path or launch command.
3. Baseline root directory or directories.
4. Output workspace directory.
5. Whether rewriting may modify the original repo or must write to a separate rewritten copy.
6. Target task type, if known.
7. Dataset source policy: must use original repo data loading, or may define a new loader.
8. Dataset split policy: must preserve original split, or user-approved changes.
9. Metric policy: must use original repo metrics, or user-approved changes.
10. Allowed framework: PyTorch only.
11. Allowed source language: Python only.
12. Handling policy for empty, non-Python, non-PyTorch, or incompatible baselines.
13. Whether model architecture changes are allowed.
14. Input compatibility policy, such as padding, resizing, masking, or model change fallback.
15. Preprocessing policy.
16. Pretrained weight policy.
17. Dependency installation policy.
18. Third-party code execution policy.
19. Minimal validation budget.
20. Profiling requirements.
21. Device policy.
22. Final report format.
23. Overwrite policy for existing files.
24. Whether defaults are allowed for missing non-critical parameters.
```

### Recommended Parameter Values

These values should be explicit in `requirements.md`:

```text
Original Repo Root:
Original Launch Script:
Baseline Root Directories:
Output Workspace:
Rewrite Target: [IN_PLACE / COPY_TO_REWRITTEN_REPO]
Allowed Language: PYTHON_ONLY
Allowed Framework: PYTORCH_ONLY
Data Policy: PRESERVE_ORIGINAL_DATALOADER
Split Policy: PRESERVE_ORIGINAL_SPLIT
Metric Policy: PRESERVE_ORIGINAL_METRICS
Training Policy: SHARED_TRAIN_LOOP
Baseline Handling: DROP_EMPTY / DROP_NON_PYTHON / DROP_NON_PYTORCH / DROP_INCOMPATIBLE
Model Architecture Change Policy: [DISALLOW / ALLOW_IF_ADAPTER_FAILS / ALLOW]
Input Adapter Policy: [REQUIRED_WHEN_NEEDED / DISALLOW / USER_CONFIRM]
Preferred Input Adapters: [pad_to_square, pad_to_multiple, resize, channel_project, add_mask, custom]
Preprocessing Policy: [ALLOW_EXPLICIT_PREPROCESS_STAGE / DISALLOW]
Pretrained Weight Policy: [ALLOW_IF_USER_PROVIDES_PATH / DISALLOW / AUTO_DISCOVER_LOCAL_ONLY]
Dependency Policy: [NO_INSTALL / INSTALL_WITH_USER_APPROVAL / USE_EXISTING_ENV_ONLY]
Third-Party Code Execution: DO_NOT_EXECUTE_BASELINE_CODE
Smoke Epochs: 5
Max Validation Batches:
Profile Metrics: [params, trainable_params, macs, flops, latency, memory]
Device: [cpu / cuda / cuda:N / auto]
Output Format: [CSV / XLSX / BOTH]
Overwrite Policy: [NO_OVERWRITE / OVERWRITE_WORKFLOW_OUTPUTS_ONLY / USER_APPROVAL]
Defaults Allowed: [YES / NO]
```

### Stage 0 Strict Rules

- Do not read deeply into baseline code yet.
- Do not rewrite code.
- Do not run training.
- Do not assume defaults unless the user allowed defaults.
- Do not install dependencies.
- Do not execute third-party baseline code.
- If a required path is missing or ambiguous, ask the user.
- If authentication or private weights are needed, ask the user to configure local access; do not ask for secrets in chat or reports.

## 4. Stage 1: Experiment Scope And Contract Lock

Agent:

```text
experiment-scope-contract-locker
```

Inputs:

```text
workspace/experiment_rewrite/reports/requirements.md
original repo files
original launch script
```

Output:

```text
workspace/experiment_rewrite/reports/experiment_contract.md
```

Allowed status:

```text
STATUS: LOCKED
STATUS: NEEDS_USER_CLARIFICATION
```

The orchestrator must not run Stage 2 unless the contract says:

```text
STATUS: LOCKED
```

### Responsibilities

This stage reads the original repo and launch script to lock the experiment contract.

It should extract:

```text
1. Original entry command.
2. Required command-line arguments.
3. Dataset names and paths.
4. Data loading pipeline.
5. Batch fields.
6. Original input shape, dtype, and semantic meaning.
7. Label shape and dtype.
8. Loss function.
9. Metrics.
10. Optimizer and scheduler, if discoverable.
11. Device and seed behavior.
12. Expected model input contract.
13. Expected model output contract.
14. Minimal runnable command for the original model.
15. Shape examples from real data, if safely obtainable.
```

### Contract Output Format

`experiment_contract.md` should contain:

```markdown
## STATUS
STATUS: [LOCKED or NEEDS_USER_CLARIFICATION]

## Clarification Questions
1. [Only when needed]

## Original Launch Contract
- Entry Command:
- Launch Script:
- Required Args:
- Optional Args:

## Dataset Contract
- Dataset Names:
- Data Root:
- Split Policy:
- Dataloader Path:
- Batch Fields:
- Input Shape:
- Label Shape:
- Input DType:
- Label DType:

## Model Contract
- Input Contract:
- Output Contract:
- Loss Contract:
- Metric Contract:

## Runtime Contract
- Device:
- Seed:
- Batch Size:
- Optimizer:
- Scheduler:

## Minimal Validation Contract
- Max Batches:
- Smoke Epochs:
- Required Checks:
- Required Profile Metrics:

## Input Compatibility Contract
- Irregular Input: [YES / NO / UNKNOWN]
- Non-Square Input: [YES / NO / UNKNOWN]
- Variable Length Input: [YES / NO / UNKNOWN]
- Mask Required: [YES / NO / UNKNOWN]
- Allowed Adapter Types:
- Model Shape Change Allowed:
```

### Stage 1 Strict Rules

- Do not rewrite code.
- Do not scan every baseline yet.
- Do not change the original dataset split.
- If launch parameters or dataset semantics are ambiguous, output `NEEDS_USER_CLARIFICATION`.
- If minimal shape probing is needed, use only the original repo logic and do not run third-party baseline code.

## 5. Stage 2: Baseline Triage And Rewrite Planning

Agent:

```text
baseline-triage-planner
```

Inputs:

```text
requirements.md
experiment_contract.md
baseline root directories
```

Outputs:

```text
workspace/experiment_rewrite/reports/baseline_inventory.csv
workspace/experiment_rewrite/reports/rewrite_plan.csv
workspace/experiment_rewrite/reports/input_adapter_plan.csv
```

Allowed status in markdown notes or CSV rows:

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

### Responsibilities

This stage does triage and planning, not implementation.

It should:

```text
1. Traverse baseline directories.
2. Identify empty folders.
3. Identify non-Python projects.
4. Identify non-PyTorch projects.
5. Detect whether a baseline has model logic worth rewriting.
6. Detect expected input format of each baseline.
7. Compare baseline expected input with the locked experiment contract.
8. Decide whether an input adapter can bridge the mismatch.
9. Detect whether preprocessing is required.
10. Detect whether pretrained weights are required.
11. Decide whether the model should be rewritten, dropped, or marked unknown.
12. Produce a concrete rewrite plan before code changes.
```

### Baseline Inventory Columns

`baseline_inventory.csv` should include:

```csv
model,source_dir,status,drop_reason,language,framework,has_python,has_pytorch,has_model_code,expected_input_format,expected_output_format,needs_input_adapter,needs_preprocess,needs_pretrain,notes
```

### Rewrite Plan Columns

`rewrite_plan.csv` should include:

```csv
model,source_dir,status,rewrite_target_file,registry_name,config_file,shared_dataloader,shared_train_loop,shared_metric,architecture_change_allowed,architecture_change_reason,preprocess_file,weight_policy,notes
```

### Input Adapter Plan Columns

`input_adapter_plan.csv` should include:

```csv
model,dataset,adapter_status,adapter_type,original_input_shape,baseline_expected_shape,adapted_input_shape,pad_mode,pad_value,preserve_mask,requires_model_change,model_change_reason,notes
```

### Input Compatibility Rule

If the original model supports irregular or non-square input but a baseline expects square CNN-style input, the preferred plan is:

```text
adapter_type: pad_to_square
preserve_mask: YES when needed
requires_model_change: NO
```

Model architecture changes should be planned only when the adapter cannot make the model valid.

### Stage 2 Strict Rules

- Do not execute baseline code.
- Do not install dependencies.
- Do not rewrite code yet.
- Do not accept a baseline as rewrite-ready unless it is Python and PyTorch or can be cleanly rewritten from visible Python/PyTorch logic.
- Do not drop a model without a recorded reason.
- Do not silently resolve input mismatch by modifying the model architecture.

## 6. Stage 3: Rewrite Execution

Agent:

```text
experiment-rewrite-executor
```

Inputs:

```text
requirements.md
experiment_contract.md
baseline_inventory.csv
rewrite_plan.csv
input_adapter_plan.csv
```

Output:

```text
workspace/experiment_rewrite/reports/implementation_manifest.csv
```

Allowed implementation row status:

```text
IMPLEMENTED
SKIPPED
BLOCKED
FAILED
```

### Responsibilities

This is the only stage that rewrites code.

It should:

```text
1. Create or update the unified entry point.
2. Create or update the model registry.
3. Create or update shared dataset entry points, using original repo logic.
4. Create or update input adapters.
5. Rewrite eligible model files into the unified framework.
6. Add explicit preprocessing files when required.
7. Add explicit weight-loading paths when required.
8. Record every created or modified file.
```

The rewrite target should still support a single entry point:

```bash
python run.py --model MODEL --dataset DATASET --mode validate_shape
python run.py --model MODEL --dataset DATASET --mode smoke_train --epochs 5
python run.py --model MODEL --dataset DATASET --mode profile
```

### Implementation Manifest Columns

`implementation_manifest.csv` should include:

```csv
model,status,source_dir,rewrite_file,registry_entry,config_file,adapter_file,preprocess_file,weight_file,modified_files,created_files,skipped_reason,blocked_reason,notes
```

### Stage 3 Strict Rules

- Do not keep baseline-specific dataloaders.
- Do not keep baseline-specific train loops.
- Do not keep baseline-specific metric implementations.
- Do not execute third-party baseline scripts.
- Do not install dependencies unless Stage 0 explicitly allowed it.
- Do not overwrite user files unless the overwrite policy allows it.
- Do not modify the model architecture for input mismatch unless `input_adapter_plan.csv` says it is required and Stage 0 allows it.

## 7. Stage 4: Minimal Validation And Profiling

Agent:

```text
minimal-validation-profiler
```

Inputs:

```text
requirements.md
experiment_contract.md
implementation_manifest.csv
rewritten repo
```

Outputs:

```text
workspace/experiment_rewrite/reports/validation_results.csv
workspace/experiment_rewrite/reports/model_profile.csv
```

Allowed validation row status:

```text
PASS
FAIL
BLOCKED
SKIPPED
```

### Responsibilities

This stage runs minimal validation only. It does not run full experiments.

Required checks:

```text
1. Build dataset using the locked dataset contract.
2. Build model from registry.
3. Run original input shape check.
4. Run input adapter shape check.
5. Run forward pass.
6. Check output shape.
7. Check loss computation.
8. Check finite output and finite loss.
9. Run short smoke training, normally 5 epochs.
10. Check backward pass and optimizer step.
11. Check metric output.
12. Count total parameters.
13. Count trainable parameters.
14. Count FLOPs and MACs when supported.
15. Optionally record latency and peak memory.
```

### Validation Result Columns

`validation_results.csv` should include:

```csv
model,dataset,status,mode,command,original_input_shape,adapted_input_shape,output_shape,label_shape,loss_ok,finite_ok,backward_ok,metric_ok,epochs,max_batches,error_type,error_message,notes
```

### Model Profile Columns

`model_profile.csv` should include:

```csv
model,dataset,status,params,trainable_params,flops,macs,batch_time_ms,peak_memory_mb,profile_command,notes
```

### Stage 4 Strict Rules

- Use real repo data and the locked dataloader contract.
- Do not run full paper-scale experiments.
- Do not tune hyperparameters.
- Do not change dataset split.
- Do not silently mark profiling as successful when FLOPs or MACs tooling fails.
- If input adapter output does not match the model expectation, mark `FAIL` and target Stage 2 or Stage 3 depending on whether the plan or implementation is wrong.

## 8. Stage 5: Report Writing

Agent:

```text
experiment-report-writer
```

Inputs:

```text
requirements.md
experiment_contract.md
baseline_inventory.csv
rewrite_plan.csv
input_adapter_plan.csv
implementation_manifest.csv
validation_results.csv
model_profile.csv
```

Outputs:

```text
workspace/experiment_rewrite/reports/final_model_summary.csv
workspace/experiment_rewrite/reports/final_summary.md
```

### Final CSV Columns

`final_model_summary.csv` should include:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

Allowed `final_status` values:

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
```

### Stage 5 Strict Rules

- Do not invent successful validation results.
- Do not hide skipped models.
- Do not merge incompatible models into `DONE`.
- Do not omit launch commands for completed models.
- Do not omit adapter information when an adapter was used.

## 9. Stage 6: Integrity Review

Agent:

```text
experiment-integrity-reviewer
```

Inputs:

```text
all reports under workspace/experiment_rewrite/reports/
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

If rejected, the reviewer must name exactly one target stage:

```text
Stage 0 Requirement Collector
Stage 1 Scope Contract Locker
Stage 2 Baseline Triage Planner
Stage 3 Rewrite Executor
Stage 4 Minimal Validation Profiler
Stage 5 Report Writer
```

### Review Checklist

The reviewer checks:

```text
1. Stage 0 collected all required parameters.
2. Stage 0 did not assume defaults without permission.
3. Stage 1 locked the original launch, dataset, shape, metric, and runtime contract.
4. Stage 2 classified every baseline directory.
5. Stage 2 recorded drop reasons for skipped models.
6. Stage 2 planned input adapters before architecture changes.
7. Stage 3 implemented only eligible models.
8. Stage 3 preserved shared dataloader, shared train loop, and shared metric.
9. Stage 3 did not execute third-party baseline scripts.
10. Stage 4 used real repo data.
11. Stage 4 checked original and adapted input shapes.
12. Stage 4 ran forward, loss, backward, smoke training, and metrics where required.
13. Stage 4 recorded params, trainable params, FLOPs, and MACs or clear failure reasons.
14. Stage 5 final CSV schema is complete.
15. Stage 5 launch commands are present for completed models.
16. Loopback target is clear if anything fails.
```

Expected output:

```markdown
## Review Checklist
1. Requirement Completeness: [Yes/No] - [Reason]
2. Parameter Validation: [Yes/No] - [Reason]
3. Experiment Contract Lock: [Yes/No] - [Reason]
4. Baseline Coverage: [Yes/No] - [Reason]
5. Drop Reason Completeness: [Yes/No] - [Reason]
6. Input Adapter Discipline: [Yes/No] - [Reason]
7. Rewrite Eligibility: [Yes/No] - [Reason]
8. Shared Framework Discipline: [Yes/No] - [Reason]
9. Third-Party Code Safety: [Yes/No] - [Reason]
10. Minimal Validation Completeness: [Yes/No] - [Reason]
11. Profiling Completeness: [Yes/No] - [Reason]
12. Final CSV Schema: [Yes/No] - [Reason]
13. Launch Command Completeness: [Yes/No] - [Reason]
14. Loopback Readiness: [Yes/No] - [Reason]

## VERDICT
VERDICT: [GO or REJECT]

## REJECT ACTION
Target Stage: [exactly one stage or Not Applicable]
Action Required: [concrete instruction]
User Input Required: [Yes/No]
```

## 10. Orchestrator Protocol

Agent:

```text
experiment-rewrite-orchestrator
```

The orchestrator controls the workflow:

```text
0. Create workspace/experiment_rewrite/reports/.
1. Run Stage 0 Requirement Collector.
2. If requirements.md says NEEDS_USER_INPUT, ask the user and stop.
3. Run Stage 1 Scope Contract Locker only after requirements.md says READY.
4. If experiment_contract.md says NEEDS_USER_CLARIFICATION, ask the user and stop.
5. Run Stage 2 Baseline Triage Planner only after experiment_contract.md says LOCKED.
6. Run Stage 3 Rewrite Executor using the approved plan.
7. Run Stage 4 Minimal Validation Profiler.
8. Run Stage 5 Report Writer.
9. Run Stage 6 Integrity Reviewer.
10. If VERDICT is GO, finalize and list artifact paths.
11. If VERDICT is REJECT, log the retry in iteration_log.md, rerun the target stage, rerun downstream affected stages, and return to Stage 6.
```

Loopback log format:

```text
Iteration # | Target Stage | Reason for Rejection | Action Taken | User Input Required
```

### Orchestrator Strict Rules

- Do not rewrite code before Stage 0 is `READY` and Stage 1 is `LOCKED`.
- Do not continue when a required artifact is missing or malformed.
- Do not run a downstream stage when the upstream status blocks it.
- Do not ask more than 3 user questions at a time.
- Do not execute third-party baseline code.
- Do not install dependencies unless explicitly allowed in Stage 0.
- Do not hide skipped or failed baselines.
- Always rerun downstream affected stages after a loopback fix.

## 11. Why This Differs From The Previous Design

The previous design was too development-oriented. It described who writes code, who tests code, and who reports results.

The corrected design is workflow-oriented:

```text
1. Parameter validation is a mandatory Stage 0.
2. Scope and repo contract locking is mandatory before baseline work.
3. Each stage writes fixed artifacts.
4. Every artifact has a status.
5. The reviewer rejects with one loopback target.
6. Implementation is only one controlled stage.
7. Input compatibility is planned before code rewriting.
8. Final output is judged by report schema and validation evidence, not by whether the code "looks implemented".
```

This structure is closer to the provided plugin: strict staged protocol, audited artifacts, status gates, and loopback review.
