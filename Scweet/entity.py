import csv
import datetime
import os
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Tweet:
    id: str = field()
    username: str = field()
    handle: str = field()
    postdate: str = field()
    text: str = field()
    embedded: str = field()
    emojis: str = field()
    reply_cnt: int = field()
    retweet_cnt: int = field()
    like_cnt: int = field()
    tweet_url: str = field()
    image_links: List[str] = field(default=None)


@dataclass
class Query:
    since: Optional[str] = field(default=None)
    until: Optional[str] = field(default=None)
    words: Optional[List[str]] = field(default=None)
    hashtag: Optional[str] = field(default=None)
    to_account: Optional[str] = field(default=None)
    from_account: Optional[str] = field(default=None)
    mention_account: Optional[str] = field(default=None)
    replies_only: Optional[bool] = field(default=False)
    interval: int = field(default=datetime.timedelta(days=1))
    lang: Optional[str] = field(default=None)
    limit: Optional[float] = field(default=float("inf"))
    display_type: Optional[str] = field(default="Top")
    proximity: Optional[bool] = field(default=False)
    geocode: Optional[str] = field(default=None)
    min_replies: Optional[str] = field(default=None)
    min_likes: Optional[str] = field(default=None)
    min_retweets: Optional[str] = field(default=None)


class LazyImport:
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None

    def __getattr__(self, name):
        if self.module is None:
            self.module = __import__(self.module_name)
        return getattr(self.module, name)


class DurabilityHandler:
    @abstractmethod
    def write(self, item):
        pass

    @abstractmethod
    def get_last_date(self):
        pass


class CSVDurabilityHandler(DurabilityHandler):
    def __init__(self, file_name, save_path="./data", override=False):
        self.pd = LazyImport("pandas")
        print("pandas version:%s" % self.pd.__version__)
        if not save_path.endswith("/"):
            save_path += "/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if not override:
            self.write_mode = 'a'
        else:
            self.write_mode = 'w'
        header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis', 'Comments', 'Likes',
                  'Retweets', 'Image link', 'Tweet URL']
        self.full_path = save_path + file_name
        self.file = open(self.full_path, self.write_mode, newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        if self.write_mode == 'w':
            self.writer.writerow(header)

    def get_last_date(self):
        df = self.pd.read_csv(self.full_path)
        return datetime.datetime.strftime(max(self.pd.to_datetime(df["Timestamp"])), '%Y-%m-%d %H:%M:%S')

    def write(self, item):
        self.writer.writerow(
            (item.username, item.handle, item.postdate, item.text, item.embedded, item.emojis, item.reply_cnt,
             item.retweet_cnt, item.like_cnt, "".join(item.image_links), item.tweet_url))
        self.file.flush()

    def __del__(self):
        self.file.close()


class MySQLDurabilityHandler(DurabilityHandler):
    def __init__(self, host: str, user: str, password: str, database: str, table: str):
        self.table = table
        pymysql = LazyImport("pymysql")
        print("pymysql version:%s" % pymysql.__version__)
        self.db = pymysql.connect(host=host, user=user, password=password, database=database,
                                  init_command="SET SESSION time_zone='+00:00'")
        self.db.autocommit(True)
        self.cursor = self.db.cursor()

    def get_last_date(self):
        self.cursor.execute("SELECT max(postdate) FROM {}".format(self.table))
        return str(self.cursor.fetchone()[0])

    def write(self, item: Tweet):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(item.postdate, '%Y-%m-%dT%H:%M:%S.000Z'))
        self.cursor.execute("INSERT INTO {} values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(self.table), (
            item.id, item.username, item.handle, timestamp, item.text, item.embedded, item.emojis, item.reply_cnt,
            item.retweet_cnt, item.like_cnt, item.tweet_url, " ".join(item.image_links)))

    def __del__(self):
        self.cursor.close()
        self.db.close()


class Filter:
    @abstractmethod
    def run(self, tweet: Tweet) -> Tweet:
        pass
