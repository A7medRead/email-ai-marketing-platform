# Frontend

The frontend is part of the MailPilot project. See the root [README](../README.md)
for setup and [ARCHITECTURE](../ARCHITECTURE.md) for the feature-folder conventions.

For local UI work, run `npm ci && npm run dev` from this directory. Run
`npm run lint` and `npm run build` before shipping frontend changes.

## Keeping page styles isolated

Each route is wrapped in a named `.ui-page-scope--<name>` boundary in
`src/app/App.jsx`. Feature CSS selectors must begin with that scope so a page
rule cannot affect another route. Routes may share a scope when they
intentionally share a stylesheet; otherwise keep scopes separate. Keep
`src/app/styles.css` to browser resets and truly app-wide rules. Shared controls
should use namespaced class names such as `.ui-button` and `.ui-card`.
