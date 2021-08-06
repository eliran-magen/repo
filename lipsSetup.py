### Created by Eliran Magen ###

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import pymel.core as pm
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import logging
import math

# creating a logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class LipsSetup(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(LipsSetup, self).__init__(parent)

		if (pm.selectPref(tso = True, q = True) == 0):
			pm.selectPref(tso = True)

		self.setWindowTitle("Lips Setup")
		self.setMinimumSize(300, 120)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_actions()
		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_actions(self):
		pass

	def create_widgets(self):
		self.upper_vert_sel_le = QtWidgets.QLineEdit()
		self.upper_vert_sel_btn = QtWidgets.QPushButton("<")
		self.upper_vert_sel_btn.setToolTip("Press here to insert your\nupper vertices selection\nNote: Please select them in order")
		self.lower_vert_sel_le = QtWidgets.QLineEdit()
		self.lower_vert_sel_btn = QtWidgets.QPushButton("<")
		self.lower_vert_sel_btn.setToolTip("Press here to insert your\nlower vertices selection\nNote: Please select them in order")
		self.upper_mid_vert_sel_le = QtWidgets.QLineEdit()
		self.upper_mid_vert_sel_btn = QtWidgets.QPushButton("<")
		self.upper_mid_vert_sel_btn.setToolTip("Press here to insert your\nupper mid vertex selection")
		self.lower_mid_vert_sel_le = QtWidgets.QLineEdit()
		self.lower_mid_vert_sel_btn = QtWidgets.QPushButton("<")
		self.lower_mid_vert_sel_btn.setToolTip("Press here to insert your\nlower mid vertex selection")
		self.head_jnt_sel_le = QtWidgets.QLineEdit()
		self.head_jnt_sel_btn = QtWidgets.QPushButton("<")
		self.head_jnt_sel_btn.setToolTip("Press here to insert your\nhead joint selection")
		self.jaw_jnt_sel_le = QtWidgets.QLineEdit()
		self.jaw_jnt_sel_btn = QtWidgets.QPushButton("<")
		self.jaw_jnt_sel_btn.setToolTip("Press here to insert your\njaw joint selection")
		self.create_btn = QtWidgets.QPushButton("Create")
		self.cancel_btn = QtWidgets.QPushButton("Cancel")

	def create_layouts(self):
		upper_vert_sel_layout = QtWidgets.QHBoxLayout()
		upper_vert_sel_layout.addWidget(self.upper_vert_sel_le)
		upper_vert_sel_layout.addWidget(self.upper_vert_sel_btn)

		lower_vert_sel_layout = QtWidgets.QHBoxLayout()
		lower_vert_sel_layout.addWidget(self.lower_vert_sel_le)
		lower_vert_sel_layout.addWidget(self.lower_vert_sel_btn)

		upper_mid_vert_sel_layout = QtWidgets.QHBoxLayout()
		upper_mid_vert_sel_layout.addWidget(self.upper_mid_vert_sel_le)
		upper_mid_vert_sel_layout.addWidget(self.upper_mid_vert_sel_btn)

		lower_mid_vert_sel_layout = QtWidgets.QHBoxLayout()
		lower_mid_vert_sel_layout.addWidget(self.lower_mid_vert_sel_le)
		lower_mid_vert_sel_layout.addWidget(self.lower_mid_vert_sel_btn)

		head_jnt_sel_layout = QtWidgets.QHBoxLayout()
		head_jnt_sel_layout.addWidget(self.head_jnt_sel_le)
		head_jnt_sel_layout.addWidget(self.head_jnt_sel_btn)

		jaw_jnt_sel_layout = QtWidgets.QHBoxLayout()
		jaw_jnt_sel_layout.addWidget(self.jaw_jnt_sel_le)
		jaw_jnt_sel_layout.addWidget(self.jaw_jnt_sel_btn)

		insert_sel_layout = QtWidgets.QFormLayout()
		insert_sel_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
		insert_sel_layout.addRow("Upper Lip Vertices:", upper_vert_sel_layout)
		insert_sel_layout.addRow("Lower Lip Vertices:", lower_vert_sel_layout)
		insert_sel_layout.addRow("Upper Lip vertex:", upper_mid_vert_sel_layout)
		insert_sel_layout.addRow("Lower Lip vertex:", lower_mid_vert_sel_layout)
		insert_sel_layout.addRow("Head Joint:", head_jnt_sel_layout)
		insert_sel_layout.addRow("Jaw Joint:", jaw_jnt_sel_layout)

		create_cancel_layout = QtWidgets.QHBoxLayout()
		create_cancel_layout.addWidget(self.create_btn)
		create_cancel_layout.addWidget(self.cancel_btn)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.setSpacing(5)
		main_layout.addStretch()
		main_layout.setContentsMargins(3, 3, 3, 3)
		main_layout.addLayout(insert_sel_layout)
		main_layout.addLayout(create_cancel_layout)

	def create_connections(self):
		self.upper_vert_sel_btn.clicked.connect(self.upperVertSelection)
		self.lower_vert_sel_btn.clicked.connect(self.lowerVertSelection)
		self.upper_mid_vert_sel_btn.clicked.connect(self.upperMidVertSelection)
		self.lower_mid_vert_sel_btn.clicked.connect(self.lowerMidVertSelection)
		self.head_jnt_sel_btn.clicked.connect(self.headJntSelection)
		self.jaw_jnt_sel_btn.clicked.connect(self.jawJntSelection)
		self.create_btn.clicked.connect(self.createLips)
		self.cancel_btn.clicked.connect(self.close)

	def upperVertSelection(self):
		sel = pm.ls(os = True, fl = True)
		vert_list = []
		for vert in sel:
			if self.validateVertex(vert):
				vert_list.append(vert)
			else:
				self.upper_vert_sel_le.setText("")
				break
		if len(vert_list) > 0: self.upper_vert_sel_le.setText(str(vert_list))

	def lowerVertSelection(self):
		sel = pm.ls(os = True, fl = True)
		vert_list = []
		for vert in sel:
			if self.validateVertex(vert):
				vert_list.append(vert)
			else:
				self.lower_vert_sel_le.setText("")
				break
		if len(vert_list) > 0: self.lower_vert_sel_le.setText(str(vert_list))

	def upperMidVertSelection(self):
		sel = pm.ls(os = True, fl = True)
		if self.validateVertex(sel):
			self.upper_mid_vert_sel_le.setText(str(sel))
		else:
			self.upper_mid_vert_sel_le.setText("")

	def lowerMidVertSelection(self):
		sel = pm.ls(os = True, fl = True)
		if self.validateVertex(sel):
			self.lower_mid_vert_sel_le.setText(str(sel))
		else:
			self.lower_mid_vert_sel_le.setText("")

	def headJntSelection(self):
		sel = pm.ls(os = True, fl = True)
		if self.validateJoint(node = sel):
			self.head_jnt_sel_le.setText(str(sel))
		else:
			self.head_jnt_sel_le.setText("")

	def jawJntSelection(self):
		sel = pm.ls(os = True, fl = True)
		if self.validateJoint(node = sel):
			self.jaw_jnt_sel_le.setText(str(sel))
		else:
			self.jaw_jnt_sel_le.setText("")

	def createLips(self):
		""" The main function, the function that creates the lip setup using the selections made before"""
		# creating the upper joints
		upper_vert_list = self.strToList(self.upper_vert_sel_le.text())
		upper_jnt_list = []
		if len(upper_vert_list) > 0:
			i = 1
			for vert in upper_vert_list:
				pm.select(cl = True)
				jnt = pm.joint(n = "upLip_{0}_jnt".format(str(i).zfill(2)), rad = 0.1, p = vert.getPosition())
				upper_jnt_list.append(jnt)
				i +=1
		else:
			om.MGlobal.displayError("Please select the upper vertices first")

		# creating the lower joints
		lower_vert_list = self.strToList(self.lower_vert_sel_le.text())
		lower_jnt_list = []
		if len(lower_vert_list) > 0:
			i = 1
			for vert in lower_vert_list:
				pm.select(cl = True)
				jnt = pm.joint(n = "loLip_{0}_jnt".format(str(i).zfill(2)), rad = 0.1, p = vert.getPosition())
				lower_jnt_list.append(jnt)
				i +=1
		else:
			om.MGlobal.displayError("Please select the lower vertices first")


	def validateVertex(self, node):
		valid = pm.filterExpand(node, sm = 31)
		if valid:
			if len(valid) == 1:
				return True
			else:
				om.MGlobal.displayError("Please only select one vertex")
		else:
			om.MGlobal.displayError("Please only select vertices")

	def validateJoint(self, node, valid = False):
		if pm.nodeType(node) == "joint":
			valid = True
		if valid:
			return True
		else:
			if len(node) > 1:
				om.MGlobal.displayError("Please only select one joint")
			else:
				om.MGlobal.displayError("Please only select joints")

	def strToList(self, string):
		"""a function that takes the input from the line edits and sets it back to lists"""
		# setting it back to list
		new_list = string.split(", ")
		new_list[0] = new_list[0][1:]
		new_list[-1] = new_list[-1][:-1]

		fixed_list = []
		for i in new_list:
			i = i.split("'")
			i = i[1]
			fixed_list.append(i)

		# making the nodes pyNodes
		return_list = []
		for node in fixed_list:
			newNode = pm.PyNode(node)
			return_list.append(newNode)
		return return_list


if __name__ == "__main__":
	try:
		lips_setup.close()
		lips_setup.deleteLater()

	except:
		pass

	finally:
		lips_setup = LipsSetup()
		lips_setup.show()