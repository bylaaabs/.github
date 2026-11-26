# AGENTS.md

guidance for any agent, or human, working in this repository. the studio-wide rules live in the handbook (bylaaabs/handbook); this file is what applies here.

## laaabs.

five people in madrid making native software, macOS first. the tools are open source, with no telemetry. the studio is `laaabs.` (lowercase, with the dot when it stands alone). products are lowercase too and are never typed in the web: baaar, clipboaaard, taaab, speaaak, caaapture, usaaage, islaaand, haaarness, finaaance.

## rules of the house

- everything lowercase; english only; never an em dash or an en dash, use " - ".
- platforms in this order: macOS, windows, iOS / iPadOS, android.
- rust for cores and services, typescript for web front ends, swift / kotlin / winui only as the native layer on a rust core.
- one repo per product, all its platforms inside; services in their own repo.
- every piece of work has an issue; branches are `<type>/<slug>`; conventional commits; pull requests only, never a push to main; never merge without being asked.
- `map/` is the map of everything and is a submodule here; `service.yaml` at the root describes this repo and must agree with `map/map/services.yaml`.
- `CLAUDE.md` is just `@AGENTS.md`. edit this file, not that one.

## this repository

`bylaaabs/.github` is the public defaults repo of the organisation. github reads it: the org profile, the issue and pull request templates, the community files and the reusable workflows every other repo inherits or calls. it is not a product or a service, so it has no `service.yaml` and no `map/` submodule.

- `profile/` is what github.com/bylaaabs shows, and most of it is drawn: `map/render.py` reads `map/repos.yml`, the wordmarks from bylaaabs/brand and the github api, and writes the header, the buttons, the map, one card per repository (light and dark) and the card list between the `repos` markers of `profile/README.md`. never edit those svgs or that list by hand: change `map/repos.yml` or `map/render.py` and rerun (`pip install -r map/requirements.txt && python3 -B map/render.py`). `.github/workflows/map.yml` redraws it every day and on every push. keep it true: statuses from laaabs.com `src/data/products.ts`, no invented versions or dates.
- a card links to the repo when it is public and to the product's page on laaabs.com while it is not, decided at render time. the renderer only ever asks github for public repositories; `map/repos.yml` lists products and public repos, never another private name. a new public repo must be added there (or under `skip`) or the run fails.
- `.github/ISSUE_TEMPLATE/*.yml` are issue forms (`feature`, `task`, `bug`) plus `config.yml` (blank issues off, contact links). a repo that ships its own templates overrides them.
- `.github/PULL_REQUEST_TEMPLATE.md` keeps exactly three sections: why, what changed, test plan, and a `closes #` line.
- `.github/workflows/*.yml` are reusable workflows (`on: workflow_call`), except `map.yml`, which runs here only. every one starts with a comment that shows how a repo calls it (`uses: bylaaabs/.github/.github/workflows/<name>.yml@main`). no third party actions beyond `actions/*`. a change here runs in every repo that calls it on the next push, so keep them small and backwards compatible; add inputs with defaults rather than renaming them.
- `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` are the org-wide community files. addresses: `security@laaabs.com` for vulnerabilities, `support@laaabs.com` for everything else.
- this repo is public. nothing private goes in it: no hostnames beyond `*.laaabs.com`, no tokens, no internal urls.

checks before a pull request: every yaml parses (`ruby -ryaml -e 'YAML.load_file(ARGV[0])' <file>`), `git grep -nP "\x{2013}|\x{2014}"` finds nothing, and the pull request title passes the same rules as `pr-title.yml`.
