# Capability Profiler support

Report reproducible problems through the [Codex skills repository issues](https://github.com/Laksh-star/codex-skills/issues).

Include the plugin version, Node.js version, operating system, command options without private paths, and the source scope/warning shown by the report. Reproduce with the bundled synthetic fixture where possible.

Do not attach a private report, local database, real task export, credentials, or request text to a public issue. If a failure requires private evidence, describe the shape of the data first; this plugin provides no private upload endpoint.

The builder needs Node.js 22 or later. If local database reading fails, it can use the session index or a supplied normalized export, and reports the reduced scope. If neither contains tasks, it stops rather than inventing a report.
