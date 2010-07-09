#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name = 'Default CC',
    version = '0.1',

    packages = ['defaultcc'],
    include_package_data = True,

    install_requires = ['trac>=0.11'],

    author = "Jean-Guilhem Rouel",
    author_email = "jean-guilhem.rouel@ercim.org",
    description = "Automatically adds a default CC list to new tickets.",
    long_description = "Automatically adds a default CC list when a new " \
        "ticket is created, based on its initial field. " \
        "CC lists can be configured per field through the ticket system admin UI",
    license = "GPLv2",
    keywords = "trac 0.11 CC ticket component",
    url = "http://trac-hacks.org/wiki/DefaultCCPlugin",
    maintainer = "Ben Miller",
    maintainer_email = "ben@isotoma.com",

    entry_points = {
        'trac.plugins': [
            'defaultcc.admin = defaultcc.admin',
            'defaultcc.main = defaultcc.main'
        ],
    },

    zip_safe = True
)
