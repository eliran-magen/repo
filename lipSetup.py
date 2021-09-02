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

class LipSetup(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(LipSetup, self).__init__(parent)

		if (pm.selectPref(tso = True, q = True) == 0):
			pm.selectPref(tso = True)

		self.setWindowTitle("Lip Setup")
		self.setMinimumSize(350, 200)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_widgets(self):
		self.reverse_cb = QtWidgets.QCheckBox("Reverse")
		self.sel_upper_edge_le = QtWidgets.QLineEdit()
		self.sel_upper_edge_btn = QtWidgets.QPushButton("<")
		self.sel_lower_edge_le = QtWidgets.QLineEdit()
		self.sel_lower_edge_btn = QtWidgets.QPushButton("<")
		self.jaw_jnt_le = QtWidgets.QLineEdit()
		self.jaw_jnt_btn = QtWidgets.QPushButton("<")
		self.setup_grp_le = QtWidgets.QLineEdit()
		self.setup_grp_btn = QtWidgets.QPushButton("<")
		self.create_btn = QtWidgets.QPushButton("Create")
		self.cancel_btn = QtWidgets.QPushButton("Cancel")

	def create_layouts(self):
		sel_upper_edge_layout = QtWidgets.QHBoxLayout()
		sel_upper_edge_layout.addWidget(self.sel_upper_edge_le)
		sel_upper_edge_layout.addWidget(self.sel_upper_edge_btn)

		sel_lower_edge_layout = QtWidgets.QHBoxLayout()
		sel_lower_edge_layout.addWidget(self.sel_lower_edge_le)
		sel_lower_edge_layout.addWidget(self.sel_lower_edge_btn)

		jaw_jnt_layout = QtWidgets.QHBoxLayout()
		jaw_jnt_layout.addWidget(self.jaw_jnt_le)
		jaw_jnt_layout.addWidget(self.jaw_jnt_btn)

		setup_grp_layout = QtWidgets.QHBoxLayout()
		setup_grp_layout.addWidget(self.setup_grp_le)
		setup_grp_layout.addWidget(self.setup_grp_btn)

		insert_layout = QtWidgets.QFormLayout()
		insert_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
		insert_layout.addRow("Insert Upper Edge: ", sel_upper_edge_layout)
		insert_layout.addRow("Insert Lower Edge: ", sel_lower_edge_layout)
		insert_layout.addRow("Insert jaw Joint: ", jaw_jnt_layout)
		insert_layout.addRow("Insert SETUP Group: ", setup_grp_layout)

		create_cancel_layout = QtWidgets.QHBoxLayout()
		create_cancel_layout.addWidget(self.create_btn)
		create_cancel_layout.addWidget(self.cancel_btn)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addWidget(self.reverse_cb)
		main_layout.addLayout(insert_layout)
		main_layout.addLayout(create_cancel_layout)

	def create_connections(self):
		self.sel_upper_edge_btn.clicked.connect(self.selUpperEgde)
		self.sel_lower_edge_btn.clicked.connect(self.selLowerEgde)
		self.jaw_jnt_btn.clicked.connect(self.selJawJnt)
		self.setup_grp_btn.clicked.connect(self.selSetupGrp)

		self.create_btn.clicked.connect(self.createLips)
		self.cancel_btn.clicked.connect(self.close)

	def createLips(self):
		jaw_jnt = pm.PyNode(self.jaw_jnt_le.text())
		head_jnt = pm.PyNode(jaw_jnt.getParent())
		setup_grp = pm.PyNode(self.setup_grp_le.text())

		# select the selected upper edges
		upper_edges = self.sel_upper_edge_le.text()
		upper_edges = upper_edges.split(", ")
		pm.select(cl = True)
		pm.select(upper_edges, add = True)

		# creating the upper curve
		upper_lip_crv = pm.polyToCurve(n = "c_upper_lip_crv", dg = 1, ch = False, usm = False)
		upper_lip_crv = pm.PyNode(upper_lip_crv[0])
		upper_cv_range = upper_lip_crv.getAttr("spans") + 1

		# select the selected lower edges
		lower_edges = self.sel_lower_edge_le.text()
		lower_edges = lower_edges.split(", ")
		pm.select(cl = True)
		pm.select(lower_edges, add = True)

		# creating the lower curve
		lower_lip_crv = pm.polyToCurve(n = "c_lower_lip_crv", dg = 1, ch = False, usm = False)
		lower_lip_crv = pm.PyNode(lower_lip_crv[0])
		if self.reverse_cb.isChecked():
			pm.reverseCurve(lower_lip_crv, rpo = True, ch = False)
		lower_cv_range = lower_lip_crv.getAttr("spans") + 1

		# creating upper curve setup
		upper_cv_list = []
		upper_jnt_list = []
		upper_loc_list = []
		follow_value = 1.0 / float(upper_lip_crv.getAttr("spans"))
		r = 2
		main_loc_grp = pm.group(n = "c_lips_main_loc_grp", em = True)
		for i in range(upper_cv_range):
			cv = pm.PyNode(upper_lip_crv + ".cv[{0}]".format(i))
			pm.select(cl = True)
			jnt = pm.joint(n = "c_upper_lip_" + str(i) + "_jnt", rad = 0.2)
			pm.parent(jnt, jaw_jnt)
			jnt.setAttr("inheritsTransform", 0)
			loc = pm.spaceLocator(n = jnt.replace("jnt", "loc"))
			for axis in "XYZ":
				loc.setAttr("localScale" + axis, 0.3)
			loc_os_grp = self.createGroupAbove(node = loc)
			loc_buffer_grp = self.createGroupAbove(node = loc, grpName = "_bufferGrp")
			loc_os_grp.setTranslation(cv.getPosition())
			pm.parentConstraint(loc, jnt, mo = False, w = 1)
			if i <= (upper_lip_crv.getAttr("spans") / 2):
				follow_amount = (float(follow_value) * float(i)) + 0.5
			else:
				follow_amount = (float(follow_value) * float(i - r)) + 0.5
				r += 2
			float_constant_node = pm.shadingNode("floatConstant", n = jnt + "_floatConst", asUtility = True)
			float_constant_node.setAttr("inFloat", follow_amount)
			self.parentConstraintBlender(parentStart = jaw_jnt, parentEnd = head_jnt, child = loc_os_grp, envelope = float_constant_node + ".outFloat", mo = True)
			pm.parent(loc_os_grp, main_loc_grp)
			upper_cv_list.append(cv)
			upper_jnt_list.append(jnt)
			upper_loc_list.append(loc)

		# creating lower curve setup
		lower_cv_list = []
		lower_jnt_list = []
		lower_loc_list = []
		follow_value = 1.0 / float(lower_lip_crv.getAttr("spans"))
		r = 2
		for i in range(lower_cv_range):
			cv = pm.PyNode(lower_lip_crv + ".cv[{0}]".format(i))
			pm.select(cl = True)
			jnt = pm.joint(n = "c_lower_lip_" + str(i) + "_jnt", rad = 0.2)
			pm.parent(jnt, jaw_jnt)
			jnt.setAttr("inheritsTransform", 0)
			loc = pm.spaceLocator(n = jnt.replace("jnt", "loc"))
			for axis in "XYZ":
				loc.setAttr("localScale" + axis, 0.3)
			loc_os_grp = self.createGroupAbove(node = loc)
			loc_buffer_grp = self.createGroupAbove(node = loc, grpName = "_bufferGrp")
			loc_os_grp.setTranslation(cv.getPosition())
			pm.parentConstraint(loc, jnt, mo = False, w = 1)
			if i <= (lower_lip_crv.getAttr("spans") / 2):
				follow_amount = (follow_value * i) + 0.5
			else:
				follow_amount = (follow_value * (i - r)) + 0.5
				r += 2
			float_constant_node = pm.shadingNode("floatConstant", n = jnt + "_floatConst", asUtility = True)
			float_constant_node.setAttr("inFloat", follow_amount)
			self.parentConstraintBlender(parentStart = head_jnt, parentEnd = jaw_jnt, child = loc_os_grp, envelope = float_constant_node + ".outFloat", mo = True)
			pm.parent(loc_os_grp, main_loc_grp)
			lower_cv_list.append(cv)
			lower_jnt_list.append(jnt)
			lower_loc_list.append(loc)

		# clean-up
		pm.parent(main_loc_grp, setup_grp)
		pm.delete(upper_lip_crv)
		pm.delete(lower_lip_crv)
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

	def selJawJnt(self):
		jaw_jnt = pm.ls(sl = True)[0]
		self.jaw_jnt_le.setText(jaw_jnt.name())

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

	def parentConstraintBlender(self, parentStart, parentEnd, child, envelope, mo = False):
		"""a function to blend between two parent constraints"""
		# creating the necessary nodes and doing the actual parent constraint
		parentStart = pm.PyNode(parentStart)
		parentEnd = pm.PyNode(parentEnd)
		pc_node = pm.parentConstraint(parentStart, parentEnd, child, n = child + "_pc", mo = mo)
		rev_node = pm.shadingNode("reverse", n = child + "_rev", asUtility = True)
		parentStart_pc = pc_node + "." + parentStart.stripNamespace() + "W0"
		parentEnd_pc = pc_node + "." + parentEnd.stripNamespace() + "W1"
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
		lip_setup.close()
		lip_setup.deleteLater()

	except:
		pass

	finally:
		lip_setup = LipSetup()
		lip_setup.show()