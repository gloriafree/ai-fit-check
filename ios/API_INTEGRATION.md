# AI Fit Check - API Integration Guide

## Overview

The iOS app communicates with a backend server for:
1. Virtual try-on processing (AI image synthesis)
2. Person image storage
3. Optional: Wardrobe sync to cloud (currently local only)

## Server Configuration

### Default URL
```
http://localhost:8000
```

### Change Server URL
In the app, go to **Profile → Settings → Server URL**

Or programmatically:
```swift
let apiService = await APIService.shared
await apiService.setServerURL("https://api.example.com")
```

## API Endpoints

### 1. POST /api/tryon
**Virtual Try-On Processing**

**Request:**
```json
{
  "clothing_image": "base64-encoded-image-string",
  "person_image": "base64-encoded-image-string or null"
}
```

**Response:**
```json
{
  "result_image": "base64-encoded-result-image",
  "status": "success"
}
```

**Usage in Code:**
```swift
let apiService = await APIService.shared
let resultData = try await apiService.tryOn(
    clothingImage: imageData,
    personImage: userProfileImageData
)
```

**Details:**
- `clothing_image`: Required. JPG/PNG of clothing item
- `person_image`: Optional. Full body photo of person wearing clothes
  - If null/not provided: AI generates generic try-on result
  - If provided: Try-on is customized to that person
- Max image size: 1024px (enforced by ImageProcessor)
- Compression: 70% JPEG quality
- Processing time: 5-15 seconds typical
- Returns: Full try-on result image as base64

**Error Responses:**
```json
{
  "error": "Invalid clothing_image format",
  "status": "error"
}
```

Common error codes:
- 400: Bad request (invalid image format/size)
- 401: Unauthorized
- 429: Rate limited
- 500: Server error
- 503: Service unavailable

### 2. POST /api/person-image
**Store User's Person Image on Server**

**Request:**
```json
{
  "person_image": "base64-encoded-image-string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Person image updated"
}
```

**Usage in Code:**
```swift
let apiService = await APIService.shared
try await apiService.uploadPersonImage(image: imageData)
```

**Details:**
- Updates the user's default person image on server
- Used for subsequent try-ons if no custom person image provided
- Useful for: Building user profile, improving personalization
- Full-body photo recommended for best results

**Note:** Currently, the app stores person image locally via App Groups. This endpoint is provided for future cloud sync capability.

## Image Format Specifications

### Clothing Images
- **Format:** JPEG or PNG
- **Max dimensions:** 1024px (width or height)
- **Aspect ratio:** Any (will be handled by API)
- **File size:** ~50-300KB after optimization
- **Content:** Clear view of clothing item, preferably on transparent or simple background
- **Recommended:** Front-facing, well-lit, no wrinkles

### Person Images
- **Format:** JPEG or PNG
- **Max dimensions:** 1024px
- **Aspect ratio:** Portrait or full-body (3:4 or 9:16 recommended)
- **Content:** Full body, visible from neck to feet
- **Pose:** Straight-on facing camera, arms at sides
- **Clothing:** Fitted clothing (sports wear, t-shirt, etc.)
- **Background:** Plain, simple, preferably light colored
- **Lighting:** Natural, even lighting (avoid shadows, backlighting)

### Result Images
- **Format:** JPEG
- **Dimensions:** Same as clothing image input
- **Content:** Person wearing the clothing item

## Request/Response Flow

### Try-On Flow
```
User selects clothing image
  ↓
ImageProcessor.optimizeImageData() - resize, compress
  ↓
APIService.tryOn() - POST /api/tryon
  ↓
Server processes (5-15 seconds)
  ↓
Response with base64 result image
  ↓
Display result
```

### Example Request
```swift
// Get image from photo library
let clothingImage = UIImage(...)

// Optimize
guard let optimizedData = ImageProcessor.optimizeImageData(clothingImage) else {
    // Handle error
}

// Get user's person image (if available)
let userProfile = await apiService.getUserProfile()

// Call API
do {
    let resultData = try await apiService.tryOn(
        clothingImage: optimizedData,
        personImage: userProfile.personImage
    )

    // Display result
    let resultImage = UIImage(data: resultData)
} catch let error as APIError {
    switch error {
    case .serverError(let statusCode):
        print("Server error: \(statusCode)")
    case .networkError(let error):
        print("Network error: \(error)")
    default:
        print("Try-on failed: \(error.localizedDescription)")
    }
}
```

## Authentication & Headers

### Current Implementation
```swift
// No authentication required
// Only required headers:
urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
```

### For Production
If you need authentication:

```swift
// Modify APIService.tryOn() to add:
urlRequest.setValue("Bearer YOUR_API_KEY", forHTTPHeaderField: "Authorization")

// Or:
urlRequest.setValue("YOUR_API_KEY", forHTTPHeaderField: "X-API-Key")
```

