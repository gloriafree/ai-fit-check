import SwiftUI

struct WardrobeView: View {
    @State private var items: [WardrobeItem] = []
    @State private var isLoading = true
    @State private var selectedItem: WardrobeItem?
    @State private var showingDeleteConfirm = false
    @State private var itemToDelete: UUID?

    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible())
    ]

    var body: some View {
        NavigationStack {
            Group {
                if items.isEmpty && !isLoading {
                    EmptyWardrobeView()
                } else if isLoading {
                    ProgressView()
                } else {
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: 12) {
                            ForEach(items, id: \.id) { item in
                                NavigationLink(destination: WardrobeItemDetailView(item: item)) {
                                    WardrobeItemCard(item: item)
                                        .contextMenu {
                                            Button(role: .destructive) {
                                                itemToDelete = item.id
                                                showingDeleteConfirm = true
                                            } label: {
                                                Label("Delete", systemImage: "trash")
                                            }
                                        }
                                }
                            }
                        }
                        .padding(16)
                    }
                }
            }
            .navigationTitle("Wardrobe")
            .onAppear {
                loadWardrobe()
            }
            .refreshable {
                loadWardrobe()
            }
        }
        .alert("Delete Item?", isPresented: $showingDeleteConfirm) {
            Button("Delete", role: .destructive) {
                if let id = itemToDelete {
                    deleteItem(id: id)
                }
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This action cannot be undone.")
        }
    }

    private func loadWardrobe() {
        isLoading = true
        Task {
            do {
                let apiService = await APIService.shared
                items = try await apiService.getWardrobe().sorted { $0.date > $1.date }
            } catch {
                print("Failed to load wardrobe: \(error)")
            }
            isLoading = false
        }
    }

    private func deleteItem(id: UUID) {
        Task {
            do {
                let apiService = await APIService.shared
                try await apiService.deleteFromWardrobe(itemID: id)
                items.removeAll { $0.id == id }
            } catch {
                print("Failed to delete item: \(error)")
            }
        }
    }
}

struct WardrobeItemCard: View {
    let item: WardrobeItem

    var body: some View {
        VStack(spacing: 0) {
            if let image = UIImage(data: item.tryonResult) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
                    .frame(height: 200)
                    .clipped()
            } else {
                Rectangle()
                    .fill(Color(white: 0.1))
                    .frame(height: 200)
            }

            VStack(alignment: .leading, spacing: 4) {
                Text(item.category)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.purple)

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

struct WardrobeItemDetailView: View {
    let item: WardrobeItem
    @Environment(\.dismiss) var dismiss

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                if let image = UIImage(data: item.tryonResult) {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                        .cornerRadius(12)
                        .shadow(radius: 4)
                }

                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Category")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text(item.category)
                                .font(.headline)
                        }

                        Spacer()

                        VStack(alignment: .trailing, spacing: 4) {
                            Text("Date")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Text(item.date.formatted(date: .abbreviated, time: .shortened))
                                .font(.headline)
                        }
                    }

                    Divider()

                    // Original Clothing
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Original Clothing")
                            .font(.subheadline)
                            .fontWeight(.semibold)

                        if let clothingImage = UIImage(data: item.clothingImage) {
                            Image(uiImage: clothingImage)
                                .resizable()
                                .scaledToFit()
                                .cornerRadius(8)
                                .frame(height: 150)
                        }
                    }

                    HStack(spacing: 12) {
                        Button(action: { shareResult() }) {
                            HStack(spacing: 6) {
                                Image(systemName: "square.and.arrow.up")
                                Text("Share")
                            }
                            .frame(maxWidth: .infinity)
                            .padding(12)
                            .background(Color.purple)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }

                        Button(action: { dismiss() }) {
                            HStack(spacing: 6) {
                                Image(systemName: "xmark")
                                Text("Close")
                            }
                            .frame(maxWidth: .infinity)
                            .padding(12)
                            .background(Color(white: 0.1))
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                    }
                }
                .padding(16)
                .background(Color(white: 0.05))
                .cornerRadius(12)

                Spacer()
            }
            .padding(16)
        }
        .navigationTitle("Try-On Details")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func shareResult() {
        guard let shareImage = UIImage(data: item.tryonResult) else { return }

        let items = [shareImage]
        let activityVC = UIActivityViewController(activityItems: items, applicationActivities: nil)

        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
            windowScene.windows.first?.rootViewController?.present(activityVC, animated: true)
        }
    }
}

struct EmptyWardrobeView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "hanger")
                .font(.system(size: 48))
                .foregroundColor(.gray)

            VStack(spacing: 8) {
                Text("Your Wardrobe is Empty")
                    .font(.headline)
                    .fontWeight(.semibold)

                Text("Try on clothes using the Share Extension or Home tab to start building your digital wardrobe")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(16)
    }
}

#Preview {
    WardrobeView()
}
