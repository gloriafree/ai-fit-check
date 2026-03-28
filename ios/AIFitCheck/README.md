# AI Fit Check - iOS SwiftUI App

A complete iOS SwiftUI application with Share Extension for virtual try-on of clothing using AI.

## Project Structure

```
AIFitCheck/
├── App/
│   └── AIFitCheckApp.swift                 # Main app entry point with TabView
├── Models/
│   └── AppModels.swift                     # Data models (WardrobeItem, UserProfile, API models)
├── Services/
│   ├── APIService.swift                    # Backend API client (async/await)
│   └── ImageProcessor.swift                # Image resizing, cropping, optimization
├── Views/
│   ├── HomeView.swift                      # Main screen with how-to guide
│   ├── TryOnView.swift                     # Try-on result display
│   ├── WardrobeView.swift                  # Saved outfits gallery
│   └── ProfileView.swift                   # User profile & settings
├── ShareExtension/
│   ├── ShareViewController.swift           # UIKit-based share extension
│   ├── ShareExtensionView.swift            # SwiftUI view for extension
│   └── Info.plist                          # Share extension configuration
└── README.md                               # This file
```

## Features

### Main App
- **Home Tab**: Welcome screen with instructions, quick try-on, and recent results
- **Wardrobe Tab**: Grid view of saved try-on results with delete functionality
- **Profile Tab**: User photo upload, profile settings, and server configuration

### Share Extension
- Appears in system share sheet across all apps (Safari, Instagram, Taobao, etc.)
- Lightweight UI for quick try-ons
- Save results directly to wardrobe
- Seamless integration with main app via App Groups

## Key Architecture

### Data Sharing
- Uses `App Group` (group.com.aifitcheck.shared) for sharing data between main app and extension
- UserDefaults with shared app group for wardrobe and profile data
- Base64 encoding for image transmission via JSON

### Image Processing
- Automatic resize to max 1024px before upload
- JPEG compression with configurable quality
- Center-crop for thumbnail generation
- Bandwidth-optimized

### API Integration
- `APIService` actor for thread-safe API calls
- Configurable server URL via settings
- Async/await throughout
- Images sent/received as base64 in JSON

## Configuration

### Server URL
Configure the backend URL in:
1. Profile → Settings → Server URL (default: http://localhost:8000)
2. Or update `@AppStorage("serverURL")` in APIService.swift

### App Groups
Ensure the following are configured in Xcode:
- **Main App**: Signing & Capabilities → App Groups → Add "group.com.aifitcheck.shared"
- **Share Extension**: Same app group configuration
- **Bundle ID**: com.aifitcheck (adjust as needed)

### Share Extension Registration
The share extension is configured in `Info.plist`:
- `NSExtensionActivationSupportsImageWithMaxCount = 1`
- Accepts only image types
- Launches with custom UIViewController

## Dependencies
- iOS 16.0+
- SwiftUI
- Foundation (URLSession, Codable)
- UIKit (for Share Extension and image handling)

## API Endpoints Expected

### POST /api/tryon
Request:
```json
{
  "clothing_image": "base64-string",
  "person_image": "base64-string or null"
}
```

Response:
```json
{
  "result_image": "base64-string",
  "status": "success"
}
```

### POST /api/person-image
Request:
```json
{
  "person_image": "base64-string"
}
```

## Design Guidelines

- **Color Scheme**: Dark theme with purple accent (#7C3AED)
- **Icons**: SF Symbols throughout
- **State Management**: @State, @AppStorage, Actor-based APIService
- **Error Handling**: Graceful error states with user-friendly messages
- **Loading States**: Progress indicators with contextual messaging

## Network Security

- Allows arbitrary loads to localhost for development
- Configure NSAppTransportSecurity for production
- HTTPS recommended for production

## Performance Considerations

- Image optimization before upload (max 1024px, 70% JPEG quality)
- Efficient grid layout with LazyVGrid
- Cached profile and wardrobe data
- Background tasks for API calls

## Future Enhancements

- Video try-on support
- Multiple clothing items simultaneously
- AR preview in main app
- Cloud sync across devices
- Advanced wardrobe organization (tags, filters)
- Try-on history with analytics

## Building & Running

1. Create Xcode project with these files
2. Configure bundle IDs and app group
3. Add Share Extension target
4. Configure signing and capabilities
5. Run on iOS 16+ device or simulator
6. Ensure backend API is running (default: localhost:8000)

## Notes

- The Share Extension requires the main app to be installed
- App Groups must be identical in both targets
- Images are stored locally; implement cloud sync if needed
- Base64 encoding increases data size; consider compression alternatives for large batches
