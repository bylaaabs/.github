# security policy

the default security policy of laaabs. it applies to every repo of the bylaaabs organisation that has no `SECURITY.md` of its own; a product may publish a more specific one.

## what to report

anything that lets someone read, change or run what they should not: in a product (baaar, haaarness, speaaak, islaaand, clipboaaard, terminaaal), in a service (`*.laaabs.com`) or in this organisation's repos and releases. examples: a way to run code, to read another person's data, to bypass signing or notarisation, a leaked secret, a dependency with a known vulnerability we ship.

**never in a public issue, discussion or pull request.**

## how to report

- email `security@laaabs.com`, subject `security: <repo> - <short summary>`.
- or open a private advisory on the affected repo: `https://github.com/bylaaabs/<repo>/security/advisories/new`.

include what you can: what it is and what it lets an attacker do, how to reproduce it (product version, platform - macOS, windows, iOS / iPadOS or android - and its version, logs), a fix if you have one, and whether you want to be credited when the fix ships.

## what to expect

1. an acknowledgement within 48 hours.
2. a verdict within 7 days: confirmed, or an explanation of why not.
3. a fix and a release as fast as we reasonably can; the disclosure date agreed with you.
4. credit in the release notes if you want it.

we never ask for an nda. we never delay a disclosure for anything but shipping the fix.

## no bounty yet

there is no bug bounty for now. we say thank you, we credit you, and we fix it.

## how we build

- no secrets in repos: `.gitignore` covers keys, certificates, provisioning profiles and `.env`.
- dependencies are intentional, licence-checked and version-pinned; audited when added.
- minimal entitlements and permissions; only what each target needs.
- hardened runtime and notarisation on every macOS build we distribute ourselves; signed builds on every platform.
- no runtime code loading, no plugins from user paths.
- no telemetry. logs never contain user content.
