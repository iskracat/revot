# -*- coding: utf-8 -*-

from datetime import timedelta as delta, datetime
from os import urandom, path
from base64 import urlsafe_b64encode as b64enc

from revot import db, celery, mail
from revot.models import Voting, Voter

from flask import render_template, url_for, current_app, request
from flask_mail import Message
from flask.ext.babel import gettext

from babel import Locale
from babel.support import Translations
from babel.dates import get_timezone, format_datetime


# Timezone used to send datetimes in mail message. Unfortunately
# we cannot guess timezone of mail reader.
TIMEZONE = get_timezone('Europe/Madrid')
DTFORMAT = "EEEE d MMMM y H:mm"

# Length of random voter id. It must be a multiple of 3.
# The corresponding URL will measure RANDOM_ID_LENGTH*4/3
# This issue must be considered: https://en.wikipedia.org/wiki/Birthday_problem
RANDOM_ID_LENGTH = 12


def activate_balloting(voting_id, when):
    return start_balloting_task.apply_async(
        (voting_id,),
        eta=when+delta(seconds=10))


@celery.task
def start_balloting_task(voting_id):
    voting = db.session.query(Voting).get(voting_id)
    # Force locales
    tzinfo = TIMEZONE
    locale = Locale.parse(voting.locale)
    # get datetime well formatted
    vstarts = format_datetime(voting.start_voting, DTFORMAT, tzinfo, locale)
    vends = format_datetime(voting.end_voting, DTFORMAT, tzinfo, locale)
    # Fetch common data for all voters
    vtitle = voting.title
    bnmax = voting.ballot.Nmax
    bnmin = voting.ballot.Nmin
    bdesc = voting.ballot.description
    boptions = voting.ballot.options
    lang = voting.locale
    for voter in voting.voters:
        args = [
            voter.id,
            vtitle,
            vstarts,
            vends,
            bnmax,
            bnmin,
            bdesc,
            boptions,
            lang]
        send_mail_to_a_voter.apply_async(args, countdown=10)


@celery.task
def send_mail_to_a_voter(
        voter_id,
        vtitle,
        vstarts,
        vends,
        bnmax,
        bnmin,
        bdesc,
        boptions,
        lang):
    # Get data needed to send ballot
    voter = db.session.query(Voter).get(voter_id)
    voting = voter.voting
    msg = Message()
    msg.add_recipient(voter.identity)
    data = {
        'name':     voter.name,
        'title':    vtitle,
        'maxopt':   bnmax,
        'blank':    bnmin == 0,
        'question': bdesc,
        'options':  boptions,
        'starts':   vstarts,
        'ends':     vends,
    }

    # Replace email identity by random identity.
    # Remove any traces of old identity.
    # get a random id and check it is unique
    randid = b64enc(urandom(RANDOM_ID_LENGTH))
    while db.session.query(Voter).filter(
            Voter.identity == randid,
            Voting.id == voting.id).count():
        randid = b64enc(urandom(RANDOM_ID_LENGTH))

    # remove user real identity, replace by random one
    voter.identity = randid
    voter.name = None
    # timestamp as ballot sent
    voter.ballot_sent = datetime.utcnow()
    # commit the changes
    db.session.commit()

    data['url'] = url_for(
        'main.do_vote',
        ident=voting.id,
        person=voter.identity,
        _external=True)

    with current_app.test_request_context():
        # Force locales in this pseudo-request to allow for translations
        request.babel_translations = Translations().load(
            path.join(current_app.root_path, 'translations'), [lang])
        # compose ballot mail and send it
        msg.subject = gettext("Ballot for voting %(title)s", title=vtitle)
        msg.body = render_template('ballot_message.txt', d=data)

    mail.send(msg)
