import SwiftUI
import UniformTypeIdentifiers
import UIKit
import PDFKit

class FilePicker: NSObject, UIDocumentPickerDelegate {
    static let shared = FilePicker()
    private var completionHandler: ((URL?) -> Void)?
    
    func pickDocument(completion: @escaping (URL?) -> Void) {
        self.completionHandler = completion
        let documentPicker = UIDocumentPickerViewController(forOpeningContentTypes: [UTType.item])
        documentPicker.delegate = self
        documentPicker.allowsMultipleSelection = false
        
        if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = scene.windows.first,
           let rootVC = window.rootViewController {
            rootVC.present(documentPicker, animated: true)
        }
    }
    
    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        if let url = urls.first {
            // Start accessing the file with security scoped resource
            if url.startAccessingSecurityScopedResource() {
                let destinationURL = getDocumentsDirectory().appendingPathComponent(url.lastPathComponent)
                do {
                    // Remove any existing file at the destination path
                    try FileManager.default.removeItem(at: destinationURL)
                } catch {
                    print("No existing file at destination path.")
                }
                do {
                    // Copy the selected file to the destination
                    try FileManager.default.copyItem(at: url, to: destinationURL)
                    self.completionHandler?(destinationURL)
                } catch {
                    print("Error copying file: \(error.localizedDescription)")
                    self.completionHandler?(nil)
                }
                // Stop accessing the file after the operation is complete
                url.stopAccessingSecurityScopedResource()
            } else {
                print("Failed to access file at: \(url.path)")
                self.completionHandler?(nil)
            }
        }
    }
    
    func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
        completionHandler?(nil)
    }
    
    private func getDocumentsDirectory() -> URL {
        let paths = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        return paths[0]
    }
}

struct ContentView: View {
    @State private var selectedFileURL: URL?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Upload File Button
                Button(action: {
                    FilePicker.shared.pickDocument { url in
                        if let url = url {
                            self.selectedFileURL = url
                            print("Selected file: \(url.lastPathComponent)")
                        }
                    }
                }) {
                    Text("Upload File")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                
                // Show Selected File Name
                if let url = selectedFileURL {
                    Text("Selected: \(url.lastPathComponent)")
                        .padding()
                }
                
                // Next Button - Navigate to FileDetailView
                if selectedFileURL != nil {
                    NavigationLink(destination: FileDetailView(fileURL: selectedFileURL!)) {
                        Text("Next")
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                }
            }
            .padding()
            .navigationBarTitleDisplayMode(.inline)
            .toolbar{
                ToolbarItem(placement: .principal){
                    Text("Valvoline")
                        .font(.system(size: 30, weight: .bold))
                        .foregroundColor(.deepNavyBlue)
                        .frame(maxWidth: .infinity)
                }
            }
        }
    }
}

/*struct FileDetailView: View {
    let fileURL: URL
    @StateObject private var ocrViewModel = OCRViewModel()
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Uploaded File:")
                .font(.headline)
            Text(fileURL.lastPathComponent)
                .font(.subheadline)
                .foregroundColor(.blue)
            
            // If PDF, display PDF
            if let pdfDocument = ocrViewModel.pdfDocument {
                PDFKitView(pdfDocument: pdfDocument)
                    .frame(height: 500)
            } else if !ocrViewModel.recognizedText.isEmpty {
                // Display the recognized text if OCR was performed
                ScrollView {
                    Text(ocrViewModel.recognizedText)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            } else {
                Text("No content loaded")
                    .padding()
            }
            
            // "Continue" button to trigger OCR
            Button(action: {
                loadFileContent()
                ocrViewModel.performOCR(fileURL: fileURL)
            }) {
                Text("Continue")
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("File Details")
    }
    
    func loadFileContent() {
        let fileExtension = fileURL.pathExtension.lowercased()
        
        // Check if file exists
        if !FileManager.default.fileExists(atPath: fileURL.path) {
            print("File does not exist at path: \(fileURL.path)")
            return
        }
        
        // Handle PDF files
        if fileExtension == "pdf" {
            if let pdf = PDFDocument(url: fileURL) {
                ocrViewModel.pdfDocument = pdf
                print("PDF file loaded successfully.")
            } else {
                print("Failed to load PDF document.")
            }
        }
        // Handle text files
        else if fileExtension == "txt" {
            do {
                _ = try String(contentsOf: fileURL, encoding: .utf8)
                print("Text file loaded successfully.")
            } catch {
                print("Failed to read text file: \(error.localizedDescription)")
            }
        }
        // Add other types of file handling here if needed
        else {
            print("Unsupported file type: \(fileExtension)")
        }
    }

}*/

struct PDFKitView: UIViewRepresentable {
    let pdfDocument: PDFDocument
    
    func makeUIView(context: Context) -> PDFView {
        let pdfView = PDFView()
        pdfView.autoScales = true
        return pdfView
    }
    
    func updateUIView(_ uiView: PDFView, context: Context) {
        uiView.document = pdfDocument
    }
}
