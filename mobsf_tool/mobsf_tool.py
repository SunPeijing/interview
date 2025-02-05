import inquirer
import subprocess
import os
# 定義不同的函數

# 顯示選單讓使用者選擇
def main_menu():
    #subprocess.run('clear')
    questions = [
        inquirer.List('function',
                      message="Please choose a function to run",
                      choices=['pull all apk', 'only pull base.apk', 'specific apk', 'upload apk', 'Exit'],
                      ),
    ]
    answers = inquirer.prompt(questions)

    # 根據使用者選擇調用相應的函數
    if answers['function'] == 'pull all apk':
        subprocess.run(['python3', 'pull_apk.py'])
    elif answers['function'] == 'only pull base.apk':
        subprocess.run(['python3', 'only_base_apk.py'])
    elif answers['function'] == 'specific apk':
        specific_apk()
    elif answers['function'] == 'upload apk':
        subprocess.run(['python3', 'upload_apk.py'])
    elif answers['function'] == 'Exit':
        print("Exiting the program...")
        exit()

def search_apk(search_term):
    package_list = get_package_list()
    matching_paths = []

    for package_info in package_list:
        # Check if the search term matches either the package or path
        if search_term.lower() in package_info.lower():
            matching_paths.append(package_info)

    return matching_paths

def get_package_list():
    """Fetch the list of installed packages and their paths using adb."""
    try:
        # Use adb to list installed packages with paths
        result = subprocess.check_output(
            "adb shell pm list packages", shell=True, stderr=subprocess.STDOUT
        )
        return result.decode('utf-8').strip().split("\n")
    except subprocess.CalledProcessError as e:
        print("Error fetching package list from adb:", e.output.decode('utf-8'))
        return []

def specific_apk():
    search_term = input("Enter search string: ").strip()
    
    if not search_term:
        print("Search term cannot be empty. Exiting.")
        return

    print(f"Searching for APKs containing '{search_term}'...")
    
    results = search_apk(search_term)

    if results:
        subprocess.run('clear')
        choices = ["All"] + [f" {package_name}" for package_name in results]
    
        questions = [
            inquirer.List('selected_apk',
                           message="Select an APK to view details",
                           choices=choices,
                           carousel=True)
        ]

        selected_apk = inquirer.prompt(questions)
        if selected_apk:
            selected_choice = selected_apk['selected_apk']
            if selected_choice == "All":
                print("\nYou selected all APKs:")
                for package_name in results:
                    pull_apk(f"{package_name}")
            else:
                pull_apk(selected_choice)
    else:
        print("No matching APKs found.")


def pull_apk(packages):
    package_name = packages.replace('package:', '').strip()    
    # 设置保存文件的路径（可以根据需求进行修改）
    if not os.path.exists(os.path.join(os.getcwd(), 'output')):
        os.makedirs(os.path.join(os.getcwd(), 'output'))
    save_path = os.path.join(os.getcwd(), 'output')
    save_file = os.path.join(os.path.join(os.getcwd(), 'output'), f"{package_name}.apk")
    # 执行 adb pull 命令
    try:
        print(f"Pulling package: {package_name}...")
        result = subprocess.check_output(['adb', 'shell', 'pm', 'path', package_name, 'base'], stderr=subprocess.STDOUT)
        apk_path = result.decode('utf-8').strip().replace('package:', '')
        copy_command = f'cp {apk_path} /sdcard/my_app.apk'
        subprocess.check_call(['adb', 'shell', f'su 0 {copy_command}'])
        subprocess.check_call(['adb', 'pull', '/sdcard/my_app.apk', save_file])
        print(f"Package {package_name} pulled successfully to {save_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error while pulling {package_name}: {e}")



# 主程序運行
if __name__ == "__main__":
    while True:
        main_menu()



