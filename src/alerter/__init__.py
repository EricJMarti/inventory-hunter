import alerter.discord
import alerter.emailer
import alerter.pushover
import alerter.slack
import alerter.telegram

from alerter.common import AlerterFactory


def init_alerters(args):
    return AlerterFactory.create(args)
