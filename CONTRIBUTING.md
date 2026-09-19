# contributing

how work happens in the bylaaabs organisation. the studio-wide rules live in the handbook ([handbook.laaabs.com](https://handbook.laaabs.com)); this is the short version that applies to every repo.

## the shape of things

- one repo per product, with all its platforms inside (`core/`, `mac/`, `ios/`, `android/`, `windows/`). services get a repo each. never a repo per platform.
- rust for every core and every service. typescript only in web front ends. swift, kotlin and winui only as the native layer on a rust core.
- `map/` is a submodule in every repo and is the map of everything; `service.yaml` at the root describes the repo and must agree with `map/map/services.yaml`. ci checks it.
- the instructions for agents and humans are in `AGENTS.md`; `CLAUDE.md` is just `@AGENTS.md`.

## how a change happens

1. **issue first.** every piece of work has an issue in its repo, with the labels the repo defines (type, area, size), a milestone and an assignee. no issue, no work. use the issue forms.
2. **branch.** from `main`, named `<type>/<slug>`: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `spike/`.
3. **commit.** conventional commits, in english, imperative, lowercase subject: `type(scope): subject`. small, logical commits; nothing unrelated bundled in.
4. **pull request.** against `main`, with `## why`, `## what changed` and `## test plan`, and `closes #n` (or `part of #n`). the title is a conventional commit too. build, lint and tests pass before it is ready.
5. **review, then merge.** nobody pushes to `main`; nobody merges their own pull request without a review; nobody force-pushes a shared branch.

keep the issue current while you work: mark it in progress, tick the definition of done as it is met, say where you left it if you stop.

## the writing rules

- everything lowercase, product names included: baaar, haaarness, speaaak, islaaand, clipboaaard, terminaaal. the studio is `laaabs.` with the dot when it stands alone.
- english only.
- never an em dash or an en dash, anywhere: prose, code, comments, commit messages. use " - ".
- platforms always in this order: macOS, windows, iOS / iPadOS, android.
- no invented facts. if you do not know, say "tbd".

## from outside the studio

pull requests from anyone are welcome on the public repos. open an issue first so we can say yes before you spend the time, and follow the rules above. by contributing you agree to the [code of conduct](CODE_OF_CONDUCT.md) and to the licence of the repo.
