import SwiftUI

struct ContentView: View {
    @State private var showEditor = false
    @State private var jsonURL: URL?
    @State private var pdfURL: URL?

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("🧪 JSON + PDF Editor Test")
                    .font(.title2)

                Button("Start Editor") {
                    if let json = loadFile(named: "sample.json"),
                       let pdf = loadFile(named: "sample.pdf") {
                        jsonURL = json
                        pdfURL = pdf
                        showEditor = true
                    }
                }
                .buttonStyle(.borderedProminent)
            }
            .navigationDestination(isPresented: $showEditor) {
                if let jsonURL, let pdfURL {
                    JsonPdfEditorView(jsonURL: jsonURL, pdfURL: pdfURL) { updatedJson in
                        print("✅ Updated JSON:", updatedJson)
                    }
                }
            }
        }
    }

    func loadFile(named name: String) -> URL? {
        guard let resource = Bundle.main.url(forResource: name, withExtension: nil) else {
            print("❌ Missing resource: \(name)")
            return nil
        }

        let fileManager = FileManager.default
        let dest = FileManager.default.temporaryDirectory.appendingPathComponent(name)

        if !fileManager.fileExists(atPath: dest.path) {
            try? fileManager.copyItem(at: resource, to: dest)
        }

        return dest
    }
}
