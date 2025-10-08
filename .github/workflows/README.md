# GitHub Actions Workflows

## Available Workflows

### 1. Build APK with EAS (`build-apk.yml`)

Uses Expo Application Services (EAS) to build the APK in the cloud.

**Pros:**
- No local Android setup required
- Handles signing automatically
- Faster builds
- Professional build service

**Cons:**
- Requires Expo account
- Requires EAS CLI setup

**Setup:**
1. Create an Expo account at https://expo.dev
2. Install EAS CLI: `npm install -g eas-cli`
3. Login: `eas login`
4. Configure build: `cd mobile && eas build:configure`
5. Get your Expo token: `eas whoami` then go to https://expo.dev/accounts/[username]/settings/access-tokens
6. Add `EXPO_TOKEN` to GitHub Secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `EXPO_TOKEN`
   - Value: Your Expo access token

**Usage:**
- Automatically triggers on push to `main` when `mobile/**` files change
- Or manually trigger from Actions tab

### 2. Build APK Locally (`build-apk-local.yml`)

Builds the APK directly in GitHub Actions without external services.

**Pros:**
- No external account required
- Free
- Full control over build process

**Cons:**
- Slower builds
- Requires manual signing setup
- More complex configuration

**Setup (Optional - for signed APKs):**

1. Generate a keystore:
   ```bash
   keytool -genkeypair -v -storetype PKCS12 -keystore release.keystore \
     -alias bookstor -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Convert keystore to base64:
   ```bash
   base64 release.keystore > keystore.base64
   ```

3. Add secrets to GitHub:
   - `ANDROID_KEYSTORE_BASE64`: Contents of keystore.base64
   - `ANDROID_KEY_ALIAS`: Your key alias (e.g., "bookstor")
   - `ANDROID_KEYSTORE_PASSWORD`: Your keystore password
   - `ANDROID_KEY_PASSWORD`: Your key password

**Usage:**
- Automatically triggers on push to `main` when `mobile/**` files change
- Or manually trigger from Actions tab
- APK will be available in Actions artifacts

## Recommended Approach

**For Development/Testing:**
Use `build-apk-local.yml` - it's free and doesn't require external accounts.

**For Production:**
Use `build-apk.yml` with EAS - it's more reliable and handles signing automatically.

## Disabling Workflows

To disable a workflow, either:
1. Delete the workflow file
2. Or rename it to `.yml.disabled`

## Downloading Built APKs

### From EAS:
1. Go to https://expo.dev
2. Navigate to your project → Builds
3. Download the APK

### From GitHub Actions:
1. Go to repository → Actions
2. Click on the workflow run
3. Scroll down to "Artifacts"
4. Download the APK

## Creating Releases

To create a release with the APK:

1. Create a git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. The workflow will automatically create a GitHub release with the APK attached

