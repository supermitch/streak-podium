import logging
import os.path
import random
from string import ascii_letters, digits

import requests
from flask import render_template, request, redirect, url_for


from config import config
from app import app, fetch, utils


@app.route('/')
def index():
    N = 20
    state = ''.join(random.SystemRandom().choice(ascii_letters + digits) for _ in range(N))
    # TODO: Set state string in SESSION variable
    return render_template('index.html',
                           client_id=config.GITHUB_CLIENT_ID,
                           auth_url='http://127.0.0.1:5000/auth',
                           scope='read:org',
                           state=state)

@app.route('/auth')
def auth():
    if 'code' in request.args:
        code = request.args['code']
        state = request.args['state']
        print('CODE', code)
        print('STATE', state)  # TODO: Compare state to stored SESSION variable

        response = fetch.post_temporary_code(code, state)

        if response.status_code == requests.codes.ok:

            utils.persist_access_token(response.json())
            return redirect(url_for('success'))
        else:
            return redirect(url_for('failure'))

    else:
        return 'Invalid request'


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/failure')
def failure():
    return render_template('failure.html')


@app.route('/streaks')
def streaks():
    response = fetch.orgs_for_user()
    if response.status_code == requests.codes.ok:
        orgs = utils.parse_orgs(response.json())
        for org in orgs:
            # TODO: Pagination
            response = fetch.members_in_org(org['login'])
            if response.status_code == requests.codes.ok:
                members = utils.parse_org_members(response.json())
                org['count'] = len(members)
                print('Found {} members'.format(org['count']))
                for member in members[-5:]:
                    response = fetch.member_page(member['login'])
                    if response.status_code == requests.codes.ok:
                        print('member account: ')
                        print(response.json())
                        response = fetch.member_contributions(member['login'])
                        if response.status_code == requests.codes.ok:
                            print('member contributions: ')
                            print(response.content)
    else:
        print(response.content)
        orgs = [
            {'login': 'rat', 'count': 1},
            {'login': 'mat', 'count': 2},
            {'login': 'hat', 'count': 3},
            {'login': 'cat', 'count': 5},
        ]

    return render_template('streaks.html',
                           orgs=orgs)

