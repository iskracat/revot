# -*- coding: utf-8 -*-

from datetime import datetime as dt, timedelta as delta
from revot import db
from revot.models import Voting, Voter, Ballot, Vote
from revot.populate import populate

@populate.route('/resetdb')
def reset_database():
    db.drop_all()
    db.create_all()

    ##########################################################################
    # closed
    basetime = dt.utcnow() - delta(days=2)
    v = Voting('vot0', 'ca', 'sebas',
               basetime,
               basetime+delta(days=1),
               basetime+delta(days=1,hours=3))
    db.session.add(v)
    v.ballot = Ballot([u'David Fernàndez',u'Artur Colau',u'Antonio Baños',u'Teresa Arrimadas'],
                      0, 1,
                      u"Vote for one candidate")
    
    vt = Voter(u'sebas@lsi.upc.edu', u'Sebas Vila') 
    v.voters.append(vt)
    vt.do_vote(1)
    vt = Voter(u'sebastia.vila@upc.edu', u'Sebastia Vila')
    v.voters.append(vt)
    vt.do_vote(3)
    vt = Voter(u'sg.jmsallan@upc.edu', u'J.M. Sallan')
    v.voters.append(vt)
    vt.do_vote(0)
    vt = Voter(u'roser.rius@upc.edu', u'Roser Rius')
    v.voters.append(vt)
    vt.do_vote()

    vt = Voter(u'maria.palau@upc.edu', u'Maria Palau')
    v.voters.append(vt)
    vt.do_vote(1)

    vt = Voter(u'josep.solernou@upc.edu', u'Josep Solernou')
    v.voters.append(vt)

    vt = Voter(u'pere.pala@upc.edu', u'Pere Palà')
    v.voters.append(vt)
    vt.do_vote(1)

    vt = Voter(u'quirze.besora@upc.edu', u'Quirze Besora')
    v.voters.append(vt)
    vt.do_vote(2)

    vt = Voter(u'marta.recasens@upc.edu', u'Marta Recasens')
    v.voters.append(vt)
    vt.do_vote(1)

    vt = Voter(u'joaquim.bellmunt@upc.edu', u'Joaquim Bellmunt')
    v.voters.append(vt)
    vt.do_vote(3)

    vt = Voter(u'francesc.de.carreres@upc.edu', u'Francesc de Carreres')
    v.voters.append(vt)
    vt.do_vote(0)

    vt = Voter(u'manel.cuyas@upc.edu', u'Manel Cuyàs')
    v.voters.append(vt)
    vt.do_vote()

    ##########################################################################
    # open in 4 minutes
    basetime = dt.utcnow()
    v = Voting('vot1', 'ca', 'sebas',
               basetime+delta(minutes=2),
               basetime+delta(minutes=4),
               basetime+delta(minutes=10))
    db.session.add(v)
    v.ballot = Ballot(['Rosses','Morenes'], 0, 1, u"Quines femelles trobes més interessants?.")
    
    vt = Voter(u'sebas.vima@gmail.com', u'Sebas Vila') 
    v.voters.append(vt)
    vt = Voter(u'tv.asimetrik@gmail.com', u'Toni Vila') 
    v.voters.append(vt)

    # ##########################################################################
    # basetime = dt.utcnow()
    # v = Voting('vot2', 'sebas',
    #            basetime,
    #            basetime+delta(days=1),
    #            basetime+delta(days=1,hours=5))
    # db.session.add(v)
    # v.voters.append(Voter(u'sebas@lsi.upc.edu', u'Sebas Vila Lsi'))
    # v.voters.append(Voter(u'sebastia.vila@upc.edu', u'Sebastia Vila'))
    # v.voters.append(Voter(u'sg.jmsallan@upc.edu', u'J.M. Sallan'))
    # v.ballot = Ballot(['yes','no'], 0, 1, u"Vote yes or no")

    # basetime = dt.utcnow() + delta(weeks=1)
    # v = Voting('vot3', 'sebas',
    #            basetime,
    #            basetime+delta(days=1),
    #            basetime+delta(days=1,hours=5))
    # db.session.add(v)
    # v.description = u'''Votació per escollir el nou cap del departament de LSI.'''
    # v.voters.append(Voter(u'pere.pala@upc.edu', u'Pere Pala'))
    # v.voters.append(Voter(u'rosa.argelaguet@upc.edu', u'Rosa Argelaguet'))
    # v.voters.append(Voter(u'josep.oliva@upc.edu', u'Josep Oliva'))
    # v.voters.append(Voter(u'jordi.bonet@upc.edu', u'Jordi Bonet'))
    # v.voters.append(Voter(u'marta.tarres@upc.edu', u'Marta Tarres'))
    # v.voters.append(Voter(u'miquel.casadevall@upc.edu', u'Miquel Casadevall'))
    # v.voters.append(Voter(u'pere.miquel.anton@upc.edu', u'Pere Miquel Anton'))
    # v.ballot = Ballot(['yes','no'], 0, 1, "Vote yes or no")

    return 'Database resetted'

