import csv
import datetime
import os
import random
from time import sleep

import pandas as pd

from .utils import init_driver, get_last_date_from_csv, log_search_page, keep_scroling, dowload_images


def scrape(since, until=None, words=None, to_account=None, from_account=None, mention_account=None, interval=5,
           lang=None,
           headless=True, limit=float("inf"), display_type="Top", resume=False, proxy=None, hashtag=None,
           show_images=False, save_images=False, save_dir="outputs", save_name=None, filter_replies=False,
           proximity=False,
           geocode=None, minreplies=None, minlikes=None, minretweets=None, filter_func=None):
    """
    scrape data from twitter using requests, starting from <since> until <until>. The program make a search between each <since> and <until_local>
    until it reaches the <until> date if it's given, else it stops at the actual date.

    return:
    data : df containing all tweets scraped with the associated features.
    save a csv file containing all tweets scraped with the associated features.
    """

    # ------------------------- Variables : 
    # header of csv
    header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis', 'Comments', 'Likes',
              'Retweets',
              'Image link', 'Tweet URL']
    # list that contains all data 
    data = []
    # unique tweet ids
    tweet_ids = set()
    # write mode 
    write_mode = 'w'
    # start scraping from <since> until <until>
    # add the <interval> to <since> to get <until_local> for the first refresh
    until_local = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
    # if <until>=None, set it to the actual date
    if until is None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    # set refresh at 0. we refresh the page for each <interval> of time.
    refresh = 0

    # ------------------------- settings :
    # file path
    if save_name:
        path = save_dir + "/" + save_name + ".csv"
    else:
        if words:
            if type(words) == str:
                words = words.split("//")
            path = save_dir + "/" + '_'.join(words) + '_' + str(since).split(' ')[0] + '_' + \
                   str(until).split(' ')[0] + '.csv'
        elif from_account:
            path = save_dir + "/" + from_account + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
                0] + '.csv'
        elif to_account:
            path = save_dir + "/" + to_account + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
                0] + '.csv'
        elif mention_account:
            path = save_dir + "/" + mention_account + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
                0] + '.csv'
        elif hashtag:
            path = save_dir + "/" + hashtag + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
                0] + '.csv'

    # create the <save_dir>
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # show images during scraping (for saving purpose)
    if save_images == True:
        show_images = True
    # initiate the driver
    driver = init_driver(headless, proxy, show_images)
    # resume scraping from previous work
    if resume:
        since = str(get_last_date_from_csv(path))[:10]
        write_mode = 'a'

    # ------------------------- start scraping : keep searching until until
    # open the file
    with open(path, write_mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_mode == 'w':
            # write the csv header
            writer.writerow(header)
        # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
        while until_local <= datetime.datetime.strptime(until, '%Y-%m-%d'):
            # number of scrolls
            scroll = 0
            # convert <since> and <until_local> to str
            if type(since) != str:
                since = datetime.datetime.strftime(since, '%Y-%m-%d')
            if type(until_local) != str:
                until_local = datetime.datetime.strftime(until_local, '%Y-%m-%d')
            # log search page between <since> and <until_local>
            path = log_search_page(driver=driver, words=words, since=since,
                                   until_local=until_local, to_account=to_account,
                                   from_account=from_account, mention_account=mention_account, hashtag=hashtag,
                                   lang=lang,
                                   display_type=display_type, filter_replies=filter_replies, proximity=proximity,
                                   geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
            # number of logged pages (refresh each <interval>)
            refresh += 1
            # number of days crossed
            # days_passed = refresh * interval
            # last position of the page : the purpose for this is to know if we reached the end of the page or not so
            # that we refresh for another <since> and <until_local>
            last_position = driver.execute_script("return window.pageYOffset;")
            # should we keep scrolling ?
            scrolling = True
            # print("looking for tweets between " + str(since) + " and " + str(until_local) + " ...")
            # print(" path : {}".format(path))
            # number of tweets parsed
            tweet_parsed = 0
            # sleep 
            sleep(random.uniform(0.5, 1.5))
            # start scrolling and get tweets
            driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
                keep_scroling(driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position,
                              filter_func)

            # keep updating <start date> and <end date> for every search
            if type(since) == str:
                since = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
            else:
                since = since + datetime.timedelta(days=interval)
            if type(since) != str:
                until_local = datetime.datetime.strptime(until_local, '%Y-%m-%d') + datetime.timedelta(days=interval)
            else:
                until_local = until_local + datetime.timedelta(days=interval)

    data = pd.DataFrame(data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis',
                                       'Comments', 'Likes', 'Retweets', 'Image link', 'Tweet URL'])

    # save images
    if save_images == True:
        print("Saving images ...")
        save_images_dir = "images"
        if not os.path.exists(save_images_dir):
            os.makedirs(save_images_dir)

        dowload_images(data["Image link"], save_images_dir)

    # close the web driver
    driver.close()

    return data
