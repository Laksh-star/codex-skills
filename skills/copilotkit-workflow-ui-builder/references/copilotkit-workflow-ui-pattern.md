# CopilotKit Workflow UI Pattern

## Existing Backend To CopilotKit Mapping

Start by listing the real workflow primitives:

- Backend endpoints: analyze, submit, poll job, stream events, fetch report, export package.
- State model: idle, running, completed, failed, offline, approved, locked, exported.
- Artifacts: reports, recommendations, comparisons, drafts, packages, logs, attachments.
- Human gates: review evidence, approve assumptions, approve decision, confirm export.

Map each primitive to one CopilotKit role:

- Context: state the copilot should read.
- Frontend tool: app action the copilot may trigger.
- Structured UI: state or output that benefits from a visual component.
- Plain answer: explanation, comparison, or next-step guidance.

## App State As Agent Context

Register compact, live state rather than large raw payloads. Include the active entity, backend status, selected evidence, recommendation, approval progress, and artifact readiness.

Good context descriptions explain what the state is and what the copilot may use it for. Avoid dumping secrets, credentials, full logs, or large documents unless the user explicitly needs them.

## Frontend Tool Registration

Expose actions that are natural inside the UI:

- open or focus a workflow panel
- select an item or comparable
- approve a review checkpoint
- retry a failed backend step
- request export after approval
- mark a package ready or locked

Tools should be narrow enough that the UI can validate preconditions. Return structured results such as `{ "approved": "recommendation" }` or `{ "opened": "report" }`.

## Structured And Generative UI Surfaces

Use structured UI for recurring decision surfaces:

- recommendation cards
- evidence/comparable panels
- approval gates
- job status and readiness panels
- package or export summaries

For community examples, label what CopilotKit is doing only if that helps readers understand the architecture. In production UIs, avoid tutorial labels unless the product is educational.

## Approval And Review Gates

Do not let the copilot silently complete high-impact actions. Make the user-visible sequence explicit:

1. Backend result exists.
2. User reviews evidence and assumptions.
3. User approves decision.
4. Package/export action unlocks.
5. Final lock/export records visible state.

The UI should show both disabled reasons and completed approval states.

## Local Fallback Versus Hosted Runtime

A local fallback agent is useful for development, demos, and no-key onboarding. It should be described as local or deterministic if it does not call a real LLM.

A hosted runtime path is the production story when the copilot needs real model calls, persistent sessions, auth, or server-side tools. Document the runtime URL, required keys, and provider fallback behavior.

Avoid phrases like "fully A2UI-generated" or "autonomous agent control" unless that exact behavior is implemented. Prefer precise wording such as "A2UI-style decision snapshot backed by live workflow state" when the UI is state-rendered.

## Validation Checklist

- Package install completes or existing lockfile is respected.
- Typecheck/build passes.
- Smoke test covers CopilotKit imports, provider wiring, context registration, tools, and backend integration points.
- Backend health or proxy route is verified when available.
- Browser check confirms the main workflow, copilot panel, approval gates, and responsive layout render correctly.
- Copilot behavior is checked before and after backend completion.
- Gated actions cannot be triggered too early.

## Community Or Article Handoff

Frame the artifact around the reusable pattern:

- "Start with a real workflow."
- "Register live state as context."
- "Expose frontend tools for app control."
- "Render structured workflow UI, not just chat text."
- "Keep human approval gates explicit."
- "Validate the integration with real app checks."

Use the specific app as the case study, not the whole point of the skill.
