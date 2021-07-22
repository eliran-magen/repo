###Created By Eliran Magen###

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import logging
import webbrowser

# creating a logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class NthSelector(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(NthSelector, self).__init__(parent)

		self.setWindowTitle("Nth Selector")
		self.setFixedSize(240, 120)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_actions()
		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_actions(self):
		self.about_action = QtWidgets.QAction("About", self)
		self.gitHub_action = QtWidgets.QAction("GitHub", self)

	def create_widgets(self):
		self.menu_bar = QtWidgets.QMenuBar()
		self.help_menu = self.menu_bar.addMenu("Help")
		self.help_menu.addAction(self.about_action)
		self.help_menu.addAction(self.gitHub_action)

		self.loop_rb = QtWidgets.QRadioButton("Loop")
		self.loop_rb.setChecked(True)
		self.ring_rb = QtWidgets.QRadioButton("Ring")

		self.nth_sb = QtWidgets.QSpinBox()
		self.nth_sb.setToolTip("Nth number that won't be selected in the loop")
		self.nth_sb.setMinimum(2)
		self.nth_sb.setValue(3)

		self.select_btn = QtWidgets.QPushButton("Select")

	def create_layouts(self):
		radio_btn_layout = QtWidgets.QHBoxLayout()
		radio_btn_layout.addStretch()
		radio_btn_layout.addWidget(self.loop_rb)
		radio_btn_layout.addWidget(self.ring_rb)

		nth_layout = QtWidgets.QHBoxLayout()
		nth_layout.addWidget(self.nth_sb)

		form_layout = QtWidgets.QFormLayout()
		form_layout.addRow("Selection Every:", nth_layout)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addWidget(self.menu_bar)
		main_layout.setSpacing(3)
		main_layout.addStretch()
		main_layout.addLayout(radio_btn_layout)
		main_layout.addLayout(form_layout)
		main_layout.addWidget(self.select_btn)

	def create_connections(self):
		self.about_action.triggered.connect(self.about)
		self.gitHub_action.triggered.connect(self.gitHub_link)
		self.select_btn.clicked.connect(self.select_loop)


	def select_loop(self):
		selEdges = pm.ls(sl = True)
		selObject = selEdges[0].node()
		sel_indices = []
		for edge in selEdges:
			try:
				sel_indices.append(edge.index())
			except:
				pm.warning("Please make sure only edges are selected")

		if self.loop_rb.isChecked():
			pm.polySelect(selObject, edgeLoop = (sel_indices))
		elif self.ring_rb.isChecked():
			pm.polySelect(selObject, edgeRing = (sel_indices))

		edgeLoop = pm.ls(sl = True)

		edgeList = []
		for edges in edgeLoop:
		    loop_indices = edges.indices()
		    for index in loop_indices:
		        edgeList.append(index)

		nth_value = self.nth_sb.value()
		del edgeList[nth_value - 1::nth_value]

		pm.select(cl = True)
		for edge in edgeList:
		    pm.select("{0}.e[{1}]".format(selObject, edge), add = True)

	def about(self):
		msg = QtWidgets.QMessageBox()
		msg.setIcon(QtWidgets.QMessageBox.Information)
		msg.setWindowTitle("About Nth Selector")
		msg.setText("This tool is used to select every Nth number\nof edges in a simple manner\n\nCreated by Eliran Magen")
		msg.exec_()

	def gitHub_link(self):
		webbrowser.open("https://github.com/eliran-magen/repo", new=1)


if __name__ == "__main__":
	try:
		nth_selector.close()
		nth_selector.deleteLater()

	except:
		pass

	finally:
		nth_selector = NthSelector()
		nth_selector.show()