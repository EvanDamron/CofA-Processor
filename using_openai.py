import base64
import json

import openai
from pydantic import BaseModel

with open('openai_api_key.txt', 'r') as file:
    api_key = file.read().replace('\n', '')
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
    signature: list[str]



# Load the image file
image_path = 'Raw Material.png'
with open(image_path, 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

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
signature might be called QC approval/Authorized Signatory  
"""


# Create the request with image and prompt
response = client.beta.chat.completions.parse(
    model="gpt-4o",
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
# client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": prompt},
#         {"role": "user", "content": image_data}
#     ],
#     response_format="json",
# )

print(response)
response_text = response.choices[0].message.content
response_json = json.loads(response_text)

# Save the response to a JSON file
output_path = 'raw material.json'
with open(output_path, 'w') as json_file:
    json.dump(response_json, json_file, indent=4)

print(f"Response saved to {output_path}")
print(response)
