#!/usr/bin/env python2
# Griver
version = "0.2.4"
# By Lukas Sabota
# 9/13/2006
# Licensed under the GPL version 3

import gtk
import gtk.glade
import os
import shutil
import sys
import pickle
import ctypes
import ctypes.util
 
def save_state():
	if widgets['h100_radio'].get_active():
		device_type = 0
	else:
		device_type = 1
	ofile = file(opt_file, 'w')
	pickle.dump(widgets['dir_entry'].get_text(), ofile)
	pickle.dump(device_type, ofile)
	ofile.close()

def load_state():
	try:
		ifile = file(opt_file, 'r')
		widgets['dir_entry'].set_text(pickle.load(ifile))
		device_type = pickle.load(ifile)
		if device_type == 0:
			widgets['h100_radio'].set_active(True)
		else:
			widgets['h300_radio'].set_active(True)
		ifile.close()
	except:
		print 'WARNING: Loading last state failed.'
		return
	

# Progress Bar Counters
counter=0
media_file_count=0

def count_media_files():
	a = 0
	for root, dirs, files in os.walk(widgets['dir_entry'].get_text()):
		for x in files:
			
			if x.lower().endswith('.mp3') or x.endswith('.ogg'):
				a += 1
	return a
	
def py_callback_func(a,b):
	widgets['status'].push(1, b)
	global counter, media_file_count
	counter += 1 
	widgets['progress'].set_fraction(float(counter)/float(media_file_count))
	widgets['progress'].set_text(str(counter) + ' of '+ str(media_file_count) + ' files')
	while gtk.events_pending():
		gtk.main_iteration_do()
	return 0

class GladeHandlers:
	def go(event):
		"""
		This function performs the actual write opperation.  It handles the progress
		bars, window refreshing, and the actual database writing itself.
		"""
		
		# device_type
		# 0 = h100 series
		# 1 = h300 series
		if widgets['h100_radio'].get_active():
			device_type=0
		else:
			device_type=1
		
		location = widgets['dir_entry'].get_text()
		
		if location == '':
			msgbox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_ERROR,
			buttons=gtk.BUTTONS_CLOSE)
			msgbox.set_markup('Please enter a device location.')
			msgbox.run()
			msgbox.destroy()
			return
		
		# Reset our progress bar counters
		widgets['status'].push(1, 'Counting files...')
		while gtk.events_pending(): 
			gtk.main_iteration_do()
		global media_file_count, counter
		counter = 0
		media_file_count = count_media_files()
		if media_file_count == 0:
			msgbox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_ERROR,
			buttons=gtk.BUTTONS_CLOSE)
			msgbox.set_markup('Griver couldn\'t find any media files in the given directory.')
			msgbox.run()
			msgbox.destroy()
			return 1
		
		widgets['main_window'].set_title('Griver - Working...')
		
		# Here we go...
		print "creating database..."
		try:
			libiriver = ctypes.CDLL("/usr/local/lib/libiriverdb.so.0")
		except:
			libiriver = ctypes.CDLL("libiriverdb.so.0")
		try:
			CFUNC = ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_int,ctypes.c_char_p)
			callback_function = CFUNC(py_callback_func)
			errcode = libiriver.iriverdb_write_with_callback(location, device_type, CFUNC(callback_function))
		except:
			errcode = 1

		widgets['main_window'].set_title('Griver')
		 
		if errcode == 0:
			msgbox = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_ERROR,
			buttons=gtk.BUTTONS_CLOSE)
			msgbox.set_markup('Griver could not write the database.')
			msgbox.run()
			msgbox.destroy()
		else: 
			print 'done writing database...'
			widgets['main_window'].set_title('Griver')
			widgets['progress'].set_fraction(0)
			widgets['progress'].set_text(' ') 
			widgets['status'].push(1, 'Done.')
	
	def browse(event):
		chooser = gtk.FileChooserDialog("Open...", None,
			gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
			(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
			gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		chooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
		chooser.set_default_response(gtk.RESPONSE_OK)

		chooser.set_current_folder(widgets['dir_entry'].get_text())

		response = chooser.run()
		chooser.hide()

		if response == gtk.RESPONSE_OK:
			widgets['dir_entry'].set_text(chooser.get_filename())
	

	def about(event):
		about = gtk.AboutDialog()
		about.set_name("gRiver")
		about.set_version(version)
		about.set_icon_from_file('./griver.png')  # broken right now; screw it
		about.set_copyright("Copyright 2009")
		about.set_license("GPL-3")
		about.set_website("http://code.google.com/p/griver/")
		about.set_authors(["Lukas Sabota <ltsmooth42 _at_ gmail _dot_ com>"])
		about.run()
		about.destroy()


	def end(event, event2=None):
		save_state()
		sys.exit(1)

class WidgetsWrapper:
	def __init__(self):
		# Search for the glade file
		glade_file = ''
		# Check first in the current directory
		if os.path.isfile('griver.ui'):
			glade_file = 'griver.ui'
		# Then check in the share directory (installed)
		elif os.path.isfile(os.path.dirname(sys.argv[0]) +\
		'/../share/griver/griver.ui'):
			glade_file = os.path.dirname(sys.argv[0])+'/../share/griver/griver.ui'
		else:
			print 'ERROR.'
			print 'Could not find the glade interface file.'
			print 'Try reinstalling the application.'
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(glade_file)
		#self.widgets = gtk.glade.XML(glade_file, "main_window")
		self.widgets = self.builder.get_object("main_window")
		self.builder.connect_signals(GladeHandlers.__dict__)

	def __getitem__(self, key):
		return self.builder.get_object(key)

def setup_environment():
	"""
	This function ensures that the options directory exists.	If it does not,
	it creates it.
	"""
	global app_config_dir, opt_file
	app_config_dir = os.getenv('HOME')+'/.griver'
	opt_file = app_config_dir + "/griver_options.dat"
	if not os.path.exists(app_config_dir):
		# this is the first time the application is run.
		# create the directory
		print 'creating application settings directory...'
		os.mkdir(app_config_dir)

def setup_widgets():
	"""
	This function creates and instance of the main window.
	"""
	global widgets
	widgets = WidgetsWrapper()
	widgets['main_window'].show_all()
	
def main_loop():
	gtk.main()

def find_library():
	if ctypes.util.find_library("iriverdb") == None:
		print "Cannot find iriverdb library.	Please install libiriverdb to run this program."
		sys.exit(5)
	

##############################################################################
# The beloved main
if __name__ == '__main__':
	print 'starting...'
	setup_environment()
	setup_widgets()
	load_state()
	find_library()
	main_loop()
