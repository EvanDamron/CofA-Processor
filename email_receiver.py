import imaplib
import email
import time
import pdfkit
import tempfile
import os
from email.header import decode_header
from PIL import Image
from docx import Document
import requests


# Email credentials
EMAIL_USER = "csdummy5@gmail.com"
EMAIL_PASS = "zkoxqfzezxkwdecl"  # App Password, NOT your actual password
IMAP_SERVER = "imap.gmail.com"


def send_pdf_to_backend(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            response = requests.post(
                'http://localhost:5000/upload-immediately',
                files={'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            )
        if response.status_code == 200:
            print(f"✅ Uploaded {pdf_path} to /upload-immediately.")
        else:
            print(f"❌ Failed to upload {pdf_path}. Response: {response.text}")
    except Exception as e:
        print(f"❌ Error uploading {pdf_path}: {e}")


def process_new_emails(mail):
    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        print("Error searching for emails.")
        return

    email_ids = messages[0].split()
    if not email_ids:
        print("No new emails found.")
        return

    for num in email_ids:
        email_id = num.decode() if isinstance(num, bytes) else str(num)

        status, data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            print(f"Error fetching email ID {email_id}")
            continue

        raw_email = None
        for item in data:
            if isinstance(item, tuple) and len(item) >= 2 and isinstance(item[1], bytes):
                raw_email = item[1]
                break

        if raw_email is None:
            print(f"Unexpected data format for email ID {email_id}")
            continue

        try:
            msg = email.message_from_bytes(raw_email)
        except Exception as e:
            print(f"Error parsing email ID {email_id}: {e}")
            continue

        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = decode_header(part.get_filename())[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()

                file_ext = filename.split('.')[-1].lower()

                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_file:
                        temp_file.write(part.get_payload(decode=True))
                        temp_file_path = temp_file.name
                    print(f"📩 Saved temp attachment: {filename} -> {temp_file_path}")

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
                        pdf_path = pdf_file.name

                    # Convert and upload
                    if file_ext in ["png", "jpg", "jpeg"]:
                        img = Image.open(temp_file_path)
                        img.convert("RGB").save(pdf_path, "PDF")
                        print(f"🖼️ Converted image to PDF")
                        send_pdf_to_backend(pdf_path)

                    elif file_ext == "txt":
                        with open(temp_file_path, "r", encoding="utf-8") as txt_file:
                            content = txt_file.read()
                        pdfkit.from_string(content, pdf_path)
                        print(f"📄 Converted text to PDF")
                        send_pdf_to_backend(pdf_path)

                    elif file_ext == "docx":
                        doc = Document(temp_file_path)
                        text = "\n".join([p.text for p in doc.paragraphs])
                        pdfkit.from_string(text, pdf_path)
                        print(f"📄 Converted DOCX to PDF")
                        send_pdf_to_backend(pdf_path)

                    elif file_ext == "pdf":
                        print(f"📎 File is already a PDF")
                        send_pdf_to_backend(temp_file_path)

                    else:
                        print(f"⚠️ Skipping unsupported file type: {filename}")

                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")

                finally:
                    # Clean up files
                    try:
                        os.remove(temp_file_path)
                        print(f"🧹 Deleted temp file: {temp_file_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete temp file: {e}")

                    try:
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
                            print(f"🧹 Deleted temp PDF: {pdf_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete temp PDF: {e}")


# Connect to email once
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)
mail.select("inbox")

print("📬 Listening for new emails... Press Ctrl+C to exit.")

try:
    while True:
        mail.noop()
        process_new_emails(mail)
        time.sleep(30)
except KeyboardInterrupt:
    print("🛑 Stopping email listener.")
finally:
    mail.logout()
