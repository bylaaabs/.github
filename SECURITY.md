# Security policy

This document is the default security policy for the [laaabs.](https://laaabs.com) studio. Individual products may publish their own `SECURITY.md` with a more specific threat model; this one applies whenever a repo doesn't.

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Two channels:

1. **Email** `oss@laaabs.com` with subject `SECURITY: <product> - <short summary>`.
2. **GitHub private advisory** on the affected repo: `https://github.com/bylaaabs/<repo>/security/advisories/new`.

Include:

- A description of the vulnerability and potential impact.
- Steps to reproduce (product version, macOS/iOS version, relevant logs).
- Suggested fix if you have one.
- Whether you'd like public credit after the fix ships.

## Response timeline

1. Acknowledgement within **48 hours**.
2. Validation within **7 days**. If false-positive, we explain and close.
3. Fix and patched release as fast as reasonably possible. Disclosure date coordinated with the reporter for credited reports.
4. Credit in release notes if desired.

We never ask reporters for an NDA. We never delay disclosure to manage PR - only to ship a fix.

## Hardening principles we follow

- No secrets in repositories. `.gitignore` covers `*.p12`, `*.mobileprovision`, signing keys, `.env`.
- Dependencies audited on add. Every Swift / npm dependency is licence-checked and version-pinned.
- Minimal entitlements. Only what each target strictly needs.
- Hardened Runtime + notarisation on every direct-distribution macOS build.
- No runtime code loading. No `dlopen`, no bundle loading from user paths.
- Logging never includes user content. Only metadata.

## Hall of fame

Researchers who responsibly disclose will be listed in the affected product's `SECURITY.md` (with their permission) as fixes ship.
