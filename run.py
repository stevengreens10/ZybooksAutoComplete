import decimal
import random

import requests
import settings
import datetime
import hashlib
import time


def checksum(activity_id, ts, token):
    md5 = hashlib.md5()
    md5.update('content_resource/{}/activity'.format(activity_id))
    md5.update(ts)
    md5.update(token)
    return md5.hexdigest()


def delay():
    # Delays the program
    min_sleep = float(settings.TIME_INTERVAL) * (1 - (float(settings.PERCENTAGE_VARIANCE) / 100))
    max_sleep = float(settings.TIME_INTERVAL) * (1 + float(settings.PERCENTAGE_VARIANCE) / 100)

    if max_sleep == min_sleep:
        time.sleep(max_sleep)
        return

    actual_sleep = float(decimal.Decimal(random.randrange(int(min_sleep * 100), int(max_sleep * 100))) / 100)
    print("Sleeping for {} seconds".format(actual_sleep))
    time.sleep(actual_sleep)


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

if login_data['success']:
    print("Login Success")

    # print(login_data)

    auth_token = login_data['session']['auth_token']
    user_id = login_data['user']['user_id']

    get_classes_url = 'https://zyserver.zybooks.com/v1/user/' + str(user_id) + '/items'
    get_classes_params = {'items': '["zybooks"]', 'auth_token': auth_token}

    get_classes_response = requests.get(get_classes_url, params=get_classes_params)
    get_classes_data = get_classes_response.json()

    for subject in get_classes_data['items']['zybooks']:
        zybook_code = subject['zybook_code']

        class_info_url = 'https://zyserver.zybooks.com/v1/zybooks'
        class_info_params = {'zybooks': '["' + zybook_code + '"]',
                             'auth_token': auth_token}

        class_info_response = requests.get(class_info_url, params=class_info_params)
        class_info_data = class_info_response.json()

        zybook = class_info_data['zybooks'][0]

        if (settings.COURSE != zybook_code
                and settings.COURSE != zybook['course']['course_call_number']
                and settings.COURSE != zybook['course']['name']):
            # Go to next zybook
            continue

        for chapter in zybook['chapters']:

            if settings.CHAPTER_NUMBER != chapter["number"]:
                # Go to next chapter
                continue

            for section in chapter['sections']:
                chapter_num = section['canonical_chapter_number']
                section_id = section['canonical_section_id']
                section_num = section['canonical_section_number']

                if str(section_num) not in settings.SECTION_NUMBERS.split(","):
                    # Go to next section if it is not in settings
                    continue

                print("Chapter " + str(chapter_num) + " : Section " + str(section_num))

                section_url = 'https://zyserver.zybooks.com/v1/zybook/NCSUCSC226ScafuroSpring2018/chapter/{}/section/{}' \
                    .format(chapter_num, section_num)
                section_params = {'auth_token': auth_token}

                section_response = requests.get(section_url, section_params)
                section_data = section_response.json()

                content_resources = section_data['section']['content_resources']

                for resource in content_resources:

                    activity_type = resource['activity_type']
                    resource_type = resource['type']
                    resource_id = resource['id']

                    payload = resource['payload']

                    resource_url = 'https://zyserver.zybooks.com/v1/content_resource/{}/activity' \
                        .format(resource_id)

                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y-%m-%dT%H:%M.000")
                    cs = checksum(resource_id, timestamp, auth_token)

                    if activity_type == 'participation':
                        print("Participation: " + str(resource))

                        participation_payload = {'auth_token': auth_token,
                                                 'complete': True,
                                                 'timestamp': timestamp,
                                                 'zybook_code': zybook_code,
                                                 '__cs__': cs}

                        if resource_type == 'multiple_choice':
                            participation_payload['answer'] = 1
                            num_questions = len(payload['questions'])
                            for i in range(num_questions):
                                participation_payload['part'] = i
                                participation_response = requests.post(resource_url,
                                                                       headers=headers,
                                                                       json=participation_payload)
                                participation_response_data = participation_response.json()
                                if participation_response_data['success'] is True:
                                    print("Question id {} number {} completed.".format(resource_id, i))
                                    delay()
                        elif resource_type == 'custom' and payload['tool'] == 'zyAnimator':
                            participation_payload['part'] = 0
                            participation_payload['metadata'] = '{"event": "animation completely watched"}'
                            participation_response = requests.post(resource_url,
                                                               headers=headers,
                                                               json=participation_payload)
                            participation_response_data = participation_response.json()
                            if participation_response_data['success'] is True:
                                print("Participation video id {} completed.".format(resource_id))
                                delay()
                    elif activity_type == 'challenge':
                        print("Challenge: " + str(resource))

else:
    print("Login information incorrect!")
