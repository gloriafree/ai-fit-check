# AI Fit Check iOS - Setup Guide

## Quick Start

### 1. Create Xcode Project

```bash
# Create a new iOS app project
# Name: AIFitCheck
# Org Identifier: com.aifitcheck (or your domain)
# Interface: SwiftUI
# Lifecycle: SwiftUI App
# Target: iOS 16.0+
```

### 2. File Structure Setup

Copy all files from the AIFitCheck directory maintaining this structure:

```
AIFitCheck/
├── App/
│   └── AIFitCheckApp.swift
├── Models/
│   └── AppModels.swift
├── Services/
│   ├── APIService.swift
│   └── ImageProcessor.swift
├── Views/
│   ├── HomeView.swift
│   ├── TryOnView.swift
│   ├── WardrobeView.swift
│   └── ProfileView.swift
├── ShareExtension/
│   ├── ShareViewController.swift
│   ├── ShareExtensionView.swift
│   └── Info.plist
└── (Build folder with generated files)
```

### 3. Main App Configuration

**Signing & Capabilities:**
1. Select AIFitCheck target
2. Go to Signing & Capabilities tab
3. Add Capability: **App Groups**
4. Add group: `group.com.aifitcheck.shared`

**Info.plist additions:**
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### 4. Create Share Extension Target

**In Xcode:**

1. File → New → Target
2. Select "Share Extension"
3. Name it: `AIFitCheckShare`
4. Team & Organization: Same as main app
5. Bundle Identifier: `com.aifitcheck.shareextension`

**Configure Extension:**

1. Select AIFitCheckShare target
2. Go to Signing & Capabilities
3. Add Capability: **App Groups**
4. Add group: `group.com.aifitcheck.shared`
5. General tab → Minimum Deployments: iOS 16.0

**Replace Extension Files:**

Delete the default files Xcode creates and add:
- `ShareViewController.swift` (replaces ShareViewController.swift)
- `ShareExtensionView.swift` (new file)
- Keep the generated `MainInterface.storyboard` but modify as below

### 5. ShareExtension Storyboard Setup

The `MainInterface.storyboard` should have:

1. View Controller Scene
   - Class: `ShareViewController`
   - Module: Leave blank
2. Delete the default view
3. Set root view controller to our ShareViewController

Alternatively, use code-only approach by modifying Info.plist:
```xml
<!-- Remove NSExtensionMainStoryboard -->
<!-- Add in NSExtension:
     NSExtensionPrincipalClass: AIFitCheckShare.ShareViewController
-->
```

### 6. Build Phases Configuration

**Main App Target:**
- Link Binary with Libraries: Add any external frameworks if needed
- Copy Bundle Resources: Ensure any assets are included

**Share Extension Target:**
- Link Binary with Libraries: (should be minimal)
- Ensure the extension can access App Groups

### 7. Scheme Configuration

1. Create a scheme for testing both targets:
   - Edit Scheme (main app)
   - Build tab → Add AIFitCheckShare as a dependency
   - This ensures extension is built with the app

### 8. Backend Configuration

**Default Server URL:** `http://localhost:8000`

Change in app by going to Profile → Settings → Server URL

**API Endpoints Required:**

```
POST /api/tryon
POST /api/person-image
```

See AppModels.swift for request/response format.

### 9. Testing the Share Extension

1. Build & run the main app on iOS 16+ device/simulator
2. Open any app (Photos, Safari, etc.)
3. Share an image
4. Look for "AI Fit Check" in the share sheet
5. Extension should appear and be functional

### 10. Provisioning Profile Settings

If using real device:

1. Register device UDID with Apple Developer
2. Update provisioning profiles
3. Ensure both targets have valid signing certificates
4. Team ID matches across both targets

## Important Configuration Details

### Bundle Identifier Format

```
Main App:          com.aifitcheck (or your.domain.aifitcheck)
Share Extension:   com.aifitcheck.shareextension
```

### App Groups

Must be identical in both targets:
```
group.com.aifitcheck.shared
```

Mismatch = data won't sync between app and extension!

### Entitlements File

Xcode auto-generates this, but manually verify both targets have:

**AIFitCheck.entitlements:**
```xml
<key>com.apple.security.application-groups</key>
<array>
    <string>group.com.aifitcheck.shared</string>
</array>
```

**AIFitCheckShare.entitlements:**
```xml
<key>com.apple.security.application-groups</key>
<array>
    <string>group.com.aifitcheck.shared</string>
</array>
```

## Troubleshooting

### Share Extension Not Appearing
- Verify App Groups are identical in both targets
- Check bundle identifier matches expectations
- Rebuild both targets
- Restart share sheet

### Data Not Syncing
- Verify UserDefaults uses `UserDefaults(suiteName: "group.com.aifitcheck.shared")`
- Check entitlements files have app groups
- Extension may need main app installed first

### API Calls Failing
- Verify server URL in Profile settings
- Check network connectivity
- Ensure localhost:8000 is accessible (may need 127.0.0.1 on some devices)
- Check NSATS settings for non-https URLs

### Images Not Processing
- Verify ImageProcessor compression quality settings
- Check max dimension (1024px) is appropriate
- Ensure UIImage conversion succeeds

## Development Tips

### Testing Share Extension Locally
```swift
// In ShareViewController, add debug print
print("Extracted image: \(attachmentImage?.size ?? .zero)")
print("Current server: \(await APIService.shared.baseURL)")
```

### Simulator Testing
- Share Extension works on simulator
- Photos app is easiest for testing
- Safari works if you have local web pages

### Device Testing
- Real device recommended for complete testing
- Provisioning profiles must be valid
- Device must be registered with Apple Developer account

### Debugging Network Calls
- Use Charles Proxy or Wireshark
- Check network activity in Xcode
- Log all API requests in APIService

## Code Organization

### Where to Add New Features

- **New Views:** Add to Views/ folder, import in AIFitCheckApp.swift
- **New Models:** Add to Models/AppModels.swift
- **New API endpoints:** Add to Services/APIService.swift
- **Image utilities:** Add to Services/ImageProcessor.swift

### Testing Checklist

- [ ] Main app launches without errors
- [ ] All three tabs work (Home, Wardrobe, Profile)
- [ ] Can upload profile photo
- [ ] Can select clothing image for try-on
- [ ] Can view wardrobe grid
- [ ] Share extension appears in share sheet
- [ ] Share extension can try on clothing
- [ ] Wardrobe syncs between app and extension
- [ ] Server URL config works
- [ ] Network errors are handled gracefully

## Production Deployment

1. Update bundle identifiers to your company domain
2. Update app group identifier
3. Update all entitlements
4. Create provisioning profiles
5. Archive and upload to App Store
6. Ensure backend API uses HTTPS
7. Update NSATS for production domain
8. Test thoroughly on various iOS 16+ devices

## References

- [Apple App Extension Documentation](https://developer.apple.com/app-extensions/)
- [Share Sheet Integration](https://developer.apple.com/documentation/foundation/nsextensionitem)
- [App Groups](https://developer.apple.com/documentation/foundation/userdefaults/3028054-init)
- [SwiftUI Documentation](https://developer.apple.com/xcode/swiftui/)
