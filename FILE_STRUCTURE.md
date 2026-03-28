# AI Fit Check iOS - Complete File Structure

## Directory Layout

```
mnt/ai_fit_check/
├── ios/
│   ├── AIFitCheck/                          # Main app files
│   │   ├── App/
│   │   │   └── AIFitCheckApp.swift          # Entry point, TabView setup
│   │   ├── Models/
│   │   │   └── AppModels.swift              # Data structures & API models
│   │   ├── Services/
│   │   │   ├── APIService.swift             # Backend API client (actor)
│   │   │   └── ImageProcessor.swift         # Image utilities
│   │   ├── Views/
│   │   │   ├── HomeView.swift               # Home tab with guide
│   │   │   ├── TryOnView.swift              # Try-on result display
│   │   │   ├── WardrobeView.swift           # Wardrobe gallery
│   │   │   └── ProfileView.swift            # Profile & settings
│   │   ├── ShareExtension/
│   │   │   ├── ShareViewController.swift    # UIKit share extension
│   │   │   ├── ShareExtensionView.swift     # SwiftUI extension UI
│   │   │   └── Info.plist                   # Extension config
│   │   ├── Utilities/
│   │   │   └── Extensions.swift             # Utility extensions
│   │   └── README.md                        # Project README
│   ├── SETUP_GUIDE.md                       # Xcode setup instructions
│   └── API_INTEGRATION.md                   # API documentation
└── FILE_STRUCTURE.md                        # This file
```

## File Descriptions

### App/ - Application Entry Point

#### AIFitCheckApp.swift (88 lines)
- `AIFitCheckApp`: Main app struct with SwiftUI Scene
- `MainTabView`: TabView with Home, Wardrobe, Profile tabs
- Dark theme configuration
- Tab switching state management

### Models/ - Data Structures

#### AppModels.swift (104 lines)
**WardrobeItem**
- `id`: UUID
- `clothingImage`: Data (base64 encoded)
- `tryonResult`: Data (base64 encoded)
- `date`: Date
- `category`: String
- Custom Codable implementation for base64 serialization

