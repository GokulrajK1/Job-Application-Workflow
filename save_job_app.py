from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import argparse
import os
import requests
import io
import json
        
class JobApplication:
    def __init__(self, company : str, role : str, resume_path : str, referral : str):
        self.company = company
        self.role = role
        self.resume_path = resume_path
        self.referral = referral

def get_google_api_services(config):
    scopes = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
    creds = None
    if os.path.exists(config["google_drive"]["token_file_path"]):
        creds = Credentials.from_authorized_user_file(config["google_drive"]["token_file_path"], scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config["google_drive"]["credentials_file_path"], scopes)
            creds = flow.run_local_server(port=0)
        with open(config["google_drive"]["token_file_path"], 'w') as token:
            token.write(creds.to_json())

    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    return drive_service, docs_service

def upload_job_app_to_google_drive(job_application : JobApplication, config : dict):
    drive_service, docs_service = get_google_api_services(config)
    application_folder_id = config["google_drive"]["application_folder_id"]
    
    query = (
        f"name = '{job_application.company}' and '{application_folder_id}' in parents "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])

    if items:
        company_folder_id = items[0]["id"]
        print(f"✅ Using existing company folder: {job_application.company} ({company_folder_id})")
    else:
        folder_metadata = {
            'name': job_application.company,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [application_folder_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        company_folder_id = folder.get('id')
        print(f"✅ Created company folder: {job_application.company} ({company_folder_id})")
    
    role_query = (
        f"name = '{job_application.role}' and '{company_folder_id}' in parents "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    role_results = drive_service.files().list(q=role_query, fields="files(id, name)").execute()
    role_items = role_results.get("files", [])

    if role_items:
        role_folder_id = role_items[0]["id"]
        print(f"📂 Using existing role folder: {job_application.role} ({role_folder_id})")
    else:
        role_folder_metadata = {
            'name': job_application.role,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [company_folder_id]
        }
        role_folder = drive_service.files().create(body=role_folder_metadata, fields='id').execute()
        role_folder_id = role_folder.get('id')
        print(f"✅ Created role folder: {job_application.role} ({role_folder_id})")

    with open(config["cover_letter_paths"]["cover_letter_paste_text_file"], "r") as file:
        cover_letter_text = file.read()
        
    doc_metadata = {'title': f"{job_application.company} {job_application.role} Cover Letter"}
    doc = docs_service.documents().create(body=doc_metadata).execute()
    doc_id = doc.get('documentId')

    drive_service.files().update(
        fileId=doc_id,
        addParents=role_folder_id,
        fields='id, parents'
    ).execute()
    
    if cover_letter_text.strip():
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': cover_letter_text
            }
        }]
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        print(f"✅ Created Google Doc for cover letter: {doc_id}")
    else:
        print("⚠️ Cover letter file is empty — created blank Google Doc instead")
    
    
    cover_letter_pdf_path = os.path.join(
       config["cover_letter_paths"]["cover_letter_download_folder_path"], 
       f"{config['applicant_details']['first_name']}_{config['applicant_details']['last_name']}_Cover_Letter.pdf"
    )
    
    request = drive_service.files().export(fileId=doc_id, mimeType="application/pdf")
    with io.FileIO(cover_letter_pdf_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"✅ Download {int(status.progress() * 100)}%")

    print(f"✅ Saved cover letter locally: {cover_letter_pdf_path}")
    
    file_metadata = {
        'name': os.path.basename(job_application.resume_path),
        'parents': [role_folder_id]
    }
    media = MediaFileUpload(job_application.resume_path, mimetype='application/pdf')
    uploaded_pdf = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ Uploaded Resume: {uploaded_pdf.get('id')}")
    
def upload_job_app_to_notion(job_application : JobApplication, config : dict):

    referral_status = {0  : "No", 1 : "Yes"}
    
    headers = {
        "Authorization": f"Bearer {config['notion']['api_key']}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "parent": {"database_id": config["notion"]["database_id"]},
        "properties": {
            "Company": {
                "title": [
                    {
                        "text": {
                            "content": job_application.company
                        }
                    }
                ]
            },
            "Position": {
                "select": {
                    "name": job_application.role
                }
            },
            "Application Status": {
                "select": {
                    "name": "Applied"
                }
            },
            "Referral": {
                "status": {
                    "name": referral_status[job_application.referral]
                }
            }
        }
    }
    
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        print(f"✅ Added application for {job_application.company} ({job_application.role}) to Notion")
    else:
        print("❌ Error:", response.status_code, response.text)
        
def generate_help_string(resume_paths):
    help_string = ""
    for i, resume_path_object in enumerate(resume_paths):
        help_string += f"{i} = {resume_path_object['role_type']}, "
    if help_string[-2:] == ", ":
        help_string = help_string[:-2]
    return help_string

def main():
    # Edit Config
    with open("config/config.json", "r") as file:
        data = file.read()
        data = data.replace("\\", "\\\\")
        config = json.loads(data)
  
    os.makedirs(config["cover_letter_paths"]["cover_letter_download_folder_path"], exist_ok=True)
    
    resume_paths = config["resume_paths"]
    
    if len(resume_paths) < 1:
        raise ValueError("Please provide at least one resume path")
    
    for resume_path_object in resume_paths:
        if not os.path.exists(resume_path_object["path"]):
            raise FileNotFoundError(f"Resume File at {resume_path_object['path']} Does Not Exist!")
    
    parser = argparse.ArgumentParser(description="Job Application Automation Tool")
    parser.add_argument("--company", help="Name of the company", default="Company", required=False)
    parser.add_argument("--role", help="Role that is being applied to", default=config["applicant_details"]["default_role"], required=False)
    parser.add_argument("--resume", type=int, choices=list(range(len(resume_paths))), default=0, help=generate_help_string(resume_paths), required=False)
    parser.add_argument("--referral", type=int, choices=[0, 1], default=0, help="0 = No Referral, 1 = Referral", required=False)
    args = parser.parse_args()
    
    job_application = JobApplication(company=args.company,
                                     role=args.role,
                                     resume_path=resume_paths[args.resume]["path"],
                                     referral=args.referral,
                                    )
    
    upload_job_app_to_google_drive(job_application, config)
    upload_job_app_to_notion(job_application, config)
    
    print(f"✅ Successfully uploaded job application for {args.company} - {args.role} ✅")


if __name__ == "__main__":
    main()
    