## Error Handling

### APIError Enum
```swift
enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case decodingError
    case networkError(Error)
    case serverError(Int)
}
```

### Handling Errors
```swift
do {
    let result = try await apiService.tryOn(...)
} catch let error as APIError {
    switch error {
    case .invalidURL:
        showAlert("Invalid server URL")
    case .invalidResponse:
        showAlert("Invalid server response")
    case .decodingError:
        showAlert("Failed to process result")
    case .networkError(let netError):
        showAlert("Network error: \(netError.localizedDescription)")
    case .serverError(let statusCode):
        showAlert("Server error: \(statusCode)")
    }
} catch {
    showAlert("Unknown error: \(error.localizedDescription)")
}
```

## Data Persistence

### Local Storage (Current)
- Wardrobe items stored in UserDefaults with App Group
- User profile stored in UserDefaults with App Group
- Images stored as base64 in JSON

### For Cloud Sync
Extend APIService with:
```swift
func syncWardrobe() async throws -> [WardrobeItem]
func pushWardrobeItem(_ item: WardrobeItem) async throws
func deleteWardrobeItem(itemID: UUID) async throws
```

## Network Configuration

### Development
**Info.plist settings:**
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>localhost</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

### Production
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <!-- Only allow HTTPS -->
</dict>
```

## Performance Considerations

### Image Optimization
- Clothing images: Resized to max 1024px, 70% JPEG quality (~80-200KB)
- Person images: Same optimization
- Reduces upload time and API server load

### Bandwidth
- Average try-on request: ~300KB (clothing + person)
- Average response: ~200-400KB (result image)
- Total per try-on: ~500-700KB

### Caching
Currently not implemented. Consider adding:
```swift
// Cache person image to avoid re-uploading
private var cachedPersonImageHash: String?

// Cache recent try-on results
@Cached(duration: 3600)
func getTryOnResult(clothingId: String) -> Data?
```

## Rate Limiting

### Recommended Backend Limits
- 60 try-ons per minute per user
- 100 try-ons per minute per IP
- 10 concurrent requests per user

### Client-Side Handling
The app automatically prevents rapid-fire requests:
- Try-on shows loading state
- Button disabled during processing
- Typical flow: User takes 10-15 seconds between requests

## Testing the API

### Local Testing
```bash
# Start mock server
python3 -m http.server 8000

# Or use a real backend with dummy responses
```

### Using cURL
```bash
curl -X POST http://localhost:8000/api/tryon \
  -H "Content-Type: application/json" \
  -d '{
    "clothing_image": "base64_data_here",
    "person_image": null
  }'
```

### Postman Collection
```json
{
  "info": { "name": "AI Fit Check API" },
  "item": [
    {
      "name": "Try On",
      "request": {
        "method": "POST",
        "url": "{{server_url}}/api/tryon",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"clothing_image\": \"{{clothing_base64}}\",\n  \"person_image\": null\n}"
        }
      }
    }
  ]
}
```

## Common Integration Issues

### Issue: 400 Bad Request
**Cause:** Invalid image format or missing field
**Solution:** Verify image is valid JPEG/PNG and base64 encoding is correct

### Issue: 413 Payload Too Large
**Cause:** Image file too large
**Solution:** ImageProcessor should handle this, but reduce max dimension to 800px

### Issue: 500 Server Error
**Cause:** Backend processing failed
**Solution:** Check backend logs, verify image content

### Issue: Connection Timeout
**Cause:** Server not responding
**Solution:** Check server URL, verify backend is running, increase timeout

### Issue: Base64 Decoding Error
**Cause:** Invalid base64 string
**Solution:** Verify ImageProcessor.optimizeImageData() output, ensure no newlines in base64

## Future Enhancements

1. **WebSocket Support:** Real-time progress updates
2. **Batch Processing:** Multiple items at once
3. **Webhooks:** Async result delivery
4. **Video Processing:** Multi-angle try-ons
5. **Model Download:** On-device ML model for faster processing
6. **Compression:** WebP format for smaller file sizes
7. **Caching:** Smart caching of person profiles
8. **Analytics:** Track try-on success rates

## Monitoring & Analytics

Consider logging:
```swift
// API call metrics
os_log("Try-on request: %@ -> %@", clothing: clothingImage.size, server: baseURL)

// Success/failure tracking
os_log("Try-on result: status=%@, duration=%@ms", status, duration)

// Error tracking
os_log(.error, "API Error: %@", errorDescription)
```

## References

- [URLSession Documentation](https://developer.apple.com/documentation/foundation/urlsession)
- [Codable](https://developer.apple.com/documentation/foundation/codable)
- [Base64 Encoding](https://developer.apple.com/documentation/foundation/data/3128659-base64encodedstring)
- [Network Security](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)
