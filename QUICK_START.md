# AI Fit Check iOS - Quick Start Guide

## 5-Minute Setup

### Step 1: Create Xcode Project (2 min)
```bash
# Create new iOS App
# Name: AIFitCheck
# Organization: com (or your domain)
# Bundle ID: com.aifitcheck
# Interface: SwiftUI
# Lifecycle: SwiftUI App
# Minimum Deployment: iOS 16.0
```

### Step 2: Add Files (2 min)
Copy all Swift files to your Xcode project maintaining this structure:
```
Sources/
  App/AIFitCheckApp.swift
  Models/AppModels.swift
  Services/APIService.swift
  Services/ImageProcessor.swift
  Views/HomeView.swift
  Views/TryOnView.swift
  Views/WardrobeView.swift
  Views/ProfileView.swift
  Utilities/Extensions.swift
```

### Step 3: Configure Capabilities (1 min)
1. Select project in Xcode
2. Select AIFitCheck target
3. Signing & Capabilities tab
4. + Capability → App Groups
5. Add: `group.com.aifitcheck.shared`

## Creating Share Extension

### Step 4: Add Extension Target (3 min)

**File → New → Target**
- Select "Share Extension"
- Name: `AIFitCheckShare`
- Team: Same as main app
- Bundle ID: `com.aifitcheck.shareextension`

**Configure Extension:**
1. Signing & Capabilities tab
2. Add App Groups: `group.com.aifitcheck.shared`
3. Minimum Deployment: iOS 16.0

**Replace Extension Files:**
- Delete `ShareViewController.swift`
- Copy our `ShareViewController.swift` to extension folder
- Copy `ShareExtensionView.swift` to extension folder
- Copy `Info.plist` to extension folder

**Storyboard Setup:**
- Keep `MainInterface.storyboard`
- Set Custom Class to `ShareViewController`
- Delete default UI (will use code-based UI)

## Build & Run

### Build the App
```bash
# Xcode menu → Product → Build
# Or: Cmd + B
```

### Run on Simulator
```bash
# Xcode menu → Product → Run
# Or: Cmd + R
# Select iOS 16+ simulator
```

### Test Share Extension
1. Open Photos app on simulator
2. Select any photo
3. Tap Share
4. Scroll right in share sheet
5. Look for "AI Fit Check"
6. Tap it!

## First Test Flow

### Main App
1. **Home Tab**: See welcome + guide
2. **Profile Tab**: Upload a selfie
3. **Home Tab**: Quick try-on with a clothing image
4. **Wardrobe Tab**: See saved results

### Share Extension
1. Open Photos app
2. Select clothing image
3. Tap Share → "AI Fit Check"
4. Tap "Try On"
5. See result
6. Tap "Save to Wardrobe"
7. Check Wardrobe tab - should see it!

## Configure Backend Server

### Default (Development)
```
http://localhost:8000
```

### Change in App
1. Open app → Profile tab
2. Scroll down to Settings
3. Enter new Server URL
4. Tap checkmark

### API Endpoints Needed
Your backend must support:
```
POST /api/tryon
POST /api/person-image
```

See `API_INTEGRATION.md` for full spec

## Common Issues & Fixes

### Share Extension Not Appearing?
```
✓ Check App Groups are identical in both targets
✓ Both targets must have group.com.aifitcheck.shared
✓ Rebuild project (Cmd + Shift + K, then Cmd + B)
✓ Restart simulator
```

### Data Not Syncing?
```
✓ Verify UserDefaults uses suiteName: "group.com.aifitcheck.shared"
✓ Check both targets have entitlements file with app groups
✓ Main app must be installed first before extension works
```

### Images Not Uploading?
```
✓ Verify server URL in Profile settings
✓ Check backend is running on http://localhost:8000
✓ Try IP address instead: http://127.0.0.1:8000
✓ On physical device: http://your-computer-ip:8000
```

### API Calls Timing Out?
```
✓ Increase timeout in APIService (default: system default ~60s)
✓ Check network connectivity
✓ Verify backend API is responding (test with curl/Postman)
```

## Project Structure at a Glance

```
Your Xcode Project
├── Main App Target (AIFitCheck)
│   ├── App/AIFitCheckApp.swift
│   ├── Models/AppModels.swift
│   ├── Services/(API, ImageProcessor)
│   ├── Views/(Home, TryOn, Wardrobe, Profile)
│   └── Utilities/Extensions.swift
│
└── Share Extension Target (AIFitCheckShare)
    ├── ShareViewController.swift
    ├── ShareExtensionView.swift
    ├── Info.plist
    ├── MainInterface.storyboard (keep)
    └── Assets/
```

## File Count

