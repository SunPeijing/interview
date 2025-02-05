import subprocess
import json
import os

apk_dir = os.path.join(os.getcwd(), 'output')
url = 'http://localhost:8001/api/v1/upload'
auth_token = '0d34c74bc75619c220c28ec1715dd371c44734ca5d7976e37db8e530472f857f'

for file_name in os.listdir(apk_dir):
    # Check if the file has an .apk extension
    if file_name.endswith('.apk'):
        apk_path = os.path.join(apk_dir, file_name)
        print(f"Uploading {apk_path}...")

        # Construct the curl command
        curl_command = f"curl -F 'file=@{apk_path}' {url} -H 'Authorization: {auth_token}'"
        
        try:
            response = subprocess.check_output(curl_command, shell=True, stderr=subprocess.STDOUT)
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
            else:
                print("Hash not found.")

        except json.JSONDecodeError:
            print("Error: Invalid JSON in response.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output.decode('utf-8')}")
