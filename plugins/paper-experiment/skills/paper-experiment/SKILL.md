---
name: paper-experiment
description: Use for staged Codex workflows that rewrite paper experiment baselines into a unified PyTorch framework. Installs repo-local custom agents, collects minimal hard parameters, locks the original repo's launch/data/shape/metric contract, checks baseline-transfer readiness, triages baseline directories, plans input adapters, rewrites eligible models, runs minimal validation/profiling, writes CSV reports, and loops back on reviewer failures.
---

# Paper Experiment

This skill installs and launches a single interactive experiment rewrite workflow.

The workflow is intended for repositories where:

- the user has an existing paper experiment repo;
- the repo has an original launch script or launch command;
- baseline implementations have been collected in one or more directories;
- the desired outcome is a unified PyTorch entry point with minimal validation and profiling, not full paper-scale experiments.

It is intentionally iterative rather than one-pass. Stage 7 can reject earlier stages and send the orchestrator back to redo only the failed stage.

## Install Agents

The plugin carries custom agent templates in `assets/agents/`, but those agents become active only after they are installed into the target repo's `.codex/agents/`.

From a local clone:

```bash
python3 scripts/install_project_agents.py --repo .
```

From an installed plugin cache, resolve the installer relative to this skill directory:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo>
```

When upgrading from an older release, clean obsolete files:

```bash
python3 ../../scripts/install_project_agents.py --repo <target-repo> --clean-obsolete
```

The installer is conservative. It copies missing files, leaves identical files unchanged, reports conflicts without overwriting, and removes old known files only when `--clean-obsolete` is passed.

## Launch

After installing agents, invoke:

```text
Use the experiment-rewrite-orchestrator custom agent and execute the staged experiment rewrite workflow.
```

Or use the launcher file:

```bash
codex exec --sandbox workspace-write --ask-for-approval never - < .codex/experiment-rewrite-workflow-prompt.md
```

## Interaction Contract

Stage 0 must collect only the hard required parameters before any repo contract lock, baseline triage, or code rewrite:

- original repository root;
- original launch script path or launch command;
- baseline root directory or directories.

All other policies use workflow defaults unless the user explicitly says otherwise. If a hard required parameter is missing, the orchestrator asks concise questions and stops.

Stage 1 locks the experiment contract by reading the original repo and launch script. If the launch, dataset, shape, metric, or runtime contract is ambiguous, the orchestrator asks clarification questions and stops.

Stage 2 checks whether the locked original task contract is sufficient for baseline model transfer. It treats baselines as model architectures to migrate into the user's task and must not require baseline original dataloaders, training loops, metrics, launch commands, evaluation protocols, or reported paper metrics.

Only after requirements are `READY`, the experiment contract is `LOCKED`, and transfer readiness is `READY` can the workflow triage baselines or rewrite code.

## Outputs

All generated outputs go under:

```text
workspace/work/paper-experiment/
```

The main final output is:

```text
workspace/report/paper-experiment/final_model_summary.csv
```

Required final CSV columns:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

## Loopback

The integrity reviewer can reject and return to:

- Stage 0 Requirement Collector;
- Stage 1 Scope Contract Locker;
- Stage 2 Baseline Transfer Readiness Checker;
- Stage 3 Baseline Triage Planner;
- Stage 4 Rewrite Executor;
- Stage 5 Minimal Validation Profiler;
- Stage 6 Report Writer.

If no new user input is required, the orchestrator retries automatically and reruns downstream affected stages.

## Non-Goals

This workflow does not:

- reproduce baseline original experiment protocols;
- run full paper-scale experiments;
- tune hyperparameters;
- search for best publication results;
- allow every baseline to keep its own dataloader;
- allow every baseline to keep its own training loop;
- allow every baseline to keep its own metric implementation;
- execute third-party baseline scripts during triage.
