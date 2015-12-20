from flask_nav.elements import *
from revot import nav
from flask.ext.babel import lazy_gettext


nav.register_element('top', Navbar(
    View('ReVot', 'main.welcome_users'),
    View(lazy_gettext('Current votings'), 'main.show_all_votings'),
    View(lazy_gettext('Define a voting'), 'main.add_voting'),
))
