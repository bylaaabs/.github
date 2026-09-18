# .github

the defaults of the bylaaabs organisation on github. public.

- `profile/README.md` is the org profile shown at [github.com/bylaaabs](https://github.com/bylaaabs).
- `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md` are the issue and pull request templates every repo inherits when it has none of its own.
- `.github/workflows/` are reusable workflows (`on: workflow_call`) the other repos call with `uses: bylaaabs/.github/.github/workflows/<name>.yml@main`.
- `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md` and `CONTRIBUTING.md` are the community files github shows on every repo of the org that lacks its own.

the studio-wide rules live in the handbook ([handbook.laaabs.com](https://handbook.laaabs.com), [bylaaabs/handbook](https://github.com/bylaaabs/handbook)). this repo only holds what github reads from here.