**UserProfile**
- `personImage`: Data? (user's full-body photo)
- `name`: String (user's name)
- Custom Codable for base64 encoding

**TryOnRequest**
- `clothingImage`: String (base64)
- `personImage`: String? (base64 or null)
- For API communication

**TryOnResponse**
- `resultImage`: String (base64 result)
- `status`: String (success/error)
- For API communication

### Services/ - Business Logic

#### APIService.swift (168 lines)
**Main Features:**
- `actor` type for thread-safe concurrent access
- Configurable base URL via `@AppStorage`
- `async`/`await` throughout

**Key Methods:**
- `tryOn(clothingImage:personImage:)` → Data
  - POST to `/api/tryon`
  - Returns result image data
  - Includes error handling

- `uploadPersonImage(image:)` → Void
  - POST to `/api/person-image`
  - Stores user's default person image

- `getWardrobe()` → [WardrobeItem]
  - Retrieves from local UserDefaults (app group)
  - Returns sorted array

- `saveToWardrobe(item:)` → Void
  - Appends item to wardrobe
  - Persists via UserDefaults

- `deleteFromWardrobe(itemID:)` → Void
  - Removes item by ID

- `getUserProfile()` → UserProfile
  - Retrieves from UserDefaults
  - Returns default if not set

- `saveUserProfile(_:)` → Void
  - Persists user profile

**Error Handling:**
```swift
enum APIError: LocalizedError
- invalidURL
- invalidResponse
- decodingError
- networkError(Error)
- serverError(Int)
```

#### ImageProcessor.swift (64 lines)
**Image Utilities:**
- `resizeImage(_:maxDimension:)` → UIImage
  - Scales to max 1024px maintaining aspect

- `centerCropImage(_:to:)` → UIImage
  - Crops to specified size from center

- `optimizeImageData(_:compressionQuality:)` → Data?
  - Resize + JPEG compression
  - Bandwidth optimized for upload

- `dataToUIImage(_:)` → UIImage?
  - Converts Data to UIImage

- `uiImageToData(_:quality:)` → Data?
  - Converts UIImage to JPEG Data

- `generateThumbnail(from:size:)` → UIImage
  - Creates square thumbnail

### Views/ - User Interface

#### HomeView.swift (302 lines)
**Features:**
- Welcome header with logo
- "How to Use" tutorial (4 steps)
- Quick try-on button (photo library picker)
- Recent try-ons grid (2 columns)
- Loading overlay during processing

**Sub-Components:**
- `HowToStep`: Tutorial step display
- `RecentTryOnCard`: Grid card for wardrobe items
- `LoadingOverlay`: Processing spinner
- `PhotoPicker`: UIImagePickerController wrapper
- `TryOnDetailView`: Navigate to item details

**State:**
- `@State private var showingImagePicker`
- `@State private var selectedImage`
- `@State private var isLoading`
- `@State private var tryOnResult`
- `@State private var error`
- `@State private var recentItems`

**Logic:**
- `performTryOn(image:)`: Calls API service
- `loadRecentItems()`: Fetches wardrobe on appear

#### TryOnView.swift (160 lines)
**Displays Try-On Results**

**States:**
- `LoadingState`: Spinner + "AI is dressing you..."
- `ErrorState`: Error message display
- `ResultState`: Result image + action buttons
- `EmptyState`: No result yet

**Actions:**
- Save to Wardrobe
- Share result (system share)
- Try Another item

#### WardrobeView.swift (248 lines)
**Wardrobe Gallery**

**Features:**
- 2-column grid of try-on results
- Pull-to-refresh functionality
- Swipe/context menu to delete
- Navigate to detail view
- Empty state with illustration
- Deletion confirmation alert

**Components:**
- `WardrobeItemCard`: Grid item preview
- `WardrobeItemDetailView`: Full-size detail view
- `EmptyWardrobeView`: Empty state

**State:**
- `@State private var items`
- `@State private var isLoading`
- `@State private var showingDeleteConfirm`
- `@State private var itemToDelete`

**Methods:**
- `loadWardrobe()`: Fetch items
- `deleteItem(id:)`: Delete with confirmation

#### ProfileView.swift (265 lines)
**User Profile & Settings**

**Sections:**
1. Profile Photo
   - Upload from photo library
   - Preview current photo
   - Photography tips (lighting, pose, background)

2. Settings
   - Configurable server URL
   - Account name field
   - Save button with feedback

3. About
   - App version
   - iOS support info

**Components:**
- `TipRow`: Tip display with icon
- `PhotoPickerForProfile`: Image picker

**Features:**
- Real-time profile update
- Auto-upload person image to API
- Server URL persistence
- Photography best-practices guide

### ShareExtension/ - System Share Sheet Integration

#### ShareViewController.swift (232 lines)
**UIKit-Based Share Extension**

**Lifecycle:**
1. User shares image from any app
2. Extension receives NSExtensionItem
3. Extracts UIImage from attachment
4. Shows preview in compact UI
5. User taps "Try On"
6. Sends to API
7. Displays result
8. Option to save to wardrobe

**UI Components:**
- `containerView`: Main card container
- `imagePreview`: Displays clothing/result
- `loadingIndicator`: Spinner during processing
- `statusLabel`: Status messages
- `tryOnButton`: Initiates try-on
- `saveButton`: Saves to wardrobe
- `doneButton`: Closes extension

**Methods:**
- `extractImage()`: Gets image from extension item
- `tryOnTapped()`: Calls API try-on
- `saveTapped()`: Saves result to wardrobe
- `doneTapped()`: Closes extension

**Flow:**
```
extractImage()
  ↓
Shows preview + "Try On" button
  ↓
tryOnTapped() [if user taps]
  ↓
Shows loading "AI is trying on..."
  ↓
API returns result
  ↓
Shows result + "Save" + "Done"
  ↓
saveTapped() [if user saves]
  ↓
Adds to wardrobe
  ↓
doneTapped() [always]
  ↓
Extension closes
```

#### ShareExtensionView.swift (249 lines)
**SwiftUI UI for Share Extension** (Alternative implementation)

**State Management:**
- `@State private var clothingImage`
- `@State private var tryOnResult`
- `@State private var isLoading`
- `@State private var error`

**Sub-Views:**
- `ImageCard`: Shows clothing, "Try On" button
- `LoadingCard`: Spinner, status message
- `ResultCard`: Result, "Save" & "Done" buttons
- `ErrorCard`: Error message
- `EmptyCard`: No image found

**Methods:**
- `performTryOn()`: API call
- `saveToWardrobe()`: Persist result
- Similar flow to ShareViewController

#### Info.plist (42 lines)
**Extension Configuration**

**Key Settings:**
```xml
NSExtensionActivationSupportsImageWithMaxCount = 1
NSExtensionPointIdentifier = com.apple.share-services
NSAppTransportSecurity: Allows localhost
```

Configures extension to:
- Accept single image from share sheet
- Handle only images (not web pages)
- Allow HTTP to localhost for development

### Utilities/ - Helper Code

#### Extensions.swift (320 lines)
**Utility Extensions**

**Color Extensions:**
- `appPurple`: Brand color (#7C3AED)
- `darkBackground`, `cardBackground`: Theme colors
- `secondaryText`: Text color

**View Extensions:**
- `cardStyle()`: Standard card styling
- `gradientBackground()`: Gradient overlay
- `shadowStyle()`: Drop shadow

**Date Extensions:**
- `formattedShort`: Medium date + time
- `formattedDateOnly`: Date only
- `timeAgoDisplay`: "2 hours ago" format

**Data Extensions:**
- `sizeInMB`, `sizeInKB`, `sizeInBytes`: File size helpers
- `isValidImage()`: Validates image data

**String Extensions:**
- `isValidURL`: Checks if valid URL
- `sanitizedURL`: Adds http:// if needed

**UIImage Extensions:**
- `resizedToFit(maxDimension:)`: Resize utility
- `jpegDataOptimized(quality:)`: Optimized JPEG
- `aspectRatio`: Width/height ratio

**Logger:**
- Structured logging with timestamps
- Debug level toggle

**Haptic Feedback:**
- `light()`, `medium()`, `heavy()`: Impact feedback
- `success()`, `error()`, `warning()`: Notification feedback

**Async Storage Actor:**
- Thread-safe UserDefaults wrapper
- Save/load/delete generics

## File Size Summary

```
App/
  AIFitCheckApp.swift                     88 lines

Models/
  AppModels.swift                        104 lines

Services/
  APIService.swift                       168 lines
  ImageProcessor.swift                    64 lines

Views/
  HomeView.swift                         302 lines
  TryOnView.swift                        160 lines
  WardrobeView.swift                     248 lines
  ProfileView.swift                      265 lines

ShareExtension/
  ShareViewController.swift              232 lines
  ShareExtensionView.swift               249 lines
  Info.plist                              42 lines

Utilities/
  Extensions.swift                       320 lines

Documentation/
  README.md                              186 lines
  API_INTEGRATION.md                     428 lines
  SETUP_GUIDE.md                         385 lines
  FILE_STRUCTURE.md                      (this file)

TOTAL CODE:               ~2,237 lines of Swift
TOTAL DOCUMENTATION:      ~1,000 lines
TOTAL PROJECT:            ~3,237 lines
```

## Code Organization Principles

1. **Separation of Concerns**
   - Models: Data only
   - Services: API & processing
   - Views: UI only
   - Utilities: Helpers

2. **Swift Best Practices**
   - `actor` for thread safety (APIService)
   - `async/await` for concurrency
   - `@StateObject`, `@State`, `@AppStorage` for state
   - Proper error handling with custom enum
   - MARK comments for sections

3. **SwiftUI Patterns**
   - Preference keys for custom styling
   - Modifier composition
   - View extraction for reusability
   - Custom containers (VStack, LazyVGrid)

4. **Image Handling**
   - Automatic optimization before upload
   - Base64 encoding for API
   - Local caching via UserDefaults
   - App Group sharing

5. **App Architecture**
   - TabView for main navigation
   - NavigationStack for detail views
   - Modal sheets for image picker
   - Action-based callbacks (onSaveToWardrobe, etc.)

## Dependencies

**Standard Library Only:**
- SwiftUI
- Foundation (URLSession, Codable, etc.)
- UIKit (for Share Extension)

**No external packages required**

## Platform Support

- **Minimum iOS:** 16.0
- **Target:** iOS 16.0+
- **iPhone:** All sizes supported
- **iPad:** Works, optimized for iPhone first
- **Dark Mode:** Always enabled

## Configuration Points

| Setting | Location | Default |
|---------|----------|---------|
| Server URL | ProfileView → Settings | http://localhost:8000 |
| App Group | APIService, Info.plist | group.com.aifitcheck.shared |
| Bundle ID | Xcode project | com.aifitcheck |
| Theme Color | Extensions.swift | Purple (#7C3AED) |
| Image Max Dim | ImageProcessor | 1024px |
| JPEG Quality | ImageProcessor | 0.7 (70%) |

## Build Requirements

- Xcode 14.0+
- Swift 5.7+
- iOS 16.0 SDK or later
- Two targets: Main App + Share Extension
- Shared App Groups entitlement

## Quick Reference

### Adding a New Screen
1. Create file in Views/
2. Create data model in Models/ if needed
3. Add to MainTabView in AIFitCheckApp.swift

### Adding API Endpoint
1. Add method to APIService
2. Create request/response models in AppModels.swift
3. Use in appropriate View

### Modifying Theme
1. Update Colors in Extensions.swift
2. Update accent colors in TabView/Buttons
3. Test dark mode

### Debugging Extension
1. Set breakpoint in ShareViewController.swift
2. Run scheme with Share Extension
3. Share image from Photos app
4. Debugger will attach to extension

## Next Steps for Development

- [ ] Create Xcode project with file structure
- [ ] Configure signing & capabilities
- [ ] Set up Share Extension target
- [ ] Implement backend API server
- [ ] Test on physical device
- [ ] Add cloud sync for wardrobe
- [ ] Implement user authentication
- [ ] Add analytics tracking
- [ ] Create App Store listing
