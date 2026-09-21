#!/usr/bin/env bash
# Wrap the pyapp-built "sasview" executable in a minimal SasView6.app bundle.
# If SIGN_IDENTITY is set, codesign the bundle (the identity must be in a keychain).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DIST_DIR="${REPO_ROOT}/tmp/packaging"
APP="${DIST_DIR}/SasView6.app"
EXE="${DIST_DIR}/sasview"
ICON="${REPO_ROOT}/src/sas/qtgui/images/ball.icns"
ENTITLEMENTS="${REPO_ROOT}/build_tools/entitlements.plist"
VERSION="${SASVIEW_VERSION:-$(cd "${REPO_ROOT}" && uv tool run --with hatch-vcs hatchling version)}"

if [[ ! -x "${EXE}" ]]; then
    echo "Expected ${EXE}. Run build_tools/build_pyapp first." >&2
    exit 1
fi

rm -rf "${APP}"
mkdir -p "${APP}/Contents/MacOS" "${APP}/Contents/Resources"
cp "${EXE}" "${APP}/Contents/MacOS/sasview"
cp "${ICON}" "${APP}/Contents/Resources/ball.icns"

cat > "${APP}/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>SasView6</string>
    <key>CFBundleDisplayName</key><string>SasView6</string>
    <key>CFBundleIdentifier</key><string>org.sasview.SasView6</string>
    <key>CFBundleExecutable</key><string>sasview</string>
    <key>CFBundleIconFile</key><string>ball.icns</string>
    <key>CFBundlePackageType</key><string>APPL</string>
    <key>CFBundleShortVersionString</key><string>${VERSION}</string>
    <key>CFBundleVersion</key><string>${VERSION}</string>
    <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

# The Python runtime is a compressed payload inside the executable, unpacked at
# first run, so the launcher is the only Mach-O in the bundle to sign.
if [[ -n "${SIGN_IDENTITY:-}" ]]; then
    codesign --force --timestamp --options=runtime \
        --entitlements "${ENTITLEMENTS}" \
        --sign "${SIGN_IDENTITY}" "${APP}"
    codesign --verify --strict --verbose=2 "${APP}"
fi

echo "Created ${APP}"
