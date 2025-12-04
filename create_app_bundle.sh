#!/bin/bash
# PDF Compare Tool - macOS App Launcher
# Creates an executable app bundle for easier launching on macOS

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$SCRIPT_DIR/PDF Compare.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"

# Create app bundle structure
mkdir -p "$MACOS_DIR"

# Create launcher script
cat > "$MACOS_DIR/pdf-compare" << 'EOF'
#!/bin/bash
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
cd "$APP_DIR"
exec bash run.sh
EOF

chmod +x "$MACOS_DIR/pdf-compare"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>pdf-compare</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.pdf-compare</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>PDF Compare</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
EOF

echo "Created: $APP_DIR"
echo "You can now launch PDF Compare from Applications or Finder"
