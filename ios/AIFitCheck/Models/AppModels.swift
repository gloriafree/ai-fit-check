import Foundation

// MARK: - Wardrobe Item
struct WardrobeItem: Identifiable, Codable {
    let id: UUID
    let clothingImage: Data
    let tryonResult: Data
    let date: Date
    let category: String

    enum CodingKeys: String, CodingKey {
        case id
        case clothingImage
        case tryonResult
        case date
        case category
    }

    init(
        id: UUID = UUID(),
        clothingImage: Data,
        tryonResult: Data,
        date: Date = Date(),
        category: String = "General"
    ) {
        self.id = id
        self.clothingImage = clothingImage
        self.tryonResult = tryonResult
        self.date = date
        self.category = category
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(clothingImage.base64EncodedString(), forKey: .clothingImage)
        try container.encode(tryonResult.base64EncodedString(), forKey: .tryonResult)
        try container.encode(date, forKey: .date)
        try container.encode(category, forKey: .category)
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(UUID.self, forKey: .id)
        let clothingString = try container.decode(String.self, forKey: .clothingImage)
        clothingImage = Data(base64Encoded: clothingString) ?? Data()
        let tryonString = try container.decode(String.self, forKey: .tryonResult)
        tryonResult = Data(base64Encoded: tryonString) ?? Data()
        date = try container.decode(Date.self, forKey: .date)
        category = try container.decode(String.self, forKey: .category)
    }
}

// MARK: - User Profile
struct UserProfile: Codable {
    var personImage: Data?
    var name: String

    init(personImage: Data? = nil, name: String = "User") {
        self.personImage = personImage
        self.name = name
    }

    enum CodingKeys: String, CodingKey {
        case personImage
        case name
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        if let personImage = personImage {
            try container.encode(personImage.base64EncodedString(), forKey: .personImage)
        }
        try container.encode(name, forKey: .name)
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        name = try container.decode(String.self, forKey: .name)
        if let imageString = try container.decodeIfPresent(String.self, forKey: .personImage) {
            personImage = Data(base64Encoded: imageString)
        } else {
            personImage = nil
        }
    }
}

// MARK: - API Models
struct TryOnRequest: Codable {
    let clothingImage: String
    let personImage: String?

    enum CodingKeys: String, CodingKey {
        case clothingImage = "clothing_image"
        case personImage = "person_image"
    }
}

struct TryOnResponse: Codable {
    let resultImage: String
    let status: String

    enum CodingKeys: String, CodingKey {
        case resultImage = "result_image"
        case status
    }
}
