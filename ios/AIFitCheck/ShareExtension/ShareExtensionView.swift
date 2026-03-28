import SwiftUI

struct ShareExtensionView: View {
    @State private var clothingImage: UIImage?
    @State private var tryOnResult: UIImage?
    @State private var isLoading = false
    @State private var error: String?
    @Environment(\.dismiss) var dismiss

    var body: some View {
        ZStack {
            Color(white: 0).ignoresSafeArea()

            VStack(spacing: 12) {
                // Header
                HStack {
                    Text("AI Fit Check")
                        .font(.headline)
                        .fontWeight(.bold)

                    Spacer()

                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.gray)
                    }
                }
                .padding(12)

                // Content
                if isLoading {
                    LoadingCard()
                } else if let error = error {
                    ErrorCard(message: error)
                } else if let result = tryOnResult {
                    ResultCard(
                        image: result,
                        onSave: saveToWardrobe,
                        onClose: { dismiss() }
                    )
                } else if let clothingImage = clothingImage {
                    ImageCard(
                        image: clothingImage,
                        onTryOn: performTryOn
                    )
                } else {
                    EmptyCard()
                }

                Spacer()
            }
            .padding(12)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    private func performTryOn() {
        guard let image = clothingImage else { return }

        isLoading = true
        error = nil

        Task {
            do {
                guard let imageData = ImageProcessor.optimizeImageData(image) else {
                    DispatchQueue.main.async {
                        self.error = "Failed to process image"
                        self.isLoading = false
                    }
                    return
                }

                let apiService = await APIService.shared
                let userProfile = await apiService.getUserProfile()

                let resultData = try await apiService.tryOn(
                    clothingImage: imageData,
                    personImage: userProfile.personImage
                )

                DispatchQueue.main.async {
                    self.tryOnResult = UIImage(data: resultData)
                    self.isLoading = false
                }
            } catch {
                DispatchQueue.main.async {
                    self.error = "Try-on failed: \(error.localizedDescription)"
                    self.isLoading = false
                }
            }
        }
    }

    private func saveToWardrobe() {
        guard let resultImage = tryOnResult,
              let resultData = resultImage.jpegData(compressionQuality: 0.8),
              let clothingImage = clothingImage,
              let clothingData = ImageProcessor.optimizeImageData(clothingImage) else {
            error = "Failed to save"
            return
        }

        let item = WardrobeItem(
            clothingImage: clothingData,
            tryonResult: resultData,
            date: Date(),
            category: "Shared"
        )

        Task {
            do {
                let apiService = await APIService.shared
                try await apiService.saveToWardrobe(item: item)
                DispatchQueue.main.async {
                    dismiss()
                }
            } catch {
                DispatchQueue.main.async {
                    self.error = "Save failed"
                }
            }
        }
    }
}

struct ImageCard: View {
    let image: UIImage
    let onTryOn: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            Image(uiImage: image)
                .resizable()
                .scaledToFill()
                .frame(height: 180)
                .clipped()
                .cornerRadius(8)

            Text("Ready to try on?")
                .font(.subheadline)
                .fontWeight(.semibold)

            Button(action: onTryOn) {
                HStack(spacing: 6) {
                    Image(systemName: "sparkles")
                    Text("Try On")
                    Spacer()
                }
                .frame(maxWidth: .infinity)
                .padding(10)
                .background(Color.purple)
                .foregroundColor(.white)
                .cornerRadius(8)
            }
        }
        .padding(12)
        .background(Color(white: 0.1))
        .cornerRadius(10)
    }
}

struct LoadingCard: View {
    var body: some View {
        VStack(spacing: 12) {
            ProgressView()
                .scaleEffect(1.2)
                .tint(.purple)

            Text("AI is dressing you...")
                .font(.subheadline)
                .fontWeight(.semibold)

            Text("This takes 5-15 seconds")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity)
        .padding(20)
        .background(Color(white: 0.1))
        .cornerRadius(10)
    }
}

struct ResultCard: View {
    let image: UIImage
    let onSave: () -> Void
    let onClose: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            Image(uiImage: image)
                .resizable()
                .scaledToFill()
                .frame(height: 200)
                .clipped()
                .cornerRadius(8)

            Text("Perfect fit!")
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(.green)

            VStack(spacing: 8) {
                Button(action: onSave) {
                    HStack(spacing: 6) {
                        Image(systemName: "bookmark.fill")
                        Text("Save to Wardrobe")
                        Spacer()
                    }
                    .frame(maxWidth: .infinity)
                    .padding(10)
                    .background(Color.purple)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }

                Button(action: onClose) {
                    HStack(spacing: 6) {
                        Image(systemName: "xmark")
                        Text("Done")
                        Spacer()
                    }
                    .frame(maxWidth: .infinity)
                    .padding(10)
                    .background(Color(white: 0.15))
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
            }
        }
        .padding(12)
        .background(Color(white: 0.1))
        .cornerRadius(10)
    }
}

struct ErrorCard: View {
    let message: String

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 32))
                .foregroundColor(.orange)

            Text("Something went wrong")
                .font(.subheadline)
                .fontWeight(.semibold)

            Text(message)
                .font(.caption)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(16)
        .background(Color(white: 0.1))
        .cornerRadius(10)
    }
}

struct EmptyCard: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "photo.fill")
                .font(.system(size: 32))
                .foregroundColor(.gray)

            Text("No image found")
                .font(.subheadline)
                .fontWeight(.semibold)

            Text("Please share an image from your photos or browser")
                .font(.caption)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(16)
        .background(Color(white: 0.1))
        .cornerRadius(10)
    }
}

#Preview {
    ShareExtensionView()
}
