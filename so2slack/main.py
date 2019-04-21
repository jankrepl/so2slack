from argparse import ArgumentParser
from collections import deque
import datetime  # noqa
import os
import time  # noqa

import requests

from slackclient import SlackClient

TAG_TO_CHANNEL = {'deep-learning': 'deeplearning',
                  'keras': 'keras',
                  'pandas': 'pandas',
                  'python': 'python',
                  'scikit-learn': 'scikit-learn'}


class Updater:
    """Main class doing all the work.

    Parameters
    ----------
    tag : str
        Tag to monitor.

    freq : int
        Number of minutes between two queries.

    illegal_tags : None or list
        If a list, then questions that contain at least one of these illegal tags are not considered.

    bot_name : str
        Name of the slack bot.


    Attributes
    ----------
    channel : str
        Name of the slack channel message will be sent to.

    so_key : None or str
        A stack overflow api key, optional. Read from an environment variable 'SO_KEY'.

    slack_key : str
        A slack token, mandatory. Read from an environment variable 'SLACK_KEY'.

    slack_client : SlackClient
        A slack bot for sending messages.

    last_update : None or int
        If int then represents UNIX timestamp of the last time the stack overflow was checked. If None,
        we have not run the script yet.

    memory : deque
        Keeps ids of the most recent questions in order to prevent accidental duplicates.

    """

    def __init__(self, tag='python', freq=5, illegal_tags=None, bot_name='lazy_lizard'):
        # Define attributes
        self.tag = tag
        self.freq = freq
        self.illegal_tags = illegal_tags or []
        self.bot_name = bot_name

        self.channel = TAG_TO_CHANNEL.get(tag, 'random')

        self.so_key = os.environ.get('SO_KEY')  # optional, possible to have more calls
        self.slack_key = os.environ['SLACK_KEY']  # mandatory

        self.slack_client = SlackClient(token=self.slack_key)

        self.last_update = int(time.mktime(datetime.datetime.now().timetuple()))

        self.memory = deque(maxlen=20)

    def run(self):
        """Main method that runs an infinite loop."""

        while True:
            last_update_dt = datetime.datetime.utcfromtimestamp(self.last_update)

            # stack overflow
            so_items = self._get_so()

            if so_items:
                print('At time {} there were {} new items'.format(last_update_dt, len(so_items)))
                self._send_slack(so_items)

            else:
                print('At time {} there were no new items.'.format(last_update_dt))

            time.sleep(int(self.freq * 60))

    def _get_so(self):
        """Get the latest stack overflow questions."""

        seconds_tol = 100  # sometimes slack times are off

        url = 'http://api.stackexchange.com/2.2/questions/unanswered'

        params = {'key': self.so_key,
                  'site': 'stackoverflow',
                  'sort': 'creation',
                  'pagesize': 10,
                  'tagged': self.tag}

        res = requests.get(url, params=params)

        try:
            _temp = res.json()
            items = _temp['items']
            quota_remaining = _temp['quota_remaining']

            print('API calls left: {}'.format(quota_remaining))

            filtered_items = [it for it in items if (it['creation_date'] >= self.last_update - seconds_tol) and
                              not (set(it['tags']) & set(self.illegal_tags)) and
                              it['question_id'] not in self.memory]

            self.memory.extend([it['question_id'] for it in filtered_items])

            return filtered_items

        except KeyError as e:
            print('Something went wrong with the request...')
            print(e)

            return []

        finally:
            self.last_update = int(time.mktime(datetime.datetime.now().timetuple()))

    def _send_slack(self, items):
        """ Send a message to slack.

        Parameters
        ----------
        items : list
            A list of question dictionaries.

        """

        for it in items:
            title = it['title']
            link = it['link']

            message = '{}\n{}'.format(title, link)

            self.slack_client.api_call('chat.postMessage',
                                       channel=self.channel,
                                       text=message,
                                       username=self.bot_name,
                                       icon_emoji=':robot_face:')


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("--tag", default='python', type=str)
    parser.add_argument("--freq", default=1, type=float)

    args = parser.parse_args()

    updater = Updater(**vars(args))

    updater.run()
