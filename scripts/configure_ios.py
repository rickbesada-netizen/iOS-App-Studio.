#!/usr/bin/env python3
"""Apply the intended Apple bundle identifier to a generated Flutter iOS project."""
from pathlib import Path
import re

bundle_id = "com.rickbesada.iosappstudio"
project = Path("ios/Runner.xcodeproj/project.pbxproj")
if not project.exists():
    raise SystemExit("Generate the iOS project first: flutter create --platforms=ios .")
original = project.read_text(encoding="utf-8")
updated, matches = re.subn(
    r"(PRODUCT_BUNDLE_IDENTIFIER\s*=\s*)[^;]+(;)",
    lambda match: f"{match.group(1)}{bundle_id}{match.group(2)}",
    original,
)
if matches == 0:
    raise SystemExit("Could not find PRODUCT_BUNDLE_IDENTIFIER in the Xcode project.")
project.write_text(updated, encoding="utf-8")
print(f"Configured {matches} bundle identifier entries as {bundle_id}")
