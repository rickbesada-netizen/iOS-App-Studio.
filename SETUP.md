# Setup: build iPhone apps from Windows

## What this is
A complete Flutter starter application and automated unsigned iOS build.
**This is not a Mac emulator.** The iOS build takes place on a real macOS runner.
The unsigned Runner.app from GitHub Actions is **not installable** on a normal iPhone. For that, configure Apple signing and TestFlight.

## 1. Verify the automatic cloud build
Open the GitHub repository > **Actions** > **Build and check iOS (unsigned)**.
The workflow runs on pushes to main. You can also select **Run workflow**.
After success, open the run > **Artifacts** > **ios-unsigned-runner**.

## 2. Edit on Windows
Install Flutter SDK, Git, and VS Code (Flutter/Dart extensions) on Windows.
Clone the repository. Use `flutter pub get` and `flutter run -d windows` only if you generate Windows platform files with:
`flutter create --platforms=windows .`.
You can also use an Android device/emulator for fast local preview:
`flutter create --platforms=android .` and `flutter run`.
Edit `lib/main.dart`; push to GitHub to compile for iOS automatically.
No Mac required for editing, Dart analysis, testing, or Android testing.

## 3. Connect Codemagic
In Codemagic, sign in with GitHub, authorise access to this repository, add it as an app,
and select `codemagic.yaml`. Choose the **ios-unsigned** workflow first.
The macOS builder runs Flutter and compiles the application.

## 4. Set up App Store Connect / TestFlight (requires Apple Developer membership)
1. Enrol in Apple Developer Program (paid membership).
2. In Apple Developer, register the bundle identifier `com.rickbesada.iosappstudio`.
3. In App Store Connect, create the corresponding application record.
4. Create an App Store Connect API key with suitable permissions, and add it **in Codemagic's integration settings**, not to GitHub.
5. Name the Codemagic integration `apple-app-store`, or change the name in `codemagic.yaml` to match yours.
6. In Codemagic iOS code signing, obtain/upload an Apple Distribution certificate and an App Store provisioning profile for this bundle ID.
7. Run the `ios-testflight` workflow, which compiles a signed IPA and submits it to TestFlight.
8. Test on an iPhone with TestFlight, finish App Store Connect metadata, privacy disclosures, screenshots, and submit for Apple review.

**Important:** App Store submission is not automatic approval. Apple reviews each app. Sensitive certificates and API keys must stay in Codemagic secret storage, never in the repository.

## 5. Make more apps
Treat this repository as a **starter template** and create one repository per production app, with its own bundle ID, App Store record, signing profile and Codemagic app connection.
On Windows, use `scripts/new_app.ps1` as a convenience for generating another Flutter project locally.
Update the bundle ID in `codemagic.yaml`, your project name in build commands, and your iOS display name before shipping each new app.

## Known limitations
- Generated iOS files are excluded from Git; the cloud runner regenerates them for each build.
- This starter app is an example interface, not a finished App Store product.
- Settings toggles are illustrative and aren't persisted.
- Real iPhone testing requires access to an iPhone and signed TestFlight distribution.
- GitHub Actions macOS runner usage and Codemagic cloud builds may incur charges after their allowances.
- Before publishing, replace the default app name, bundle ID, icons and sample content.
