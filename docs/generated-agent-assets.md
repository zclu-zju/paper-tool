# Generated Agent Assets

This repository follows the `paper-tool` research branch layout while using original Deep Paper Search content.

- Project agent TOML: `.codex/agents/*.toml`
- Project prompts: `prompts/*.md`
- Launcher prompt: `.codex/deep-paper-search-workflow-prompt.md`
- Plugin assets: `plugins/deep-paper-search/assets/`
- Plugin installer: `plugins/deep-paper-search/scripts/install_project_agents.py`
- Agent manifest: `plugins/deep-paper-search/assets/agent_manifest.json`
- Config template: `config/deep-paper-search.example.yaml`

The generator parses `deep-paper-search-agent-system-design.md` and writes 79 agent TOML files plus 79 project prompt files. Each project agent prompt is expected to be at least 1000 words.
