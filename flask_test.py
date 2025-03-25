import base64

from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from PIL import Image as PILImage
import os
import io
import model_eval
import json

app = Flask(__name__)


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']

    try:
        # Save temporarily
        filepath = 'temp_file'
        file.save(filepath)

        # Open with fitz (PyMuPDF)
        doc = fitz.open(filepath)

        # Convert first page to image (as example)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        image = PILImage.open(io.BytesIO(pix.tobytes("png")))
        image_path = 'output.png'
        image.save(image_path)


        # Send to chatGPT
        response = extract_json_from_image(prompt, model, image_path)
        print(response)

        print("Processed!")  # Prints to your terminal when a file is processed

        # Cleanup
        doc.close()
        os.remove(filepath)

        return {'message': 'File received and processed successfully!'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


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


prompt = """Based on the image I give you, extract the relevant information and store it in a JSON file. If a field 
                    is not present, write "N/A". 

                    product_name might be called Product Name/Material
                    product_description might be called Description/Details
                    customer_material_number might be called Part number/Product Code/Description  
                    quantity might be called Volume/Amount  
                    batch_number might be called Lot Number  
                    manufacturing_date might be called Production Date  
                    delivery_number might be called Delivery No/Dispatch Code/Shipment ID  
                    delivery_item might be called Product Name/Product Description/Shipped item  
                    delivery_date Shipping Date/Dispatch Date, Oil Transport Date  
                    receiving_date might be called Arrival Date/Entry Date  
                    oil_additives might be called Chemical Modifiers/Performance Additives/Lubricant Enhancers  
                    Customer Number  
                    purchase_order_number might be called PO number/Order No  
                    tank_number might be called Tank ID  
                    Vehicle Number
                    Shelf Life Exp Date  

                    The following fields will appear in a table format. Each field is a column of the table. If there are missing values, 
                    replace them with "N/A". If the entire column is missing, replace the entire column with "N/A". Every column will have the
                    same number of rows once the N/A values are filled in.

                    test_name might be called Test Method/Lubricant Testing Method/QC inspection Type  
                    appearance might be called Property  
                    value might be called Results  
                    uom might be called Measurement Unit/Volume Standard/Lubricant Unit  
                    min_spec might be called LCL/Lower Limit/Allowable Value/Min Performance Threshold  
                    max_spec might be called UCL/Upper Limit/Maximum Allowable Value/Max Performance Threshold  

                    min_spec and max_spec may be in the same column on the CofA.

                    signature might be called QC approval/Authorized Signatory, and may be printed or signed. 
                    it's usually at the bottom of the document.

                    """
model = "gpt-4o"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
