import UIKit

struct ImageProcessor {
    static let maxDimension: CGFloat = 1024

    // MARK: - Image Conversion
    static func dataToUIImage(_ data: Data) -> UIImage? {
        UIImage(data: data)
    }

    static func uiImageToData(_ image: UIImage, quality: CGFloat = 0.8) -> Data? {
        image.jpegData(compressionQuality: quality)
    }

    // MARK: - Image Resizing
    static func resizeImage(_ image: UIImage, maxDimension: CGFloat = maxDimension) -> UIImage {
        let scale = image.size.width > image.size.height
            ? maxDimension / image.size.width
            : maxDimension / image.size.height

        guard scale < 1 else { return image }

        let newSize = CGSize(
            width: image.size.width * scale,
            height: image.size.height * scale
        )

        let renderer = UIGraphicsImageRenderer(size: newSize)
        return renderer.image { _ in
            image.draw(in: CGRect(origin: .zero, size: newSize))
        }
    }

    // MARK: - Center Crop
    static func centerCropImage(_ image: UIImage, to size: CGSize) -> UIImage {
        let scale = max(size.width / image.size.width, size.height / image.size.height)
        let scaledSize = CGSize(width: image.size.width * scale, height: image.size.height * scale)

        let x = (scaledSize.width - size.width) / 2
        let y = (scaledSize.height - size.height) / 2

        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { context in
            image.draw(at: CGPoint(x: -x, y: -y))
        }
    }

    // MARK: - Optimized Data for Upload
    static func optimizeImageData(_ image: UIImage, compressionQuality: CGFloat = 0.7) -> Data? {
        let resized = resizeImage(image, maxDimension: maxDimension)
        return uiImageToData(resized, quality: compressionQuality)
    }

    // MARK: - Generate Thumbnail
    static func generateThumbnail(from image: UIImage, size: CGSize = CGSize(width: 200, height: 200)) -> UIImage {
        centerCropImage(image, to: size)
    }
}
