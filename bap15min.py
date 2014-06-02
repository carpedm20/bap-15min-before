#-*- coding: utf-8 -*-
from xvfbwrapper import Xvfb
from datetime import datetime
import facebook
import mechanize
import urllib2
import json
import atexit
import sys, os
import Image
import requests
import jinja2
from selenium import webdriver

from config import fb_email, fb_pass, page_id, udid, collegeSeq, foodTotal

class Menu:
    def __init__(self, name, location, main, others):
        self.name = name
        self.location = location
        self.main = main
        self.others = others

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

bap_time = [[7, 00, 'A'], [11, 20, 'B'], [17, 00, 'C']]
bap_index = 2

templateLoader = jinja2.FileSystemLoader( searchpath="/" )
templateEnv = jinja2.Environment( loader=templateLoader )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, 'bap15min_jinja.html')

template = templateEnv.get_template( TEMPLATE_FILE )

while True:
#for i in range(3):
#if True:
  try:
    date = u'%s월 %s일' % (datetime.now().month, datetime.now().day)

    if bap_index == 0:
        food = u'조식'
    elif bap_index == 1:
        food = u'중식'
    else:
        food = u'석식'

    hour = datetime.now().hour
    minute = datetime.now().minute

    target_hour = bap_time[bap_index][0]
    target_min = bap_time[bap_index][1]
    target_section = bap_time[bap_index][2]

    if hour is target_hour and minute is target_min:
    #if True:
        bap_index = (bap_index + 1) % len(bap_time)

        payload = {'udid': udid,
                   'collegeSeq': collegeSeq,
                   'curdate': ''}

        r = requests.post(foodTotal, data=payload)
        j = json.loads(r.text)

        food_list = []
        menus = []

        for shop in j['shopList']:
            try:
                name = shop['name']
                location = shop['locName']

                main = []
                others = []

                for i in shop['foodList']:
                    if i['section'] == target_section:
                        main.append(i['mainFood'])
                        others.append(i['foods'].split(','))

                        print main[0]

                max_length = 0
                for other in others:
                    if len(other) > max_length:
                        max_length = len(other)

                new_others = []
                for i in range(max_length):
                    subs = []
                    for other in others:
                        try:
                            subs.append(other[i])
                        except:
                            subs.append(' ')
                    new_others.append(subs)

                menu = Menu(name, location, main, new_others)
                menus.append(menu)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        outputText = template.render(menus=menus, date=date, food=food)

        f = open('bap15min.html', 'w')
        f.write(outputText.encode('utf8'))
        f.close()

        file_name = 'screenshot.png'

        browser = webdriver.Firefox()
        if len(menus) > 4:
            browser.set_window_size(1000,1000)
        browser.get('http://hexa.perl.sh/~carpedm30/bap15min.html')
        browser.save_screenshot(file_name)

        app_access = get_app_access()
        print " [%] APP_ACCESS : " + app_access

        content = '제작자 : 김태훈(carpedm20)'

        graph = facebook.GraphAPI(app_access)
        #graph.put_wall_post(content)

        graph.put_photo(open(file_name), content)

  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    
    #continue
