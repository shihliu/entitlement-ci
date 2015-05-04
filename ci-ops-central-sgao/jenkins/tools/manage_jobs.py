#!/usr/bin/env python

from contextlib import closing
from threading import current_thread
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from jenkins_cli import JenkinsCLI
import urllib
import json
import re
import shlex
import logging


DEFAULT_JENKINS_URL = 'http://localhost:8080'
DEFAULT_HELP_MSG = "default %(default)s"

FMT = "%(levelname)s:%(name)s:%(threadName)s: %(message)s"


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('--jenkins', action='store',
                        default=DEFAULT_JENKINS_URL,
                        help="Jenkins url, default=%(default)s")
    parser.add_argument('-v', '--view', action='append', help="view name",
                        required=True)
    parser.add_argument('-u', '--user', action='store', help=DEFAULT_HELP_MSG)
    parser.add_argument('-p', '--passwd', action='store',
                        help=DEFAULT_HELP_MSG)
    parser.add_argument('-r', '--regex', action='store', type=re.compile)
    parser.add_argument('-d', '--debug', action='store_const',
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('--dry', action='store_true', default=False)
    parser.add_argument('-w', '--workers', action='store', type=int,
                        default=1, help=DEFAULT_HELP_MSG)
    parser.add_argument('cmd', nargs=1, help='jenkins-cli command, '
                        'you can use {job} as job name')
    return parser


class ViewResolver(object):
    JSON_SUFF = '/api/json'
    VIEW_PATH = '/view/'

    def __init__(self, url):
        super(ViewResolver, self).__init__()
        self.url = url

    def __call__(self, view):
        return self._fetch_jobs(view)

    def _fetch_jobs(self, view):
        view = [self.url] + view.split('/')
        url = self.VIEW_PATH.join(view) + self.JSON_SUFF
        with closing(urllib.urlopen(url)) as fh:
            try:
                dict_from_json = json.load(fh)
            except ValueError:
                raise ValueError("Bad view name: %s" % url)
        return set([str(x['name']) for x in dict_from_json['jobs']])


class Wrapper(object):
    def __init__(self, cli):
        super(Wrapper, self).__init__()
        self.cli = cli

    def __call__(self, job, cmd):
        th = current_thread()
        th.setName(job)  # in order to display job_name in log message

        if ' ' in cmd:
            cmd = shlex.split(cmd.format(job=job))
        else:
            cmd = [cmd, job]

        if self.cli is None:  # dry run
            logging.info("Would be executed: %s", cmd)
        else:
            self.cli.exec_cmd(cmd)


def main():
    parser = create_parser()
    opt = parser.parse_args()

    logging.basicConfig(level=opt.debug, format=FMT)

    resolver = ViewResolver(opt.jenkins)

    jobs = set()

    for view in opt.view:
        jobs |= resolver(view)

    if opt.regex:  # filter jobs according to regex
        for job in jobs.copy():
            if not opt.regex.match(job):
                jobs.remove(job)

    if opt.dry:
        wrapper = Wrapper(None)
    else:
        cli = JenkinsCLI(opt.jenkins)
        if opt.user and opt.passwd:
            cli.login(opt.user, opt.passwd)
        wrapper = Wrapper(cli)

    with ThreadPoolExecutor(opt.workers) as pool:
        for job in jobs:
            pool.submit(wrapper, job, opt.cmd[0])


if __name__ == "__main__":
    main()