# vibehacks

Personal one-off Python projects, each in its own top-level directory. Tasks are agent-driven and script-oriented — not reusable libraries.

## Repository structure

```
vibehacks/
  <task-name>/       # one directory per task
    main.py          # primary entry point
    requirements.txt # per-task deps (or pyproject.toml if needed)
    .env.example     # template for any secrets (never commit .env)
    README.md        # optional, only if the task is non-obvious
```

Each task directory is fully self-contained. No shared code between tasks.

## Python conventions

- **Python version**: 3.11+
- **Dependencies**: use `uv` for virtual environments and package management (`uv venv`, `uv pip install`)
- **Style**: follow PEP 8; use `ruff` for linting/formatting (`ruff check`, `ruff format`)
- **Type hints**: use them on function signatures; skip for obvious locals
- **No tests** unless the task has logic worth validating
- Scripts should be runnable directly: `python main.py` or via `uv run`

## Agent / Claude API conventions

- Use the Anthropic Python SDK (`anthropic`)
- Default to `claude-opus-4-7`; drop to `claude-sonnet-4-6` for cost-sensitive tasks or `claude-haiku-4-5-20251001` for speed
- Always include prompt caching (`cache_control`) on large static context
- Stream responses when output may be long
- Store API keys in `.env`, loaded via `python-dotenv`; never hardcode

## Code style

- No docstrings on obvious functions
- Comments only when the WHY is non-obvious
- Prefer simple scripts over classes; use classes only when state genuinely warrants it
- No premature abstraction — three similar lines beats a helper for a one-off script
- Fail loudly: let exceptions propagate rather than swallowing errors silently

## Starting a new task

1. Create `<task-name>/` directory
2. Set up venv: `cd <task-name> && uv venv && source .venv/bin/activate`
3. Install deps: `uv pip install anthropic python-dotenv` (plus task-specific packages)
4. Create `.env` from `.env.example` and populate `ANTHROPIC_API_KEY`

## Shell / SSH environment

If `git push` fails with a public key error in VSCode extension:
- **Preferred**: run git commands from the terminal (not VSCode UI) — it inherits the shell with SSH agent loaded
- **Alternative**: switch remote URL to HTTPS (`git remote set-url origin https://...`)
- **CLI**: exit and relaunch the session to refresh SSH environment

## Secrets

- `.env` is gitignored — never commit it
- Always provide a `.env.example` with placeholder values
