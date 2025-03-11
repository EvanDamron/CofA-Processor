import SwiftUI

struct OCRResultView: View {
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
            
            Spacer()
        }
        .padding()
        .navigationTitle("OCR Results")
    }
}
