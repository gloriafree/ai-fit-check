import UIKit
import Social

class ShareViewController: UIViewController {
    private var attachmentImage: UIImage?
    private var tryonResult: UIImage?
    private var isLoading = false

    private lazy var containerView: UIView = {
        let view = UIView()
        view.backgroundColor = UIColor(white: 0.1, alpha: 1)
        view.layer.cornerRadius = 12
        view.clipsToBounds = true
        return view
    }()

    private lazy var imagePreview: UIImageView = {
        let iv = UIImageView()
        iv.contentMode = .scaleAspectFill
        iv.clipsToBounds = true
        return iv
    }()

    private lazy var loadingIndicator: UIActivityIndicatorView = {
        let spinner = UIActivityIndicatorView(style: .medium)
        spinner.color = UIColor(hue: 0.75, saturation: 1, brightness: 0.9, alpha: 1)
        return spinner
    }()

    private lazy var statusLabel: UILabel = {
        let label = UILabel()
        label.font = UIFont.systemFont(ofSize: 14, weight: .medium)
        label.textColor = .white
        label.textAlignment = .center
        label.numberOfLines = 2
        return label
    }()

    private lazy var tryOnButton: UIButton = {
        var config = UIButton.Configuration.filled()
        config.baseBackgroundColor = UIColor(hue: 0.75, saturation: 1, brightness: 0.9, alpha: 1)
        config.baseForegroundColor = .white
        config.title = "Try On"
        config.image = UIImage(systemName: "sparkles")
        config.imagePadding = 8
        var container = AttributeContainer()
        container.font = UIFont.systemFont(ofSize: 14, weight: .semibold)
        config.attributedTitle = AttributedString("Try On", attributes: container)

        let button = UIButton(configuration: config)
        button.addTarget(self, action: #selector(tryOnTapped), for: .touchUpInside)
        return button
    }()

    private lazy var saveButton: UIButton = {
        var config = UIButton.Configuration.filled()
        config.baseBackgroundColor = UIColor(white: 0.2, alpha: 1)
        config.baseForegroundColor = .white
        config.title = "Save"
        config.image = UIImage(systemName: "bookmark.fill")
        config.imagePadding = 6
        var container = AttributeContainer()
        container.font = UIFont.systemFont(ofSize: 14, weight: .semibold)
        config.attributedTitle = AttributedString("Save", attributes: container)

        let button = UIButton(configuration: config)
        button.addTarget(self, action: #selector(saveTapped), for: .touchUpInside)
        button.isHidden = true
        return button
    }()

    private lazy var doneButton: UIButton = {
        var config = UIButton.Configuration.filled()
        config.baseBackgroundColor = UIColor(white: 0.2, alpha: 1)
        config.baseForegroundColor = .white
        config.title = "Done"
        config.image = UIImage(systemName: "xmark")
        config.imagePadding = 6
        var container = AttributeContainer()
        container.font = UIFont.systemFont(ofSize: 14, weight: .semibold)
        config.attributedTitle = AttributedString("Done", attributes: container)

        let button = UIButton(configuration: config)
        button.addTarget(self, action: #selector(doneTapped), for: .touchUpInside)
        return button
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        extractImage()
    }

    private func setupUI() {
        view.backgroundColor = UIColor(white: 0, alpha: 0.4)

        view.addSubview(containerView)
        containerView.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            containerView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            containerView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            containerView.widthAnchor.constraint(equalToConstant: 300),
            containerView.heightAnchor.constraint(equalToConstant: 400)
        ])

        // Image Preview
        containerView.addSubview(imagePreview)
        imagePreview.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            imagePreview.topAnchor.constraint(equalTo: containerView.topAnchor),
            imagePreview.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            imagePreview.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            imagePreview.heightAnchor.constraint(equalToConstant: 220)
        ])

