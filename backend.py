import base64

from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from PIL import Image as PILImage
import os
import io
import model_eval
import json
from dataParse import upload_pdf_and_get_url, insert_cofa_and_tests_from_dict

app = Flask(__name__)


import tempfile
pdf_url = None

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    global pdf_url
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    uploaded_file = request.files['file']

    try:
        # Save to a temporary file with .pdf extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            uploaded_file.save(tmp.name)
            filepath = tmp.name

        # Open with fitz (PyMuPDF)
        doc = fitz.open(filepath)

        # Convert first page to image (as example)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        image = PILImage.open(io.BytesIO(pix.tobytes("png")))
        image_path = 'output.png'
        image.save(image_path)

        #filename = uploaded_file.filename or "uploaded.pdf"
        #with open(filepath, 'rb') as file_stream:
        #    pdf_url = upload_pdf_and_get_url(file_stream, filename)
        pdf_url = upload_pdf_and_get_url(filepath)

        # Send to chatGPT
        response = extract_json_from_image(prompt, model, image_path)
        print(response)
        print("Processed!")

        # Cleanup
        doc.close()
        os.remove(filepath)

        return jsonify(response), 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/upload-immediately', methods=['POST'])
def upload_immediately():
    global pdf_url
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']

    try:
        # Save temporarily
        filepath = 'temp_file'
        file.save(filepath)

        # Open with fitz (PyMuPDF)
        doc = fitz.open(filepath)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        image = PILImage.open(io.BytesIO(pix.tobytes("png")))
        image_path = 'output.png'
        image.save(image_path)

        pdf_url = upload_pdf_and_get_url(filepath)

        # Extract data using the model
        response = extract_json_from_image(prompt, model, image_path)
        print(response)
        print("Processed and storing in DB...")

        # Populate the database directly
        populate_database(response)

        # Cleanup
        doc.close()
        os.remove(filepath)

        return {'message': 'File processed and data stored successfully!'}, 200

    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/verify', methods=['POST'])
def verify_and_save():
    try:
        corrected_data = request.json
        if not corrected_data:
            return {'error': 'No JSON data provided'}, 400

        populate_database(corrected_data)

        return {'message': 'Database populated successfully!'}, 200

    except Exception as e:
        return {'error': str(e)}, 500

# Populate the database
def populate_database(data: dict):
	insert_cofa_and_tests_from_dict(data, pdf_url)



def extract_json_from_image(prompt: str, model: str, image_path: str) -> dict:
    """
    Function to extract structured data from an image using OpenAI API.

    :param prompt: The instruction prompt for OpenAI
    :param model: The OpenAI model to use (e.g., "gpt-4o", "gpt-4o-mini")
    :param image_path: The path to the image file to be processed
    :return: Extracted JSON data as a dictionary
    """
    # Encode the image as base64
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    try:
        # Call the OpenAI API
        response = model_eval.client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",
                 "content": [{
                     "type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{image_data}"}
                 }]
                 }
            ],
            response_format=model_eval.CofaInfo,  # Ensure the response is structured in JSON format
        )

        # Parse JSON response
        response_text = response.choices[0].message.content
        response_json = json.loads(response_text)

        return response_json

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


prompt = test_prompt = """You are tasked with extracting structured data from an image of a Certificate of Analysis (CofA). Perform OCR, then carefully extract and organize the information into the provided JSON format.

                        **General Extraction Rules:**
                        - If a field is not present, write "N/A".
                        - Be aware that fields might have multiple alternative names as listed below.

                        **General Information Fields:**
                        - product_name (alternatively: Product Name, Material)
                        - product_description (alternatively: Description, Details)
                        - customer_material_number (alternatively: Part number, Product Code, Description)
                        - quantity (alternatively: Volume, Amount)
                        - batch_number (alternatively: Lot Number)
                        - manufacturing_date (alternatively: Production Date)
                        - delivery_number (alternatively: Delivery No, Dispatch Code, Shipment ID)
                        - delivery_item (alternatively: Product Name, Product Description, Shipped item)
                        - delivery_date (alternatively: Shipping Date, Dispatch Date, Oil Transport Date)
                        - receiving_date (alternatively: Arrival Date, Entry Date)
                        - oil_additives (alternatively: Chemical Modifiers, Performance Additives, Lubricant Enhancers)
                        - customer_number (Customer Number)
                        - purchase_order_number (alternatively: PO number, Order No)
                        - tank_number (alternatively: Tank ID)
                        - vehicle_number (Vehicle Number)
                        - shelf_life_expiration_date (Shelf Life Exp Date)

                        **Tabular Information:**
                        The following fields must be extracted from any table present. Each field corresponds to a column. 

                        - test_name (alternatively: Test Method, Lubricant Testing Method, QC inspection Type)
                        - appearance (alternatively: Property, Characteristics)
                        - value (alternatively: Results)
                        - uom (alternatively: Measurement Unit, Volume Standard, Lubricant Unit)
                        - min_spec (alternatively: LCL, Lower Limit, Allowable Value, Min Performance Threshold)
                        - max_spec (alternatively: UCL, Upper Limit, Maximum Allowable Value, Max Performance Threshold)

                        **Special Rules for Tabular Data:**
                        - Check the actual column headers, as the data is frequently misaligned. Rearrange data to match the appropriate header.
                        - If `min_spec` and `max_spec` appear combined in a single column, split them accordingly. If only one value is present for both, use the same value in both fields.
                        - If data for any field is missing, replace it with "N/A". If an entire column is missing, fill the entire column with "N/A". All columns must have the same number of rows after filling missing values.

                        **Signature Extraction:**
                        - Extract the signature from the bottom of the document. Signature might be labeled QC approval or Authorized Signatory and may be printed or signed. If missing, use "N/A".

                        **Accuracy and Validation:**
                        - Double-check extracted values against the original document, ensuring the extracted columns are correctly labeled.
                        - Prioritize accuracy and clarity over speed.
                        """
model = "gpt-4o"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
