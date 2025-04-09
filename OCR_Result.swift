import SwiftUI

struct OCRResultView: View {
    @State private var serverResponse: String = "Waiting for response..."
    var selectedFileURL: URL?
    let recognizedText: String
    
    var body: some View {
        VStack(spacing: 20) {
            Text("OCR Results:")
                .font(.headline)
            
            ScrollView {
                Text(recognizedText)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            
            Divider()
            
            Text("Server Response:")
                .font(.headline)
            
            ScrollView {
                Text(serverResponse)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.yellow.opacity(0.2))
                    .cornerRadius(10)
            }
            
            Button(action: {
                if let fileURL = selectedFileURL {
                    uploadFile(fileURL: fileURL)
                } else {
                    serverResponse = "No file selected!"
                }
            }) {
                Text("Send to Python")
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("OCR Results")
    }
    
    /*/// Function to upload file to Flask
    func uploadFile(fileURL: URL) {
        let url = URL(string: "http://34.204.5.67:5000/upload")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST, GET"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        let fileName = fileURL.lastPathComponent
        let mimeType = "application/pdf" // Adjust the mime type if it's an image
        
        // File data
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        
        if let fileData = try? Data(contentsOf: fileURL) {
            body.append(fileData)
        }
        
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        // Send request
        let task = URLSession.shared.uploadTask(with: request, from: body) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.serverResponse = "Error: \(error.localizedDescription)"
                }
                return
            }
            
            if let data = data, let responseString = String(data: data, encoding: .utf8) {
                DispatchQueue.main.async {
                    self.serverResponse = "Python Response: \(responseString)"
                }
            }
        }
        
        task.resume()*/
    func uploadFile(fileURL: URL) {
        let url = URL(string: "https://34.194.202.42:5000/upload")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        let fileName = fileURL.lastPathComponent
        let mimeType = "application/pdf"
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        
        if let fileData = try? Data(contentsOf: fileURL) {
            body.append(fileData)
        }
        
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        let task = URLSession.shared.uploadTask(with: request, from: body) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    self.serverResponse = "Error: \(error.localizedDescription)"
                    print("Upload Error: \(error)")
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("Status code: \(httpResponse.statusCode)")
                    print("Headers: \(httpResponse.allHeaderFields)")
                    
                    if httpResponse.statusCode != 200 {
                        self.serverResponse = "Server Error: \(httpResponse.statusCode)"
                        return
                    }
                }
                
                if let data = data, let responseString = String(data: data, encoding: .utf8) {
                    self.serverResponse = "Python Response: \(responseString)"
                    print("Server Response: \(responseString)")
                } else {
                    self.serverResponse = "No response or invalid data from server."
                    print("Empty or bad response from server.")
                }
            }
        }
        task.resume()
    
    }
}
