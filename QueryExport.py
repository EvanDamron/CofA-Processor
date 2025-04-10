import os
import requests
import psycopg2
from msal import PublicClientApplication

# === DATABASE CONFIG ===
DB_CONFIG = {
    'host': '34.194.202.42',
    'dbname': 'cofa_db',
    'user': 'admin',
    'password': 'admin123',
    'port': 5432,
}

# === SHAREPOINT CONFIG ===
client_id = "42d4bf53-30f7-4522-ba5e-83a5dff792d6"
tenant_id = "2b30530b-69b6-4457-b818-481cb53d42ae"
authority = f"https://login.microsoftonline.com/{tenant_id}"
scopes = ["Files.ReadWrite.All", "Sites.ReadWrite.All"]
sharepoint_site_hostname = "luky.sharepoint.com"
site_path = "/sites/CS499-CofA"
#sharepoint_folder = "Shared Documents/COFA_PDFs_NEW"

# === LOCAL SETUP ===
OUTPUT_DIR = "downloaded_pdfs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def authenticate_microsoft_graph():
    app = PublicClientApplication(client_id=client_id, authority=authority)
    result = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes=scopes, account=accounts[0])
    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise Exception("Device flow initiation failed.")
        print(f"🔐 Go to: {flow['verification_uri']}")
        print(f"🔑 Enter the code: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise Exception(f"Authentication failed.\nDetails: {result.get('error_description')}")
    return result["access_token"]


def get_sharepoint_drive_ids(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    site_url = f"https://graph.microsoft.com/v1.0/sites/{sharepoint_site_hostname}:{site_path}"
    site_id = requests.get(site_url, headers=headers).json()["id"]
    drive_id = requests.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive", headers=headers).json()["id"]
    return site_id, drive_id


def upload_to_sharepoint(file_path, drive_id, headers, sharepoint_folder):
    file_name = os.path.basename(file_path)
    upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{sharepoint_folder}/{file_name}:/content"
    with open(file_path, "rb") as f:
        upload_resp = requests.put(upload_url, headers=headers, data=f)
    if upload_resp.status_code in [200, 201]:
        print(f"✅ Uploaded: {file_name}")
    else:
        print(f"❌ Failed to upload {file_name} ({upload_resp.status_code})")
        print(upload_resp.text)


def download_pdf_from_url(url, idx):
    try:
        response = requests.get(url)
        response.raise_for_status()
        local_path = os.path.join(OUTPUT_DIR, f"file_{idx}.pdf")
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"📥 Downloaded: {local_path}")
        return local_path
    except Exception as e:
        print(f"⚠️ Failed to download from {url}: {e}")
        return None


def fetch_pdf_links_from_db(sql_query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return [row[0] for row in rows if isinstance(row[0], str) and row[0].startswith("http")]
    except Exception as e:
        print(f"DB Error: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def main():
    sql_query = input("Enter your SQL query to fetch PDF URLs: ").strip()
    user_folder = input("Enter the SharePoint folder (inside 'Shared Documents') to upload PDFs to: ").strip()
    sharepoint_folder = f"Shared Documents/{user_folder}"
    pdf_urls = fetch_pdf_links_from_db(sql_query)
    if not pdf_urls:
        print("No valid PDF URLs found.")
        return

    print("🔐 Authenticating with Microsoft Graph...")
    token = authenticate_microsoft_graph()
    headers = {"Authorization": f"Bearer {token}"}
    _, drive_id = get_sharepoint_drive_ids(token)

    print("⬇️ Downloading PDFs and ⬆️ Uploading to SharePoint...")
    for idx, url in enumerate(pdf_urls, start=1):
        local_pdf = download_pdf_from_url(url, idx)
        if local_pdf:
            upload_to_sharepoint(local_pdf, drive_id, headers, sharepoint_folder)


if __name__ == "__main__":
    main()
