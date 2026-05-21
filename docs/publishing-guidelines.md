# Publishing Guidelines

Use these checks before sharing a skill publicly.

## Skill Quality

- The skill has a clear trigger description in `SKILL.md`.
- The skill solves a recurring workflow, not a one-off project note.
- Instructions are concise enough to load during real Codex work.
- Detailed patterns live in `references/` instead of bloating `SKILL.md`.
- The skill avoids private credentials, customer data, and machine-specific paths.

## Validation

- Run the skill validator.
- Inspect the generated `agents/openai.yaml`.
- Test the skill against at least one realistic workspace.
- Record what was tested in the release checklist.

## Community Framing

- Describe the reusable pattern first.
- Use project-specific work only as the example.
- Be precise about local fallbacks, hosted runtimes, generated UI, and model/API requirements.
- Include install instructions that work from a fresh clone.

## Versioning

For now, version skills through Git history. If a skill becomes widely used, add a short version note inside its reference file or a small `metadata` section in `agents/openai.yaml` only when needed.
