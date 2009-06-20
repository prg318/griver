#!/usr/bin/env python
from distutils.core import setup

setup(name="griver",
		version="0.2.1",
		scripts = ['griver'],
		data_files=[('share/griver/', ['griver.glade']),
                ('share/pixmaps/', ['griver.svg']),
      			    ('share/applications/', ['griver.desktop'])],
		author = "Lukas Sabota",
		author_email = "punkrockguy318@comcast.net",
		url = "http://dietschnitzel.com/griver"
		)

