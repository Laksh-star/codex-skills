---
name: copilotkit-workflow-ui-builder
description: Build, plan, or review a CopilotKit-powered UI around an existing workflow, backend, internal tool, or decision process. Use when Codex is asked to add CopilotKit to an app, turn backend state into a copilot-aware interface, register app context or frontend tools, design structured/generative UI surfaces, add human approval gates, validate a CopilotKit integration, or prepare a community-ready CopilotKit walkthrough or article from a real workflow.
---

# CopilotKit Workflow UI Builder

## Operating Principle

Turn the existing workflow into the center of the product. The copilot should read, explain, and operate real app state; it should not become a detached chat widget beside a fake demo.

Use the reference only when implementation details are needed: `references/copilotkit-workflow-ui-pattern.md`.

## Workflow

1. Inspect the current app before designing.
   - Identify the framework, package manager, backend entrypoints, API clients, state types, and primary user journey.
   - Find real workflow states, endpoints, events, jobs, reports, approvals, exports, or artifacts that the UI can expose.
   - Prefer existing app patterns and component conventions over new abstractions.

2. Map the workflow to CopilotKit responsibilities.
   - Register live workflow state as agent context.
   - Expose only useful app actions as frontend tools: navigation, approval, selection, export, retry, or report actions.
   - Use structured UI for decision cards, evidence panels, review gates, summaries, or next-step surfaces.
   - Keep backend-generated results as the source of truth. Do not fabricate completed analysis before the backend has produced it.

3. Build the UI around the workflow.
   - Put the workflow surface first and the copilot in a supporting position unless the product is explicitly chat-first.
   - Make status, progress, approval state, and backend readiness visible in the main UI.
   - Add human-in-the-loop gates where business decisions, exports, destructive changes, or external publication happen.
   - Label CopilotKit-powered surfaces clearly when the request involves education, community sharing, or article screenshots.

4. Handle runtime honestly.
   - Support a local fallback agent when useful for no-key development.
   - Support a hosted/runtime URL path when the project needs a real LLM-backed copilot.
   - State precisely what is local, what is hosted, what is mocked, and what depends on API keys.
   - Avoid overclaiming A2UI, generative UI, or agent control if the implementation is state-rendered React plus registered tools.

5. Validate with real usage.
   - Run repo-native checks first: smoke tests, typechecks, builds, backend health checks, or API contract tests.
   - For frontend changes, use browser verification or screenshots when available.
   - Confirm the copilot cannot invent workflow results before backend completion.
   - Confirm approvals/tools visibly change state and gated actions unlock only when intended.

6. Produce a handoff.
   - Include run commands, environment variables, backend requirements, validation results, and known limitations.
   - For community-facing output, frame the work as a reusable CopilotKit workflow UI pattern, with the specific app as the example.

## Implementation Checklist

- Existing workflow is still usable without the copilot.
- Copilot context contains enough state to answer grounded questions.
- Frontend tools are narrow, named clearly, and return useful results.
- Structured UI surfaces reflect real state or tool output.
- Loading, failed, offline, and incomplete states are explicit.
- Approval and export actions have visible before/after state.
- Documentation distinguishes local fallback agents from hosted runtimes.

## Fallbacks

If the backend is unavailable, preserve the app shell and show honest offline or setup guidance. If API keys are missing, keep local inspection, planning, and deterministic UI validation working. If browser automation is unavailable, run build/smoke checks and describe the remaining visual risk.
