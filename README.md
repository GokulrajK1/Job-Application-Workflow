# Job Application Automation Tool

A Python-based automation tool that streamlines submitting job applications by integrating **Google Drive/Docs** and **Notion**. This tool automatically uploads your resume and cover letter to a structured Google Drive folder hierarchy and logs the application in a Notion database.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Google API Setup](#google-api-setup)
- [Notion API Setup](#notion-api-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Notes & Tips](#notes--tips)

---

## Project Overview

This tool automates the process of applying to jobs by:

1. Uploading your resume to Google Drive within a structured folder hierarchy:  
   `Applications > Company > Role`.
2. Creating a Google Doc for your cover letter and exporting it as PDF.
3. Logging the application in a Notion database, including company, role, application status, and referral information.
4. Dynamically supporting multiple resumes, allowing you to choose the correct one for each role based on your `config.json`.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10+
- pip (Python package installer)
- A Google account
- A Notion account

---

## Installation

1. **Clone the repository**:

```bash
git clone <repository_url>
cd <repository_folder>
```

2. **Set up a virtual environment**:

```bash
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

3. **Install required Python packages**:

```bash
pip install -r requirements.txt
```

---

## Google API Setup

Follow these steps to configure Google Drive and Docs API:

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Click **Select a project > New Project**.
   - Name it something like `JobApplicationAutomation`.

2. **Enable APIs**:
   - In the Dashboard, go to **APIs & Services > Library**.
   - Search for **Google Drive API** and click **Enable**.
   - Search for **Google Docs API** and click **Enable**.

3. **Create OAuth 2.0 Credentials**:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth client ID**.
   - Select **Desktop App** as the application type.
   - Name it appropriately (e.g., `JobAppToolClient`).
   - Click **Create** and download the JSON file.

4. **Move your Google credentials**:
   - Place your downloaded `credentials.json` into the provided empty `google_creds` folder.

5. **Obtain your Google Drive Folder IDs**:
   - Go to your Google Drive.
   - Navigate to the folder you want to use for applications (or create a new one).
   - Open the folder and copy the part of the URL after `folders/`. This is your folder ID.

6. **Run the script once**:
   - The first time you run the tool, it will prompt you to log in to your Google account.
   - This will generate `google_creds/token.json` automatically.

---

## Google Credentials Folder

This folder is intended to store your Google OAuth credentials locally. **Do not commit your credentials.json or token.json** to GitHub.

Place your files here:

- `credentials.json` — downloaded from Google Cloud Console
- `token.json` — automatically generated after first run

.gitignore already ignores these files.

## Notion API Setup

1. **Create a Notion Integration**:
   - Go to [Notion Developers](https://www.notion.so/my-integrations).
   - Click **New Integration**.
   - Give it a name (e.g., `JobApplicationAutomationIntegration`).
   - Copy the **Integration Token**.

2. **Share your database with the integration**:
   - Open your Notion database.
   - Click **Share > Invite**.
   - Search for your integration name and invite it.

3. **Obtain your Notion Database ID**:
   - Open your database in a web browser.
   - The URL looks like `https://www.notion.so/workspace/DatabaseName-xxxxxxxxxxxxxxxxxxxxxx`.
   - Copy the part after the last `/` (usually a long string with hyphens removed) as the Database ID.

4. **Update `config.json`** with your API key and Database ID.

---

## Configuration

You will find a file in the repository called `config_example.json`. Simply copy this file, rename it to `config.json`, and edit it with your details.

Here is a **filled example** for reference:

```json
{
  "applicant_details": {
    "first_name": "John",
    "last_name": "Doe",
    "default_role": "Software Engineer"
  },
  "cover_letter_paths": {
    "cover_letter_download_folder_path": "./cover_letters",
    "cover_letter_paste_text_file": "./cover_letters/cover_letter_template.txt"
  },
  "resume_paths": [
    {
      "role_type": "Software Engineer",
      "path": "./resumes/software_engineer_resume.pdf"
    },
    {
      "role_type": "Data Scientist",
      "path": "./resumes/data_scientist_resume.pdf"
    }
  ],
  "google_drive": {
    "application_folder_id": "YOUR_GOOGLE_DRIVE_FOLDER_ID",
    "token_file_path": "google_creds/token.json",
    "credentials_file_path": "google_creds/credentials.json"
  },
  "notion": {
    "api_key": "YOUR_NOTION_INTEGRATION_TOKEN",
    "database_id": "YOUR_NOTION_DATABASE_ID"
  }
}
```

**Tips to get folder IDs:**
- Navigate to the folder in Google Drive.
- Copy the URL after `folders/`. This is the `application_folder_id`.

---

## Usage

Run the tool with the following command:

```bash
python main.py --company "Company Name" --role "Role Name" --resume 0 --referral 1
```

- `--company`: Name of the company.
- `--role`: Role title.
- `--resume`: Index of the resume to use (from `config.json`). Supports multiple resumes.
- `--referral`: 0 = No, 1 = Yes

### Full help message

```bash
usage: main.py [-h] [--company COMPANY] [--role ROLE] [--resume {0,1}] [--referral {0,1}]

Job Application Automation Tool

optional arguments:
  -h, --help           show this help message and exit
  --company COMPANY    Name of the company
  --role ROLE          Role that is being applied to
  --resume {0,1}      Resume to use: 0 = Software Engineer, 1 = Data Scientist
  --referral {0,1}    0 = No Referral, 1 = Referral
```

---

## Project Structure

```
project_folder/
├─ venv/
├─ config/
│  └─ config.json
├─ google_creds/
│  ├─ credentials.json
│  └─ token.json
├─ cover_letters/
│  └─ cover_letter_template.txt
├─ resumes/
│  ├─ software_engineer_resume.pdf
│  └─ data_scientist_resume.pdf
├─ main.py
└─ requirements.txt
```

---

## Notes & Tips

- Ensure your cover letter text file exists and is not empty.
- First-time Google OAuth may require browser authentication.
- Use different resume indices for different role types as defined in `config.json`.
- Make sure your Notion database has the necessary columns: Company (Title), Position (Select), Application Status (Select), Referral (Status).

