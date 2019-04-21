import datetime  # noqa
import os
import time  # noqa

from slackclient import SlackClient

TAG_TO_CHANNEL = {'python': 'python',
                  'scikit-learn': 'scikit-learn'}


class Updater:
    """Main class doing all the work.

    Parameters
    ----------
    tag : str
        Tag to monitor.

    update_frequency_mins : int
        Number of minutes between two queries.

    illegal_tags : None or list
        If a list, then questions that contain at least one of these illegal tags are not considered.


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

    """

    def __init__(self, tag='python', update_frequency_mins=5, illegal_tags=None):
        # define attributes
        self.tag = tag
        self.update_frequency_mins = update_frequency_mins
        self.illegal_tags = illegal_tags or []

        self.channel = TAG_TO_CHANNEL.get(tag, 'random')

        self.so_key = os.environ.get('SO_KEY')  # optional, possible to have more calls
        self.slack_key = os.environ['SLACK_KEY']  # mandatory

        self.slack_client = SlackClient(token=self.slack_key)

        self.last_update = None

    def run(self):
        """Main method that runs an infinite loop."""
        pass

    def _get_so(self):
        """Get the latest stack overflow questions."""
        pass

    def _send_slack(self, items):
        """ Send a message to slack.

        Parameters
        ----------
        items : list
            A list of question dictionaries.

        """
        pass
