import subprocess
import os
def get_installed_packages():
    # 儲存有效的 package 名稱
    valid_packages = []

    try:
        # 使用 adb 執行 `pm list packages` 指令
        result = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'], stderr=subprocess.STDOUT)
        
        # 將結果解碼並分行
        packages = result.decode('utf-8').splitlines()
        
        # 處理每個 package 的結果
        for package in packages:
            if package.startswith('package:'):
                valid_packages.append(package.replace('package:', '').strip())
        
    except subprocess.CalledProcessError as e:
        # 捕捉執行過程中的錯誤
        print(f"ADB 執行錯誤: {e.output.decode('utf-8')}")
    except Exception as e:
        # 捕捉其它異常
        print(f"發生未知錯誤: {str(e)}")
    
    return valid_packages

# 執行並取得所有有效的 package 名稱
packages = get_installed_packages()

def get_apk_path(package_name):
    """
    使用 `adb pm path` 獲取包名對應的 APK 路徑
    """
    try:
        result = subprocess.check_output(['adb', 'shell', 'pm', 'path', package_name, '|', 'grep', 'base'], stderr=subprocess.STDOUT)
        apk_path = result.decode('utf-8').strip().replace('package:', '')
        return apk_path
    except subprocess.CalledProcessError as e:
        print(f"錯誤：無法獲取 {package_name} 的 APK 路徑。")
        return None
    except Exception as e:
        print(f"發生未知錯誤：{str(e)}")
        return None

def pull_apk(package_name):
    """
    使用 `adb pull` 下載 APK 並重命名為 package_name.apk
    """
    try:
        # 確保資料夾存在
        if not os.path.exists(os.path.join(os.getcwd(), 'output')):
            os.makedirs(os.path.join(os.getcwd(), 'output'))

        # 取得 APK 路徑
        apk_path = get_apk_path(package_name)
        if apk_path:
            # 使用 adb pull 下載 APK
            save_file = os.path.join(os.path.join(os.getcwd(), 'output'), f"{package_name}.apk")
            subprocess.check_call(['adb', 'pull', apk_path, save_file])
            print(f"已成功下載 {package_name} 的 APK 到 {save_file}")
        else:
            print(f"{package_name} APK 路徑無效，跳過下載。")
    except subprocess.CalledProcessError as e:
        print(f"錯誤：無法拉取 {package_name} 的 APK 文件。")
    except Exception as e:
        print(f"發生未知錯誤：{str(e)}")

def pull_apks_from_list(package_list):
    """
    遍歷所有 package，並將 APK 下載並重命名
    """
    for package in package_list:
        pull_apk(package)

# 顯示結果
if packages:
    pull_apks_from_list(packages)
else:
    print("沒有找到有效的 package 名稱。")

