import SwiftUI
import PDFKit

struct AccuracyCheckerViewExternal: View {
    let pdfURL: URL // PDF to verify against
    
    @State private var jsonData: [String: Any] = [:] // Original JSON from server
    @State private var textFields: [String: String] = [:] // Editable fields
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var submissionSuccess = false
    
    var body: some View {
        HStack(alignment: .top) {
            // PDF viewer
            PDFKitView(pdfDocument: PDFDocument(url: pdfURL)!)
                .frame(width: 400)
            
            // Right pane: dynamic form or loading/error
            if isLoading {
                ProgressView("Loading JSON...")
                    .padding()
            } else if let errorMessage = errorMessage {
                Text("Error: \(errorMessage)")
                    .foregroundColor(.red)
                    .padding()
            } else {
                ScrollView {
                    VStack(alignment: .leading, spacing: 15) {
                        ForEach(jsonData.keys.sorted(), id: \.self) { key in
                            VStack(alignment: .leading) {
                                Text(key.capitalized)
                                    .font(.headline)
                                
                                if let value = jsonData[key] {
                                    if let array = value as? [Any] {
                                        ForEach(array.indices, id: \.self) { i in
                                            TextField("\(key) \(i+1)", text: Binding(
                                                get: { textFields["\(key)_\(i)"] ?? "" },
                                                set: { textFields["\(key)_\(i)"] = $0 }
                                            ))
                                            .textFieldStyle(RoundedBorderTextFieldStyle())
                                        }
                                    } else {
                                        TextField("\(key)", text: Binding(
                                            get: { textFields[key] ?? "" },
                                            set: { textFields[key] = $0 }
                                        ))
                                        .textFieldStyle(RoundedBorderTextFieldStyle())
                                    }
                                }
                            }
                        }
                        
                        Button("Approve & Submit") {
                            submitJSON()
                        }
                        .padding()
                        .background(Color.green)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .padding()
                }
            }
        }
        .onAppear {
            fetchJSON()
        }
        .navigationTitle("Accuracy Checker")
        .alert(isPresented: $submissionSuccess) {
            Alert(title: Text("Success"), message: Text("Data has been submitted successfully!"), dismissButton: .default(Text("OK")))
        }
    }
    
    func fetchJSON() {
        guard let encodedName = pdfURL.lastPathComponent.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let url = URL(string: "http://34.204.5.67:5000/upload?filename=\(encodedName)") else {
            errorMessage = "Invalid URL."
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    errorMessage = error.localizedDescription
                } else if let data = data {
                    do {
                        if let decoded = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                            jsonData = decoded
                            for (key, value) in decoded {
                                if let array = value as? [Any] {
                                    for i in array.indices {
                                        textFields["\(key)_\(i)"] = String(describing: array[i])
                                    }
                                } else {
                                    textFields[key] = String(describing: value)
                                }
                            }
                        }
                    } catch {
                        errorMessage = "Failed to parse JSON."
                    }
                }
                isLoading = false
            }
        }.resume()
    }
    
    func submitJSON() {
        var updatedJSON: [String: Any] = [:]
        
        for (key, value) in jsonData {
            if value is [Any] {
                var array: [String] = []
                for i in 0..<(value as! [Any]).count {
                    array.append(textFields["\(key)_\(i)"] ?? "")
                }
                updatedJSON[key] = array
            } else {
                updatedJSON[key] = textFields[key] ?? ""
            }
        }
        
        guard let url = URL(string: "http://34.204.5.67:5000/verify"),
              let jsonData = try? JSONSerialization.data(withJSONObject: updatedJSON) else {
            errorMessage = "Failed to encode JSON."
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { _, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    errorMessage = "Submit error: \(error.localizedDescription)"
                } else {
                    errorMessage = nil
                    submissionSuccess = true
                }
            }
        }.resume()
    }
}
