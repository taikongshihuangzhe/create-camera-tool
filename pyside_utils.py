#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a third party library

from PySide import QtGui

import pysideuic
import xml.etree.ElementTree as xml
from cStringIO import StringIO


def loadUiType(ui_file):
        """Load UI File.

        Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
        and then execute it in a special frame to retrieve the form_class.

        SOURCE: http://kiaran.net/post/64316332303/maya-2014-custom-ui-using-pyside-and-qt-designer
        """
        parsed = xml.parse(ui_file)
        widget_class = parsed.find('widget').get('class')
        form_class = parsed.find('class').text

        with open(ui_file, 'r') as f:
            o = StringIO()
            frame = {}

            pysideuic.compileUi(f, o, indent=0)
            pyc = compile(o.getvalue(), '<string>', 'exec')
            exec pyc in frame

            # Fetch the base_class and form class based on their type in the xml from designer
            form_class = frame['Ui_%s' % form_class]
            base_class = eval('QtGui.%s' % widget_class)

        return form_class, base_class
