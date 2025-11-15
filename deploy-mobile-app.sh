#!/bin/bash
# 🚀 GALION PLATFORM - Mobile App Deployment System
# Automated iOS/Android app building and app store deployment

set -e

echo "📱 GALION PLATFORM - MOBILE APP DEPLOYMENT"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
MOBILE_APP_DIR="./galion-app/mobile"
BUILD_DIR="./mobile-builds"
EXPO_CLI="npx expo-cli@latest"

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if mobile app exists
check_mobile_app() {
    log "Checking mobile app structure..."

    if [ ! -d "$MOBILE_APP_DIR" ]; then
        error "Mobile app directory not found: $MOBILE_APP_DIR"
    fi

    if [ ! -f "$MOBILE_APP_DIR/app.json" ] && [ ! -f "$MOBILE_APP_DIR/app.config.js" ]; then
        warning "Expo/React Native config not found. Creating basic config..."
        create_expo_config
    fi

    if [ ! -f "$MOBILE_APP_DIR/package.json" ]; then
        warning "package.json not found. Creating mobile app package.json..."
        create_mobile_package_json
    fi

    success "Mobile app structure verified"
}

# Create Expo configuration
create_expo_config() {
    log "Creating Expo configuration..."

    cat > "$MOBILE_APP_DIR/app.json" << 'EOF'
{
  "expo": {
    "name": "Galion Voice AI",
    "slug": "galion-voice-ai",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#667eea"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.galion.voiceai",
      "buildNumber": "1.0.0"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#667eea"
      },
      "package": "com.galion.voiceai",
      "versionCode": 1,
      "permissions": [
        "android.permission.RECORD_AUDIO",
        "android.permission.MODIFY_AUDIO_SETTINGS",
        "android.permission.INTERNET",
        "android.permission.ACCESS_NETWORK_STATE"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      [
        "expo-av",
        {
          "microphonePermission": "Allow Galion Voice AI to access your microphone for voice interactions."
        }
      ]
    ],
    "extra": {
      "eas": {
        "projectId": "your-project-id-here"
      }
    }
  }
}
EOF

    success "Expo configuration created"
}

# Create mobile app package.json
create_mobile_package_json() {
    log "Creating mobile app package.json..."

    cat > "$MOBILE_APP_DIR/package.json" << 'EOF'
{
  "name": "galion-voice-ai-mobile",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "eject": "expo eject",
    "build:android": "expo build:android",
    "build:ios": "expo build:ios",
    "submit:android": "expo submit --platform android",
    "submit:ios": "expo submit --platform ios",
    "publish": "expo publish",
    "test": "jest"
  },
  "dependencies": {
    "expo": "~49.0.0",
    "expo-status-bar": "~1.6.0",
    "react": "18.2.0",
    "react-native": "0.72.6",
    "expo-av": "~13.4.1",
    "expo-linear-gradient": "~12.3.0",
    "expo-speech": "~11.3.0",
    "@react-native-async-storage/async-storage": "1.18.2",
    "@expo/vector-icons": "^13.0.0",
    "expo-constants": "~14.4.2",
    "expo-linking": "~5.0.2",
    "expo-router": "2.0.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.14",
    "@types/react-native": "~0.72.3",
    "typescript": "^5.1.3",
    "jest": "^29.2.1",
    "jest-expo": "~49.0.0"
  },
  "jest": {
    "preset": "jest-expo",
    "transformIgnorePatterns": [
      "node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg))"
    ]
  },
  "private": true
}
EOF

    success "Mobile app package.json created"
}

# Setup Expo account and project
setup_expo_account() {
    log "Setting up Expo account and project..."

    # Check if Expo CLI is available
    if ! command -v npx >/dev/null 2>&1; then
        error "npx not found. Please install Node.js first."
    fi

    # Check Expo login status
    if ! npx expo whoami >/dev/null 2>&1; then
        warning "Not logged into Expo. Please run: npx expo login"
        echo ""
        echo "📋 EXPO ACCOUNT SETUP:"
        echo "======================"
        echo "1. Create account at: https://expo.dev/signup"
        echo "2. Run: npx expo login"
        echo "3. Get your access token from: https://expo.dev/settings/access-tokens"
        echo "4. Set EXPO_TOKEN environment variable"
        echo ""
        read -p "Have you completed Expo login? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            warning "Expo login skipped. Some features may not work."
            return 1
        fi
    fi

    success "Expo account configured"
}

