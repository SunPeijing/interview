import subprocess
import time
import inquirer
import json

# 假設這是你的 curl 執行函數
def execute_curl_command(command):
    """執行 curl 命令"""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error executing curl: {result.stderr}")
        raise Exception(f"Error: {result.stderr}")
    return result.stdout

def get_user_inputs():
    """使用 inquirer 收集用戶輸入並加入預設值"""
    questions = [
        inquirer.Text("NESSUS_URL", message="請輸入 Nessus URL", default="https://localhost:8834"),
        inquirer.Text("USERNAME", message="請輸入 Nessus 帳號", default="nate"),
        inquirer.Password("PASSWORD", message="請輸入 Nessus 密碼", default="123456"),
    ]
    return inquirer.prompt(questions)

def authenticate(NESSUS_URL, USERNAME, PASSWORD):
    """登入並取得 Token"""
    url = f"{NESSUS_URL}/session"
    curl_command = [
        "curl", "-k", "-X", "POST", url,
        "-d", f'{{"username": "{USERNAME}", "password": "{PASSWORD}"}}',
        "-H", "Content-Type: application/json"
    ]
    response = execute_curl_command(curl_command)
    token = response.split('"token":"')[1].split('"')[0]
    return token

def get_policy_template(NESSUS_URL, token):
    """獲取策略模板列表，並讓用戶選擇策略"""
    url = f"{NESSUS_URL}/policies"
    headers = {"X-Cookie": f"token={token}"}
    
    curl_command = [
        "curl", "-k", "-X", "GET", url,
        "-H", f"X-Cookie: token={token}"
    ]
    
    response = execute_curl_command(curl_command)
    # 將返回的JSON字符串轉換為字典
    policies = json.loads(response)
    
    # 讓用戶選擇策略
    policy_choices = []
    for policy in policies["policies"]:
        policy_choices.append({
            'name': policy["name"], 
            'value': {
                'template_uuid': policy["template_uuid"],
                'policy_id': policy["id"]
            }
        })
    
    # 使用 inquirer 顯示選項並讓用戶選擇
    select_policy = inquirer.prompt([
        inquirer.List('policy',
                      message="選擇一個掃描策略",
                      choices=policy_choices)
    ])['policy']
    
    return select_policy['value']

def get_target_input():
    """讓使用者輸入掃描目標"""
    target_question = [
        inquirer.Text("TARGETS", message="請輸入掃描目標 (多個以逗號分隔)", default="example.com,test.com"),
    ]
    target_input = inquirer.prompt(target_question)
    return target_input['TARGETS']

def create_scan(NESSUS_URL, token, TARGETS, policy_uuid, policy_id):
    """建立掃描"""
    headers = {"X-Cookie": f"token={token}"}
    scan_payload = {
        "uuid": policy_uuid,
        "settings": {
            "name": f"Web Scan for {TARGETS}",
            "description": f"Scan for {TARGETS}",
            "emails": "",
            "enabled": "true",
            "launch": "ONETIME",  # 假設是一次性掃描
            "folder_id": 1,       # 假設在文件夾ID 1中
            "policy_id": policy_id,
            "scanner_id": 1,      # 假設使用ID 1的掃描器
            "text_targets": TARGETS,
            "agent_group_id": []
        }
    }
    
    # 將字典轉換為JSON字符串
    json_payload = json.dumps(scan_payload)
    
    url = f"{NESSUS_URL}/scans"
    
    curl_command = [
        "curl", "-k", "-X", "POST", url,
        "-H", f"X-Cookie: token={token}",
        "-d", json_payload,  # 使用JSON字符串而非字典
        "-H", "Content-Type: application/json"
    ]
    
    response = execute_curl_command(curl_command)
    print(f"{response}")
    # 從返回的結果中解析scan_id
    response_json = json.loads(response)
    scan_id = response_json['scan']['id']
    
    return scan_id

def launch_scan(NESSUS_URL, token, scan_id):
    """啟動掃描"""
    headers = f"X-Cookie: token={token}"
    url = f"{NESSUS_URL}/scans/{scan_id}/launch"
    
    curl_command = [
        "curl", "-k", "-X", "POST", url,
        "-H", headers
    ]
    
    execute_curl_command(curl_command)

def wait_for_scan_completion(NESSUS_URL, token, scan_id):
    """等待掃描完成"""
    headers = f"X-Cookie: token={token}"
    url = f"{NESSUS_URL}/scans/{scan_id}"
    while True:
        curl_command = [
            "curl", "-k", "-X", "GET", url,
            "-H", headers
        ]
        response = execute_curl_command(curl_command)
        status = response.split('"status":"')[1].split('"')[0]
        print(f"掃描狀態: {status}")
        if status == "completed":
            break
        time.sleep(10)

def download_report(NESSUS_URL, token, scan_id):
    """下載報告"""
    headers = f"X-Cookie: token={token}"
    
    # 1. 請求生成報告
    export_url = f"{NESSUS_URL}/scans/{scan_id}/export"
    curl_command = [
        "curl", "-k", "-X", "POST", export_url,
        "-d", '{"format": "pdf"}',
        "-H", headers,
        "-H", "Content-Type: application/json"
    ]
    response = execute_curl_command(curl_command)
    file_id = response.split('"file":')[1].split(',')[0]

    # 2. 下載報告
    download_url = f"{NESSUS_URL}/scans/{scan_id}/export/{file_id}/download"
    curl_command = [
        "curl", "-k", "-X", "GET", download_url,
        "-H", headers, "-o", "nessus_report.pdf"
    ]
    
    execute_curl_command(curl_command)
    print("報告已下載為 nessus_report.pdf")

def main():
    user_inputs = get_user_inputs()
    NESSUS_URL = user_inputs["NESSUS_URL"]
    USERNAME = user_inputs["USERNAME"]
    PASSWORD = user_inputs["PASSWORD"]

    try:
        token = authenticate(NESSUS_URL, USERNAME, PASSWORD)
        
        # 從 get_policy_template 中獲取選擇的策略的 template_uuid 和 policy_id
        selected_policy = get_policy_template(NESSUS_URL, token)
        policy_uuid = selected_policy['template_uuid']
        policy_id = selected_policy['policy_id']
        
        # 提示用戶輸入掃描目標
        TARGETS = input("請輸入掃描目標 (多個以逗號分隔): ")
        
        # 創建掃描並獲取 scan_id
        scan_id = create_scan(NESSUS_URL, token, TARGETS, policy_uuid, policy_id)
        
        # 啟動掃描
        launch_scan(NESSUS_URL, token, scan_id)
        
        # 等待掃描完成
        wait_for_scan_completion(NESSUS_URL, token, scan_id)
        
        # 下載報告
        download_report(NESSUS_URL, token, scan_id)
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()