- **Swift Files**: 8
- **Models**: 1 file (4 data structures)
- **Services**: 2 files (API, Image processing)
- **Views**: 4 files (Home, TryOn, Wardrobe, Profile)
- **Extension**: 2 files + 1 Info.plist
- **Documentation**: 4 files

**Total**: ~3,200 lines of production code

## Key Features Checklist

### Main App
- [x] Three-tab navigation (Home, Wardrobe, Profile)
- [x] User profile photo upload
- [x] Server URL configuration
- [x] Photo library image picker
- [x] Try-on API integration
- [x] Wardrobe grid gallery
- [x] Delete from wardrobe
- [x] Error handling & loading states
- [x] Dark theme with purple accent

### Share Extension
- [x] Appears in system share sheet
- [x] Receives images from any app
- [x] Try-on functionality
- [x] Save to wardrobe
- [x] Loading states
- [x] Error handling
- [x] App Group data sharing
- [x] Compact card-based UI

### Services
- [x] Async/await API calls
- [x] Image optimization (resize, compress)
- [x] Base64 encoding/decoding
- [x] Thread-safe actor pattern
- [x] Error handling with custom enum
- [x] Local wardrobe persistence

## Environment Variables

Optional - not required, but useful for testing:

```bash
# In ProductionConfiguration.xcconfig (optional)
SERVER_URL = http://localhost:8000
APP_GROUP = group.com.aifitcheck.shared
BUNDLE_ID = com.aifitcheck
```

## Testing Checklist

Run through these before deploying:

```
✓ App launches without crashes
✓ All three tabs are accessible
✓ Can upload profile photo
✓ Can pick clothing image
✓ Wardrobe shows saved items
✓ Share extension appears in share sheet
✓ Can try on from extension
✓ Can save from extension
✓ Wardrobe syncs between app/extension
✓ Error messages are clear
✓ Loading states work
✓ Server URL can be changed
✓ Works on iPhone 14+ simulator
✓ Dark mode looks good
✓ No console warnings/errors
```

## Next Steps

### Short Term
1. ✓ Get app running
2. ✓ Get share extension working
3. ✓ Test with your backend API
4. ✓ Test on physical device

### Medium Term
1. Add cloud sync for wardrobe
2. Implement user authentication
3. Add wardrobe filters/search
4. Add sharing between users
5. Add analytics

### Long Term
1. AR try-on preview
2. Video support
3. Multiple items at once
4. AI style recommendations
5. Social features

## Documentation Files

For deeper understanding, read in this order:

1. **FILE_STRUCTURE.md** - Line-by-line breakdown
2. **SETUP_GUIDE.md** - Detailed Xcode setup
3. **API_INTEGRATION.md** - Backend integration
4. **README.md** - General overview

## Support Resources

- Apple SwiftUI Docs: https://developer.apple.com/xcode/swiftui/
- Share Extension Guide: https://developer.apple.com/documentation/uikit/share_extension
- URLSession Async: https://developer.apple.com/documentation/foundation/urlsession

## Customization Quick Tips

### Change Brand Color
Edit `Extensions.swift`:
```swift
static let appPurple = Color(red: 0.49, green: 0.23, blue: 0.93)
// Change RGB values to your color
```

### Change App Name
In Xcode: Targets → General → Display Name

### Change Server URL
In APIService.swift:
```swift
@AppStorage("serverURL") private var serverURLString = "https://your-api.com"
```

### Change App Group
1. Find all instances of `"group.com.aifitcheck.shared"`
2. Replace with your group ID
3. Update in Xcode Capabilities for both targets

## Performance Tips

The app is optimized for:
- **Image Upload**: Automatic resize + compression
- **Memory**: Base64 only during API calls, then discarded
- **Bandwidth**: ~500-700KB per try-on
- **Battery**: Efficient async/await, no background tasks
- **Responsive UI**: Proper loading states

## Production Checklist

Before uploading to App Store:

```
Code Quality
✓ No console warnings
✓ Remove DEBUG code blocks
✓ Use HTTPS for server URL
✓ Update API error messages

Configuration
✓ Update bundle IDs
✓ Update provisioning profiles
✓ Remove localhost exceptions
✓ Enable code signing

Testing
✓ Test on multiple devices
✓ Test on iOS 16+ versions
✓ Test all error scenarios
✓ Test wardrobe sync

Privacy
✓ Privacy Policy updated
✓ Photo Library permissions explained
✓ Camera permissions explained
```

## That's It!

You now have:
- ✅ Complete iOS app with SwiftUI
- ✅ Share Extension for quick access
- ✅ API integration ready to use
- ✅ Professional dark theme
- ✅ Production-ready code
- ✅ Comprehensive documentation

**Happy coding! 🚀**
