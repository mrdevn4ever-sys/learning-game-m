#!/usr/bin/env bash
set -euo pipefail
export DEVELOPER_DIR=/Applications/Xcode_27.2.app/Contents/Developer
xcodebuild -version
sdk="$(xcrun --sdk iphonesimulator --show-sdk-version)"
[[ "$sdk" == 27.* ]] || { printf '%s\n' 'Unerwartetes iPad-SDK'; exit 1; }
work="${RUNNER_TEMP:?}/chnobel-native"
mkdir -p "$work"
# Runner-private outputs only: never upload artifacts from the public repository.
swift test --package-path produkt/Packages --xunit-output "$work/swift.xml"
python produkt/werkzeuge/ci/native_evidence.py xunit "$work/swift.xml"
xcrun simctl list devices available -j > "$work/simulators.json"
udid="$(python produkt/werkzeuge/ci/native_evidence.py simulator "$work/simulators.json" --sdk "$sdk")"
xcodebuild -project produkt/App/Chnobel.xcodeproj -scheme Chnobel   -destination "id=$udid" -derivedDataPath "$work/DerivedData"   -resultBundlePath "$work/UI.xcresult" CODE_SIGNING_ALLOWED=NO   -parallel-testing-enabled NO test
xcrun xcresulttool get test-results summary --path "$work/UI.xcresult" > "$work/ui-summary.json"
python produkt/werkzeuge/ci/native_evidence.py xcresult "$work/ui-summary.json"
xcodebuild -project produkt/App/Chnobel.xcodeproj -scheme Chnobel   -configuration Release -destination 'generic/platform=iOS Simulator'   -derivedDataPath "$work/ReleaseDerivedData" CODE_SIGNING_ALLOWED=NO build
