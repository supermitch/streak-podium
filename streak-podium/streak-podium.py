import argparse

import parse
import read


def setup_args():
    """
    Add and return command line arguments.
    """
    parser = argparse.ArgumentParser('Streak Podium')
    parser.add_argument('-f', '--file', help='member list input filename')
    parser.add_argument('-o', '--org', help='organization to sort')
    parser.add_argument('-l', '--limit', type=int, default=5, help='limit number of users')
    parser.add_argument('-b', '--best', action='store_true', help='sort by best (default by latest)')
    return parser.parse_args()


def gather_usernames(args):
    """
    Return username list from chosen input source.
    """
    if args.file:
        return read.input_file(args.file)
    elif args.org:
        return read.org_members(args.org)
    else:
        return ['supermitch']  # Some default for now


def main():
    args = setup_args()

    print('Running Streak Podium')
    print('---------------------')

    kind = 'file' if args.file else 'Github org'
    name = args.file if args.file else args.org
    print('Input is {} [{}]'.format(kind, name))
    print('\tlimiting query to {} users'.format(args.limit))

    print('Gathering usernames...')
    usernames = gather_usernames(args)
    print('\tfound {} usernames'.format(len(usernames)))

    print('Reading streaks...')
    svgs = (read.svg_data(username) for username in usernames[:args.limit])

    commits = (parse.extract_commits(svg) for svg in svgs)
    streaks = {user: parse.find_streaks(x) for user, x in zip(usernames, commits)}

    print('\tfound {} streaks'.format(len(streaks)))
    if args.best:
        sort_attrib = 'best'
    else:
        sort_attrib = 'latest'

    sorted_streaks = sorted(streaks.items(), key=lambda t: getattr(t[1], sort_attrib), reverse=True)

    print('\nTop {} streaks:'.format(sort_attrib))
    print('============')
    for user, streak in sorted_streaks:
        print('{} - best: {} - latest: {}'.format(user, streak.best, streak.latest))


if __name__ == '__main__':
    main()

