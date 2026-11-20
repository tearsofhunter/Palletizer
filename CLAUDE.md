# Palletizer — working notes for Claude

## Two artifacts, two jobs

| Role | Artifact | Slug | Capabilities |
|---|---|---|---|
| **Workspace** (owner edits, saved to db) | Palletizer | `799a181b-bda7-4903-babb-ef8486912c2b` | `db`, `user`, `downloads` |
| **Review link** (coworkers, no sign-in) | Palletizer — Review | `a566aeb5-42dc-4386-8229-18c1aabe731f` | **none** |

Review URL to share: https://claude.ai/artifact/MRco3g58NuxaYVAp3tFCy4

### Rule: never declare capabilities on the review copy
Any declared capability (especially `db`) makes claude.ai require a sign-in, and the
link preview turns into the Claude logo instead of a screenshot. The review copy must
stay capability-free. The app detects this automatically and runs in LocalStore mode
(bundled `projects/*.json` + the viewer's own localStorage; export uses a Blob link).

## Refreshing the review copy
1. `db_get` the workspace (`799a…`) at `projects/<id>` and, if it has `edits`/`moves`/
   settings/group changes, merge them into `projects/<id>.json` here.
2. `python3 tools/build.py`
3. `list_files` on `a566…`, then `publish_files` with `index.html`,
   `projects/index.json`, `projects/*.json` (`shared_live: "public"`, mode `replace`).
4. Republish the same files to the workspace too if the app code changed.
5. Commit and push.

## New projects
Input is a Rhino model interpreted by Claude (`tools/geometry/`). Write a new
`projects/<id>.json` (format `palletizer-project` v1), add it to `projects/index.json`,
then publish to both artifacts. The workspace copies new bundled projects into its db on load.

`*.3dm` files stay out of the repo (it is public).
