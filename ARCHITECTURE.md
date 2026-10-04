# Application structure

This repository is organized by product capability. A change to one capability
should be easy to locate: its API, business logic, persistence access, schemas,
and domain models live together under the same backend feature. The frontend uses
the same capability boundaries for pages and feature-specific components.

## Backend rules

- `app/features/<feature>/` owns one product capability. `api.py` exposes its
  HTTP surface, `service.py` contains business rules, `repository.py` owns database
  queries, `schemas.py` validates requests/responses, and `model.py` owns its ORM
  entities. Larger features may split a layer into a subpackage.
- Features may depend on shared `app/core/` and `app/infrastructure/` modules and
  on another feature's public service/schema/model interface. Avoid importing a
  feature's repository from unrelated features.
- `app/core/` is for cross-feature security, configuration, dependencies, and
  errors. `app/infrastructure/` owns database/session and external integrations.
- `app/workers/` contains long-running processes. Worker entrypoints call feature
  services; HTTP startup must not start a scheduler or mutate the schema.
- Alembic remains the sole owner of schema changes. `app/main.py` only composes
  routers and middleware. `app/features/model_registry.py` imports ORM models so
  SQLAlchemy relationships register consistently for the API and migrations.

## Frontend rules

- `src/app/` owns the router and application-wide providers/styles.
- `src/features/<feature>/` owns feature pages and feature-only components.
- `src/shared/` owns reusable UI, API transport, hooks, utilities, and shared assets.
- `src/layouts/` owns authenticated application chrome and route guards.
- Keep pages focused on composing screens. Move reusable stateful UI and API
  operations into feature components/hooks/services as they become complex.
- Every route is wrapped in a `ui-page-scope--<name>` boundary in `app/App.jsx`.
  Feature CSS selectors must be prefixed with that page scope so styles cannot
  affect another route. When a stylesheet is intentionally shared by related
  routes, give those routes one shared scope and document that relationship.
- Keep `app/styles.css` limited to deliberate browser resets and app-wide base
  rules. Do not add global element styling (`h1`, `p`, `button`, etc.) there;
  define it in the route scope or in a namespaced shared component.
- Shared UI styles must use component-specific class names such as `ui-button`
  and `ui-card`. Avoid generic selectors that can match feature markup.
- Load route pages with `React.lazy` and place their routes under one
  `Suspense` boundary. Import heavy libraries (charts, rich-text editors, etc.)
  from the feature that uses them so visitors download them only on those routes.

## Change workflow

1. Put new behavior in the owning feature; keep public URLs and response shapes
   stable unless an API change is intentional.
2. Add database changes through Alembic and update the owning model/schema.
3. Keep cross-feature dependencies one-way where practical; put genuinely shared
   contracts in `app/core` or `src/shared` instead of creating circular imports.
4. Run backend import/compile checks and frontend lint/build before deployment.

Legacy snapshots and scratch fixtures belong in `archive/`, not in runtime source
folders. Runtime data (`.env`, SQLite database, uploads, and backups) stays outside
source control and is not part of feature modules.
