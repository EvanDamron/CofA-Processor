import SwiftUI
import PDFKit
import Vision

struct FileDetailView: View {
    let fileURL: URL
    @State private var fileContent: String?
    @State private var pdfDocument: PDFDocument?
    @State private var recognizedText: String = "No content loaded" // For OCR results
    @State private var isOCRComplete: Bool = false // Flag to indicate OCR completion
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Uploaded File:")
                .font(.headline)
            Text(fileURL.lastPathComponent)
                .font(.subheadline)
                .foregroundColor(.blue)
            
            // If PDF, display PDF
            if let pdfDocument = pdfDocument {
                PDFKitView(pdfDocument: pdfDocument)
                    .frame(height: 500)
            } else if let content = fileContent {
                // Display content for text files
                ScrollView {
                    Text(content)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            } else {
                Text("No content loaded")
                    .padding()
            }
            
            // "Continue" button to trigger OCR
            Button(action: {
                loadFileContentAndPerformOCR()
            }) {
                Text("Continue")
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            
            // If OCR is complete, show a link to the OCRResultView page
            if isOCRComplete {
                NavigationLink(destination: OCRResultView(recognizedText: recognizedText)) {
                    Text("View OCR Results")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("File Details")
    }
    
    func loadFileContentAndPerformOCR() {
        let fileExtension = fileURL.pathExtension.lowercased()
        
        // Check if file exists
        if !FileManager.default.fileExists(atPath: fileURL.path) {
            print("File does not exist at path: \(fileURL.path)")
            self.fileContent = "File does not exist."
            return
        }
        
        // Handle PDF files
        if fileExtension == "pdf" {
            if let pdf = PDFDocument(url: fileURL) {
                self.pdfDocument = pdf
                self.fileContent = nil // Clear text content if it's a PDF
                print("PDF file loaded successfully.")
                
                // Perform OCR on the first page of the PDF
                if let firstPage = pdf.page(at: 0) {
                    let pdfImage = firstPage.thumbnail(of: CGSize(width: 300, height: 400), for: .mediaBox)
                    performOCR(on: pdfImage)
                }
            } else {
                print("Failed to load PDF document.")
                self.fileContent = "Failed to load PDF."
            }
        }
        // Handle text files
        else if fileExtension == "txt" {
            do {
                let content = try String(contentsOf: fileURL, encoding: .utf8)
                self.fileContent = content
                print("Text file loaded successfully.")
            } catch {
                print("Failed to read text file: \(error.localizedDescription)")
                self.fileContent = "Failed to load text content."
            }
        }
        else {
            self.fileContent = "Unsupported file type"
            print("Unsupported file type: \(fileExtension)")
        }
    }
    
    func performOCR(on image: UIImage) {
        // Convert UIImage to CIImage
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
            isOCRComplete = true
        }
    }
    
    func handleDetectedText(request: VNRequest, error: Error?) {
        if let error = error {
            print("OCR error: \(error.localizedDescription)")
            recognizedText = "OCR error"
            isOCRComplete = true
            return
        }
        
        // Extract the recognized text
        guard let observations = request.results as? [VNRecognizedTextObservation] else {
            recognizedText = "No text found"
            isOCRComplete = true
            return
        }
        
        var recognizedString = ""
        for observation in observations {
            recognizedString += observation.topCandidates(1).first?.string ?? ""
            recognizedString += "\n"
        }
        
        // Update the recognized text and set OCR complete flag
        recognizedText = recognizedString.isEmpty ? "No text found" : recognizedString
        isOCRComplete = true
    }
}
