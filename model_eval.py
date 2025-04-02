import base64
import json
import openai
from pydantic import BaseModel
import os

# Initialize OpenAI client
# read api key from text file
api_key = os.getenv("OPENAI_API_KEY")
client = openai.Client(api_key=api_key)


class CofaInfo(BaseModel):
    product_name: str
    product_description: str
    customer_material_number: str
    quantity: str
    batch_number: str
    manufacturing_date: str
    delivery_number: str
    delivery_item: str
    delivery_date: str
    receiving_date: str
    oil_additives: str
    customer_number: str
    purchase_order_number: str
    tank_number: str
    vehicle_number: str
    shelf_life_exp_date: str

    test_name: list[str]
    appearance: list[str]
    value: list[str]
    uom: list[str]
    min_spec: list[str]
    max_spec: list[str]

    signature: str


def extract_json_from_image(prompt: str , model: str, image_path: str) -> dict:
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
        response = client.beta.chat.completions.parse(
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
            response_format=CofaInfo,  # Ensure the response is structured in JSON format
        )

        # Parse JSON response
        response_text = response.choices[0].message.content
        response_json = json.loads(response_text)

        return response_json

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


# Example Usage
if __name__ == "__main__":
    test_prompt = """You are tasked with extracting structured data from an image of a Certificate of Analysis (CofA). Perform OCR, then carefully extract and organize the information into the provided JSON format.

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
    test_model = "gpt-4o"
    # Define the output directory
    output_dir = "4o_json"
    os.makedirs(output_dir, exist_ok=True)

    image_folder = "cofa pngs"  # Folder containing images
    for image_filename in os.listdir(image_folder):
        if not image_filename.endswith(".png"):
            continue  # Skip non-PNG files

        image_path = os.path.join(image_folder, image_filename)
        print(f"Processing image: {image_filename}")

        json_response = extract_json_from_image(test_prompt, test_model, image_path)

        # Generate the filename: e.g., "oronite_prompt1.json"
        cofa_name = image_filename.replace(".png", "")  # Remove file extension
        output_filename = f"{cofa_name}_prompt1.json"
        output_path = os.path.join(output_dir, output_filename)

        # Save response to JSON file
        with open(output_path, "w") as json_file:
            json.dump(json_response, json_file, indent=4)

        print(f"Response saved to {output_path}\n")
