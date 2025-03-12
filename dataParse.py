import json
import psycopg2

def clean_signature(signature):
    # Format the signature correctly
    if isinstance(signature, list):
        # Join the list into a single string.
        signature = ''.join(signature)
    return signature.replace('{', '').replace('}', '').replace('"', '')

def normalize_na(value):
    """
    If the value is a form of null switch it with None so the value in the database stays as NULL.
    """
    return None if value in ("N/A", "null", "Null") else value

# Connect to the database
def insert_cofa_and_tests(json_path):
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        user="admin",
        password="admin123",
        dbname="cofa_db"
    )
    cursor = connection.cursor()

    # Load the JSON file
    with open (json_path, "r") as f:
        data = json.load(f)


    # Insert query for the CofA
    insert_query = """
        INSERT INTO cofas(
            product_name,
            product_description,
            customer_material_number,
            quantity,
            batch_number,
            manufacturing_date,
            delivery_number,
            delivery_item,
            delivery_date,
            receiving_date,
            oil_additives,
            customer_number,
            purchase_order_number,
            tank_number,
            vehicle_number,
            shelf_life_exp_date,
            signature
        )
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """


    cursor.execute(
        insert_query,
        (
            normalize_na(data.get("product_name", "")),
            normalize_na(data.get("product_description", "")),
            normalize_na(data.get("customer_material_number", "")),
            normalize_na(data.get("quantity", "")),
            normalize_na(data.get("batch_number", "")),
            normalize_na(data.get("manufacturing_date", "")),
            normalize_na(data.get("delivery_number", "")),
            normalize_na(data.get("delivery_item", "")),
            normalize_na(data.get("delivery_date", "")),
            normalize_na(data.get("receiving_date", "")),
            normalize_na(data.get("oil_additives", "")),
            normalize_na(data.get("customer_number", "")),
            normalize_na(data.get("purchase_order_number", "")),
            normalize_na(data.get("tank_number", "")),
            normalize_na(data.get("vehicle_number", "")),
            normalize_na(data.get("shelf_life_exp_date", "")),
            clean_signature(normalize_na(data.get("signature", "")))
        )
    )
    # Get the ID associated with this CofA
    new_cofa_id = cursor.fetchone()[0]

    # Insert query for the test data
    # Potentially add signature at the end if need be
    insert_cofa_tests_sql = """
        INSERT INTO cofa_tests (
            cofa_id,
            test_name,
            appearance,
            value,
            uom,
            min_spec,
            max_spec
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # Extract data from the json file
    test_names = data.get("test_name", [])
    appearances = data.get("appearance", [])
    values_ = data.get("value", [])
    uoms = data.get("uom", [])
    min_specs = data.get("min_spec", [])
    max_specs = data.get("max_spec", [])

    length = min(
        len(test_names),
        len(appearances),
        len(values_),
        len(uoms),
        len(min_specs),
        len(max_specs),
    )

    for i in range(length):
        cursor.execute(
            insert_cofa_tests_sql,
            (
                new_cofa_id,
                normalize_na(test_names[i]),
                normalize_na(appearances[i]),
                normalize_na(values_[i]),
                normalize_na(uoms[i]),
                normalize_na(min_specs[i]),
                normalize_na(max_specs[i]),
            )
        )


    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    # Change raw material.json into whatever variable the json files will be coming in as
    insert_cofa_and_tests("yubase_prompt1.json")