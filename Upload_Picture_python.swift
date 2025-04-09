import Foundation

extension Data {
    mutating func append(_ string: String) {
        if let data = string.data(using: .utf8) {
            append(data)
        }
    }
}

func uploadPDF(to urlString: String, fileURL: URL, completion: @escaping ([String: Any]?, String?) -> Void) {
    guard let url = URL(string: urlString) else {
        completion(nil, "❌ Invalid URL")
        return
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    
    let boundary = "Boundary-\(UUID().uuidString)"
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
    
    var body = Data()
    let filename = fileURL.lastPathComponent
    let mimetype = "application/pdf"
    
    body.append("--\(boundary)\r\n")
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n")
    body.append("Content-Type: \(mimetype)\r\n\r\n")
    
    do {
        let fileData = try Data(contentsOf: fileURL)
        body.append(fileData)
    } catch {
        completion(nil, "❌ Failed to read PDF: \(error.localizedDescription)")
        return
    }
    
    body.append("\r\n--\(boundary)--\r\n")
    request.httpBody = body
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion(nil, "❌ Upload failed: \(error.localizedDescription)")
            return
        }
        
        guard let data = data else {
            completion(nil, "❌ No response data")
            return
        }
        
        do {
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                completion(json, nil)
            } else {
                completion(nil, "❌ Could not parse JSON")
            }
        } catch {
            completion(nil, "❌ JSON parsing error: \(error.localizedDescription)")
        }
    }.resume()
}
