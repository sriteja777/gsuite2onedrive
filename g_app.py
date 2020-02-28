import io
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import config
import requests
import os
from humanize import naturalsize


class GoogleApp:
    def __init__(self):
        self.config = config.google_c
        self.credentials = None
        self.gdrive_service = None
        pass

    def authorize(self):
        if os.path.exists('token.pickle'):
            with open(self.config["token_file"], 'rb') as token:
                self.credentials = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config['credentials_file'], self.config['scopes'])
                self.credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.config["token_file"], 'wb') as token:
                pickle.dump(self.credentials, token)

    def build_gdrive_service(self):
        if not self.credentials:
            self.authorize()
        self.gdrive_service = build('drive', 'v3', credentials=self.credentials)

    def download_file_from_id(self, file_id, mime_type=None,extension=''):
        file_headers = self.gdrive_service.files().get(fileId=file_id).execute()
        request = None
        if not mime_type:
            request = self.gdrive_service.files().get_media(fileId=file_id)
        else:
            request = self.gdrive_service.files().export_media(fileId=file_id, mimeType=mime_type)
        # print()
        # print(request.headers,type(request))
        fh = io.FileIO(file_headers["name"] + extension, 'wb')
        downloader = MediaIoBaseDownload(fh, request,chunksize=102400)
        done = False
        try:
            while done is False:
                status, done = downloader.next_chunk()
                print(file_headers["name"], "   downloaded %d%%." % int(status.progress() * 100))
        except HttpError as e:
            print(file_headers["name"] + "  file downloading failed beacause of following error: ",e)

    def export_using_requests(self, file_id, filename, download_url):
        # file_headers = self.gdrive_service.files().get(fileId=file_id).execute()
        headers = {'Authorization': 'Bearer ' + self.credentials.token}
        # url = "https://docs.google.com/feeds/download/presentations/Export"
        # params = {"id": file_id, "exportFormat": export_format}
        # filename = file_headers["name"]
        file = requests.get(download_url, headers=headers, stream=True)
        downloaded = 0
        with open(filename, 'wb') as f:
            for chunk in file.iter_content(10240):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    print("\r" + filename + " downloaded " + str(naturalsize(downloaded)) ,end='')
        print()
        file.close()

    def download_files_from_mimetype(self, mime_type, out_dir, export_mt, extension):
        cwd = os.getcwd()
        os.chdir(out_dir)
        results = self.gdrive_service.files().list(
            q="mimeType='" + mime_type + "'",
            fields="nextPageToken, files(id, name, exportLinks, size)").execute()
        files = results.get('files', [])
        print(len(files))
        if not files:
            return 2 # No files found
        else:
            for file in files:
                # self.download_file_from_id(file["id"], mime_type=out_type,extension=extension)
                # print(file)
                self.export_using_requests(file["id"], file["name"] + extension, file["exportLinks"][export_mt])
                # print(file["name"], file["exportLinks"][export_mt])
        os.chdir(cwd)

    def run(self):
        file_id = "1xOBIpKxTWyC321Wi4vRVtzf2owmOzXpNVAdd756EUFQ"
        self.build_gdrive_service()
        for dt in config.maps_ext:
            if not os.path.isdir(dt["out_dir"]):
                os.mkdir(dt["out_dir"])
            print(dt["out_dir"], ':')
            self.download_files_from_mimetype(**dt)
        # self.export_using_requests(file_id, "docx", ".docx")
        # self.download_file_from_id(file_id, mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        # self.download_files_from_mimetype("application/vnd.google-apps.presentation", 'slides',
        #                                   out_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",extension='.pptx')

if __name__ == "__main__":
    gApp = GoogleApp()
    gApp.run()
