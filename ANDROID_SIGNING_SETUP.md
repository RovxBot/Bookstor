# Android APK Signing Setup

This guide will help you create a signing certificate for building signed Android APKs.

## Prerequisites

You need Java Development Kit (JDK) installed.

### Install Java on macOS

**Option 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Java
brew install openjdk@17

# Link it so it's available system-wide
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

**Option 2: Download from Oracle**
1. Go to https://www.oracle.com/java/technologies/downloads/
2. Download Java 17 or later for macOS
3. Install the .dmg file

**Verify installation:**
```bash
java -version
```

## Step 1: Generate Keystore

Once Java is installed, run this command:

```bash
keytool -genkeypair -v -storetype PKCS12 \
  -keystore bookstor-release.keystore \
  -alias bookstor \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

**You'll be prompted for:**

1. **Keystore password** - Choose a strong password (you'll need this!)
2. **Key password** - Press Enter to use the same password as keystore
3. **First and last name** - Your name or "Bookstor"
4. **Organizational unit** - Can leave blank or put "Development"
5. **Organization** - Can leave blank or put your name
6. **City/Locality** - Your city
7. **State/Province** - Your state
8. **Country code** - Two letter code (e.g., AU, US, GB)

**Example:**
```
Enter keystore password: MySecurePassword123!
Re-enter new password: MySecurePassword123!
What is your first and last name?
  [Unknown]:  Sam Cooke
What is the name of your organizational unit?
  [Unknown]:  Development
What is the name of your organization?
  [Unknown]:  Bookstor
What is the name of your City or Locality?
  [Unknown]:  Sydney
What is the name of your State or Province?
  [Unknown]:  NSW
What is the two-letter country code for this unit?
  [Unknown]:  AU
Is CN=Sam Cooke, OU=Development, O=Bookstor, L=Sydney, ST=NSW, C=AU correct?
  [no]:  yes

Enter key password for <bookstor>
	(RETURN if same as keystore password):  [Press Enter]
```

This will create a file called `bookstor-release.keystore` in your current directory.

## Step 2: Secure Your Keystore

**IMPORTANT:** Keep this file safe and NEVER commit it to git!

```bash
# Move it to a secure location
mkdir -p ~/.android-keys
mv bookstor-release.keystore ~/.android-keys/

# Set restrictive permissions
chmod 600 ~/.android-keys/bookstor-release.keystore
```

The keystore is already in `.gitignore` so it won't be committed.

## Step 3: Convert to Base64 (for GitHub Secrets)

```bash
base64 -i ~/.android-keys/bookstor-release.keystore -o ~/bookstor-keystore.base64
```

This creates a base64-encoded version that you can safely store in GitHub Secrets.

## Step 4: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these four secrets:

### Secret 1: ANDROID_KEYSTORE_BASE64
- **Name:** `ANDROID_KEYSTORE_BASE64`
- **Value:** Contents of `~/bookstor-keystore.base64`
  ```bash
  cat ~/bookstor-keystore.base64
  ```
  Copy and paste the entire output

### Secret 2: ANDROID_KEY_ALIAS
- **Name:** `ANDROID_KEY_ALIAS`
- **Value:** `bookstor`

### Secret 3: ANDROID_KEYSTORE_PASSWORD
- **Name:** `ANDROID_KEYSTORE_PASSWORD`
- **Value:** The password you entered when creating the keystore

### Secret 4: ANDROID_KEY_PASSWORD
- **Name:** `ANDROID_KEY_PASSWORD`
- **Value:** Same as keystore password (if you pressed Enter when prompted)

## Step 5: Test the Workflow

1. Make a small change to any file in `mobile/`
2. Commit and push:
   ```bash
   git add mobile/
   git commit -m "Test Android build"
   git push
   ```
3. Go to **Actions** tab on GitHub
4. Watch the "Build Android APK (Local)" workflow run
5. Once complete, download the signed APK from Artifacts

## Step 6: Clean Up

```bash
# Remove the base64 file (you don't need it anymore)
rm ~/bookstor-keystore.base64
```

## Important Notes

### Keep These Safe:
- ✅ `~/.android-keys/bookstor-release.keystore` - Your keystore file
- ✅ Your keystore password
- ✅ Your key alias (`bookstor`)

### If You Lose These:
- ❌ You cannot update your app on Google Play Store
- ❌ You'll need to create a new keystore and release as a new app
- ❌ Users will need to uninstall and reinstall

### Backup Your Keystore:
```bash
# Backup to encrypted USB drive or cloud storage
cp ~/.android-keys/bookstor-release.keystore /path/to/secure/backup/
```

## Troubleshooting

### "keytool: command not found"
Java is not installed or not in PATH. Follow the Java installation steps above.

### "Keystore was tampered with, or password was incorrect"
You entered the wrong password. Try again with the correct password.

### GitHub Actions fails with "apksigner: command not found"
The workflow will automatically install Android SDK tools. If it fails, check the Actions logs.

### APK won't install on device
Make sure you've enabled "Install from Unknown Sources" in your Android settings.

## Verifying Your Signed APK

After downloading the APK from GitHub Actions:

```bash
# Check the signature
jarsigner -verify -verbose -certs your-app.apk

# Should show "jar verified"
```

## Next Steps

Once your keystore is set up and secrets are added to GitHub:

1. The workflow will automatically build signed APKs
2. Download from Actions → Artifacts
3. Install on your Android device
4. When ready for production, use the same keystore for Google Play Store

---

**Remember:** Keep your keystore and passwords safe! You'll need them for every app update.

