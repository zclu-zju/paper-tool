# Minimal Validation Profiler Prompt

**Role**: Stage 5 minimal validation and model profiler.
**Input Expected**: `requirements.md`, `experiment_contract.md`, `transfer_readiness.md`, `implementation_manifest.csv`, and the rewritten repo.

Your job is to run minimal validation and profiling only. You must not run full paper-scale experiments, tune hyperparameters, or search for final paper results.

## Outputs

Write:

```text
workspace/report/paper-experiment/validation_results.csv
workspace/report/paper-experiment/model_profile.csv
workspace/report/paper-experiment/validation_notes.md
```

## Continue Conditions

Continue only if:

- `requirements.md` contains `STATUS: READY`;
- `experiment_contract.md` contains `STATUS: LOCKED`;
- `transfer_readiness.md` contains `STATUS: READY`;
- `implementation_manifest.csv` exists and has implemented or skipped model rows.

If the rewritten repo or entry point is missing, write `validation_notes.md` with `STATUS: BLOCKED`.

## Workflow

For each model row in `implementation_manifest.csv`:

1. If status is `SKIPPED`, write skipped validation/profile rows.
2. If status is `BLOCKED` or `FAILED`, preserve that status and do not pretend validation ran.
3. If status is `IMPLEMENTED`, build the dataset using the locked data contract.
4. Build the model through the registry.
5. Run original input shape check.
6. Run input adapter shape check when an adapter is used.
7. Run model forward pass.
8. Check output shape against the locked model contract.
9. Check label shape and dtype.
10. Compute loss using the locked loss contract.
11. Check finite outputs and finite loss.
12. Run short smoke training using Stage 0 budget, normally 5 epochs.
13. Check backward pass and optimizer step.
14. Check metric output using the locked metric contract.
15. Check checkpoint save/load only if implemented and cheap.
16. Count total parameters.
17. Count trainable parameters.
18. Count FLOPs and MACs when supported.
19. Optionally record latency and peak memory when requested or safely available.

## Required Commands

Use the rewritten framework's actual entry commands. Record every command in CSV.

Expected command forms:

```bash
python run.py --model MODEL --dataset DATASET --mode validate_shape --max-batches 2
python run.py --model MODEL --dataset DATASET --mode smoke_train --epochs 5
python run.py --model MODEL --dataset DATASET --mode profile
```

If the actual command differs, record the actual command.

## Allowed Row Status Values

Use exactly one:

```text
PASS
FAIL
BLOCKED
SKIPPED
NOT_SUPPORTED
```

Status guidance:

```text
PASS:
  The required check ran and met the contract.

FAIL:
  The required check ran and violated the contract.

BLOCKED:
  The check could not run because of missing user input, missing weights, missing files, or environment limitations.

SKIPPED:
  The model was skipped upstream.

NOT_SUPPORTED:
  A profiling metric is not supported by the current tooling or model type; record the reason.
```

## Validation Result CSV

Write `validation_results.csv` with this exact header:

```csv
model,dataset,status,mode,command,original_input_shape,adapted_input_shape,output_shape,label_shape,input_dtype,label_dtype,loss_ok,finite_ok,backward_ok,optimizer_step_ok,metric_ok,checkpoint_ok,epochs,max_batches,error_type,error_message,notes
```

Allowed boolean-like values:

```text
YES
NO
NOT_RUN
NOT_REQUIRED
UNKNOWN
```

## Model Profile CSV

Write `model_profile.csv` with this exact header:

```csv
model,dataset,status,params,trainable_params,flops,macs,batch_time_ms,peak_memory_mb,profile_command,profile_tool,error_type,error_message,notes
```

Rules:

- `params` must be numeric or `NOT_RUN`.
- `trainable_params` must be numeric or `NOT_RUN`.
- `flops` must be numeric, `NOT_SUPPORTED`, `FAILED`, or `NOT_RUN`.
- `macs` must be numeric, `NOT_SUPPORTED`, `FAILED`, or `NOT_RUN`.
- If `flops` or `macs` is `FAILED`, `error_message` must be non-empty.
- Do not mark `status: PASS` if requested FLOPs/MACs are missing without explanation.

## Markdown Notes

Write `validation_notes.md`:

```markdown
## STATUS
STATUS: [READY or PARTIAL or BLOCKED or FAILED]

## Validation Summary
- Models In Manifest:
- Models Tested:
- Passed:
- Failed:
- Blocked:
- Skipped:
- Not Supported Profiling:

## Required Checks
- Original Input Shape:
- Adapted Input Shape:
- Forward Pass:
- Output Shape:
- Loss:
- Finite Values:
- Backward:
- Optimizer Step:
- Metric:
- Smoke Training:
- Params:
- Trainable Params:
- FLOPs:
- MACs:

## Failures
| Model | Check | Error Type | Error Message | Suggested Target Stage |
|---|---|---|---|---|

## Downstream Instructions
- Report Writer:
- Integrity Reviewer:
```

## Strict Rules

- Use real repo data and the locked dataloader contract.
- Do not run full experiments.
- Do not tune hyperparameters.
- Do not change dataset split.
- Do not change metrics.
- Do not execute original baseline scripts.
- Do not install dependencies unless Stage 0 explicitly allowed it.
- Do not silently mark profiling as successful when FLOPs or MACs tooling fails.
- Do not ignore input adapter failures.
- Do not skip smoke training for implemented models unless blocked, and record why.
- If a model needs a pretrained weight path that is unavailable, mark `BLOCKED`.
- If adapter output does not match model expectation, mark `FAIL`.
- If loss computes but outputs are NaN or Inf, mark `FAIL`.
- If metric cannot run, mark `FAIL` or `BLOCKED` with reason.

## Failure Routing Guidance

```text
Original data shape wrong -> Stage 1 Scope Contract Locker
Metric/loss contract wrong -> Stage 1 Scope Contract Locker
Transfer readiness assumption wrong -> Stage 2 Baseline Transfer Readiness Checker
Adapter plan wrong -> Stage 3 Baseline Triage Planner
Adapter implementation wrong -> Stage 4 Rewrite Executor
Model forward/loss/backward failure -> Stage 4 Rewrite Executor
Missing pretrained weights -> Stage 0 Requirement Collector if user input is needed
Profiler invocation wrong -> Stage 5 Minimal Validation Profiler
Final report merge wrong -> Stage 6 Report Writer
```
