from datetime import datetime as  dt
from datetime import timedelta as delta
from flask import render_template, g, url_for, abort, request, flash, redirect, current_app
from revot.models import get_object_or_404, Voting, Voter, Ballot
from revot.main import main
from revot.babel import get_locale
from revot import db
from forms import BallotForm, VotingForm
from tasks import activate_balloting
from flask.ext.babel import gettext
from flask.ext.login import login_required


@main.before_request
def before_request():
    g.locale = get_locale()

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        if not next_is_valid(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@main.route('/')
def welcome_users():
    vote_page = url_for('main.show_all_votings')
    return render_template('welcome.html', vote_page=vote_page)

@main.route('/voting')
@login_required
def show_all_votings():
    # fetch current votations
    v = [ (v, url_for('main.show_voting', ident=v.id))
          for v in Voting.query.order_by(Voting.start_voting.desc()).all() ]
    return render_template('current-votings.html', votings=v)


@main.route('/voting/<int:ident>')
@login_required
def show_voting(ident):
    # FALTA considerar l'owner
    voting = get_object_or_404(Voting, Voting.id == ident)
    # Voting view depends on state
    if voting.state == 0:
        # Called to vote
        return render_template('voting-called.html', voting=voting, voters=voting.voters)
    if voting.state == 1:
        # Sending ballots
        return render_template('voting-open.html', voting=voting)
    if voting.state == 2:
        # Open to vote
        return render_template('voting-open.html', voting=voting)
    if voting.state == 3:
        # Closed
        return render_template('voting-result.html',
                               voting=voting,
                               ballot=voting.ballot,
                               voters=voting.voters,
                               result=voting.results())
    else:
        abort(500)


@main.route('/voting/<int:ident>/ballot')
def show_ballot(ident):
    # CAL VEURE QUAN TE SENTIT
    voting = get_object_or_404(Voting, Voting.id == ident)
    if voting.ballot:
        return render_template('show-ballot.html', entry=voting, b=voting.ballot)
    else:
        abort(501)


@main.route('/voting/<int:ident>/<person>', methods=['GET', 'POST'])
@login_required
def do_vote(ident, person):
    # assert voting is open to vote  else redirect to voting page
    voting = get_object_or_404(Voting, Voting.id == ident)
    # Maybe it is better to return a 404. Otherise scanners can
    # detect correct ballot url's before voting opens.
    if voting.state < 2:
        flash(gettext('Voting is not open yet. You cannot vote until it opens.'))
        return redirect(url_for('main.show_voting', ident=ident))
    elif voting.state > 2:
        flash(gettext('Voting is closed. No more votes allowed.'))
        return redirect(url_for('main.show_voting', ident=ident))
    # check voter and ballot exists, check for duplicate votes
    voter  = get_object_or_404(Voter,
                               Voter.voting_id==ident,
                               Voter.identity==person)
    if not voter.voting.ballot:
        abort(501)
    elif voter.voted:
        abort(410) # attempt to duplicate votes

    # create the ballot form
    form = BallotForm(min=voter.voting.ballot.Nmin,max=voter.voting.ballot.Nmax)
    form.options.choices = list(enumerate(voter.voting.ballot.options))
    # on POST
    if form.validate_on_submit():
        voter.ballot_received = dt.utcnow()
        voter.do_vote(*form.options.data)
        flash(gettext('Thank you for voting'))
        return redirect(url_for('main.show_voting', ident=ident))
    # send TEMPLATE
    return render_template('cast-ballot.html',
                           form=form,
                           voting=voter.voting,
                           ballot=voter.voting.ballot)


@main.route('/voting/add', methods=['GET', 'POST'])
@login_required
def add_voting():
    form = VotingForm()
    # setup late choices
    form.duration.choices=[
        (5,       gettext(u'5 minutes')),
        (30,      gettext(u'half an hour')),
        (60,      gettext(u'1 hour')),
        (60*3,    gettext(u'3 hours')),
        (60*6,    gettext(u'6 hours')),
        (60*12,   gettext(u'12 hours')),
        (60*24,   gettext(u'1 day')),
        (60*24*2, gettext(u'2 days')),
        (60*24*3, gettext(u'3 days'))]
    form.send_ballots.choices=[
        (-1,      gettext(u'now')),
        (60*6,    gettext(u'6 hours before')),
        (60*12,   gettext(u'12 hours before')),
        (60*24,   gettext(u'1 day before')),
        (60*24*2, gettext(u'2 days before')),
        (60*24*3, gettext(u'3 days before')),
        (60*24*4, gettext(u'4 days before'))]
    form.language.choices=current_app.config['LANGUAGES'].items()
    # on POST, create the voting
    if form.validate_on_submit():
        # Process relative times
        if form.send_ballots.data < 0:
            balloting_starts = dt.utcnow() + delta(minutes=1)
        else:
            balloting_starts = form.starts.data - delta(minutes=form.send_ballots.data)
        votation_ends    = form.starts.data + delta(minutes=form.duration.data)
        # Create a complete votation
        v = Voting(form.title.data,
                   form.language.data,
                   'sebas',
                   balloting_starts,
                   form.starts.data,
                   votation_ends,
                   form.descr.data)
        db.session.add(v)
        # Enroll voters
        for line in form.roll.data.splitlines():
            email, name = line.split(',')
            voter = Voter(email.strip(), name.strip())
            v.voters.append(voter)
        # Create the ballot
        v.ballot = Ballot(form.options.data,
                          0 if form.blanks_allowed.data else 1,
                          form.max_options.data,
                          form.question.data)
        db.session.flush() # to get the id
        # Activate the task to send ballots
        activate_balloting(v.id, balloting_starts)
        # Commit
        db.session.commit()
        # Redirect to the voting
        return redirect(url_for('main.show_voting', ident=v.id))

    # send TEMPLATE
    return render_template('edit-voting.html', form=form)
