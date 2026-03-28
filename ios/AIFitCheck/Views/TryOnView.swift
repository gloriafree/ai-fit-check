import SwiftUI

struct TryOnView: View {
    let clothingImage: Data
    let isLoading: Bool
    let result: Data?
    let error: String?
    let onSaveToWardrobe: () -> Void
    let onTryAnother: () -> Void
    let onShare: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            if isLoading {
                LoadingState()
            } else if let error = error {
                ErrorState(message: error)
            } else if let result = result {
                ResultState(
                    resultImage: result,
                    onSaveToWardrobe: onSaveToWardrobe,
                    onShare: onShare,
                    onTryAnother: onTryAnother
                )
            } else {
                EmptyState()
            }
        }
        .padding(16)
    }
}

struct LoadingState: View {
    var body: some View {
        VStack(spacing: 24) {
            Spacer()

            ProgressView()
                .scaleEffect(1.5)
                .tint(.purple)

            VStack(spacing: 8) {
                Text("AI is dressing you...")
                    .font(.headline)
                    .fontWeight(.semibold)

                Text("This usually takes 5-15 seconds")
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct ErrorState: View {
    let message: String

    var body: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: "exclamationmark.circle.fill")
                .font(.system(size: 48))
                .foregroundColor(.red)

            VStack(spacing: 8) {
                Text("Something Went Wrong")
                    .font(.headline)
                    .fontWeight(.semibold)

                Text(message)
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct ResultState: View {
    let resultImage: Data
    let onSaveToWardrobe: () -> Void
    let onShare: () -> Void
    let onTryAnother: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            // Result Image
            if let image = UIImage(data: resultImage) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .cornerRadius(12)
                    .shadow(radius: 4)
            }

            // Action Buttons
            VStack(spacing: 12) {
                Button(action: onSaveToWardrobe) {
                    HStack(spacing: 8) {
                        Image(systemName: "bookmark.fill")
                        Text("Save to Wardrobe")
                        Spacer()
                    }
                    .frame(maxWidth: .infinity)
                    .padding(12)
                    .background(Color.purple)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }

                HStack(spacing: 12) {
                    Button(action: onShare) {
                        HStack(spacing: 6) {
                            Image(systemName: "square.and.arrow.up")
                            Text("Share")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(Color(white: 0.1))
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }

                    Button(action: onTryAnother) {
                        HStack(spacing: 6) {
                            Image(systemName: "arrow.clockwise")
                            Text("Try Another")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(Color(white: 0.1))
                        .foregroundColor(.white)
                        .cornerRadius(8)
                    }
                }
            }

            Spacer()
        }
    }
}

struct EmptyState: View {
    var body: some View {
        VStack(spacing: 16) {
            Spacer()

            Image(systemName: "camera.viewfinder")
                .font(.system(size: 48))
                .foregroundColor(.gray)

            VStack(spacing: 8) {
                Text("Ready to Try On")
                    .font(.headline)
                    .fontWeight(.semibold)

                Text("Pick a clothing image to get started")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview {
    TryOnView(
        clothingImage: Data(),
        isLoading: false,
        result: nil,
        error: nil,
        onSaveToWardrobe: {},
        onTryAnother: {},
        onShare: {}
    )
}
