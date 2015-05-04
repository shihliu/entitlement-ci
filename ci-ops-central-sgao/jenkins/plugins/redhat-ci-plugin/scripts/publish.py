#!/usr/bin/python

import argparse
import stomp

types = [
    'pull-request',
    'code-quality-checks-done',
    'security-checks-done',
    'peer-review-done',
    'component-build-done',
    'tier-0-testing-done',
    'unit-test-coverage-done',
    'tier-1-testing-done',
    'update-defect-status',
    'test-coverage-done',
    'tier-2-integration-testing-done',
    'product-build-done',
    'tier-2-validation-testing-done',
    'product-test-coverage-done',
    'early-performance-testing-done',
    'early-security-testing-done',
    'functional-testing-done',
    'tier-3-testing-done',
    'nonfunctional-testing-done',
    'product-accepted-for-release-testing',
    'product-build-in-staging',
    'ootb-testing-done',
    'image-uploaded'
]


def parse_args():
    "Parse command line arguments."
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Publish a message to the Red Hat CI message bus.'
    )
    parser.add_argument(
        '--user',
        dest='user',
        metavar='<user>',
        required=True,
        help='Username to use to connect to the message bus.'
    )
    parser.add_argument(
        '--password',
        dest='password',
        metavar='<password>',
        required=True,
        help='Password to use to connect to the message bus.'
    )
    parser.add_argument(
        '--type',
        dest='type',
        metavar='<message>',
        required=True,
        choices=types,
        help='Message type to publish.'
    )
    parser.add_argument(
        '--header',
        dest='headers',
        metavar='<headers>',
        action='append',
        help='Header key:value pair to include in message.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--body',
        dest='body',
        metavar='<body>',
        help='Body of message.'
    )
    group.add_argument(
        '--body-file',
        dest='bodyfile',
        metavar='<body-file>',
        help='File to use as body of message.'
    )
    parser.add_argument(
        '--host',
        dest='host',
        metavar='<host>',
        default='ci-bus.lab.eng.rdu2.redhat.com',
        help='Message bus host.'
    )
    parser.add_argument(
        '--port',
        dest='port',
        metavar='<port>',
        type=int,
        default=61613,
        help='Message bus port.'
    )
    parser.add_argument(
        '--destination',
        dest='destination',
        metavar='<destination>',
        default='/topic/CI',
        help='Message bus topic/subscription.'
    )
    return parser.parse_args()


def main():
    "Publish a message on the CI bus."
    args = parse_args()
    headers = {}
    headers["CI_TYPE"] = args.type
    if args.headers:
        for header in args.headers:
            h = header.split(":")
            key = h[0]
            value = h[1]
            headers[key] = value

    body = ""
    if args.body:
        body = args.body
    if args.bodyfile:
        with open(args.bodyfile, "r") as f:
            body = f.read()

    conn = stomp.Connection([(args.host, args.port)])
    conn.start()
    conn.connect(login=args.user, passcode=args.password)
    if stomp.__version__[0] < 4:
        conn.send(message=body, headers=headers, destination=args.destination)
    else:
        conn.send(body=body, headers=headers, destination=args.destination)
    conn.disconnect()
    print 'Message sent.'

if __name__ == '__main__':
    main()