# Install mobile app dependencies
install_mobile_dependencies() {
    log "Installing mobile app dependencies..."

    cd "$MOBILE_APP_DIR"

    if [ ! -d "node_modules" ]; then
        npm install
        success "Dependencies installed"
    else
        success "Dependencies already installed"
    fi

    cd - >/dev/null
}

# Create mobile app assets
create_mobile_assets() {
    log "Creating mobile app assets..."

    mkdir -p "$MOBILE_APP_DIR/assets"

    # Create a simple icon placeholder
    cat > "$MOBILE_APP_DIR/assets/icon.png" << 'EOF'
# This would be a PNG icon file
# In a real deployment, you'd have actual icon files
EOF

    cat > "$MOBILE_APP_DIR/assets/splash.png" << 'EOF'
# This would be a PNG splash screen file
# In a real deployment, you'd have actual splash screen files
EOF

    cat > "$MOBILE_APP_DIR/assets/adaptive-icon.png" << 'EOF'
# This would be an Android adaptive icon file
# In a real deployment, you'd have actual icon files
EOF

    success "Mobile app assets created (placeholders)"
}

# Build Android APK
build_android() {
    log "Building Android APK..."

    cd "$MOBILE_APP_DIR"

    # Create build directory
    mkdir -p "../../$BUILD_DIR/android"

    # Build Android APK using Expo
    if [ -n "$EXPO_TOKEN" ]; then
        EXPO_TOKEN="$EXPO_TOKEN" npx expo export --platform android
    else
        npx expo export --platform android
    fi

    # Move build artifacts
    if [ -d "dist" ]; then
        cp -r dist/* "../../$BUILD_DIR/android/"
        success "Android build completed"
    else
        warning "Android build completed but no dist directory found"
    fi

    cd - >/dev/null
}

# Build iOS IPA
build_ios() {
    log "Building iOS IPA..."

    cd "$MOBILE_APP_DIR"

    # Create build directory
    mkdir -p "../../$BUILD_DIR/ios"

    # Build iOS IPA using Expo (requires macOS)
    if [ -n "$EXPO_TOKEN" ]; then
        EXPO_TOKEN="$EXPO_TOKEN" npx expo export --platform ios
    else
        npx expo export --platform ios
    fi

    # Move build artifacts
    if [ -d "dist" ]; then
        cp -r dist/* "../../$BUILD_DIR/ios/"
        success "iOS build completed"
    else
        warning "iOS build completed but no dist directory found"
    fi

    cd - >/dev/null
}

# Submit to app stores
submit_app_stores() {
    log "Preparing app store submissions..."

    echo ""
    echo "📱 APP STORE SUBMISSION REQUIREMENTS:"
    echo "===================================="
    echo ""

    echo "🎯 GOOGLE PLAY STORE (Android):"
    echo "-------------------------------"
    echo "Required files:"
    echo "  • APK or AAB file: $BUILD_DIR/android/"
    echo "  • Screenshots (required): 2-8 screenshots per device type"
    echo "  • Feature graphic: 1024x500px"
    echo "  • Icon: 512x512px"
    echo "  • Privacy policy URL: https://galion.app/privacy"
    echo "  • Store listing details"
    echo ""

    echo "🍎 APP STORE CONNECT (iOS):"
    echo "--------------------------"
    echo "Required files:"
    echo "  • IPA file: $BUILD_DIR/ios/"
    echo "  • Screenshots (required): Multiple sizes for different devices"
    echo "  • App icon: 1024x1024px"
    echo "  • App store icons: Various sizes"
    echo "  • Privacy policy URL: https://galion.app/privacy"
    echo "  • App review information"
    echo "  • TestFlight beta testing setup"
    echo ""

    echo "🔧 SUBMISSION COMMANDS:"
    echo "======================="
    echo ""
    echo "Android (using EAS Build):"
    echo "  cd $MOBILE_APP_DIR"
    echo "  npx eas build --platform android --type archive"
    echo "  npx eas submit --platform android"
    echo ""
    echo "iOS (using EAS Build):"
    echo "  cd $MOBILE_APP_DIR"
    echo "  npx eas build --platform ios --type archive"
    echo "  npx eas submit --platform ios"
    echo ""

    warning "Manual app store submission required. Use the commands above or submit through web interfaces."
}

# Setup OTA updates
setup_ota_updates() {
    log "Setting up Over-The-Air (OTA) updates..."

    # Create OTA update configuration
    cat > "$MOBILE_APP_DIR/ota-config.json" << 'EOF'
{
  "updates": {
    "enabled": true,
    "checkAutomatically": "ON_LOAD",
    "fallbackToCacheTimeout": 0
  },
  "assetBundlePatterns": [
    "**/*"
  ],
  "ios": {
    "bundleIdentifier": "com.galion.voiceai"
  },
  "android": {
    "package": "com.galion.voiceai"
  }
}
EOF

    # Create update script
    cat > update-mobile-app.sh << 'EOF'
