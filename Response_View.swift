import SwiftUI

struct ResponseView: View {
    @State private var responseData: [String: String] = [:]
    @State private var errorText: String?
    
    var body: some View {
        VStack(spacing: 20) {
            if let errorText = errorText {
                Text("Error: \(errorText)").foregroundColor(.red)
            }
            
            ForEach(responseData.sorted(by: { $0.key < $1.key }), id: \.key) { key, value in
                VStack(alignment: .leading) {
                    Text(key).font(.headline)
                    Text(value)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                }
            }
            
            Button("Fetch from Flask") {
                fetchFromBackend()
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(10)
            
            Spacer()
        }
        .padding()
    }
    
    func fetchFromBackend() {
        guard let url = URL(string: "http://34.194.202.42:5000/verify") else {
            self.errorText = "Invalid URL"
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.errorText = error.localizedDescription
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    self.errorText = "No data received"
                }
                return
            }
            
            do {
                if let json = try JSONSerialization.jsonObject(with: data) as? [String: String] {
                    DispatchQueue.main.async {
                        self.responseData = json
                    }
                } else {
                    DispatchQueue.main.async {
                        self.errorText = "Invalid JSON format"
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    self.errorText = "JSON parsing failed: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}
