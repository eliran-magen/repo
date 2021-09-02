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

		self.DONE = False

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
		self.upper_vert_sel_btn.setToolTip("Press here to insert your\nupper vertices selection\nNote: Please select them in order\nadvised to select from right to left")
		self.lower_vert_sel_le = QtWidgets.QLineEdit()
		self.lower_vert_sel_btn = QtWidgets.QPushButton("<")
		self.lower_vert_sel_btn.setToolTip("Press here to insert your\nlower vertices selection\nNote: Please select them in order\nadvised to select from right to left")
		self.head_jnt_sel_le = QtWidgets.QLineEdit()
		self.head_jnt_sel_btn = QtWidgets.QPushButton("<")
		self.head_jnt_sel_btn.setToolTip("Press here to insert your\nhead joint selection")
		self.jaw_jnt_sel_le = QtWidgets.QLineEdit()
		self.jaw_jnt_sel_btn = QtWidgets.QPushButton("<")
		self.jaw_jnt_sel_btn.setToolTip("Press here to insert your\njaw joint selection")
		self.create_btn = QtWidgets.QPushButton("Create")
		self.apply_btn = QtWidgets.QPushButton("Apply")
		self.cancel_btn = QtWidgets.QPushButton("Cancel")

	def create_layouts(self):
		upper_vert_sel_layout = QtWidgets.QHBoxLayout()
		upper_vert_sel_layout.addWidget(self.upper_vert_sel_le)
		upper_vert_sel_layout.addWidget(self.upper_vert_sel_btn)

		lower_vert_sel_layout = QtWidgets.QHBoxLayout()
		lower_vert_sel_layout.addWidget(self.lower_vert_sel_le)
		lower_vert_sel_layout.addWidget(self.lower_vert_sel_btn)

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
		insert_sel_layout.addRow("Head Joint:", head_jnt_sel_layout)
		insert_sel_layout.addRow("Jaw Joint:", jaw_jnt_sel_layout)

		create_cancel_layout = QtWidgets.QHBoxLayout()
		create_cancel_layout.addWidget(self.create_btn)
		create_cancel_layout.addWidget(self.apply_btn)
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
		self.head_jnt_sel_btn.clicked.connect(self.headJntSelection)
		self.jaw_jnt_sel_btn.clicked.connect(self.jawJntSelection)
		self.create_btn.clicked.connect(self.created)
		self.create_btn.clicked.connect(self.createLips)
		self.apply_btn.clicked.connect(self.createLips)
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
		if len(vert_list) > 0:
			self.upper_vert_sel_le.setText(str(vert_list))
		else:
			om.MGlobal.displayError("Please select vertices first")

	def lowerVertSelection(self):
		sel = pm.ls(os = True, fl = True)
		vert_list = []
		for vert in sel:
			if self.validateVertex(vert):
				vert_list.append(vert)
			else:
				self.lower_vert_sel_le.setText("")
				break
		if len(vert_list) > 0:
			self.lower_vert_sel_le.setText(str(vert_list))
		else:
			om.MGlobal.displayError("Please select vertices first")

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

	def created(self):
		"""a function that is meant to close the window if the user presses create and not apply"""
		self.DONE = True

	def createLips(self):
		"""The main function, the function that creates the lip setup using the selections made before"""
		###Upper Lips###
		# creating the upper joints
		upper_vert_list = self.strToList(self.upper_vert_sel_le.text())
		upper_jnt_list = []
		if len(upper_vert_list) > 0:
			i = 1
			for vert in upper_vert_list:
				pm.select(cl = True)
				jnt = pm.joint(n = "upLip_{0}_jnt".format(str(i).zfill(2)), rad = 0.1, p = vert.getPosition())
				upper_jnt_list.append(jnt)
				i += 1
		else:
			om.MGlobal.displayError("Please select the upper vertices first")

		# determining important joints and joint lists
		mid_upper_jnt_index = int(math.floor(float(len(upper_jnt_list)) / 2.0))
		mid_upper_jnt = upper_jnt_list[mid_upper_jnt_index]

		left_upper_jnt_index = int(math.floor(float(mid_upper_jnt_index) + (float(mid_upper_jnt_index) / 2.0)))
		left_upper_jnt = upper_jnt_list[left_upper_jnt_index]

		right_upper_jnt_index = int(math.floor(float(mid_upper_jnt_index) - (float(mid_upper_jnt_index) / 2.0)))
		right_upper_jnt = upper_jnt_list[right_upper_jnt_index]

		mid_upper_jnt_list = upper_jnt_list[right_upper_jnt_index + 1:left_upper_jnt_index]
		right_upper_jnt_list = upper_jnt_list[1:mid_upper_jnt_index]
		left_upper_jnt_list = upper_jnt_list[mid_upper_jnt_index + 1:-1]

		upper_lip_jnt_list = upper_jnt_list[1:-1]

		# creating the controls
		upper_lip_ctrl = pm.circle(n = "c_upper_lip_ctrl", s = 4, d = 1, r = 0.3, ch = False)[0]
		upper_lip_ctrl.setAttr("rz", 45)
		pm.makeIdentity(upper_lip_ctrl, a = True)
		upper_lip_ctrl.setTranslation(mid_upper_jnt.getTranslation())

		upper_lip_mid_ctrl = pm.circle(n = "c_upper_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		upper_lip_mid_ctrl.setTranslation(mid_upper_jnt.getTranslation())

		upper_lip_right_ctrl = pm.circle(n = "r_upper_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		upper_lip_right_ctrl.setTranslation(right_upper_jnt.getTranslation())

		upper_lip_left_ctrl = pm.circle(n = "l_upper_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		upper_lip_left_ctrl.setTranslation(left_upper_jnt.getTranslation())

		upper_lip_ctrl_list = [upper_lip_ctrl, upper_lip_mid_ctrl, upper_lip_right_ctrl, upper_lip_left_ctrl]

		# setting up group hierarchies for the joints and controls
		upper_lip_jnt_main_grp = pm.group(n = "upper_lip_jnt_grp", em = True)
		try:
			head_jnt = self.makePyNode(self.strToList(self.head_jnt_sel_le.text())[0])
		except:
			om.MGlobal.displayError("Please first insert the head joint")
		upper_lip_ctrl_main_grp = pm.group(n = "upper_lip_ctrl_grp", em = True)

		for jnt in upper_jnt_list:
			pm.parent(jnt, upper_lip_jnt_main_grp)
			self.makeJointHierarchy(jnt)

		for ctrl in upper_lip_ctrl_list:
			pm.parent(ctrl, upper_lip_ctrl_main_grp)
			self.makeControlHierarchy(ctrl)

		## making the joints and the controls follow what they should
		# upper lip control
		index = int(math.ceil(float(len(upper_lip_jnt_list)) / 2.0))
		sub = 1.0 / float(index)

		self.jntsFollowMainCtrl(index = index, sub = sub, ctrl = upper_lip_ctrl, main_jnt = mid_upper_jnt, jnt_list = upper_lip_jnt_list)

		mid_upper_md_node = mid_upper_jnt.getParent().getParent().connections()[0]
		pm.connectAttr(mid_upper_md_node + ".output", upper_lip_mid_ctrl.getParent() + ".translate")

		right_upper_md_node = right_upper_jnt.getParent().getParent().connections()[0]
		pm.connectAttr(right_upper_md_node + ".output", upper_lip_right_ctrl.getParent() + ".translate")

		left_upper_md_node = left_upper_jnt.getParent().getParent().connections()[0]
		pm.connectAttr(left_upper_md_node + ".output", upper_lip_left_ctrl.getParent() + ".translate")

		# upper mid tweak control
		indexRange = (int(math.floor(float(len(upper_jnt_list)) / 3)) / 2)
		sub = 1.0 / float(indexRange)

		self.jntsFollowTweakCtrl(indexRange = indexRange, sub = sub, index = mid_upper_jnt_index, ctrl = upper_lip_mid_ctrl, main_jnt = mid_upper_jnt, jnt_list = upper_lip_jnt_list)

		# upper right tweak control
		indexRange = (int(math.floor(float(len(upper_jnt_list)) / 3)) / 2)
		sub = 1.0 / float(indexRange)

		self.jntsFollowTweakCtrl(indexRange = indexRange, sub = sub, index = right_upper_jnt_index,ctrl = upper_lip_right_ctrl, main_jnt = right_upper_jnt, jnt_list = upper_lip_jnt_list)

		# upper left tweak control
		indexRange = (int(math.floor(float(len(upper_jnt_list)) / 3)) / 2)
		sub = 1.0 / float(indexRange)

		self.jntsFollowTweakCtrl(indexRange = indexRange, sub = sub, index = left_upper_jnt_index ,ctrl = upper_lip_left_ctrl, main_jnt = left_upper_jnt, jnt_list = upper_lip_jnt_list)

		for ctrl in upper_lip_ctrl_list:
			pm.setAttr(ctrl + ".rotate", l = True)
			pm.setAttr(ctrl + ".scale", l = True)

		###Lower Lips###
		# creating the lower joints
		lower_vert_list = self.strToList(self.lower_vert_sel_le.text())
		lower_jnt_list = []
		if len(lower_vert_list) > 0:
			i = 1
			for vert in lower_vert_list:
				pm.select(cl = True)
				jnt = pm.joint(n = "loLip_{0}_jnt".format(str(i).zfill(2)), rad = 0.1, p = vert.getPosition())
				pm.setAttr(jnt + ".rz", 180)
				lower_jnt_list.append(jnt)
				i += 1
		else:
			om.MGlobal.displayError("Please select the lower vertices first")

		# determining important joints and joint lists
		mid_lower_jnt_index = int(math.floor(float(len(lower_jnt_list)) / 2.0))
		mid_lower_jnt = lower_jnt_list[mid_lower_jnt_index]

		left_lower_jnt_index = int(math.floor(float(mid_lower_jnt_index) + (float(mid_lower_jnt_index) / 2.0)))
		left_lower_jnt = lower_jnt_list[left_lower_jnt_index]

		right_lower_jnt_index = int(math.floor(float(mid_lower_jnt_index) - (float(mid_lower_jnt_index) / 2.0)))
		right_lower_jnt = lower_jnt_list[right_lower_jnt_index]

		mid_lower_jnt_list = lower_jnt_list[right_lower_jnt_index + 1:left_lower_jnt_index]
		right_lower_jnt_list = lower_jnt_list[1:mid_lower_jnt_index]
		left_lower_jnt_list = lower_jnt_list[mid_lower_jnt_index + 1:-1]

		lower_lip_jnt_list = lower_jnt_list[1:-1]

		# creating the controls
		lower_lip_ctrl = pm.circle(n = "c_lower_lip_ctrl", s = 4, d = 1, r = 0.3, ch = False)[0]
		lower_lip_ctrl.setAttr("rz", 45)
		pm.makeIdentity(lower_lip_ctrl, a = True)
		lower_lip_ctrl.setTranslation(mid_lower_jnt.getTranslation())
		lower_lip_ctrl.setRotation(mid_lower_jnt.getRotation())

		lower_lip_mid_ctrl = pm.circle(n = "c_lower_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		lower_lip_mid_ctrl.setTranslation(mid_lower_jnt.getTranslation())
		lower_lip_mid_ctrl.setRotation(mid_lower_jnt.getRotation())

		lower_lip_right_ctrl = pm.circle(n = "r_lower_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		lower_lip_right_ctrl.setTranslation(right_lower_jnt.getTranslation())
		lower_lip_right_ctrl.setRotation(right_lower_jnt.getRotation())

		lower_lip_left_ctrl = pm.circle(n = "l_lower_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		lower_lip_left_ctrl.setTranslation(left_lower_jnt.getTranslation())
		lower_lip_left_ctrl.setRotation(left_lower_jnt.getRotation())

		lower_lip_ctrl_list = [lower_lip_ctrl, lower_lip_mid_ctrl, lower_lip_right_ctrl, lower_lip_left_ctrl]

		# setting up group hierarchies for the joints and controls
		lower_lip_jnt_main_grp = pm.group(n = "lower_lip_jnt_grp", em = True)
		head_jnt = self.makePyNode(self.strToList(self.head_jnt_sel_le.text())[0])
		lower_lip_ctrl_main_grp = pm.group(n = "lower_lip_ctrl_grp", em = True)

		for jnt in lower_jnt_list:
			pm.parent(jnt, lower_lip_jnt_main_grp)
			self.makeJointHierarchy(jnt)

		for ctrl in lower_lip_ctrl_list:
			pm.parent(ctrl, lower_lip_ctrl_main_grp)
			self.makeControlHierarchy(ctrl)

		## making the joints and the controls follow what they should
		# lower lip control
		index = int(math.ceil(float(len(lower_lip_jnt_list)) / 2.0))
		sub = 1.0 / float(index)

		self.jntsFollowMainCtrl(index = index, sub = sub, ctrl = lower_lip_ctrl, main_jnt = mid_lower_jnt, jnt_list = lower_lip_jnt_list)

		mid_lower_md_node = mid_lower_jnt.getParent().getParent().connections()[0]
		pm.connectAttr(mid_lower_md_node + ".output", lower_lip_mid_ctrl.getParent() + ".translate")

		right_lower_md_node = right_lower_jnt.getParent().getParent().connections()[0]
		pm.connectAttr(right_lower_md_node + ".output", lower_lip_right_ctrl.getParent() + ".translate")

		left_lower_md_node = left_lower_jnt.getParent().getParent().connections()[0]
		pm.connectAttr(left_lower_md_node + ".output", lower_lip_left_ctrl.getParent() + ".translate")

		# lower mid tweak control
		indexRange = (int(math.floor(float(len(lower_jnt_list)) / 3)) / 2)
		sub = 1.0 / float(indexRange)

		self.jntsFollowTweakCtrl(indexRange = indexRange, sub = sub, index = mid_lower_jnt_index, ctrl = lower_lip_mid_ctrl, main_jnt = mid_lower_jnt, jnt_list = lower_lip_jnt_list)

		# lower right tweak control
		indexRange = (int(math.floor(float(len(lower_jnt_list)) / 3)) / 2)
		sub = 1.0 / float(indexRange)

		self.jntsFollowTweakCtrl(indexRange = indexRange, sub = sub, index = right_lower_jnt_index,ctrl = lower_lip_right_ctrl, main_jnt = right_lower_jnt, jnt_list = lower_lip_jnt_list)

		# lower left tweak control
		indexRange = (int(math.floor(float(len(lower_jnt_list)) / 3)) / 2)
		sub = 1.0 / float(indexRange)

		self.jntsFollowTweakCtrl(indexRange = indexRange, sub = sub, index = left_lower_jnt_index ,ctrl = lower_lip_left_ctrl, main_jnt = left_lower_jnt, jnt_list = lower_lip_jnt_list)

		# creating main lips control and making the joints and controls follow the head
		main_lip_jnt_grp = pm.group(n = "main_lip_jnt_grp", em = True)
		pm.parent(upper_lip_jnt_main_grp, main_lip_jnt_grp)
		pm.parent(lower_lip_jnt_main_grp, main_lip_jnt_grp)

		main_lips_ctrl = pm.circle(n = "c_main_lips_ctrl", s = 4, d = 1, r = 0.7, ch = False)[0]
		main_lips_ctrl.setAttr("rz", 45)
		pm.makeIdentity(main_lips_ctrl, a = True)
		main_lips_ctrl.setTranslation(self.calculateAveragePos(mid_upper_jnt.getTranslation(space = "world"), mid_lower_jnt.getTranslation(space = "world")))
		main_lips_ctrl.setRotation(mid_upper_jnt.getRotation())
		self.makeControlHierarchy(main_lips_ctrl)
		pm.parent(upper_lip_ctrl_main_grp, main_lips_ctrl)
		pm.parent(lower_lip_ctrl_main_grp, main_lips_ctrl)

		self.matrixConstraint(parent = head_jnt, child = main_lips_ctrl.getAllParents()[-1])

		self.matrixConstraint(parent = main_lips_ctrl, child = main_lip_jnt_grp)

		for ctrl in lower_lip_ctrl_list:
			pm.setAttr(ctrl + ".rotate", l = True)
			pm.setAttr(ctrl + ".scale", l = True)

		###Corner Lips###
		## left corner lip
		# determining corner lip joints and creating a tweak control for them
		left_corner_jnt_list = [upper_jnt_list[-1], upper_jnt_list[-2], lower_jnt_list[-2], lower_jnt_list[-1]]
		left_corner_ctrl = pm.circle(n = "l_corner_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		left_corner_ctrl.setTranslation(self.calculateAveragePos(left_corner_jnt_list[0].getTranslation(space = "world"), left_corner_jnt_list[-1].getTranslation(space = "world")))
		left_corner_ctrl.setRotation(mid_upper_jnt.getRotation())
		self.makeControlHierarchy(left_corner_ctrl)

		# making the necessary joints follow the tweak control
		self.cornerJntsFollowTweakCtrl(ctrl = left_corner_ctrl, jnt_list = left_corner_jnt_list)

		# main left corner lip control
		left_corner_main_ctrl = pm.circle(n = "l_corner_lip_ctrl", s = 4, d = 1, r = 0.3, ch = False)[0]
		left_corner_main_ctrl.setAttr("rz", 45)
		pm.makeIdentity(left_corner_main_ctrl, a = True)
		left_corner_main_ctrl.setTranslation(left_corner_ctrl.getTranslation(space = "world"))
		left_corner_main_ctrl.setRotation(left_corner_ctrl.getRotation(space = "world"))
		self.makeControlHierarchy(left_corner_main_ctrl)

		left_upper_jnt_corner_list = upper_jnt_list[mid_upper_jnt_index + 1:-1]
		left_upper_jnt_corner_list.append(upper_jnt_list[-1])
		left_upper_jnt_corner_list.reverse()
		left_lower_jnt_corner_list = lower_jnt_list[mid_lower_jnt_index + 1:-1]
		left_lower_jnt_corner_list.append(lower_jnt_list[-1])
		left_lower_jnt_corner_list.reverse()

		sub = 1.0 / float(len(left_upper_jnt_corner_list))
		self.cornerJntsFollowMainCtrl(indexRange = len(left_upper_jnt_corner_list), sub = sub, ctrl = left_corner_main_ctrl, upper_jnt_list = left_upper_jnt_corner_list, lower_jnt_list = left_lower_jnt_corner_list)
		pm.parent(left_corner_ctrl.getAllParents()[-1], left_corner_main_ctrl)
		pm.parent(left_corner_main_ctrl.getAllParents()[-1], main_lips_ctrl)

		upper_left_corner_md_node = left_upper_jnt.getParent().getParent().getParent().connections()[0]
		pm.connectAttr(upper_left_corner_md_node + ".output", upper_lip_left_ctrl.getParent().getParent() + ".translate")

		lower_left_corner_md_node = left_lower_jnt.getParent().getParent().getParent().connections()[0]
		pm.connectAttr(lower_left_corner_md_node + ".output", lower_lip_left_ctrl.getParent().getParent() + ".translate")

		## right corner lip
		# determining corner lip joints and creating a tweak control for them
		right_corner_jnt_list = [upper_jnt_list[0], upper_jnt_list[1], lower_jnt_list[1], lower_jnt_list[0]]
		right_corner_ctrl = pm.circle(n = "l_corner_lip_tweak_ctrl", s = 8, d = 3, r = 0.15, ch = False)[0]
		right_corner_ctrl.setTranslation(self.calculateAveragePos(right_corner_jnt_list[0].getTranslation(space = "world"), right_corner_jnt_list[-1].getTranslation(space = "world")))
		right_corner_ctrl.setRotation(mid_upper_jnt.getRotation())
		pm.setAttr(right_corner_ctrl + ".ry", 180)
		self.makeControlHierarchy(right_corner_ctrl)

		# making the necessary joints follow the tweak control
		self.cornerJntsFollowTweakCtrl(ctrl = right_corner_ctrl, jnt_list = right_corner_jnt_list, inverse = True)

		# main right corner lip control
		right_corner_main_ctrl = pm.circle(n = "r_corner_lip_ctrl", s = 4, d = 1, r = 0.3, ch = False)[0]
		right_corner_main_ctrl.setAttr("rz", 45)
		pm.makeIdentity(right_corner_main_ctrl, a = True)
		right_corner_main_ctrl.setTranslation(right_corner_ctrl.getTranslation(space = "world"))
		right_corner_main_ctrl.setRotation(right_corner_ctrl.getRotation(space = "world"))
		self.makeControlHierarchy(right_corner_main_ctrl)

		right_upper_jnt_corner_list = upper_jnt_list[0:mid_upper_jnt_index]
		right_lower_jnt_corner_list = lower_jnt_list[0:mid_lower_jnt_index]

		sub = 1.0 / float(len(right_upper_jnt_corner_list))
		self.cornerJntsFollowMainCtrl(indexRange = len(right_upper_jnt_corner_list), sub = sub, ctrl = right_corner_main_ctrl, upper_jnt_list = right_upper_jnt_corner_list, lower_jnt_list = right_lower_jnt_corner_list, inverse = True)
		pm.parent(right_corner_ctrl.getAllParents()[-1], right_corner_main_ctrl)
		pm.parent(right_corner_main_ctrl.getAllParents()[-1], main_lips_ctrl)

		upper_right_corner_md_node = right_upper_jnt.getParent().getParent().getParent().connections()[0]
		pm.connectAttr(upper_right_corner_md_node + ".output", upper_lip_right_ctrl.getParent().getParent() + ".translate")

		lower_right_corner_md_node = right_lower_jnt.getParent().getParent().getParent().connections()[0]
		pm.connectAttr(lower_right_corner_md_node + ".output", lower_lip_right_ctrl.getParent().getParent() + ".translate")

		###Jaw###
		# getting the jaw joint from the UI
		try:
			jaw_jnt = self.makePyNode(self.strToList(self.jaw_jnt_sel_le.text())[0])
		except:
			om.MGlobal.displayError("Please first insert the jaw joint")
			self.DONE = False

		# making the mid lower joint and control follow the jaw completely
		pm.parentConstraint(jaw_jnt, mid_lower_jnt.getParent().getParent().getParent().getParent(), mo = True)
		for attr in ["translate", "rotate", "scale"]:
			pm.connectAttr(mid_lower_jnt.getParent().getParent().getParent().getParent() + "." + attr, lower_lip_ctrl.getParent().getParent().getParent() + "." + attr)
			pm.connectAttr(mid_lower_jnt.getParent().getParent().getParent().getParent() + "." + attr, lower_lip_mid_ctrl.getParent().getParent().getParent() + "." + attr)

		# adding the "envelope" attribute to the main lips control
		main_lips_ctrl.addAttr("cornersFollowJaw", at = "float", min = 0, max = 1.0, dv = 0.5, k = True)

		# making the corner joints and controls follow what they should
		self.blendMatrices(parentStart = mid_upper_jnt.getParent().getParent().getParent().getParent(), parentEnd = mid_lower_jnt.getParent().getParent().getParent().getParent(), child = upper_jnt_list[0].getParent().getParent().getParent().getParent(), envelope = main_lips_ctrl + ".cornersFollowJaw")
		self.blendMatrices(parentStart = mid_upper_jnt.getParent().getParent().getParent().getParent(), parentEnd = mid_lower_jnt.getParent().getParent().getParent().getParent(), child = upper_jnt_list[-1].getParent().getParent().getParent().getParent(), envelope = main_lips_ctrl + ".cornersFollowJaw")
		self.blendMatrices(parentStart = mid_upper_jnt.getParent().getParent().getParent().getParent(), parentEnd = mid_lower_jnt.getParent().getParent().getParent().getParent(), child = lower_jnt_list[0].getParent().getParent().getParent().getParent(), envelope = main_lips_ctrl + ".cornersFollowJaw")
		self.blendMatrices(parentStart = mid_upper_jnt.getParent().getParent().getParent().getParent(), parentEnd = mid_lower_jnt.getParent().getParent().getParent().getParent(), child = lower_jnt_list[-1].getParent().getParent().getParent().getParent(), envelope = main_lips_ctrl + ".cornersFollowJaw")

		for attr in ["translate", "rotate", "scale"]:
			pm.connectAttr(upper_jnt_list[-1].getParent().getParent().getParent().getParent() + "." + attr, left_corner_main_ctrl.getParent().getParent().getParent() + "." + attr)

		right_corner_translate_md_node = pm.shadingNode("multiplyDivide", n = "right_corner_translate_md", asUtility = True)
		right_corner_translate_md_node.setAttr("input2X", -1)
		right_corner_translate_md_node.setAttr("input2Z", -1)
		right_corner_rotate_md_node = pm.shadingNode("multiplyDivide", n = "right_corner_rotate_md", asUtility = True)
		right_corner_rotate_md_node.setAttr("input2X", -1)
		right_corner_rotate_md_node.setAttr("input2Z", -1)
		pm.connectAttr(upper_jnt_list[0].getParent().getParent().getParent().getParent() + ".translate", right_corner_translate_md_node + ".input1")
		pm.connectAttr(upper_jnt_list[0].getParent().getParent().getParent().getParent() + ".rotate", right_corner_rotate_md_node + ".input1")
		pm.connectAttr(right_corner_translate_md_node + ".output", right_corner_main_ctrl.getParent().getParent().getParent() + ".translate")
		pm.connectAttr(right_corner_rotate_md_node + ".output", right_corner_main_ctrl.getParent().getParent().getParent() + ".rotate")

		if self.DONE == True:
			_logger.info("Built Succesfully")
			self.close()
		else:
			_logger.info("Built Succesfully")

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

	def makeJointHierarchy(self, jnt):
		# creating the necessary groups
		top_grp = pm.group(n = jnt.replace("jnt", "grp"), em = True)
		trsOs_grp = pm.group(n = jnt.replace("jnt", "trsOs"), em = True)
		trsBuffer_grp = pm.group(n = jnt.replace("jnt", "trsBuffer"), em = True)
		osGrp_grp = pm.group(n = jnt.replace("jnt", "osGrp"), em = True)
		tweakGrp_grp = pm.group(n = jnt.replace("jnt", "tweakGrp"), em = True)

		# moving the groups to where they should be
		jnt = self.makePyNode(jnt)
		top_grp.setTransformation(jnt.getTransformation())
		trsOs_grp.setTransformation(jnt.getTransformation())
		trsBuffer_grp.setTransformation(jnt.getTransformation())
		osGrp_grp.setTransformation(jnt.getTransformation())
		tweakGrp_grp.setTransformation(jnt.getTransformation())

		# parenting correct hierarchy
		pm.parent(top_grp, jnt.getParent())
		pm.parent(trsOs_grp, top_grp)
		pm.parent(trsBuffer_grp, trsOs_grp)
		pm.parent(osGrp_grp, trsBuffer_grp)
		pm.parent(tweakGrp_grp, osGrp_grp)
		pm.parent(jnt, tweakGrp_grp)

	def makeControlHierarchy(self, ctrl):
		# creating the necessary groups
		top_grp = pm.group(n = ctrl.replace("ctrl", "grp"), em = True)
		trsOs_grp = pm.group(n = ctrl.replace("ctrl", "trsOs"), em = True)
		trsBuffer_grp = pm.group(n = ctrl.replace("ctrl", "trsBuffer"), em = True)
		osGrp_grp = pm.group(n = ctrl.replace("ctrl", "osGrp"), em = True)

		# moving the groups to where they should be
		ctrl = self.makePyNode(ctrl)
		top_grp.setTransformation(ctrl.getTransformation())
		trsOs_grp.setTransformation(ctrl.getTransformation())
		trsBuffer_grp.setTransformation(ctrl.getTransformation())
		osGrp_grp.setTransformation(ctrl.getTransformation())

		# parenting correct hierarchy
		pm.parent(top_grp, ctrl.getParent())
		pm.parent(trsOs_grp, top_grp)
		pm.parent(trsBuffer_grp, trsOs_grp)
		pm.parent(osGrp_grp, trsBuffer_grp)
		pm.parent(ctrl, osGrp_grp)

	def makePyNode(self, node):
		pyNode = pm.PyNode(node)
		return pyNode

	def matrixConstraint(self, parent, child):
		"""a function that creates a matrix constraint to save the cost of a parent constraint. also maintains offset"""
		parent = str(parent)
		child = str(child)
		# creating the necessary nodes
		main_multMtx = pm.shadingNode("multMatrix", n = parent + "_" + child + "_multMtx", asUtility = True)
		main_decoMtx = pm.createNode("decomposeMatrix", n = parent + "_" + child + "_decoMtx")

		child_parentInverse_decoMtx = pm.createNode("decomposeMatrix", n = child + "_parentInverse_decoMtx")
		offset_decoMtx = pm.createNode("decomposeMatrix", n = parent + "_" + child + "_os_decoMtx")

		multMtx = pm.shadingNode("multMatrix", asUtility = True)

		# connecting stuff
		pm.connectAttr(child + ".worldMatrix[0]", multMtx + ".matrixIn[0]")
		pm.connectAttr(parent + ".worldInverseMatrix[0]", multMtx + ".matrixIn[1]")
		pm.connectAttr(multMtx + ".matrixSum", offset_decoMtx + ".inputMatrix")
		pm.disconnectAttr(offset_decoMtx + ".inputMatrix")
		pm.delete(multMtx)

		pm.connectAttr(child + ".parentInverseMatrix[0]", child_parentInverse_decoMtx + ".inputMatrix")
		pm.disconnectAttr(child_parentInverse_decoMtx + ".inputMatrix")

		pm.connectAttr(offset_decoMtx + ".inputMatrix", main_multMtx + ".matrixIn[0]")
		pm.connectAttr(parent + ".worldMatrix[0]", main_multMtx + ".matrixIn[1]")
		pm.connectAttr(child_parentInverse_decoMtx + ".inputMatrix", main_multMtx + ".matrixIn[2]")

		pm.connectAttr(main_multMtx + ".matrixSum", main_decoMtx + ".inputMatrix")

		pm.connectAttr(main_decoMtx + ".outputTranslate", child + ".translate")
		pm.connectAttr(main_decoMtx + ".outputRotate", child + ".rotate")
		pm.connectAttr(main_decoMtx + ".outputScale", child + ".scale")

		return main_decoMtx

	def calculateAveragePos(self, pos1, pos2):
		""" a function to calculate the position between two points"""
		pos1X, pos1Y, pos1Z = pos1
		pos2X, pos2Y, pos2Z = pos2

		newPosX = (pos1X + pos2X) / 2
		newPosY = (pos1Y + pos2Y) / 2
		newPosZ = (pos1Z + pos2Z) / 2

		newPos = [newPosX, newPosY, newPosZ]

		return newPos

	def jntsFollowMainCtrl(self, index, sub, ctrl, main_jnt, jnt_list):
		for i in range(index):
			x = 1 - (sub * i)
			md_node = pm.shadingNode("multiplyDivide", asUtility = True)
			pm.connectAttr(ctrl + ".translate", md_node + ".input1")
			for letter in "XYZ":
				pm.setAttr(md_node + ".input2" + letter, x)
			if i == 0:
				pm.connectAttr(md_node + ".output", main_jnt.getParent().getParent() + ".translate", f = True)
			else:
				right_grp = jnt_list[index - 1 - i].getParent().getParent()
				left_grp = jnt_list[index - 1 + i].getParent().getParent()
				pm.connectAttr(md_node + ".output", right_grp + ".translate", f = True)
				pm.connectAttr(md_node + ".output", left_grp + ".translate", f = True)

	def jntsFollowTweakCtrl(self, indexRange, sub, index ,ctrl, main_jnt, jnt_list):
		for i in range(indexRange):
			x = 1 - (sub * i)
			md_node = pm.shadingNode("multiplyDivide", asUtility = True)
			pm.connectAttr(ctrl + ".translate", md_node + ".input1")
			for letter in "XYZ":
				pm.setAttr(md_node + ".input2" + letter, x)
			if i == 0:
				pm.connectAttr(md_node + ".output", main_jnt.getParent() + ".translate")
			else:
				right_grp = jnt_list[index - 1 - i].getParent()
				left_grp = jnt_list[index - 1 + i].getParent()
				pm.connectAttr(md_node + ".output", right_grp + ".translate")
				pm.connectAttr(md_node + ".output", left_grp + ".translate")

	def cornerJntsFollowTweakCtrl(self, ctrl, jnt_list, inverse = False):
		md_node_main_up = pm.shadingNode("multiplyDivide", asUtility = True)
		pm.connectAttr(ctrl + ".translate", md_node_main_up + ".input1")
		pm.connectAttr(md_node_main_up + ".output", jnt_list[0].getParent() + ".translate")

		md_node_main_down = pm.shadingNode("multiplyDivide", asUtility = True)
		pm.connectAttr(ctrl + ".translate", md_node_main_down + ".input1")
		for letter in "XYZ":
			if letter == "Z":
				pm.setAttr(md_node_main_down + ".input2" + letter, 1)
			else:
				pm.setAttr(md_node_main_down + ".input2" + letter, -1)
		pm.connectAttr(md_node_main_down + ".output", jnt_list[-1].getParent() + ".translate")

		md_node_up = pm.shadingNode("multiplyDivide", asUtility = True)
		pm.connectAttr(ctrl + ".translate", md_node_up + ".input1")
		for letter in "XYZ":
			pm.setAttr(md_node_up + ".input2" + letter, 0.5)
		pm.connectAttr(md_node_up + ".output", jnt_list[1].getParent() + ".translate")

		md_node_down = pm.shadingNode("multiplyDivide", asUtility = True)
		pm.connectAttr(ctrl + ".translate", md_node_down + ".input1")
		for letter in "XYZ":
			if letter == "Z":
				pm.setAttr(md_node_down + ".input2" + letter, 0.5)
			else:
				pm.setAttr(md_node_down + ".input2" + letter, -0.5)
		pm.connectAttr(md_node_down + ".output", jnt_list[-2].getParent() + ".translate")

		if inverse == True:
			md_nodes_list = [md_node_main_up, md_node_main_down, md_node_up, md_node_down]
			for md_node in md_nodes_list:
				for letter in "XZ":
					md_node.setAttr("input2" + letter, (md_node.getAttr("input2" + letter) * -1))

	def cornerJntsFollowMainCtrl(self, indexRange, sub, ctrl, upper_jnt_list, lower_jnt_list, inverse = False):
		md_nodes_list = []
		for i in range(indexRange):
			x = 1 - (sub * i)
			md_node_up = pm.shadingNode("multiplyDivide", asUtility = True)
			pm.connectAttr(ctrl + ".translate", md_node_up + ".input1")
			for letter in "XYZ":
				pm.setAttr(md_node_up + ".input2" + letter, x)
			pm.connectAttr(md_node_up + ".output", upper_jnt_list[i].getParent().getParent().getParent() + ".translate")
			md_nodes_list.append(md_node_up)

			md_node_down = pm.shadingNode("multiplyDivide", asUtility = True)
			pm.connectAttr(ctrl + ".translate", md_node_down + ".input1")
			for letter in "XYZ":
				if letter == "Z":
					pm.setAttr(md_node_down + ".input2" + letter, (x * 1))
				else:
					pm.setAttr(md_node_down + ".input2" + letter, (x * -1))
			pm.connectAttr(md_node_down + ".output", lower_jnt_list[i].getParent().getParent().getParent() + ".translate")
			md_nodes_list.append(md_node_down)

		if inverse == True:
			for md_node in md_nodes_list:
				for letter in "XZ":
					md_node.setAttr("input2" + letter, (md_node.getAttr("input2" + letter) * -1))

	def blendMatrices(self, parentStart, parentEnd, child, envelope):
		"""a function to blend between two matrix constraints"""
		# creating the matrix constraints and breaking the connections
		parentStart_decoMtx_node = self.matrixConstraint(parent = parentStart, child = child)
		self.breakConnections(node = child)
		parentEnd_decoMtx_node = self.matrixConstraint(parent = parentEnd, child = child)
		self.breakConnections(node = child)
		# blending
		blendMtx_node = pm.createNode("blendMatrix", n = child + "_blendMtx")
		pm.connectAttr(parentStart_decoMtx_node + ".inputMatrix", blendMtx_node + ".target[0].targetMatrix")
		pm.connectAttr(parentEnd_decoMtx_node + ".inputMatrix", blendMtx_node + ".target[1].targetMatrix")
		pm.connectAttr(envelope, blendMtx_node + ".envelope")
		# connecting the blend
		main_decoMtx = pm.createNode("decomposeMatrix", n = child + "_decoMtx")
		pm.connectAttr(blendMtx_node + ".outputMatrix", main_decoMtx + ".inputMatrix")
		pm.connectAttr(main_decoMtx + ".outputTranslate", child + ".translate")
		pm.connectAttr(main_decoMtx + ".outputRotate", child + ".rotate")
		pm.connectAttr(main_decoMtx + ".outputScale", child + ".scale")

		return main_decoMtx

	def breakConnections(self, node, connections = ["translate", "rotate", "scale"]):
		"""a function that is used to break the connections of a certain node (as CBdeleteConnections doesn't work for some reason)"""
		for attr in connections:
			pm.disconnectAttr(node + "." + attr)

	def transferDecoMtx(self, decoMtx, node):
		"""mostly for the occasion when there is a need to transfer the decoMtx nodes from the joints to their ctrls to follow properly"""
		pm.connectAttr(decoMtx + ".outputTranslate", node + ".translate")
		pm.connectAttr(decoMtx + ".outputRotate", node + ".rotate")
		pm.connectAttr(decoMtx + ".outputScale", node + ".scale")

	def parentConstraintBlender(self, parentStart, parentEnd, child, envelope):
		"""sadly the matrix system has failed me so moving on to parent constraints because giving up sucks"""
		# creating the necessary nodes and doing the actual parent constraint
		pc_node = pm.parentConstraint(parentStart, parentEnd, child, n = child + "_pc", mo = True)
		rev_node = pm.shadingNode("reverse", n = child + "_rev", asUtility = True)
		parentStart_pc = pc_node + "." + parentStart + "W0"
		parentEnd_pc = pc_node + "." + parentEnd + "W1"
		# making necessary connections
		pm.connectAttr(envelope, parentEnd_pc)
		pm.connectAttr(envelope, rev_node + ".inputX")
		pm.connectAttr(rev_node + ".outputX", parentStart_pc)
		return pc_node


if __name__ == "__main__":
	try:
		lips_setup.close()
		lips_setup.deleteLater()

	except:
		pass

	finally:
		lips_setup = LipsSetup()
		lips_setup.show()