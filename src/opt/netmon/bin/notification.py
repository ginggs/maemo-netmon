# -*- coding: utf-8 -*-
# NetMon Notification Module
# Copyright 2010 by P. Kozak <maemo@golwen.net>
# http://netmon.golwen.net/
# This software is provided under an open source license - use at your own risk.

import dbus

class Notification():

	def __init__(self):
		bus = dbus.SystemBus()
		dbus_object = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
		self.notification = dbus.Interface(dbus_object, 'org.freedesktop.Notifications')

	def info(self, message):
		return self.notification.SystemNoteInfoprint(message)

	def dialog(self, message):
		return self.notification.SystemNoteDialog(message, 0, 'OK')