#!/bin/bash
# Update mobile app and publish OTA updates

echo "📱 Updating Galion Mobile App..."

cd galion-app/mobile

# Update version
node -e "
const config = require('./app.json');
config.expo.version = require('semver').inc(config.expo.version, 'patch');
config.expo.ios.buildNumber = config.expo.version;
config.expo.android.versionCode = parseInt(config.expo.android.versionCode) + 1;
require('fs').writeFileSync('./app.json', JSON.stringify(config, null, 2));
"

# Publish update
npx expo publish --release-channel production

echo "✅ Mobile app updated and published!"
EOF

    chmod +x update-mobile-app.sh

    success "OTA update system configured"
}

# Create mobile app testing service
setup_mobile_testing() {
    log "Setting up mobile app testing..."

    # Create test configuration
    cat > "$MOBILE_APP_DIR/e2e/jest.config.js" << 'EOF'
module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEnv: ['<rootDir>/setup-tests.js'],
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/?(*.)+(spec|test).js',
    '**/__tests__/**/*.test.ts',
    '**/?(*.)+(spec|test).ts',
  ],
  collectCoverageFrom: [
    '**/*.{js,jsx,ts,tsx}',
    '!**/node_modules/**',
    '!**/coverage/**',
    '!**/*.config.js',
  ],
  coverageReporters: ['html', 'text', 'lcov'],
}
EOF

    # Create test setup file
    cat > "$MOBILE_APP_DIR/e2e/setup-tests.js" << 'EOF'
import 'react-native-gesture-handler/jestSetup'
import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock'

jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage)
jest.mock('expo-av')
jest.mock('expo-linear-gradient')
jest.mock('expo-speech')

// Mock Expo modules
jest.mock('expo-constants', () => ({
  manifest: {
    version: '1.0.0',
  },
}))
EOF

    success "Mobile app testing configured"
}

# Create distribution service
create_distribution_service() {
    log "Setting up mobile app distribution..."

    # Create distribution configuration
    mkdir -p distribution

    cat > distribution/mobile-app-distribution.md << 'EOF'
# 📱 Galion Mobile App Distribution Guide

## Build Commands

### Development Builds
```bash
# Start development server
npm start

# Run on Android emulator/device
npm run android

# Run on iOS simulator/device (macOS only)
npm run ios

# Run on web
npm run web
```

### Production Builds

#### Using Expo Application Services (EAS)
```bash
# Install EAS CLI
npm install -g @expo/eas-cli

# Login to EAS
eas login

# Configure EAS
eas build:configure

# Build for Android
eas build --platform android

# Build for iOS (requires macOS)
eas build --platform ios

# Build both platforms
eas build --platform all
```

#### Manual Expo Builds
```bash
# Build Android APK
expo build:android

# Build iOS IPA
expo build:ios
```

## App Store Submissions

### Google Play Store

1. **Prepare Assets:**
   - APK or AAB file from build
   - Screenshots (2-8 per device type)
   - Feature graphic (1024x500px)
   - App icon (512x512px)
   - Privacy policy URL

2. **Submission Process:**
   - Go to Google Play Console
   - Create new release
   - Upload APK/AAB
   - Fill store listing
   - Submit for review

### Apple App Store

1. **Prepare Assets:**
   - IPA file from build
   - Screenshots (various sizes)
   - App icons (1024x1024px + smaller variants)
   - App store icons
   - Privacy policy

2. **Submission Process:**
   - Use EAS Submit or manual submission
   - Create App Store Connect record
   - Upload build via Transporter or EAS
   - Fill store information
   - Submit for review

## OTA Updates

### Publish Updates
```bash
# Publish update to production
expo publish --release-channel production

# Publish update to staging
expo publish --release-channel staging
```

### Update Configuration
- Updates are automatic for Expo Go users
- Published updates are delivered via Expo's CDN
- Users need to restart app to get updates

## Testing

### Unit Tests
```bash
npm test
```

### E2E Tests
```bash
# Using Detox (requires setup)
npx detox test
```

### Device Testing
- Use Expo Go app for quick testing
- TestFlight for iOS beta testing
- Google Play Beta for Android testing

## Distribution Channels

### Development
- Expo Go app
- Development builds
- Local network testing

### Beta Testing
- TestFlight (iOS)
- Google Play Beta (Android)
- Expo's release channels

### Production
- Apple App Store
- Google Play Store
- Enterprise distribution (optional)

## Version Management

### Version Bumping
```bash
# Patch version
npm version patch

# Minor version
npm version minor

# Major version
npm version major
```

### Build Numbers
- iOS: Increment CFBundleVersion in app.json
- Android: Increment versionCode in app.json

## Environment Configuration

### API Endpoints
```javascript
// Development
API_URL: 'http://localhost:8010'

// Staging
API_URL: 'https://api-staging.galion.app'

// Production
API_URL: 'https://api.galion.app'
```

### Feature Flags
```javascript
// Enable/disable features per environment
FEATURE_VOICE_AI: true
FEATURE_OFFLINE_MODE: false
FEATURE_ANALYTICS: true
```
EOF

    success "Mobile app distribution guide created"
}

