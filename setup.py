import os
from distutils.core import setup

setup(
    name = "django_divan",
    version = "0.1.0",
    url = 'http://github.com/olifantworkshop/django_divan',
    license = 'BSD',
    description = "Build user controllable schemas with SQL and CouchDB.",
    author = 'Jonathan Lukens',
    author_email = 'jonathan@threadsafelabs.com',
    packages = ['divan'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
