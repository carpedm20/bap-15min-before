#-*- coding: utf-8 -*-
from xvfbwrapper import Xvfb
import time, datetime
import facebook
import mechanize
import urllib2
import json
import atexit
import sys, os
import Image
import requests

from datetime import datetime

from config import fb_email, fb_pass, page_id, udid, collegeSeq, foodTotal

vdisplay = Xvfb()
vdisplay.start()

def exit_handler():
    print "DEAD"
    vdisplay.stop()

atexit.register(exit_handler)

facebook_app_link='https://www.facebook.com/dialog/oauth?scope=manage_pages,publish_stream&redirect_uri=http://carpedm20.blogspot.kr&response_type=token&client_id=641444019231608'

def get_second_from_timestamp(v):
    return time.mktime(datetime.datetime.strptime(v, "%d/%m/%Y %H:%M:%S").timetuple())

def get_app_access():
    link='https://www.facebook.com/dialog/oauth?scope=manage_pages,publish_stream&redirect_uri=http://carpedm20.blogspot.kr&response_type=token&client_id=641444019231608'

    br_mech = mechanize.Browser()
    br_mech.set_handle_robots(False)

    #print '[1] open link'
    br_mech.open(link)

    #print '[2] current url : ' + br_mech.geturl()

    br_mech.form = list(br_mech.forms())[0]
    control = br_mech.form.find_control("email")
    control.value=fb_email
    control = br_mech.form.find_control("pass")
    control.value=fb_pass

    #print '[3] submit'
    br_mech.submit()

    #print '[4] current url : ' + br_mech.geturl()

    app_access = br_mech.geturl().split('token=')[1].split('&expires')[0]
    page_app_access_url = "https://graph.facebook.com/me/accounts?access_token=" + app_access

    j = urllib2.urlopen(page_app_access_url)
    j = json.loads(j.read())

    for d in j['data']:
        if d['id'] == page_id:
            app_access = d['access_token']
            break

    return app_access

bap_time = [[7, 30, 'A'], [11, 30, 'B'], [17, 30, 'C']]
bap_index = 0

while True:
  try:
    hour = datetime.now().hour
    minute = datetime.now().minute

    target_hour = bap_time[bap_index][0]
    target_min = bap_time[bap_index][1]
    target_section = bap_time[bap_index][2]

    if hour is target_hour and minute is target_min:
        bap_index = (bap_index + 1) % len(bap_time)

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

        app_access = get_app_access()
        print " [%] APP_ACCESS : " + app_access

        content = message
        content += '\r\n\r\n제작자 : 김태훈(carpedm20)'

        graph = facebook.GraphAPI(app_access)
        graph.put_wall_post(content)
        #graph.put_photo(open(new_file_name), content)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    
    #continue