        // Status/Loading
        containerView.addSubview(loadingIndicator)
        containerView.addSubview(statusLabel)
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        statusLabel.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            loadingIndicator.centerXAnchor.constraint(equalTo: containerView.centerXAnchor),
            loadingIndicator.topAnchor.constraint(equalTo: imagePreview.bottomAnchor, constant: 20),
            statusLabel.centerXAnchor.constraint(equalTo: containerView.centerXAnchor),
            statusLabel.topAnchor.constraint(equalTo: loadingIndicator.bottomAnchor, constant: 12),
            statusLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 16),
            statusLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -16)
        ])

        statusLabel.text = "Ready to try on"

        // Buttons
        let buttonStack = UIStackView(arrangedSubviews: [tryOnButton, saveButton, doneButton])
        buttonStack.axis = .vertical
        buttonStack.spacing = 8
        buttonStack.distribution = .fillEqually
        containerView.addSubview(buttonStack)
        buttonStack.translatesAutoresizingMaskIntoConstraints = false

        NSLayoutConstraint.activate([
            buttonStack.bottomAnchor.constraint(equalTo: containerView.bottomAnchor, constant: -12),
            buttonStack.leadingAnchor.constraint(equalTo: containerView.leadingAnchor, constant: 12),
            buttonStack.trailingAnchor.constraint(equalTo: containerView.trailingAnchor, constant: -12),
            buttonStack.heightAnchor.constraint(equalToConstant: 100)
        ])
    }

    private func extractImage() {
        guard let extensionItem = extensionContext?.inputItems.first as? NSExtensionItem else {
            statusLabel.text = "No image found"
            return
        }

        let itemProvider = extensionItem.attachments?.first
        guard itemProvider?.hasItemConformingToTypeIdentifier("public.image") ?? false else {
            statusLabel.text = "Please share an image"
            return
        }

        itemProvider?.loadItem(forTypeIdentifier: "public.image", options: nil) { [weak self] item, error in
            DispatchQueue.main.async {
                if let url = item as? URL {
                    if let data = try? Data(contentsOf: url) {
                        self?.attachmentImage = UIImage(data: data)
                        self?.imagePreview.image = self?.attachmentImage
                    }
                } else if let image = item as? UIImage {
                    self?.attachmentImage = image
                    self?.imagePreview.image = image
                } else {
                    self?.statusLabel.text = "Could not load image"
                }
            }
        }
    }

    @objc private func tryOnTapped() {
        guard !isLoading else { return }
        guard let clothingImage = attachmentImage else {
            statusLabel.text = "No image selected"
            return
        }

        isLoading = true
        tryOnButton.isEnabled = false
        loadingIndicator.startAnimating()
        statusLabel.text = "AI is trying on..."

        Task {
            do {
                guard let imageData = ImageProcessor.optimizeImageData(clothingImage) else {
                    DispatchQueue.main.async {
                        self.statusLabel.text = "Image processing failed"
                        self.isLoading = false
                        self.tryOnButton.isEnabled = true
                        self.loadingIndicator.stopAnimating()
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
                    self.tryonResult = UIImage(data: resultData)
                    self.imagePreview.image = self.tryonResult
                    self.statusLabel.text = "Try-on complete!"
                    self.loadingIndicator.stopAnimating()
                    self.isLoading = false
                    self.tryOnButton.isHidden = true
                    self.saveButton.isHidden = false
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusLabel.text = "Try-on failed"
                    self.loadingIndicator.stopAnimating()
                    self.isLoading = false
                    self.tryOnButton.isEnabled = true
                }
            }
        }
    }

    @objc private func saveTapped() {
        guard let resultImage = tryonResult,
              let resultData = resultImage.jpegData(compressionQuality: 0.8),
              let clothingData = ImageProcessor.optimizeImageData(attachmentImage ?? UIImage()) else {
            statusLabel.text = "Save failed"
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
                    self.statusLabel.text = "Saved to wardrobe!"
                }
            } catch {
                DispatchQueue.main.async {
                    self.statusLabel.text = "Save failed"
                }
            }
        }
    }

    @objc private func doneTapped() {
        extensionContext?.completeRequest(returningItems: nil, completionHandler: nil)
    }
}
