import decimal
import random
from getpass import getpass

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
    # print("Sleeping for {} seconds".format(actual_sleep))
    time.sleep(actual_sleep)


def send_post(url, payload, headers=None):
    if headers:
        r = requests.post(url, json=payload, headers=headers)
        return r.json()
    else:
        r = requests.post(url, json=payload)
        return r.json()


def send_get(url, params):
    r = requests.get(url, params=params)
    return r.json()


email = raw_input("Enter your e-mail for Zybooks: ")
# print("Enter your password for Zybooks: ")
password = getpass()

print("")

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

login_data = send_post("https://zyserver.zybooks.com/v1/signin", login_payload, headers=headers)

if login_data['success']:
    print("Login Success")

    # print(login_data)

    auth_token = login_data['session']['auth_token']
    user_id = login_data['user']['user_id']

    get_classes_url = 'https://zyserver.zybooks.com/v1/user/' + str(user_id) + '/items'
    get_classes_params = {'items': '["zybooks"]', 'auth_token': auth_token}

    get_classes_data = send_get(get_classes_url, get_classes_params)

    for subject in get_classes_data['items']['zybooks']:
        zybook_code = subject['zybook_code']

        class_info_url = 'https://zyserver.zybooks.com/v1/zybooks'
        class_info_params = {'zybooks': '["' + zybook_code + '"]',
                             'auth_token': auth_token}

        class_info_data = send_get(class_info_url, class_info_params)

        zybook = class_info_data['zybooks'][0]
        
        # print(zybook)

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

                if str(section_num) not in settings.SECTION_NUMBERS.split(",") \
                        and settings.SECTION_NUMBERS != '*':
                    # Go to next section if it is not in settings
                    continue

                print("\n---Chapter " + str(chapter_num) + " : Section " + str(section_num) + "---\n")

                section_url = 'https://zyserver.zybooks.com/v1/zybook/{}/chapter/{}/section/{}' \
                    .format(zybook_code, chapter_num, section_num)
                section_params = {'auth_token': auth_token}

                section_data = send_get(section_url, section_params)

                content_resources = section_data['section']['content_resources']

                for resource in content_resources:
                    # print(resource)
                    activity_type = resource['activity_type']
                    resource_type = resource['type']
                    resource_id = resource['id']
                    num_parts = resource['parts']

                    payload = resource['payload']

                    resource_url = 'https://zyserver.zybooks.com/v1/content_resource/{}/activity' \
                        .format(resource_id)

                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y-%m-%dT%H:%M.000")
                    cs = checksum(resource_id, timestamp, auth_token)

                    answer_payload = {'auth_token': auth_token, 'complete': True, 'timestamp': timestamp,
                                      'zybook_code': zybook_code, '__cs__': cs, 'metadata': '{}', 'answer': 1}

                    for i in range(num_parts):
                        answer_payload['part'] = i
                        response_data = send_post(resource_url, answer_payload)
                        if response_data['success'] is True:

                            type_str = resource_type
                            if type_str == 'custom':
                                type_str = payload['tool']
                            print('{} "{}" id {} part {} completed.'
                                  .format(activity_type.title(), type_str, resource_id, i + 1))
                            delay()
                        else:
                            print('{} "{}" id {} part {} failed.'
                                  .format(activity_type.title(), type_str, resource_id, i + 1))
else:
    print("Login information incorrect!")
