import Foundation

func fetchData() {
    guard let url = URL(string: "http://34.194.202.42:5000/upload") else { return }
    
    let task = URLSession.shared.dataTask(with: url) { data, response, error in
        if let error = error {
            print("Error: \(error)")
            return
        }
        
        if let data = data {
            do {
                let jsonResponse = try JSONSerialization.jsonObject(with: data, options: [])
                print("Response from Flask: \(jsonResponse)")
            } catch {
                print("JSON Parsing Error: \(error)")
            }
        }
    }
    task.resume()
}

