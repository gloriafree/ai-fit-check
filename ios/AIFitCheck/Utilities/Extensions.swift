import SwiftUI
import Foundation

// MARK: - Color Extensions
extension Color {
    static let appPurple = Color(red: 0.49, green: 0.23, blue: 0.93)
    static let darkBackground = Color(white: 0.08)
    static let cardBackground = Color(white: 0.1)
    static let secondaryText = Color(white: 0.6)
}

// MARK: - View Extensions
extension View {
    func cardStyle() -> some View {
        padding(16)
            .background(Color.cardBackground)
            .cornerRadius(12)
    }

    func gradientBackground() -> some View {
        background(
            LinearGradient(
                gradient: Gradient(colors: [
                    Color.darkBackground,
                    Color.cardBackground
                ]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }

    func shadowStyle() -> some View {
        shadow(color: Color.black.opacity(0.3), radius: 4, x: 0, y: 2)
    }
}

// MARK: - Date Formatting
extension Date {
    var formattedShort: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: self)
    }

    var formattedDateOnly: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: self)
    }

    var timeAgoDisplay: String {
        let calendar = Calendar.current
        let components = calendar.dateComponents([.day, .hour, .minute], from: self, to: Date())

        if let days = components.day, days > 0 {
            return days == 1 ? "1 day ago" : "\(days) days ago"
        } else if let hours = components.hour, hours > 0 {
            return hours == 1 ? "1 hour ago" : "\(hours) hours ago"
        } else if let minutes = components.minute, minutes > 0 {
            return minutes == 1 ? "1 minute ago" : "\(minutes) minutes ago"
        } else {
            return "Just now"
        }
    }
}

// MARK: - Data Extensions
extension Data {
    var sizeInMB: Double {
        Double(count) / 1_024_000
    }

    var sizeInKB: Double {
        Double(count) / 1_024
    }

    var sizeInBytes: Int {
        count
    }

    func isValidImage() -> Bool {
        guard count > 0 else { return false }
        guard let image = UIImage(data: self) else { return false }
        return image.size.width > 0 && image.size.height > 0
    }
}

// MARK: - String Extensions
extension String {
    var isValidURL: Bool {
        if let url = URL(string: self) {
            return UIApplication.shared.canOpenURL(url)
        }
        return false
    }

    var sanitizedURL: String {
        let trimmed = trimmingCharacters(in: .whitespaces)
        if !trimmed.hasPrefix("http://") && !trimmed.hasPrefix("https://") {
            return "http://\(trimmed)"
        }
        return trimmed
    }
}

// MARK: - UIImage Extensions
extension UIImage {
    func resizedToFit(maxDimension: CGFloat) -> UIImage {
        let scale = size.width > size.height
            ? maxDimension / size.width
            : maxDimension / size.height

        guard scale < 1 else { return self }

        let newSize = CGSize(width: size.width * scale, height: size.height * scale)
        let renderer = UIGraphicsImageRenderer(size: newSize)

        return renderer.image { _ in
            draw(in: CGRect(origin: .zero, size: newSize))
        }
    }

    func jpegDataOptimized(quality: CGFloat = 0.75) -> Data? {
        jpegData(compressionQuality: quality)
    }

    var aspectRatio: CGFloat {
        size.height > 0 ? size.width / size.height : 1
    }
}

// MARK: - View Controller Extensions
extension UIViewController {
    var hasNotch: Bool {
        guard #available(iOS 11.0, *) else { return false }
        return UIApplication.shared.windows[0].safeAreaInsets.top >= 44
    }
}

// MARK: - Logging Helper
struct Logger {
    enum LogLevel: String {
        case debug = "DEBUG"
        case info = "INFO"
        case warning = "WARNING"
        case error = "ERROR"
    }

    static func log(
        _ message: String,
        level: LogLevel = .info,
        file: String = #file,
        function: String = #function,
        line: Int = #line
    ) {
        let filename = (file as NSString).lastPathComponent
        let timestamp = ISO8601DateFormatter().string(from: Date())

        #if DEBUG
        print("[\(timestamp)] [\(level.rawValue)] \(filename):\(line) \(function) - \(message)")
        #endif
    }
}

// MARK: - Safe Area Helper
struct SafeAreaInsets {
    static var top: CGFloat {
        guard #available(iOS 11.0, *) else { return 0 }
        return UIApplication.shared.windows.first?.safeAreaInsets.top ?? 0
    }

    static var bottom: CGFloat {
        guard #available(iOS 11.0, *) else { return 0 }
        return UIApplication.shared.windows.first?.safeAreaInsets.bottom ?? 0
    }
}

// MARK: - Haptic Feedback Helper
struct HapticFeedback {
    static func light() {
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }

    static func medium() {
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
    }

    static func heavy() {
        UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
    }

    static func success() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }

    static func error() {
        UINotificationFeedbackGenerator().notificationOccurred(.error)
    }

    static func warning() {
        UINotificationFeedbackGenerator().notificationOccurred(.warning)
    }
}

// MARK: - Binding Extensions
extension Binding {
    func onChange(_ handler: @escaping (Value) -> Void) -> Binding<Value> {
        Binding(
            get: { wrappedValue },
            set: { newValue in
                wrappedValue = newValue
                handler(newValue)
            }
        )
    }
}

// MARK: - Async Storage Helper
actor AsyncStorage {
    static let shared = AsyncStorage()

    private let queue = DispatchQueue(label: "com.aifitcheck.storage", attributes: .concurrent)

    func save<T: Encodable>(_ value: T, forKey key: String) throws {
        let data = try JSONEncoder().encode(value)
        var sync = true
        queue.async(flags: .barrier) {
            UserDefaults(suiteName: "group.com.aifitcheck.shared")?.set(data, forKey: key)
            sync = false
        }
        while sync { usleep(1000) }
    }

    func load<T: Decodable>(_ type: T.Type, forKey key: String) throws -> T? {
        guard let data = UserDefaults(suiteName: "group.com.aifitcheck.shared")?.data(forKey: key) else {
            return nil
        }
        return try JSONDecoder().decode(T.self, from: data)
    }

    func delete(forKey key: String) {
        UserDefaults(suiteName: "group.com.aifitcheck.shared")?.removeObject(forKey: key)
    }
}

// MARK: - Result Type Extension
extension Result {
    func mapError(_ transform: (Failure) -> Failure) -> Result<Success, Failure> {
        mapError(transform)
    }

    var value: Success? {
        try? get()
    }

    var error: Failure? {
        guard case .failure(let error) = self else { return nil }
        return error
    }
}
