from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import logging

# creating a logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class ClassName(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(ClassName, self).__init__(parent)

		self.setWindowTitle("Window Title")
		self.setMinimumSize(200, 200)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_widgets(self):
		pass

	def create_layouts(self):
		pass

	def create_connections(self):
		pass


if __name__ == "__main__":
	try:
		class_name.close()
		class_name.deleteLater()

	except:
		pass

	finally:
		class_name = ClassName()
		class_name.show()