# Main deployment function
main() {
    case "${1:-setup}" in
        "setup")
            check_mobile_app
            setup_expo_account
            create_mobile_assets
            install_mobile_dependencies
            setup_mobile_testing
            setup_ota_updates
            create_distribution_service
            success "Mobile app setup completed!"
            ;;
        "build")
            check_mobile_app
            case "${2:-both}" in
                "android")
                    build_android
                    ;;
                "ios")
                    build_ios
                    ;;
                "both")
                    build_android
                    build_ios
                    ;;
            esac
            ;;
        "submit")
            submit_app_stores
            ;;
        "update")
            if [ -f "galion-app/mobile/update-mobile-app.sh" ]; then
                bash galion-app/mobile/update-mobile-app.sh
            else
                error "Update script not found. Run setup first."
            fi
            ;;
        "status")
            echo "📱 MOBILE APP DEPLOYMENT STATUS"
            echo "================================"
            echo ""

            if [ -d "$MOBILE_APP_DIR" ]; then
                echo -e "${GREEN}✅ Mobile app directory: Present${NC}"

                if [ -f "$MOBILE_APP_DIR/package.json" ]; then
                    echo -e "${GREEN}✅ Package.json: Present${NC}"
                else
                    echo -e "${RED}❌ Package.json: Missing${NC}"
                fi

                if [ -f "$MOBILE_APP_DIR/app.json" ]; then
                    echo -e "${GREEN}✅ Expo config: Present${NC}"
                else
                    echo -e "${RED}❌ Expo config: Missing${NC}"
                fi

                if [ -d "$BUILD_DIR" ]; then
                    echo -e "${GREEN}✅ Build directory: Present${NC}"
                    echo "Build artifacts: $(find $BUILD_DIR -name "*.apk" -o -name "*.aab" -o -name "*.ipa" 2>/dev/null | wc -l) files"
                else
                    echo -e "${YELLOW}⚠️  Build directory: Not created${NC}"
                fi
            else
                echo -e "${RED}❌ Mobile app directory: Missing${NC}"
            fi

            echo ""
            echo "📋 Next Steps:"
            echo "1. Run: ./deploy-mobile-app.sh setup"
            echo "2. Run: ./deploy-mobile-app.sh build android"
            echo "3. Run: ./deploy-mobile-app.sh build ios (macOS only)"
            echo "4. Submit to app stores using the distribution guide"
            ;;
        "help"|*)
            echo "Galion Platform Mobile App Deployment"
            echo ""
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Commands:"
            echo "  setup      - Initial mobile app setup and configuration"
            echo "  build      - Build mobile app (android|ios|both)"
            echo "  submit     - Prepare for app store submission"
            echo "  update     - Publish OTA update"
            echo "  status     - Show mobile app deployment status"
            echo "  help       - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 setup"
            echo "  $0 build android"
            echo "  $0 build both"
            echo "  $0 status"
            echo ""
            echo "Requirements:"
            echo "  • Node.js and npm"
            echo "  • Expo CLI account"
            echo "  • For iOS builds: macOS with Xcode"
            echo "  • For app store submission: Developer accounts"
            ;;
    esac
}

# Run main function
main "$@"
