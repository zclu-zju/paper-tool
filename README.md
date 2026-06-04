# Baseline Experiment

Codex plugin and project-local multi-agent workflow for rewriting paper experiment baselines into a unified PyTorch experiment framework.

The workflow installs custom Codex agents into a target experiment repository, then runs a staged protocol:

1. collect and validate required parameters;
2. lock the original launch/data/shape/metric contract;
3. triage baseline folders;
4. plan input adapters;
5. rewrite eligible Python/PyTorch baselines;
6. run minimal validation and profiling;
7. write CSV reports;
8. run integrity review with loopback.

## Install From Git

Clone this repository:

```bash
git clone git@github.com:zcluu/baseline-experiment.git
cd baseline-experiment
```

Install the workflow agents into a target experiment repo:

```bash
python3 scripts/install_project_agents.py --repo /path/to/target-experiment-repo
```

Then run the workflow from the target experiment repo:

```bash
cd /path/to/target-experiment-repo
codex exec --sandbox workspace-write --ask-for-approval never - < .codex/experiment-rewrite-workflow-prompt.md
```

Or in an interactive Codex session:

```text
Use the experiment-rewrite-orchestrator custom agent and execute the staged experiment rewrite workflow.
```

## Install As A Codex Git Marketplace

Add this repository as a Codex marketplace:

```bash
codex plugin marketplace add git@github.com:zcluu/baseline-experiment.git
```

Install the plugin from that marketplace:

```bash
codex plugin add experiment-rewrite-workflows@baseline-experiment
```

Start a new Codex thread after installing the plugin. In the target experiment repo, ask Codex:

```text
Install experiment rewrite workflow agents.
```

Then launch the installed repo-local workflow:

```bash
codex exec --sandbox workspace-write --ask-for-approval never - < .codex/experiment-rewrite-workflow-prompt.md
```

## Development Install Into Current Repo

When developing this plugin locally, install its templates into the current directory:

```bash
python3 scripts/install_project_agents.py --repo .
```

The installer is conservative:

- missing files are copied;
- identical files are left unchanged;
- conflicting files are skipped unless `--force` is used;
- obsolete files are removed only with `--clean-obsolete`.

## Main Outputs

The workflow writes reports under:

```text
workspace/experiment_rewrite/
```

The main final artifact is:

```text
workspace/experiment_rewrite/reports/final_model_summary.csv
```

Required final CSV columns:

```csv
model,source_dir,final_status,drop_reason,rewrite_file,registry_entry,config_file,adapter_type,adapter_file,original_input_shape,adapted_input_shape,preprocess_file,needs_preprocess,needs_pretrain,weight_file,shape_test,smoke_train,profile_done,params,trainable_params,flops,macs,validate_command,smoke_train_command,profile_command,notes
```

## Plugin Layout

```text
.codex-plugin/plugin.json
assets/agents/
assets/prompts/codex/
assets/prompts/project/
scripts/install_project_agents.py
skills/experiment-rewrite/SKILL.md
```

The `.codex/` and `prompts/` directories in this repo are the installed project-local copies used for local testing.
