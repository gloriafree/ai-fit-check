import SwiftUI
import PhotosUI

struct ProfileView: View {
    @State private var userProfile: UserProfile = UserProfile()
    @State private var showingImagePicker = false
    @State private var selectedImage: UIImage?
    @State private var serverURL: String = "http://localhost:8000"
    @State private var isSaving = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Profile Photo Section
                    VStack(spacing: 16) {
                        Text("Your Profile Photo")
                            .font(.headline)
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity, alignment: .leading)

                        VStack(spacing: 16) {
                            // Profile Photo Preview
                            if let imageData = userProfile.personImage,
                               let image = UIImage(data: imageData)
                            {
                                Image(uiImage: image)
                                    .resizable()
                                    .scaledToFill()
                                    .frame(height: 250)
                                    .clipped()
                                    .cornerRadius(12)
                            } else {
                                ZStack {
                                    Rectangle()
                                        .fill(Color(white: 0.1))

                                    VStack(spacing: 8) {
                                        Image(systemName: "person.crop.square.fill")
                                            .font(.system(size: 40))
                                            .foregroundColor(.gray)
                                        Text("No Photo")
                                            .font(.subheadline)
                                            .foregroundColor(.gray)
                                    }
                                }
                                .frame(height: 250)
                                .cornerRadius(12)
                            }

                            Button(action: { showingImagePicker = true }) {
                                HStack(spacing: 8) {
                                    Image(systemName: "photo.fill")
                                    Text("Update Photo")
                                    Spacer()
                                }
                                .frame(maxWidth: .infinity)
                                .padding(12)
                                .background(Color.purple)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                            }
                        }

                        // Photography Tips
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Tips for Best Results")
                                .font(.subheadline)
                                .fontWeight(.semibold)

                            VStack(alignment: .leading, spacing: 8) {
                                TipRow(icon: "sun.max.fill", text: "Use natural or bright lighting")
                                TipRow(icon: "camera.fill", text: "Full body, straight pose facing camera")
                                TipRow(icon: "background", text: "Plain or simple background")
                                TipRow(icon: "hands.and.sparkles", text: "Wear fitted clothing for accuracy")
                            }
                        }
                        .padding(12)
                        .background(Color(white: 0.05))
                        .cornerRadius(8)
                    }

                    Divider()

                    // Settings Section
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Settings")
                            .font(.headline)
                            .fontWeight(.semibold)

                        VStack(alignment: .leading, spacing: 8) {
                            Text("Server URL")
                                .font(.subheadline)
                                .foregroundColor(.gray)

                            HStack(spacing: 8) {
                                TextField("http://localhost:8000", text: $serverURL)
                                    .textFieldStyle(.roundedBorder)
                                    .font(.caption)
                                    .textInputAutocapitalization(.never)
                                    .autocorrectionDisabled(true)

                                Button(action: saveSettings) {
                                    if isSaving {
                                        ProgressView()
                                            .scaleEffect(0.8)
                                    } else {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundColor(.green)
                                    }
                                }
                                .disabled(isSaving)
                            }
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            Text("Account Name")
                                .font(.subheadline)
                                .foregroundColor(.gray)

                            TextField("Your name", text: $userProfile.name)
                                .textFieldStyle(.roundedBorder)
                                .font(.subheadline)
                        }
                    }

                    // App Info
                    VStack(alignment: .leading, spacing: 12) {
                        Text("About")
                            .font(.headline)
                            .fontWeight(.semibold)

                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Version")
                                    .foregroundColor(.gray)
                                Spacer()
                                Text("1.0.0")
                                    .fontWeight(.semibold)
                            }

                            HStack {
                                Text("iOS Support")
                                    .foregroundColor(.gray)
                                Spacer()
                                Text("16.0+")
                                    .fontWeight(.semibold)
                            }
                        }
                        .padding(12)
                        .background(Color(white: 0.05))
                        .cornerRadius(8)
                    }

                    Spacer()
                }
                .padding(16)
            }
            .navigationTitle("Profile")
            .sheet(isPresented: $showingImagePicker) {
                PhotoPickerForProfile(image: $selectedImage)
            }
            .onChange(of: selectedImage) { _, newImage in
                if let newImage = newImage {
                    if let imageData = ImageProcessor.optimizeImageData(newImage) {
                        userProfile.personImage = imageData
                        Task {
                            do {
                                let apiService = await APIService.shared
                                try await apiService.uploadPersonImage(image: imageData)
                            } catch {
                                print("Failed to upload person image: \(error)")
                            }
                        }
                        saveProfile()
                    }
                }
            }
            .onAppear {
                loadProfile()
                loadServerURL()
            }
        }
    }

    private func saveSettings() {
        isSaving = true
        Task {
            let apiService = await APIService.shared
            await apiService.setServerURL(serverURL)
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                isSaving = false
            }
        }
    }

    private func saveProfile() {
        Task {
            let apiService = await APIService.shared
            await apiService.saveUserProfile(userProfile)
        }
    }

    private func loadProfile() {
        Task {
            let apiService = await APIService.shared
            userProfile = await apiService.getUserProfile()
        }
    }

    private func loadServerURL() {
        if let saved = UserDefaults.standard.string(forKey: "serverURL") {
            serverURL = saved
        }
    }
}

struct TipRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(.purple)
                .frame(width: 24)

            Text(text)
                .font(.caption)
                .foregroundColor(.gray)
        }
    }
}

struct PhotoPickerForProfile: UIViewControllerRepresentable {
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
        let parent: PhotoPickerForProfile

        init(_ parent: PhotoPickerForProfile) {
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

#Preview {
    ProfileView()
}
