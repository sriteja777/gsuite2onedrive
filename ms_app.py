import os

import config
from msal import PublicClientApplication
import json
import local_server
import urllib.parse
import webbrowser
import requests
import pickle
import mimetypes
from copy import copy
import msal
from time import time
from humanize import naturalsize

class MSApp:
    def __init__(self):
        self.config = config.ms_azure
        self.app = PublicClientApplication(self.config["client_id"], authority=config.ms_authority_url)
        self._access_token = None
        self.credentials = None

    def get_authorization_code(self):
        params = {
            'client_id': self.config["client_id"],
            'scopes': self.config["scopes"],
            'response_type': 'code',
            'redirect_uri': self.config["redirect_uri"]
        }
        url = self.app.get_authorization_request_url(**params)
        webbrowser.open(url, 2)
        local_server.run()
        return local_server.a_code

    def token_expired(self):
        diff = time() - self.credentials["created_at"]
        print(60 - diff / 60, ' minutes until token expiry')
        if diff > 3500:
            return True

        return False

    def dump_credentials(self):
        with open('token_ms.pickle', 'wb') as f:
            pickle.dump(self.credentials, f)

    def authorize(self):
        if os.path.exists('token_ms.pickle'):
            with open("token_ms.pickle", 'rb') as token:
                self.credentials = pickle.load(token)
            # print(self.credentials)

        if not self.credentials or self.token_expired():
            code = self.get_authorization_code()
            self.credentials = self.app.acquire_token_by_authorization_code(
                code, scopes=self.config['scopes'], redirect_uri="http://localhost:8080")
            self.credentials["created_at"] = time()
            # accounts = self.app.get_accounts()
            # print(accounts[0])
            # print(self.credentials, type(self.credentials))

        if "access_token" in self.credentials:
            # print(self.credentials["access_token"])  # Yay!
            self.dump_credentials()
            self._access_token = self.credentials["access_token"]
            print("Authorization of MS successful")
            return 0
        else:
            print(self.credentials.get("error"))
            print(self.credentials.get("error_description"))
            print(self.credentials.get("correlation_id"))
            return 1

    def run_query(self, query, req_method, headers=None, req_body=None):
        if not self._access_token:
            self.authorize()

        req_headers = {
            'Authorization': 'Bearer ' + self._access_token,
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }
        if headers:
            for key in headers:
                req_headers[key] = headers[key]
        data = None
        if req_method == "POST":
            data = requests.post(query, headers=req_headers, json=req_body).json()
        if req_method == "GET":
            data = requests.get(query, headers=req_headers)
        if req_method == "PUT":
            data = requests.put(query, data=req_body, headers=req_headers).json()
        return data

    def upload_file(self, local_path, server_path):
        file_size = os.path.getsize(local_path)
        if file_size > config.upload_size_limit:
            print(local_path," is a large file")
            self.upload_large_file(local_path, server_path)
            return
        url = config.ms_graph_drive_url
        query = url + '/root:' + server_path + ':/content'
        with open(local_path, 'rb') as file:
            content = file.read()
        print(query)
        req = self.run_query(query, "PUT", req_body=content)
        # print(req, req.text)
        # print(req)
        if "error" in req:
            print("Failed")
        return req

    def upload_large_file(self, local_path, server_path):
        file_size = os.path.getsize(local_path)
        url = config.ms_graph_drive_url
        query = url + '/root:' + server_path + ':/createUploadSession'
        response = self.run_query(query, "POST")
        # print(response)
        upload_url = response["uploadUrl"]
        headers = {'Content-Length': 0, 'Content-Range': ""}

        with open(local_path, 'rb') as f:
            content = f.read(327680)
            left = 0
            right = len(content) - 1
            while content:
                headers['Content-Length'] = str(len(content))
                headers['Content-Range'] = "bytes " + str(left) + '-' + str(right) + '/' + str(file_size)
                response = requests.put(upload_url, headers=headers, data=content).json()
                # print(response)
                if "error" in response:
                    print("Uploading " + local_path + " failed because of ", response["error"]["code"], response["error"]["code"])
                    break
                left = right + 1
                content = f.read(327680)
                right = right + len(content)
                print('Uploading ' + local_path.split('/')[-1], naturalsize(right),end='\r',flush=True)
            print()


    def create_dir(self, name):
        query = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        body = {
            "name": name,
            "folder": {}
        }
        self.run_query(query, "POST", None, body)

    def upload_folder(self, local_path):
        dirname = local_path.split('/')[-1]
        files = []
        for f in os.listdir(local_path):
            fpath = os.path.join(local_path, f)
            if os.path.isfile(fpath):
                files.append((f, fpath))
        self.create_dir(dirname)
        dirname = dirname.replace(":", " ")

        for filename,filepath in files:
            filename = filename.replace(":", " ")
            self.upload_file(filepath, '/' + dirname + '/' + filename)

    def run(self):
        # query = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        # body = {
        #     "name": "Google Slides",
        #     "folder": {}
        # }
        # print(self.run_query(query, "POST", None, body))
        # # query = "https://graph.microsoft.com/v1.0/me/drive/root:/temp/Document.docx:/content"

        # data = self.run_query(query,"GET")
        # print(data.headers)
        headers = {}
        self.create_dir("large")
        # self.upload_large_file("Google Docs/Biometric_database.docx", "/large/Biometric_database.docx")
        for folder in config.upload_dirs:
            print(folder)
            self.upload_folder(folder)
        # print(self.upload_file("slides/Maths_Project.pptx", "/Google Slides/" + "Maths_Project.pptx").json())
        # print(self.upload_file())

if __name__ == "__main__":
    ms_app = MSApp()
    ms_app.run()





