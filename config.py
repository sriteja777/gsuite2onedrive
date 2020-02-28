ms_azure = {
    'client_id': '02009db5-f24d-4c9f-a122-a4b3690ce718',
    'redirect_uri': 'http://localhost:8080',
    'scopes': ['files.readwrite'],
    'tenant_id': '031a3bbc-cf7c-4e2b-96ec-867555540a1c',
}

google_c = {
    'scopes': ['https://www.googleapis.com/auth/drive.metadata.readonly',
               'https://www.googleapis.com/auth/drive.readonly'],
    'credentials_file': './credentials.json',
    'token_file': 'token.pickle'
}

ms_authority_url = 'https://login.microsoftonline.com/' + ms_azure["tenant_id"]
ms_graph_drive_url = "https://graph.microsoft.com/v1.0/me/drive"

maps_ext = [
    {"out_dir": "Google Docs", "extension": ".docx", "export_mt": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "mime_type": "application/vnd.google-apps.document"},
    {"out_dir": "Google Slides", "extension": ".pptx", "export_mt": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "mime_type": "application/vnd.google-apps.presentation"},
    {"out_dir": "Google Sheets", "extension": ".xlsx", "export_mt": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "mime_type": "application/vnd.google-apps.spreadsheet"}
]

upload_dirs = ["Google Docs", "Google Slides", "Google Sheets"]
upload_size_limit = 4 * 1024 * 1024