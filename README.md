# Paper Experiment

Codex plugin and project-local multi-agent workflow for rewriting paper experiment baselines into a unified PyTorch experiment framework.

The workflow installs custom Codex agents into a target experiment repository, then runs a staged protocol:

1. collect only the hard required paths and lock workflow defaults;
2. lock the original launch/data/shape/metric contract;
3. check whether the locked original task contract is sufficient for baseline model transfer;
4. triage baseline folders and plan input adapters;
5. rewrite eligible Python/PyTorch model structures;
6. run minimal validation and profiling;
7. write CSV reports;
8. run integrity review with loopback.

Stage 0 hard required inputs are only:

```text
1. Original repository root.
2. Original launch script path or original launch command.
3. Baseline root directory or directories.
```

Baselines are treated as model architectures to migrate into the user's original task. The workflow does not require baseline original training loops, dataloaders, metrics, launch commands, or reported paper metrics.

## Install From GitHub

```bash
codex plugin marketplace add git@github.com:zcluu/paper-experiment.git --ref main
codex plugin add paper-experiment@paper-experiment
```

Start a new Codex session after installation.

## Development Source

This repository is the source of truth for the `paper-experiment` plugin package. Develop prompts, agents, installer behavior, and the skill under:

```text
plugins/paper-experiment/
```

For compatibility with the original repo layout, root-level `.codex-plugin/`, `assets/`, `scripts/`, and `skills/` are kept synchronized with the plugin package. The `paper-tool` repository is only the aggregate marketplace and integration-test target.

## Install Agents Into A Target Repo

For a local clone:

```bash
python3 plugins/paper-experiment/scripts/install_project_agents.py --repo /path/to/target-experiment-repo --clean-obsolete
```

Or with the root-level compatibility installer:

```bash
python3 scripts/install_project_agents.py --repo /path/to/target-experiment-repo --clean-obsolete
```

If installed through Codex, ask Codex in the target repo:

```text
Use paper-experiment.

Install the paper experiment workflow agents into this repository.
```

## Run The Workflow

After installing agents:

```bash
cd /path/to/target-experiment-repo
codex exec --sandbox workspace-write --ask-for-approval never - < .codex/experiment-rewrite-workflow-prompt.md
```

Or in an interactive Codex session:

```text
Use paper-experiment.

Rewrite my paper experiment baselines after collecting requirements. Use workspace/report/paper-experiment for reports and workspace/work/paper-experiment for non-report working files.
```

## Main Outputs

Reports are plugin-scoped:

```text
workspace/report/paper-experiment/requirements.md
workspace/report/paper-experiment/experiment_contract.md
workspace/report/paper-experiment/transfer_readiness.md
workspace/report/paper-experiment/baseline_inventory.csv
workspace/report/paper-experiment/rewrite_plan.csv
workspace/report/paper-experiment/input_adapter_plan.csv
workspace/report/paper-experiment/implementation_manifest.csv
workspace/report/paper-experiment/validation_results.csv
workspace/report/paper-experiment/model_profile.csv
workspace/report/paper-experiment/final_model_summary.csv
workspace/report/paper-experiment/final_summary.md
workspace/report/paper-experiment/integrity_report.md
workspace/report/paper-experiment/iteration_log.md
```

Non-report execution artifacts are plugin-scoped:

```text
workspace/work/paper-experiment/
workspace/work/paper-experiment/rewritten_repo/
```

Required final CSV columns:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

## Plugin Layout

```text
plugins/paper-experiment/.codex-plugin/plugin.json
plugins/paper-experiment/assets/agents/
plugins/paper-experiment/assets/prompts/codex/
plugins/paper-experiment/assets/prompts/project/
plugins/paper-experiment/scripts/install_project_agents.py
plugins/paper-experiment/skills/paper-experiment/SKILL.md
```
