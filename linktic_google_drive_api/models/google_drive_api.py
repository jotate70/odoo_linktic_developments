from __future__ import print_function

import os.path
import io
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class LinkticGoggleDriveApi(models.AbstractModel):
    _name = 'linktic.google.drive.config'
    _auto = False
    _abstract = True
    _description = 'class used to connect to drive and all drives scopes, processes'

    def set_google_drive_service(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        odoo_dir = os.path.dirname(os.path.realpath(__file__)).rsplit('/', 1)[0]
        token_dir = os.path.join(odoo_dir, 'token.json')
        credentials_dir = os.path.join(odoo_dir, 'credentials.json')
        if os.path.exists(token_dir):
            creds = Credentials.from_authorized_user_file(token_dir, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_dir, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_dir, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('drive', 'v3', credentials=creds)
        except HttpError as error:
            print(f'An error occurred: {error}')
            raise ValidationError(_(f'An error occurred: {error}'))

        return service

    def convert_drive_files_to_attachments(self, drive_service, model, res_id):
        # select resource to get drive folder and to attach the files
        # The repository url field has to be named "document_repository"
        res_obj = self.env[model].browse(res_id)
        drive_folder = res_obj.document_repository.split('/')[-1]

        # Search for files in the folder or URL
        query = f"'{drive_folder}' in parents"
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        # Download each file in the folder or URL
        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            # Save the file to disk
            with open(file_name, 'wb') as f:
                f.write(fh.getvalue())

            # Create ir_attachment record and remove file
            with open(file_name, 'rb') as f:
                base64_datas = base64.b64decode(f.read())
                self.env['ir.attachment'].create({
                    'name': file_name,
                    'type': 'binary',
                    'datas': base64_datas,
                    'res_model': model,
                    'res_id': res_id,
                    'company_id': res_obj.company_id.id,
                })

            os.remove(file_name)

        res_obj.converted_to_attachments = True
