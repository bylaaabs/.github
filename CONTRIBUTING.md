# contributing

how work happens in the bylaaabs organisation. the studio-wide rules live in the handbook ([handbook.laaabs.com](https://handbook.laaabs.com)); this is the short version that applies to every repo.

## the shape of things

- one repo per product, with all its platforms inside (`core/`, `mac/`, `ios/`, `android/`, `windows/`). services get a repo each. never a repo per platform.
- rust for every core and every service. typescript only in web front ends. swift, kotlin and winui only as the native layer on a rust core.
- `service.yaml` at the root describes the repo for the studio's own map. the `map/` submodule it is checked against is private: you do not need it to build or to open a pull request, `git submodule update` may skip it, and ci checks it on our side.
- the instructions for agents and humans are in `AGENTS.md`; `CLAUDE.md` is just `@AGENTS.md`.

## how a change happens

1. **issue first.** every piece of work has an issue in its repo, opened with the issue forms. inside the studio it also gets the labels the repo defines (type, area, size), a milestone and an assignee; from outside, we add those for you.
2. **branch.** from `main`, named `<type>/<slug>`: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `spike/`.
3. **commit.** conventional commits, in english, imperative, lowercase subject: `type(scope): subject`. small, logical commits; nothing unrelated bundled in.
4. **pull request.** against `main`, with `## why`, `## what changed` and `## test plan`, and `closes #n` (or `part of #n`). the title is a conventional commit too. build, lint and tests pass before it is ready.
5. **review, then merge.** nobody pushes to `main`; nobody merges their own pull request without a review; nobody force-pushes a shared branch.

keep the issue current while you work: mark it in progress, tick the definition of done as it is met, say where you left it if you stop.

## the writing rules

- everything lowercase, product names included: baaar, clipboaaard, taaab, speaaak, caaapture, usaaage, islaaand, haaarness, finaaance. the studio is `laaabs.` with the dot when it stands alone.
- english only.
- never an em dash or an en dash, anywhere: prose, code, comments, commit messages. use " - ".
- platforms always in this order: macOS, windows, iOS / iPadOS, android.
- no invented facts. if you do not know, say "tbd".

## from outside the studio

pull requests from anyone are welcome on the public repos. open an issue first so we can say yes before you spend the time, and follow the rules above. a good first one is [labelled as such](https://github.com/search?q=org%3Abylaaabs+is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22%2C%22good+first+task%22&type=issues). by contributing you agree to the [code of conduct](CODE_OF_CONDUCT.md) and to the licence of the repo: Apache-2.0 for the tools.

found a vulnerability? never in an issue: see [SECURITY.md](SECURITY.md).
