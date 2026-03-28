import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case decodingError
    case networkError(Error)
    case serverError(Int)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid server response"
        case .decodingError:
            return "Failed to decode response"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .serverError(let statusCode):
            return "Server error: \(statusCode)"
        }
    }
}

actor APIService {
    static let shared = APIService()

    @AppStorage("serverURL") private var serverURLString = "http://localhost:8000"

    var baseURL: URL {
        URL(string: serverURLString) ?? URL(string: "http://localhost:8000")!
    }

    func setServerURL(_ url: String) {
        serverURLString = url
    }

    // MARK: - Try On
    func tryOn(clothingImage: Data, personImage: Data? = nil) async throws -> Data {
        let clothingBase64 = clothingImage.base64EncodedString()
        let personBase64 = personImage?.base64EncodedString()

        let request = TryOnRequest(
            clothingImage: clothingBase64,
            personImage: personBase64
        )

        let encoder = JSONEncoder()
        let requestData = try encoder.encode(request)

        var urlRequest = URLRequest(url: baseURL.appendingPathComponent("/api/tryon"))
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = requestData

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            throw APIError.serverError(httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        let tryOnResponse = try decoder.decode(TryOnResponse.self, from: data)

        guard let resultData = Data(base64Encoded: tryOnResponse.resultImage) else {
            throw APIError.decodingError
        }

        return resultData
    }

    // MARK: - Person Image Management
    func uploadPersonImage(image: Data) async throws {
        let base64String = image.base64EncodedString()
        let payload: [String: String] = ["person_image": base64String]

        let encoder = JSONEncoder()
        let requestData = try encoder.encode(payload)

        var urlRequest = URLRequest(url: baseURL.appendingPathComponent("/api/person-image"))
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = requestData

        let (_, response) = try await URLSession.shared.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard httpResponse.statusCode == 200 else {
            throw APIError.serverError(httpResponse.statusCode)
        }
    }

    // MARK: - Wardrobe Management
    func getWardrobe() async throws -> [WardrobeItem] {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        let userDefaults = UserDefaults(suiteName: "group.com.aifitcheck.shared")
        guard let wardrobeData = userDefaults?.data(forKey: "wardrobe") else {
            return []
        }

        let wardrobe = try decoder.decode([WardrobeItem].self, from: wardrobeData)
        return wardrobe
    }

    func saveToWardrobe(item: WardrobeItem) async throws {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601

        var wardrobe = try await getWardrobe()
        wardrobe.append(item)

        let wardrobeData = try encoder.encode(wardrobe)
        let userDefaults = UserDefaults(suiteName: "group.com.aifitcheck.shared")
        userDefaults?.set(wardrobeData, forKey: "wardrobe")
    }

    func deleteFromWardrobe(itemID: UUID) async throws {
        var wardrobe = try await getWardrobe()
        wardrobe.removeAll { $0.id == itemID }

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601

        let wardrobeData = try encoder.encode(wardrobe)
        let userDefaults = UserDefaults(suiteName: "group.com.aifitcheck.shared")
        userDefaults?.set(wardrobeData, forKey: "wardrobe")
    }

    func getUserProfile() -> UserProfile {
        let userDefaults = UserDefaults(suiteName: "group.com.aifitcheck.shared")
        if let profileData = userDefaults?.data(forKey: "userProfile") {
            let decoder = JSONDecoder()
            if let profile = try? decoder.decode(UserProfile.self, from: profileData) {
                return profile
            }
        }
        return UserProfile()
    }

    func saveUserProfile(_ profile: UserProfile) {
        let encoder = JSONEncoder()
        if let profileData = try? encoder.encode(profile) {
            let userDefaults = UserDefaults(suiteName: "group.com.aifitcheck.shared")
            userDefaults?.set(profileData, forKey: "userProfile")
        }
    }
}
