from operator import itemgetter
from datetime import datetime as dt
from flask import abort
from revot import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import exc
from flask.ext.babel import lazy_gettext
from flask.ext.login import UserMixin


def get_object_or_404(model, *criterion):
    try:
        return model.query.filter(*criterion).one()
    except exc.NoResultFound, exc.MultipleResultsFound:
        abort(404)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, id, password):
        self.id = id
        self.password = password

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Voting(db.Model):
    __tablename__ = 'votings'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    description = db.Column(db.String(200))
    locale = db.Column(db.String(2))
    owner = db.Column(db.String(50), db.ForeignKey('users.id'))
    send_ballot = db.Column(db.DateTime)
    start_voting = db.Column(db.DateTime)
    end_voting = db.Column(db.DateTime)
    voters = db.relationship("Voter",
                             backref='voting',
                             cascade="all, delete, delete-orphan")
    ballot = db.relationship("Ballot",
                             uselist=False,
                             backref='voting',
                             cascade="all, delete, delete-orphan")

    def __init__(self, title, lang, owner, send_ballot, start, end, desc=None):
        self.description = desc
        self.locale = lang
        self.title = title
        self.owner = owner
        self.send_ballot = send_ballot
        self.start_voting = start
        self.end_voting = end

    @hybrid_property
    def state(self):
        """
        Returns the state of the voting in this instant.

        Returns:
           int: The state of the voting according to this code:

              0. Called to vote
              1. Sending ballots
              2. Open to vote
              3. Closed
        """
        now = dt.utcnow()
        if now < self.send_ballot:
            return 0
        elif self.send_ballot <= now < self.start_voting:
            return 1
        elif self.start_voting <= now < self.end_voting:
            return 2
        else:
            return 3

    @hybrid_property
    def roll_length(self):
        """
        The number of enrolled voters in this voting
        """
        return db.session.query(Voter).\
            join(Voting).\
            filter(Voting.id == self.id).\
            count()

    def results(self):
        """
        Returns the (partial) results of the voting
        """
        res_num = db.session.query(
            Vote.vote,
            db.func.count(Vote.vote)).\
            join(Voter).join(Voting).\
            filter(Voting.id == self.id).\
            group_by(Vote.vote).\
            all()
        options = self.ballot.full_options
        votes = sum(votes for option, votes in res_num)
        enrolled = self.roll_length
        return dict(
            enrolled=enrolled,
            votes=votes,
            abstentions=(enrolled - votes),
            result=sorted([(options[i], votesa) for i, votesa in res_num],
                          key=itemgetter(1), reverse=True)
        )

    def __repr__(self):
        return '<Votation %r>' % (self.title)


class Voter(db.Model):
    """
    A voter is a registered person in an actual voting
    """
    __tablename__ = 'voters'

    id = db.Column(db.Integer, primary_key=True)
    voting_id = db.Column(db.Integer, db.ForeignKey('votings.id'))

    identity = db.Column(db.String(250))
    name = db.Column(db.String(70))
    ballot_sent = db.Column(db.DateTime)
    ballot_received = db.Column(db.DateTime)
    vote = db.relationship("Vote",
                           backref='voter',
                           cascade="all, delete, delete-orphan")

    def __init__(self, identity, name=None):
        self.name = name
        self.identity = identity
        self.ballot_sent = None
        self.ballot_received = None

    @hybrid_property
    def voted(self):
        return bool(self.ballot_received)

    @hybrid_property
    def voted_options(self):
        r = db.session.query(Vote.vote).\
            join(Voter).\
            filter(Voter.id == self.id).all()
        options = self.voting.ballot.full_options
        return [options[v[0]] for v in r]

    def do_vote(self, *args):
        # falta checks i saltar excepcions.
        self.ballot_received = dt.utcnow()
        if len(args) == 0:
            self.vote.append(Vote(-1))
        else:
            for e in args:
                self.vote.append(Vote(e))

    def __repr__(self):
        return '<Voter %r(%r)>' % (self.name, self.identity)


class Ballot(db.Model):
    """
    Defines a ballot in an actual voting.
    A ballot is a sequence of M options from which 0<=N<=M can be choosed.
    """
    __tablename__ = 'ballots'

    id = db.Column(db.Integer, primary_key=True)
    voting_id = db.Column(db.Integer, db.ForeignKey('votings.id'))

    description = db.Column(db.Text)
    options = db.Column(db.PickleType)  # A list of strings. Numbered from 0
    M = db.Column(db.Integer)
    Nmin = db.Column(db.Integer)
    Nmax = db.Column(db.Integer)

    def __init__(self, options, Nmin=0, Nmax=None, descr=None):
        self.description = descr
        self.options = options
        self.M = len(options)
        self.Nmin = Nmin if (0 <= Nmin <= self.M) else 0
        self.Nmax = Nmax if (Nmax and 0 <= Nmax <= self.M) else self.M

    @hybrid_property
    def full_options(self):
        # to recognize blank votes
        return self.options + [lazy_gettext(u'Blank vote')]

    def __repr__(self):
        return '<Ballot %r (%i of %i)>' % (self.options, self.M, self.Nmax)


class Vote(db.Model):
    """
    Defines a vote. This results from a voter submiting a ballot. When
    several options can be simultaneously choosed in a ballot, the same
    number of votes are registered. A vote of -1 value means a blank vote.
    """
    __tablename__ = 'votes'

    voter_id = db.Column(
        db.Integer,
        db.ForeignKey('voters.id'),
        primary_key=True)
    vote = db.Column(db.SmallInteger, primary_key=True, nullable=True)

    def __init__(self, vote=-1):
        self.vote = vote

    @hybrid_property
    def full_vote(self, voter_id):
        r = db.session.query(Vote.vote).\
            join(Voter).\
            filter(voter.id == self.voter_id).all()
        return r

    def __repr__(self):
        return '<Vote %i %i>' % (self.voter_id, self.vote)
