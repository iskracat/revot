#!/usr/bin/env python
import os
from revot import create_app, db
from revot.models import Voting, Voter, Ballot
from flask.ext.script import Manager, Shell, Server

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, Voting=Voting, Voter=Voter, Ballot=Ballot)

manager.add_command('shell', Shell(make_context = make_shell_context))
manager.add_command("runserver", Server())

if __name__ == '__main__':
    manager.run()
