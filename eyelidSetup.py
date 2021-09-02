### Created by Eliran Magen for a job with second floor studios ###

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

class EyelidSetup(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(EyelidSetup, self).__init__(parent)

		if (pm.selectPref(tso = True, q = True) == 0):
			pm.selectPref(tso = True)

		self.setWindowTitle("Eyelid Setup")
		self.setMinimumSize(350, 200)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_widgets(self):
		self.reverse_cb = QtWidgets.QCheckBox("Reverse")
		self.side_l_rb = QtWidgets.QRadioButton("L")
		self.side_l_rb.setChecked(True)
		self.side_r_rb = QtWidgets.QRadioButton("R")
		self.sel_upper_edge_le = QtWidgets.QLineEdit()
		self.sel_upper_edge_btn = QtWidgets.QPushButton("<")
		self.sel_lower_edge_le = QtWidgets.QLineEdit()
		self.sel_lower_edge_btn = QtWidgets.QPushButton("<")
		self.eye_jnt_le = QtWidgets.QLineEdit()
		self.eye_jnt_btn = QtWidgets.QPushButton("<")
		self.setup_grp_le = QtWidgets.QLineEdit()
		self.setup_grp_btn = QtWidgets.QPushButton("<")
		self.create_btn = QtWidgets.QPushButton("Create")
		self.cancel_btn = QtWidgets.QPushButton("Cancel")

	def create_layouts(self):
		sides_layout = QtWidgets.QHBoxLayout()
		sides_layout.addWidget(self.side_l_rb)
		sides_layout.addWidget(self.side_r_rb)
		sides_layout.addStretch()

		sel_upper_edge_layout = QtWidgets.QHBoxLayout()
		sel_upper_edge_layout.addWidget(self.sel_upper_edge_le)
		sel_upper_edge_layout.addWidget(self.sel_upper_edge_btn)

		sel_lower_edge_layout = QtWidgets.QHBoxLayout()
		sel_lower_edge_layout.addWidget(self.sel_lower_edge_le)
		sel_lower_edge_layout.addWidget(self.sel_lower_edge_btn)

		eye_jnt_layout = QtWidgets.QHBoxLayout()
		eye_jnt_layout.addWidget(self.eye_jnt_le)
		eye_jnt_layout.addWidget(self.eye_jnt_btn)

		setup_grp_layout = QtWidgets.QHBoxLayout()
		setup_grp_layout.addWidget(self.setup_grp_le)
		setup_grp_layout.addWidget(self.setup_grp_btn)

		insert_layout = QtWidgets.QFormLayout()
		insert_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
		insert_layout.addRow("Insert Upper Edge: ", sel_upper_edge_layout)
		insert_layout.addRow("Insert Lower Edge: ", sel_lower_edge_layout)
		insert_layout.addRow("Insert Eye Joint: ", eye_jnt_layout)
		insert_layout.addRow("Insert SETUP Group: ", setup_grp_layout)

		create_cancel_layout = QtWidgets.QHBoxLayout()
		create_cancel_layout.addWidget(self.create_btn)
		create_cancel_layout.addWidget(self.cancel_btn)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addWidget(self.reverse_cb)
		main_layout.addLayout(sides_layout)
		main_layout.addLayout(insert_layout)
		main_layout.addLayout(create_cancel_layout)

	def create_connections(self):
		self.sel_upper_edge_btn.clicked.connect(self.selUpperEgde)
		self.sel_lower_edge_btn.clicked.connect(self.selLowerEgde)
		self.eye_jnt_btn.clicked.connect(self.selEyeJnt)
		self.setup_grp_btn.clicked.connect(self.selSetupGrp)

		self.create_btn.clicked.connect(self.createEyelids)
		self.cancel_btn.clicked.connect(self.close)

	def createEyelids(self):
		#determine side
		if self.side_l_rb.isChecked():
			side = "l"
		if self.side_r_rb.isChecked():
			side = "r"

		eye_jnt = pm.PyNode(self.eye_jnt_le.text())
		setup_grp = pm.PyNode(self.setup_grp_le.text())

		# select the selected upper edges
		upper_edges = self.sel_upper_edge_le.text()
		upper_edges = upper_edges.split(", ")
		pm.select(cl = True)
		pm.select(upper_edges, add = True)

		# creating the upper curve
		upper_edges_crv = pm.polyToCurve(n = side + "_upper_eyelid_crv", dg = 1, ch = False, usm = False)
		upper_edges_crv = pm.PyNode(upper_edges_crv[0])
		upper_cv_range = upper_edges_crv.getAttr("spans") + 1
		upper_eyelid_crv = pm.rebuildCurve(upper_edges_crv, d = 1, kcp = True, rpo = True, rt = 0, kr = 0, ch = False)[0]

		# select the selected lower edges
		lower_edges = self.sel_lower_edge_le.text()
		lower_edges = lower_edges.split(", ")
		pm.select(cl = True)
		pm.select(lower_edges, add = True)

		# creating the lower curve
		lower_edges_crv = pm.polyToCurve(n = side + "_lower_eyelid_crv", dg = 1, ch = False, usm = False)
		lower_edges_crv = pm.PyNode(lower_edges_crv[0])
		if self.reverse_cb.isChecked():
			pm.reverseCurve(lower_edges_crv, rpo = True, ch = False)
		lower_cv_range = lower_edges_crv.getAttr("spans") + 1
		lower_eyelid_crv = pm.rebuildCurve(lower_edges_crv, d = 1, kcp = True, rpo = True, rt = 0, kr = 0, ch = False)[0]

		# creating upper curve setup
		upper_cv_list = []
		upper_jnt_list = []
		upper_loc_list = []
		main_loc_grp = pm.group(n = side + "_eyelid_main_loc_grp", em = True)
		for i in range(upper_cv_range):
			cv = pm.PyNode(upper_eyelid_crv + ".cv[{0}]".format(i))
			pm.select(cl = True)
			parent_jnt = pm.joint(n = side + "_upper_eyelid_0_" + str(i) + "_jnt", rad = 0.5)
			pm.matchTransform(parent_jnt, eye_jnt)
			pm.parent(parent_jnt, eye_jnt)
			pm.select(cl = True)
			child_jnt = pm.joint(n = side + "_upper_eyelid_1_" + str(i) + "_jnt", rad = 0.1)
			pm.parent(child_jnt, parent_jnt)
			child_jnt.setAttr("inheritsTransform", 0)
			loc = pm.spaceLocator(n = child_jnt.replace("jnt", "loc"))
			for axis in "XYZ":
				loc.setAttr("localScale" + axis, 0.3)
			loc_blinkHeight_grp = self.createGroupAbove(node = loc, grpName = loc + "_blinkHeight_grp")
			loc_blink_grp = self.createGroupAbove(node = loc, grpName = loc + "_blink_grp")
			loc_blink_grp.setAttr("inheritsTransform", 0)
			loc_blinkHeight_grp.setTranslation(cv.getPosition())
			pm.parentConstraint(parent_jnt, loc_blinkHeight_grp, mo = True, w = 1)
			POCI_node = pm.shadingNode("pointOnCurveInfo", n = side + "_upper_eyelid_POCI_" + str(i), asUtility = True)
			POCI_node.setAttr("turnOnPercentage", 1)
			parameterValue = i * (1.0 / float(upper_cv_range - 1))
			POCI_node.setAttr("parameter", parameterValue)
			pm.connectAttr(upper_eyelid_crv + ".worldSpace[0]", POCI_node + ".inputCurve")
			pm.connectAttr(POCI_node + ".position", child_jnt + ".translate")
			loc_decoMtx = pm.shadingNode("decomposeMatrix", n = loc + "_decoMtx", asUtility = True)
			pm.connectAttr(loc + ".worldMatrix[0]", loc_decoMtx + ".inputMatrix")
			pm.connectAttr(loc_decoMtx + ".outputTranslate", upper_eyelid_crv + ".controlPoints[{0}]".format(i))
			pm.parent(loc_blinkHeight_grp, main_loc_grp)
			upper_cv_list.append(cv)
			upper_jnt_list.append(child_jnt)
			upper_loc_list.append(loc)

		# creating the lower curve setup
		lower_cv_list = []
		lower_jnt_list = []
		lower_loc_list = []
		for i in range(lower_cv_range):
			cv = pm.PyNode(lower_eyelid_crv + ".cv[{0}]".format(i))
			pm.select(cl = True)
			parent_jnt = pm.joint(n = side + "_lower_eyelid_0_" + str(i) + "_jnt", rad = 0.5)
			pm.matchTransform(parent_jnt, eye_jnt)
			pm.parent(parent_jnt, eye_jnt)
			pm.select(cl = True)
			child_jnt = pm.joint(n = side + "_lower_eyelid_1_" + str(i) + "_jnt", rad = 0.1)
			pm.parent(child_jnt, parent_jnt)
			child_jnt.setAttr("inheritsTransform", 0)
			loc = pm.spaceLocator(n = child_jnt.replace("jnt", "loc"))
			for axis in "XYZ":
				loc.setAttr("localScale" + axis, 0.3)
			loc_blinkHeight_grp = self.createGroupAbove(node = loc, grpName = loc + "_blinkHeight_grp")
			loc_blink_grp = self.createGroupAbove(node = loc, grpName = loc + "_blink_grp")
			loc_blink_grp.setAttr("inheritsTransform", 0)
			loc_blinkHeight_grp.setTranslation(cv.getPosition())
			pm.parentConstraint(parent_jnt, loc_blinkHeight_grp, mo = True, w = 1)
			POCI_node = pm.shadingNode("pointOnCurveInfo", n = side + "_lower_eyelid_POCI_" + str(i), asUtility = True)
			POCI_node.setAttr("turnOnPercentage", 1)
			parameterValue = i * (1.0 / float(lower_cv_range - 1))
			POCI_node.setAttr("parameter", parameterValue)
			pm.connectAttr(lower_eyelid_crv + ".worldSpace[0]", POCI_node + ".inputCurve")
			pm.connectAttr(POCI_node + ".position", child_jnt + ".translate")
			loc_decoMtx = pm.shadingNode("decomposeMatrix", n = loc + "_decoMtx", asUtility = True)
			pm.connectAttr(loc + ".worldMatrix[0]", loc_decoMtx + ".inputMatrix")
			pm.connectAttr(loc_decoMtx + ".outputTranslate", lower_eyelid_crv + ".controlPoints[{0}]".format(i))
			pm.parent(loc_blinkHeight_grp, main_loc_grp)
			pm.select(cl = True)
			lower_cv_list.append(cv)
			lower_jnt_list.append(child_jnt)
			lower_loc_list.append(loc)

		# setup that requires both up and down
		if upper_cv_range != lower_cv_range:
			pm.error("must select the same number of vertices up and down")
		else:
			if setup_grp.hasAttr("blinkHeight"):
				blink_height = setup_grp + ".blinkHeight"
				blink = setup_grp + ".blink"
			else:
				setup_grp.addAttr("eyelids", at = "enum", en = "----------", k = False)
				setup_grp.setAttr("eyelids", e = True, cb = True)
				setup_grp.addAttr("blinkHeight", at = "float", min = 0, max = 1.0, dv = 0.5, k = True)
				setup_grp.addAttr("blink", at = "float", min = 0, max = 1.0, dv = 0, k = True)
				blink_height = setup_grp + ".blinkHeight"
				blink = setup_grp + ".blink"
			mid_loc_list = []
			mid_loc_grp = pm.group(n = side + "_eyelid_mid_loc_grp", em = True)
			for i in range(upper_cv_range):
				mid_loc = pm.spaceLocator(n = side + "_mid_" + str(i) + "_loc")
				mid_loc.setAttr("visibility", 0)
				upper_loc = upper_loc_list[i]
				lower_loc = lower_loc_list[i]
				upper_loc_blinkHeight_grp = upper_loc.getParent().getParent()
				lower_loc_blinkHeight_grp = lower_loc.getParent().getParent()
				upper_loc_blink_grp = upper_loc.getParent()
				lower_loc_blink_grp = lower_loc.getParent()
				blink_height_mtx = self.blendWorldMatrices(parentStart = upper_loc_blinkHeight_grp, parentEnd = lower_loc_blinkHeight_grp, child = mid_loc, envelope = blink_height)
				self.parentConstraintBlender(parentStart = upper_loc_blinkHeight_grp, parentEnd = mid_loc, child = upper_loc_blink_grp, envelope = blink)
				self.parentConstraintBlender(parentStart = lower_loc_blinkHeight_grp, parentEnd = mid_loc, child = lower_loc_blink_grp, envelope = blink)
				pm.parent(mid_loc, mid_loc_grp)
				mid_loc_list.append(mid_loc)

		## eye aim
		# creating the eye aim joint
		eyeAim_jnt = pm.duplicate(eye_jnt, po = True, n = eye_jnt.replace("eye", "eyeAim"))[0]
		eyeAim_jnt.setAttr("radius", 0.3)
		pm.parent(eyeAim_jnt, eye_jnt)

		# creating the aim locator
		eyeAim_loc = pm.spaceLocator(n = eyeAim_jnt.replace("jnt", "loc"))
		eyeAim_loc.setTranslation(eyeAim_jnt.getTranslation("world"))
		eyeAim_loc.setAttr("tz", eyeAim_loc.getAttr("tz") + 15)
		pm.makeIdentity(eyeAim_loc, a = True)
		pm.aimConstraint(eyeAim_loc, eyeAim_jnt, mo = True, w = 1, aimVector = [0, 0, 1], upVector = [0, 1, 0], worldUpType = "vector", worldUpVector = [0, 1, 0])

		# clean-up
		pm.parent(main_loc_grp, setup_grp)
		pm.parent(mid_loc_grp, setup_grp)
		pm.parent(upper_eyelid_crv, setup_grp)
		pm.parent(lower_eyelid_crv, setup_grp)
		_logger.info("Built Succesfully")
		self.close()

	def selUpperEgde(self):
		edges = pm.ls(os = True, fl = True)
		if edges:
			self.sel_upper_edge_le.setText("")
		for edge in edges:
			if edge == edges[-1]:
				self.sel_upper_edge_le.setText(self.sel_upper_edge_le.text() + edge.name())
			else:
				self.sel_upper_edge_le.setText(self.sel_upper_edge_le.text() + edge.name() + ", ")

	def selLowerEgde(self):
		edges = pm.ls(os = True, fl = True)
		if edges:
			self.sel_lower_edge_le.setText("")
		for edge in edges:
			if edge == edges[-1]:
				self.sel_lower_edge_le.setText(self.sel_lower_edge_le.text() + edge.name())
			else:
				self.sel_lower_edge_le.setText(self.sel_lower_edge_le.text() + edge.name() + ", ")

	def selEyeJnt(self):
		eye_jnt = pm.ls(sl = True)[0]
		self.eye_jnt_le.setText(eye_jnt.name())

	def selSetupGrp(self):
		setup_grp = pm.ls(sl = True)[0]
		self.setup_grp_le.setText(setup_grp.name())

	def matrixConstraint(self, parent, child, t = True, r = True, s = True):
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

		if t == True:
			pm.connectAttr(main_decoMtx + ".outputTranslate", child + ".translate")
		if r == True:
			pm.connectAttr(main_decoMtx + ".outputRotate", child + ".rotate")
		if s == True:
			pm.connectAttr(main_decoMtx + ".outputScale", child + ".scale")

		return main_decoMtx

	def blendWorldMatrices(self, parentStart, parentEnd, child, envelope):
		"""a function to blend between two world matrices"""
		blend_mtx = pm.shadingNode("blendMatrix", n = parentStart + "_" + parentEnd + "blendMtx", asUtility = True)
		deco_mtx = pm.shadingNode("decomposeMatrix", n = blend_mtx.replace("blendMtx", "decoMtx"), asUtility = True)
		pm.connectAttr(parentStart + ".worldMatrix[0]", blend_mtx + ".inputMatrix")
		pm.connectAttr(parentEnd + ".worldMatrix[0]", blend_mtx + ".target[0].targetMatrix")
		pm.connectAttr(envelope, blend_mtx + ".envelope")
		pm.connectAttr(blend_mtx + ".outputMatrix", deco_mtx + ".inputMatrix")
		pm.connectAttr(deco_mtx + ".outputTranslate", child + ".translate")
		return blend_mtx

	def parentConstraintBlender(self, parentStart, parentEnd, child, envelope):
		"""a function to blend between two parent constraints"""
		# creating the necessary nodes and doing the actual parent constraint
		pc_node = pm.parentConstraint(parentStart, parentEnd, child, n = child + "_pc", mo = False)
		rev_node = pm.shadingNode("reverse", n = child + "_rev", asUtility = True)
		parentStart_pc = pc_node + "." + parentStart + "W0"
		parentEnd_pc = pc_node + "." + parentEnd + "W1"
		# making necessary connections
		pm.connectAttr(envelope, parentEnd_pc)
		pm.connectAttr(envelope, rev_node + ".inputX")
		pm.connectAttr(rev_node + ".outputX", parentStart_pc)
		return pc_node

	def createGroupAbove(self, node, grpName = "_osGrp"):
		node = pm.PyNode(node)
		grp = pm.group(n = node + grpName, em = True)
		node_pos = pm.xform(node, q = True, ws = True, m = True)
		pm.xform(grp, ws = True, m = node_pos)
		pm.parent(grp, node.getParent())
		pm.parent(node, grp)
		return grp


if __name__ == "__main__":
	try:
		eyelid_setup.close()
		eyelid_setup.deleteLater()

	except:
		pass

	finally:
		eyelid_setup = EyelidSetup()
		eyelid_setup.show()