import SwiftUI
import PhotosUI

struct HomeView: View {
    @State private var showingImagePicker = false
    @State private var selectedImage: UIImage?
    @State private var isLoading = false
    @State private var tryOnResult: Data?
    @State private var error: String?
    @State private var recentItems: [WardrobeItem] = []

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(spacing: 8) {
                        Image(systemName: "sparkles")
                            .font(.system(size: 40))
                            .foregroundColor(.purple)

                        Text("AI Fit Check")
                            .font(.title)
                            .fontWeight(.bold)

                        Text("Virtual Try-On Magic")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 20)

                    // How to Use Section
                    VStack(alignment: .leading, spacing: 12) {
                        Text("How to Use")
                            .font(.headline)
                            .fontWeight(.semibold)

                        VStack(alignment: .leading, spacing: 12) {
                            HowToStep(number: "1", text: "Browse any shopping app (Safari, Instagram, Taobao...)")
                            HowToStep(number: "2", text: "Tap Share → select \"AI Fit Check\"")
                            HowToStep(number: "3", text: "Instantly see yourself wearing that item")
                            HowToStep(number: "4", text: "Save to your digital wardrobe")
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
                    .background(Color(white: 0.1))
                    .cornerRadius(12)

                    // Quick Try-On Button
                    Button(action: { showingImagePicker = true }) {
                        HStack(spacing: 8) {
                            Image(systemName: "photo.fill")
                            Text("Quick Try-On")
                            Spacer()
                            Image(systemName: "arrow.right")
                        }
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(Color.purple)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }

                    // Recent Try-Ons
                    if !recentItems.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Recent Try-Ons")
                                .font(.headline)
                                .fontWeight(.semibold)

                            LazyVGrid(
                                columns: [GridItem(.flexible()), GridItem(.flexible())],
                                spacing: 12
                            ) {
                                ForEach(recentItems.prefix(4), id: \.id) { item in
                                    NavigationLink(destination: TryOnDetailView(item: item)) {
                                        RecentTryOnCard(item: item)
                                    }
                                }
                            }
                        }
                    }

                    Spacer()
                }
                .padding(16)
            }
            .navigationTitle("Home")
            .sheet(isPresented: $showingImagePicker) {
                PhotoPicker(image: $selectedImage)
            }
            .onChange(of: selectedImage) { _, newImage in
                if let newImage = newImage {
                    performTryOn(image: newImage)
                }
            }
            .onAppear {
                loadRecentItems()
            }
        }
        .overlay {
            if isLoading {
                LoadingOverlay()
            }
        }
        .alert("Error", isPresented: .constant(error != nil), actions: {
            Button("OK") { error = nil }
        }, message: {
            Text(error ?? "")
        })
    }

    private func performTryOn(image: UIImage) {
        isLoading = true
        error = nil

        Task {
            do {
                guard let imageData = ImageProcessor.optimizeImageData(image) else {
                    error = "Failed to process image"
                    isLoading = false
                    return
                }

                let apiService = await APIService.shared
                let userProfile = await apiService.getUserProfile()

                let resultData = try await apiService.tryOn(
                    clothingImage: imageData,
                    personImage: userProfile.personImage
                )

                tryOnResult = resultData
                selectedImage = nil

                // Navigate to result
                isLoading = false
            } catch {
                self.error = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func loadRecentItems() {
        Task {
            do {
                let apiService = await APIService.shared
                recentItems = try await apiService.getWardrobe().sorted { $0.date > $1.date }
            } catch {
                print("Failed to load wardrobe: \(error)")
            }
        }
    }
}

struct HowToStep: View {
    let number: String
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Text(number)
                .font(.headline)
                .fontWeight(.bold)
                .frame(width: 32, height: 32)
                .background(Color.purple)
                .cornerRadius(6)
                .foregroundColor(.white)

            Text(text)
                .font(.subheadline)
                .lineLimit(3)

            Spacer()
        }
    }
}

struct RecentTryOnCard: View {
    let item: WardrobeItem

    var body: some View {
        VStack(spacing: 0) {
            if let image = UIImage(data: item.tryonResult) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
                    .frame(height: 180)
                    .clipped()
            } else {
                Rectangle()
                    .fill(Color(white: 0.1))
                    .frame(height: 180)
            }

            VStack(alignment: .leading, spacing: 4) {
                Text(item.category)
                    .font(.caption)
                    .foregroundColor(.gray)

                Text(item.date.formatted(date: .abbreviated, time: .omitted))
                    .font(.caption2)
                    .foregroundColor(.gray)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(8)
            .background(Color(white: 0.05))
        }
        .cornerRadius(8)
        .clipped()
    }
}

struct LoadingOverlay: View {
    var body: some View {
        ZStack {
            Color.black.opacity(0.4)
                .ignoresSafeArea()

            VStack(spacing: 16) {
                ProgressView()
                    .scaleEffect(1.5)

                Text("AI is dressing you...")
                    .font(.subheadline)
                    .foregroundColor(.white)
            }
            .padding(32)
            .background(Color(white: 0.1))
            .cornerRadius(12)
        }
    }
}

struct PhotoPicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .photoLibrary
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_: UIImagePickerController, context _: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: PhotoPicker

        init(_ parent: PhotoPicker) {
            self.parent = parent
        }

        func imagePickerController(
            _: UIImagePickerController,
            didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
        ) {
            if let image = info[.originalImage] as? UIImage {
                parent.image = image
            }
            parent.dismiss()
        }
    }
}

struct TryOnDetailView: View {
    let item: WardrobeItem

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                if let image = UIImage(data: item.tryonResult) {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                        .cornerRadius(12)
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text(item.category)
                        .font(.headline)
                    Text(item.date.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                Spacer()
            }
            .padding(16)
        }
        .navigationTitle("Try-On Result")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    HomeView()
}
