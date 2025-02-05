import subprocess
import json
import os
import asyncio

apk_dir = os.path.join(os.getcwd(), 'output')
url = 'http://localhost:8001/api/v1/upload'
auth_token = '081a4ac5e170bad681cc78615154d7be55cf78f6d902f1d877f4997eb610bfc2'

for file_name in os.listdir(apk_dir):
    # Check if the file has an .apk extension
    if file_name.endswith('.apk'):
        apk_path = os.path.join(apk_dir, file_name)
        print(f"Uploading {apk_path}...")

        # Construct the curl command
        curl_upload_command = f"curl -F 'file=@{apk_path}' http://localhost:8001/api/v1/upload -H 'Authorization: {auth_token}'"
        try:
            response = subprocess.check_output(curl_upload_command, shell=True, stderr=subprocess.STDOUT)
            # Decode the byte response to string
            response_str = response.decode('utf-8')
    
            json_start = response_str.find('{')
    
            json_content = response_str[json_start:]

            # Parse the JSON
            response_json = json.loads(json_content)

            # Extract and print the hash value
            file_hash = response_json.get('hash')
            if file_hash:
                print(f"{file_name}: {file_hash}")
                try:
                    curl_scan_command = f"curl -X POST http://localhost:8001/api/v1/scan --data 'hash={file_hash}' -H 'Authorization: {auth_token}'"
                    subprocess.check_output(curl_scan_command, shell=True, stderr=subprocess.STDOUT)
                    curl_pdf_command = f"curl -X POST --url http://localhost:8001/api/v1/download_pdf --data 'hash={file_hash}' -H 'Authorization: {auth_token}' --output {file_hash}.pdf"
                    subprocess.check_output(curl_pdf_command, shell=True, stderr=subprocess.STDOUT)
                    #print(f"Request sent successfully for hash {file_hash}.")
                except Exception as e:
                    print(f"Error occurred while sending request with curl: {e}")
            else:
                print("Hash not found.")

        except json.JSONDecodeError:
            print("Error: Invalid JSON in response.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output.decode('utf-8')}")
