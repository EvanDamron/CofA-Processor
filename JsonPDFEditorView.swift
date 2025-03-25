import SwiftUI
import PDFKit

// MARK: - JSON + PDF Editor View

struct JsonPdfEditorView: View {
    let jsonURL: URL
    let pdfURL: URL
    let onComplete: (_ updatedJson: [String: Any]) -> Void

    @State private var jsonDict: [String: AnyCodable] = [:]
    @State private var fieldStorage: [String: [String]] = [:]
    @Environment(\.dismiss) var dismiss
    @State private var showAlert = false
    @State private var savedFileName: String?

    var body: some View {
        HStack {
            PDFViewWrapper(url: pdfURL)
                .frame(width: 400)

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    ForEach(fieldStorage.keys.sorted(), id: \.self) { key in
                        VStack(alignment: .leading) {
                            Text(key.capitalized)
                                .font(.headline)

                            ForEach(fieldStorage[key]!.indices, id: \.self) { i in
                                TextField("Item \(i+1)", text: Binding(
                                    get: { fieldStorage[key]![i] },
                                    set: { fieldStorage[key]![i] = $0 }
                                ))
                                .textFieldStyle(.roundedBorder)
                            }
                        }
                    }

                    Button("Approve & Submit") {
                        for (key, values) in fieldStorage {
                            jsonDict[key] = values.count == 1 ? AnyCodable(values.first!) : AnyCodable(values)
                        }
                        let finalData = jsonDict.mapValues { $0.value }

                        // ✅ Automatically save new file
                        saveApprovedJSON(finalData)

                        onComplete(finalData)
                        showAlert = true
                    }
                    .padding(.top)
                    .alert("✅ Data Saved to \(savedFileName ?? "")", isPresented: $showAlert) {
                        Button("OK") { dismiss() }
                    }
                }
                .padding()
            }
        }
        .onAppear {
            loadJSON()
        }
    }

    private func loadJSON() {
        do {
            let data = try Data(contentsOf: jsonURL)
            let decoded = try JSONDecoder().decode([String: AnyCodable].self, from: data)
            self.jsonDict = decoded

            for (key, value) in decoded {
                if let arr = value.value as? [Any] {
                    fieldStorage[key] = arr.map { "\($0)" }
                } else {
                    fieldStorage[key] = ["\(value.value)"]
                }
            }
        } catch {
            print("❌ Error loading JSON:", error)
        }
    }

    private func saveApprovedJSON(_ json: [String: Any]) {
        do {
            let data = try JSONSerialization.data(withJSONObject: json, options: .prettyPrinted)

            let originalName = jsonURL.deletingPathExtension().lastPathComponent
            let approvedFileName = "\(originalName)Approved.json"
            let approvedURL = FileManager.default.temporaryDirectory.appendingPathComponent(approvedFileName)

            try data.write(to: approvedURL)
            savedFileName = approvedFileName
            print("✅ Saved approved JSON to:", approvedURL.path)
        } catch {
            print("❌ Error saving approved JSON:", error)
        }
    }
}
