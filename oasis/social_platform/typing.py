# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
from enum import Enum


class ActionType(Enum):
    EXIT = "exit"
    REFRESH = "refresh"
    SEARCH_USER = "search_user"
    SEARCH_POSTS = "search_posts"
    CREATE_POST = "create_post"
    LIKE_POST = "like_post"
    UNLIKE_POST = "unlike_post"
    DISLIKE_POST = "dislike_post"
    UNDO_DISLIKE_POST = "undo_dislike_post"
    REPORT_POST = "report_post"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"
    MUTE = "mute"
    UNMUTE = "unmute"
    TREND = "trend"
    SIGNUP = "sign_up"
    REPOST = "repost"
    QUOTE_POST = "quote_post"
    UPDATE_REC_TABLE = "update_rec_table"
    CREATE_COMMENT = "create_comment"
    LIKE_COMMENT = "like_comment"
    UNLIKE_COMMENT = "unlike_comment"
    DISLIKE_COMMENT = "dislike_comment"
    UNDO_DISLIKE_COMMENT = "undo_dislike_comment"
    DO_NOTHING = "do_nothing"
    PURCHASE_PRODUCT = "purchase_product"
    INTERVIEW = "interview"
    JOIN_GROUP = "join_group"
    LEAVE_GROUP = "leave_group"
    SEND_TO_GROUP = "send_to_group"
    CREATE_GROUP = "create_group"
    LISTEN_FROM_GROUP = "listen_from_group"
    START_BROWSER = "start_browser"
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE_TEXT = "type_text"
    EXTRACT_DOM = "extract_dom"
    CLOSE_BROWSER = "close_browser"
    FETCH_RSS_FEED = "fetch_rss_feed"

    @classmethod
    def get_default_twitter_actions(cls):
        return [
            cls.START_BROWSER,
            cls.NAVIGATE,
            cls.CLICK,
            cls.TYPE_TEXT,
            cls.EXTRACT_DOM,
            cls.CLOSE_BROWSER,
            cls.FETCH_RSS_FEED,
        ]

    @classmethod
    def get_default_reddit_actions(cls):
        return [
            cls.START_BROWSER,
            cls.NAVIGATE,
            cls.CLICK,
            cls.TYPE_TEXT,
            cls.EXTRACT_DOM,
            cls.CLOSE_BROWSER,
            cls.FETCH_RSS_FEED,
        ]


class RecsysType(Enum):
    TWITTER = "twitter"
    TWHIN = "twhin-bert"
    REDDIT = "reddit"
    RANDOM = "random"


class DefaultPlatformType(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
