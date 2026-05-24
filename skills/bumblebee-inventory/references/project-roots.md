# Bumblebee Project Roots

Use the smallest root that answers the user's question.

## Default behavior

The bundled script defaults to the current working directory. This is the safest behavior for a shareable skill because it avoids hardcoded private paths.

```bash
skills/bumblebee-inventory/scripts/bumblebee_scan.sh inventory
```

## Explicit roots

Use `--only-root` for a single publishable repo scan:

```bash
skills/bumblebee-inventory/scripts/bumblebee_scan.sh inventory --only-root /path/to/repo
```

Use repeated `--root` flags to add more roots to the default current directory:

```bash
skills/bumblebee-inventory/scripts/bumblebee_scan.sh inventory \
  --root /path/to/repo-a \
  --root /path/to/repo-b
```

## Curated local root sets

For a personal workspace, keep curated root lists outside the public skill repo. Good places:

- a wrapper script in your private dotfiles
- an environment variable-driven launcher
- local notes under `$CODEX_HOME`

Avoid committing machine-specific paths such as `/Users/<name>/...` into a public skill.

## Noise guidance

Avoid treating dependency caches as scan roots:

- `node_modules`
- `.venv`
- `venv`
- `.next`
- `.vite`
- `vendor`
- build or cache directories

For routine use, prefer Bumblebee `project` scans over `deep` scans. Use `deep` only for explicit incident response.
