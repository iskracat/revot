from setuptools import setup, find_packages
import os

name = "revot"
version = "0.1"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=version,
    description="revot software",
    long_description=read('README'),
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords="",
    author="",
    author_email='',
    url='',
    license='',
    package_dir={'': '.'},
    packages=find_packages('.'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Babel==2.1.1',
        'Flask==0.10.1',
        'Flask-Babel==0.9',
        'Flask-Bootstrap==3.3.5.6',
        'Flask-Mail==0.9.1',
        'Flask-Moment==0.5.1',
        'Flask-SQLAlchemy==2.0',
        'Flask-Script==2.0.5',
        'Flask-WTF==0.12',
        'Jinja2==2.8',
        'MarkupSafe==0.23',
        'Pygments==2.0.2',
        'SQLAlchemy==1.0.8',
        'Sphinx==1.3.1',
        'WTForms==2.0.2',
        'Werkzeug==0.10.4',
        'alabaster==0.7.6',
        'amqp==1.4.7',
        'anyjson==0.3.3',
        'argparse==1.2.1',
        'billiard==3.3.0.20',
        'blinker==1.4',
        'celery==3.1.18',
        'docutils==0.12',
        'dominate==2.1.16',
        'flask-nav==0.4',
        'itsdangerous==0.24',
        'kombu==3.0.26',
        'python-dateutil==2.4.2',
        'pytz==2015.6',
        'redis==2.10.3',
        'six==1.9.0',
        'snowballstemmer==1.2.0',
        'speaklater==1.3',
        'sphinx-rtd-theme==0.1.9',
        'visitor==0.1.2',
        'wsgiref==0.1.2',
        'Flask-Login==0.3.2',
        'flask-bcrypt'
    ],
    entry_points="""
    [console_scripts]
    flask-ctl = revot.script:run

    [paste.app_factory]
    main = revot.script:make_app
    debug = revot.script:make_debug
    """,
)
