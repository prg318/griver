#!/usr/bin/env python
from distutils.core import setup

setup(name="griver",
		version="0.2.2",
		scripts = ['griver'],
		data_files=[('share/griver/', ['griver.glade']),
                ('share/pixmaps/', ['griver.svg']),
      			    ('share/applications/', ['griver.desktop'])],
		author = "Lukas Sabota",
		author_email = "ltsmooth42 _at_ gmail _dot_ com",
		url = "http://code.google.com/p/griver/"
		)

