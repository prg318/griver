#!/usr/bin/env python2
from distutils.core import setup

setup(name="griver",
		version="0.2.2",
		scripts = ['griver.py'],
		data_files=[('share/griver/', ['griver.ui']),
			('share/pixmaps/', ['griver.svg']),
			('share/applications/', ['griver.desktop'])],
		author = "Lukas Sabota",
		author_email = "ltsmooth42 _at_ gmail _dot_ com",
		url = "http://code.google.com/p/griver/")

