import SwiftUI
import PDFKit
import Vision

struct FileDetailView: View {
    let fileURL: URL
    @State private var fileContent: String?
    @State private var serverMessage: String?
    @State private var pdfDocument: PDFDocument?
    @State private var recognizedText: String = "No content loaded" // For OCR results
    @State private var isOCRComplete: Bool = false // Flag to indicate OCR completion
    @State private var resultFromServer: [String: Any] = [:]
    @State private var showResult = false
    @State private var errorMessage: String?
    @State private var goToEditor = false
    //@State private var resultFromServer: [String: Any] = [:]
    
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
                ScrollView {
                    Text(content)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            } else {
                Text("No content loaded")
                    .padding()
            }
           /* uploadPDF(to: "http://34.194.202.42:5000/upload", fileURL: fileURL) { result, error in
                DispatchQueue.main.async {
                    if let result = result {
                        self.resultFromServer = result
                        self.isOCRComplete = true
                    } else if let error = error {
                        self.errorMessage = error
                    }
                }
            }*/
            
            if isOCRComplete {
                Button("Continue to Accuracy Checker") {
                    goToEditor = true
                }
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
                
                NavigationLink(
                    destination: AccuracyCheckerViewExternal(pdfURL: fileURL, initialJSON: resultFromServer),
                    isActive: $goToEditor
                ) {
                    EmptyView()
                }
            }
            NavigationLink(
                destination: ChatGPTResultView(result: resultFromServer),
                isActive: $showResult
            ) {
                EmptyView()
            }
            
            if let error = errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .padding()
            }
            
            // Navigate to Accuracy Checker (external view)
            
            
            Spacer()
        }
        
        .navigationTitle("File Details")
        .onAppear {
            uploadPDF(to: "http://34.194.202.42:5000/upload", fileURL: fileURL) { result, error in
                DispatchQueue.main.async {
                    if let result = result {
                        self.resultFromServer = result
                        self.isOCRComplete = true
                    } else if let error = error {
                        self.errorMessage = error
                    }
                }
            }
        }
        .padding()
        .navigationTitle("File Details")
    }
    
    func loadFileContentAndPerformOCR() {
        let fileExtension = fileURL.pathExtension.lowercased()
        
        if !FileManager.default.fileExists(atPath: fileURL.path) {
            print("File does not exist at path: \(fileURL.path)")
            self.fileContent = "File does not exist."
            return
        }
        
        if fileExtension == "pdf" {
            if let pdf = PDFDocument(url: fileURL) {
                self.pdfDocument = pdf
                self.fileContent = nil
                print("PDF file loaded successfully.")
                
                if let firstPage = pdf.page(at: 0) {
                    let pdfImage = firstPage.thumbnail(of: CGSize(width: 300, height: 400), for: .mediaBox)
                    performOCR(on: pdfImage)
                }
            } else {
                print("Failed to load PDF document.")
                self.fileContent = "Failed to load PDF."
            }
        } else if fileExtension == "txt" {
            do {
                let content = try String(contentsOf: fileURL, encoding: .utf8)
                self.fileContent = content
                print("Text file loaded successfully.")
            } catch {
                print("Failed to read text file: \(error.localizedDescription)")
                self.fileContent = "Failed to load text content."
            }
        } else {
            self.fileContent = "Unsupported file type"
            print("Unsupported file type: \(fileExtension)")
        }
    }
    
    func performOCR(on image: UIImage) {
        guard let ciImage = CIImage(image: image) else {
            print("Failed to convert UIImage to CIImage")
            return
        }
        
        let request = VNRecognizeTextRequest(completionHandler: handleDetectedText)
        request.recognitionLevel = .accurate
        
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
        
        recognizedText = recognizedString.isEmpty ? "No text found" : recognizedString
        isOCRComplete = true
    }
}
