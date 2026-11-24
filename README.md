# iOS App Studio

Build Flutter iPhone applications **from Windows**, without owning a Mac.

This repository includes:
- A functional Flutter starter app with dark themed Home and Settings screens.
- GitHub Actions analysis, widget tests, and an **unsigned** iOS build on a macOS runner.
- Codemagic workflows for unsigned builds and signed **TestFlight** releases.
- A Windows PowerShell helper for generating other Flutter apps.
- Consistent iOS bundle ID configuration.

**Start here:** [SETUP.md](SETUP.md)

## Status and caveats
The cloud builds are configured but cannot be considered tested until their first successful runs. An unsigned `Runner.app` is only a compilation artifact, **not** an installable IPA. Apple Developer Program membership, a distribution certificate, a provisioning profile, and App Store Connect access are required to install on iPhones via TestFlight or publish to the Apple App Store.

Never commit signing keys or Apple API credentials. Store them in Codemagic's secure settings.
