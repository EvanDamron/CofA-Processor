import SwiftUI

struct ChatGPTResultView: View {
    let result: [String: Any]
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                ForEach(result.sorted(by: { $0.key < $1.key }), id: \.key) { key, value in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(key.capitalized)
                            .font(.headline)
                        Text("\(value)")
                            .font(.body)
                            .padding(8)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(8)
                    }
                }
                
                Button("Save") {
                    print("✅ Data saved or sent to database")
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color.green)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            .padding()
        }
        .navigationTitle("ChatGPT Result")
    }
}
