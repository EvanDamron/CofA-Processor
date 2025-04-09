import SwiftUI
import Vision
import PDFKit
import UIKit

class OCRViewModel: ObservableObject {
    @Published var recognizedText: String = "No content loaded"
    @Published var pdfDocument: PDFDocument?
    
    func performOCR(fileURL: URL) {
        let fileExtension = fileURL.pathExtension.lowercased()
        
        // Check if the file is a PDF
        if fileExtension == "pdf" {
            // Extract the first page of the PDF as an image
            if let pdfDocument = PDFDocument(url: fileURL),
               let pdfPage = pdfDocument.page(at: 0) {
                let pdfImage = pdfPage.thumbnail(of: CGSize(width: 300, height: 400), for: .mediaBox)
                recognizeText(from: pdfImage)
            }
        } else {
            // Handle other file types (images)
            if let image = UIImage(contentsOfFile: fileURL.path) {
                recognizeText(from: image)
            }
        }
    }
    
    private func recognizeText(from image: UIImage) {
        // Convert image to CIImage
        guard let ciImage = CIImage(image: image) else {
            print("Failed to convert UIImage to CIImage")
            return
        }
        
        // Create a request for recognizing text
        let request = VNRecognizeTextRequest(completionHandler: handleDetectedText)
        request.recognitionLevel = .accurate
        
        // Perform the OCR request
        let requestHandler = VNImageRequestHandler(ciImage: ciImage, options: [:])
        do {
            try requestHandler.perform([request])
        } catch {
            print("Failed to perform OCR: \(error.localizedDescription)")
            recognizedText = "OCR failed"
        }
    }
    
    private func handleDetectedText(request: VNRequest, error: Error?) {
        if let error = error {
            print("OCR error: \(error.localizedDescription)")
            recognizedText = "OCR error"
            return
        }
        
        // Extract the recognized text
        guard let observations = request.results as? [VNRecognizedTextObservation] else {
            recognizedText = "No text found"
            return
        }
        
        var recognizedString = ""
        for observation in observations {
            recognizedString += observation.topCandidates(1).first?.string ?? ""
            recognizedString += "\n"
        }
        
        // Update the recognized text
        recognizedText = recognizedString.isEmpty ? "No text found" : recognizedString
    }
}
