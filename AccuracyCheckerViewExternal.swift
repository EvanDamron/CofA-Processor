import SwiftUI
import PDFKit

struct AccuracyCheckerViewExternal: View {
    let pdfURL: URL
    let initialJSON: [String: Any]
    
    @State private var jsonData: [(key: String, value: Any)] = []
    @State private var textFields: [String: String] = [:]
    @State private var submissionSuccess = false
    @State private var errorMessage: String?
    
    var body: some View {
        HStack(alignment: .top) {
            PDFKitView(pdfDocument: PDFDocument(url: pdfURL)!)
                .frame(width: 400)
            
            ScrollView {
                VStack(alignment: .leading, spacing: 15) {
                    if let errorMessage = errorMessage {
                        Text("Error: \(errorMessage)")
                            .foregroundColor(.red)
                            .padding(.bottom)
                    }
                    
                    ForEach(0..<jsonData.count, id: \.self) { index in
                        let key = jsonData[index].key
                        let value = jsonData[index].value
                        
                        VStack(alignment: .leading) {
                            Text(key.capitalized)
                                .font(.headline)
                            
                            if let array = value as? [Any] {
                                ForEach(0..<array.count, id: \.self) { i in
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
        .navigationTitle("ChatGPT Result")
        .onAppear {
            loadInitialJSON()
        }
        .alert(isPresented: $submissionSuccess) {
            Alert(
                title: Text("Success"),
                message: Text("Data has been submitted successfully!"),
                dismissButton: .default(Text("OK"))
            )
        }
    }
    
    private func loadInitialJSON() {
        jsonData = initialJSON.sorted { $0.key < $1.key }
        for (key, value) in initialJSON {
            if let array = value as? [Any] {
                for i in array.indices {
                    textFields["\(key)_\(i)"] = String(describing: array[i])
                }
            } else {
                textFields[key] = String(describing: value)
            }
        }
    }
    
    private func submitJSON() {
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
        
        guard let url = URL(string: "http://34.194.202.42:5000/verify"),
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
