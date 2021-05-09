#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import parsel
import datetime


def write_line_to_file(filename, line):
    f = open(filename, "a+")
    f.write(line)
    f.close()


def get_house_num():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
        # AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }
    url = "https://sh.ke.com/ershoufang/"
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        selector = parsel.Selector(response.text)
        lis = selector.css('div.resultDes')
        nums_of_house = lis.css('span::text').get().strip()
        # print("success! get status 200")
        return int(nums_of_house)
    else:
        # print("fail! get status 200")
        return -1


def format_house_num_with_time(nums):
    time1_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # time1_str = datetime.datetime.now()
    line_str = "%s,%d\n" % (time1_str, nums)
    print(line_str)
    return line_str


def pull_beike_num_job(file_name):
    res = get_house_num()
    if res < 0:
        print("error! please check your network")
    else:
        format_str = format_house_num_with_time(res)
        write_line_to_file(file_name, format_str)


def get_house_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
        # AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }
    # url = "https://sh.ke.com/xiaoqu/5011000018368/"
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        selector = parsel.Selector(response.text)
        lis = selector.css('div.xiaoquPrice')
        house_price = lis.css('span::text').get().strip()
        # print("success! get status 200")
        lis = selector.css('h1.main')
        house_name = lis.css('h1::text').get().strip()
        return house_name, house_price
    else:
        # print("fail! get status 200")
        return -1, -1


def format_house_price_with_time(name, price):
    time1_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # time1_str = datetime.datetime.now()
    line_str = "%s,%s,%s\n" % (time1_str, name, price)
    print(line_str)
    return line_str


def pull_beike_price_job(file_name, url):
    name, price = get_house_price(url)
    if int(price) < 0:
        print("error get price! please check your network")
    else:
        format_str = format_house_price_with_time(name, price)
        write_line_to_file(file_name, format_str)


def cp_to_nginx(source, dest):
    cmd = "cp -f %s %s" % (source, dest)
    print(cmd)
    os.system(cmd)


if __name__ == '__main__':
    num_file_name = "n.txt"
    price_file_name = "p.txt"
    source_file_name = "/root/kanfangbao/kanfangbao/{n.txt,p.txt}"
    dest_file_path = "/root/nginx_kfb/"
    price_url_1 = "https://sh.ke.com/xiaoqu/5011000018368/"
    price_url_2 = "https://sh.ke.com/xiaoqu/5011000015731/"

    # debug
    # scheduler = BlockingScheduler()
    # scheduler.add_job(pull_beike_num_job, 'interval', seconds=3, max_instances=10, args=[num_file_name])
    # scheduler.add_job(pull_beike_price_job, 'interval', seconds=2, max_instances=10, args=[price_file_name,price_url_1])
    # scheduler.add_job(pull_beike_price_job, 'interval', seconds=2, max_instances=10, args=[price_file_name,price_url_2])
    # scheduler.add_job(cp_to_nginx, 'interval', seconds=10, max_instances=10,
    #                   args=[source_file_name, dest_file_path])

    scheduler = BlockingScheduler()
    scheduler.add_job(pull_beike_num_job, 'cron', hour='8,20', minute=20, max_instances=10, args=[num_file_name])
    scheduler.add_job(pull_beike_price_job, 'cron', hour='8,20', minute=25, max_instances=10,
                      args=[price_file_name, price_url_1])
    scheduler.add_job(pull_beike_price_job, 'cron', hour='8,20', minute=30, max_instances=10,
                      args=[price_file_name, price_url_2])
    scheduler.add_job(cp_to_nginx, 'cron', hour='8,20', minute=35, max_instances=10,
                      args=[source_file_name, dest_file_path])

    print("schedule task at hour='8-10', minute=20-35")
    print('Press Ctrl+ C to exit')
    #
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    # pull_beike_price_job('a.txt', url)
