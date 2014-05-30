from config import *
import json
import requests
import sys, os

target_section = 'A'

payload = {'udid': udid,
           'collegeSeq': collegeSeq,
           'curdate': ''}

r = requests.post(foodTotal, data=payload)
j = json.loads(r.text)

food_list = []

for shop in j['shopList']:
    try:
        location = shop['name'] + ' - ' + shop['locName']

        main = []
        others = []

        for i in j['shopList'][0]['foodList']:
            if i['section'] == target_section:
                main.append(i['mainFood'])
                others.append(', '.join(i['foods'].split(',')))

        food_format = '[ %s ]\r\n' % location

        for i, m in enumerate(main):
            food_format += '* %s *\r\n- %s\r\n\r\n' % (m, others[i])

        food_format = food_format[:-3]

        food_list.append(food_format.encode('utf-8'))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

message = '\r\n\r\n'.join(food_list)

