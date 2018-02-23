import requests
import json

email = raw_input("Enter your e-mail for Zybooks: ")
password = raw_input("Enter your password for Zybooks: ")

login_payload = {"email": email, "password": password}

headers = {'accept': 'application/json, text/javascript, */*; q=0.01',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'en-US,en;q=0.9',
           'connection': 'keep-alive',
           'content-type': 'application/json',
           'host': 'zyserver.zybooks.com',
           'origin': 'learn.zybooks.com',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
           }

login_response = requests.post("https://zyserver.zybooks.com/v1/signin", headers=headers, json=login_payload)

login_data = login_response.json()

if login_data["success"]:
    print("Login Success")

    # print(login_data)

    auth_token = login_data['session']['auth_token']
    user_id = login_data['user']['user_id']

    get_classes_url = 'https://zyserver.zybooks.com/v1/user/' + str(user_id) + '/items'
    get_classes_params = {'items': '["zybooks"]', 'auth_token': auth_token}

    get_classes_response = requests.get(get_classes_url, params=get_classes_params)
    get_classes_data = get_classes_response.json()

    for subject in get_classes_data["items"]["zybooks"]:
        zybook_code = subject["zybook_code"]

        class_info_url = 'https://zyserver.zybooks.com/v1/zybooks'
        class_info_params = {'zybooks': '["' + zybook_code + '"]',
                             'auth_token': auth_token}

        class_info_response = requests.get(class_info_url, params=class_info_params)
        class_info_data = class_info_response.json()

        zybook = class_info_data["zybooks"][0]

        for chapter in zybook["chapters"]:
            for section in chapter["sections"]:
                chapter_num = section["canonical_chapter_number"]
                section_id = section["canonical_section_id"]
                section_num = section["canonical_section_number"]

                section_url = 'https://zyserver.zybooks.com/v1/zybook/NCSUCSC226ScafuroSpring2018/chapter/{}/section/{}'\
                    .format(chapter_num, section_num)
                section_params = {'auth_token': auth_token}

                section_response = requests.get(section_url, section_params)
                section_data = section_response.json()
                

else:
    print("Login information incorrect!")
