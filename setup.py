import os
from distutils.core import setup

setup(
    name = "django-divan",
    version = "0.1.0",
    url = 'http://github.com/marinho/django-divan',
    license = 'BSD',
    description = "Build user controllable schemas with SQL and CouchDB or MongoDB.",
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
