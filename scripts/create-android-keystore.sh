#!/bin/bash

# Script to create Android signing keystore for Bookstor

set -e

echo "=========================================="
echo "Bookstor Android Keystore Generator"
echo "=========================================="
echo ""

# Check if Java is installed
if ! command -v keytool &> /dev/null; then
    echo "❌ Error: Java is not installed or keytool is not in PATH"
    echo ""
    echo "Please install Java first:"
    echo ""
    echo "On macOS with Homebrew:"
    echo "  brew install openjdk@17"
    echo "  sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk"
    echo ""
    echo "Or download from: https://www.oracle.com/java/technologies/downloads/"
    echo ""
    exit 1
fi

echo "✅ Java is installed"
java -version
echo ""

# Create secure directory for keystore
KEYSTORE_DIR="$HOME/.android-keys"
KEYSTORE_FILE="$KEYSTORE_DIR/bookstor-release.keystore"
BASE64_FILE="$HOME/bookstor-keystore.base64"

mkdir -p "$KEYSTORE_DIR"

# Check if keystore already exists
if [ -f "$KEYSTORE_FILE" ]; then
    echo "⚠️  Warning: Keystore already exists at $KEYSTORE_FILE"
    read -p "Do you want to overwrite it? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Cancelled. Existing keystore preserved."
        exit 0
    fi
    rm "$KEYSTORE_FILE"
fi

echo "Creating Android signing keystore..."
echo ""
echo "You'll be prompted for:"
echo "  1. Keystore password (choose a strong password!)"
echo "  2. Your name and organization details"
echo "  3. Key password (press Enter to use same as keystore password)"
echo ""
echo "⚠️  IMPORTANT: Remember your password! You'll need it for every app update."
echo ""

# Generate keystore
keytool -genkeypair -v -storetype PKCS12 \
  -keystore "$KEYSTORE_FILE" \
  -alias bookstor \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Set restrictive permissions
chmod 600 "$KEYSTORE_FILE"

echo ""
echo "✅ Keystore created successfully!"
echo ""
echo "Location: $KEYSTORE_FILE"
echo ""

# Convert to base64 for GitHub Secrets
echo "Converting to base64 for GitHub Secrets..."
base64 -i "$KEYSTORE_FILE" -o "$BASE64_FILE"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add these secrets to GitHub:"
echo "   Go to: https://github.com/RovxBot/Bookstor/settings/secrets/actions"
echo ""
echo "   Secret 1: ANDROID_KEYSTORE_BASE64"
echo "   Value: Copy from this file:"
echo "   $ cat $BASE64_FILE"
echo ""
echo "   Secret 2: ANDROID_KEY_ALIAS"
echo "   Value: bookstor"
echo ""
echo "   Secret 3: ANDROID_KEYSTORE_PASSWORD"
echo "   Value: [The password you just entered]"
echo ""
echo "   Secret 4: ANDROID_KEY_PASSWORD"
echo "   Value: [Same as keystore password]"
echo ""
echo "2. Clean up the base64 file after adding to GitHub:"
echo "   $ rm $BASE64_FILE"
echo ""
echo "3. Backup your keystore to a secure location:"
echo "   $ cp $KEYSTORE_FILE /path/to/secure/backup/"
echo ""
echo "⚠️  NEVER lose this keystore or password!"
echo "   Without it, you cannot update your app on Google Play Store."
echo ""

