from flask import Flask, jsonify, render_template, request, make_response
from service import GoogleDriveService
import io
import zipfile


app = Flask(__name__, template_folder="templates")


class DownloadFiles:

    def __init__(self):
        self.app = app
        self.service = GoogleDriveService().build()
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/files', 'get_files', self.get_files, methods=['GET'])
        self.app.add_url_rule('/download', 'download_files', self.download_files, methods=['POST'])

    def index(self):
        return render_template("index.html")

    # @app.route('/files', methods=['GET'])
    def get_files(self):
        results = self.service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name)",
            q="mimeType != 'application/vnd.google-apps.folder'").execute()
        items = results.get('files', [])
        return jsonify({'files': items})

    def download_selected_files(self, file_ids):
        # store zip in memory
        zip_buffer = io.BytesIO()

        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_id in file_ids:
                    new_id = file_id.strip("[").strip("]").replace('"', "")
                    file_metadata = self.service.files().get(fileId=new_id).execute()
                    file_name = file_metadata['name']
                    file_request = self.service.files().get_media(fileId=new_id)
                    file_content = file_request.execute()

                    # Add the file content to the zip archive
                    zip_file.writestr(file_name, file_content)

        except Exception as e:
            # Handle any errors that may occur during file download
            print(f"Error downloading files: {e}")
            return jsonify({'message': 'Error downloading files.'}), 500

        # Set the buffer's position to the beginning after writing all files
        zip_buffer.seek(0)

        # Create a response with the zip file data and appropriate headers
        response = make_response(zip_buffer.getvalue())
        response.headers.set('Content-Type', 'application/zip')
        response.headers.set('Content-Disposition', 'attachment; filename=selected_files.zip')
        response.headers.set('Content-Length', str(len(zip_buffer.getvalue())))

        return response

    def download_files(self):
        file_ids = request.form.getlist('files')
        if not file_ids:
            return jsonify({'message': 'No files selected.'}), 400

        # Pass the selected file IDs to the download_selected_files() function
        return self.download_selected_files(file_ids)


if __name__ == "__main__":
    my_app = DownloadFiles()
    app.run()
