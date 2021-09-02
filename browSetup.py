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

class BrowSetup(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(BrowSetup, self).__init__(parent)

		self.setWindowTitle("Brow Setup")
		self.setMinimumSize(350, 150)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_widgets(self):
		self.side_l_rb = QtWidgets.QRadioButton("L")
		self.side_l_rb.setChecked(True)
		self.side_r_rb = QtWidgets.QRadioButton("R")
		self.sel_edge_le = QtWidgets.QLineEdit()
		self.sel_edge_btn = QtWidgets.QPushButton("<")
		self.head_jnt_le = QtWidgets.QLineEdit()
		self.head_jnt_btn = QtWidgets.QPushButton("<")
		self.setup_grp_le = QtWidgets.QLineEdit()
		self.setup_grp_btn = QtWidgets.QPushButton("<")
		self.create_btn = QtWidgets.QPushButton("Create")
		self.cancel_btn = QtWidgets.QPushButton("Cancel")

	def create_layouts(self):
		sides_layout = QtWidgets.QHBoxLayout()
		sides_layout.addWidget(self.side_l_rb)
		sides_layout.addWidget(self.side_r_rb)
		sides_layout.addStretch()

		sel_edge_layout = QtWidgets.QHBoxLayout()
		sel_edge_layout.addWidget(self.sel_edge_le)
		sel_edge_layout.addWidget(self.sel_edge_btn)

		head_jnt_layout = QtWidgets.QHBoxLayout()
		head_jnt_layout.addWidget(self.head_jnt_le)
		head_jnt_layout.addWidget(self.head_jnt_btn)

		setup_grp_layout = QtWidgets.QHBoxLayout()
		setup_grp_layout.addWidget(self.setup_grp_le)
		setup_grp_layout.addWidget(self.setup_grp_btn)

		insert_layout = QtWidgets.QFormLayout()
		insert_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
		insert_layout.addRow("Insert Edge: ", sel_edge_layout)
		insert_layout.addRow("Insert Head Joint: ", head_jnt_layout)
		insert_layout.addRow("Insert SETUP Group: ", setup_grp_layout)

		create_cancel_layout = QtWidgets.QHBoxLayout()
		create_cancel_layout.addWidget(self.create_btn)
		create_cancel_layout.addWidget(self.cancel_btn)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.addLayout(sides_layout)
		main_layout.addLayout(insert_layout)
		main_layout.addLayout(create_cancel_layout)

	def create_connections(self):
		self.sel_edge_btn.clicked.connect(self.selEgde)
		self.head_jnt_btn.clicked.connect(self.selHeadJnt)
		self.setup_grp_btn.clicked.connect(self.selSetupGrp)

		self.create_btn.clicked.connect(self.createBrows)
		self.cancel_btn.clicked.connect(self.close)

	def createBrows(self):
		#determine side
		if self.side_l_rb.isChecked():
			side = "l"
		if self.side_r_rb.isChecked():
			side = "r"

		head_jnt = pm.PyNode(self.head_jnt_le.text())
		setup_grp = pm.PyNode(self.setup_grp_le.text())

		# select the selected edges
		edges = self.sel_edge_le.text()
		edges = edges.split(", ")
		pm.select(cl = True)
		pm.select(edges, add = True)

		# creating the curve
		edges_crv = pm.polyToCurve(dg = 1, ch = False, usm = False, n = side + "_brow_crv")
		edges_crv = pm.PyNode(edges_crv[0])
		cv_range = edges_crv.getAttr("spans") + 1
		brow_crv = pm.rebuildCurve(edges_crv, d = 3, kcp = True, rpo = True, rt = 0, kr = 0, ch = False)[0]

		# creating joints
		cv_list = []
		jnt_list = []
		loc_list = []
		for i in range(cv_range):
			cv = pm.PyNode(brow_crv + ".cv[{0}]".format(i))
			pm.select(cl = True)
			jnt = pm.joint(n = side + "_brow_" + str(i) + "_jnt", rad = 0.3)
			pm.parent(jnt, head_jnt)
			jnt.setAttr("inheritsTransform", 0)
			loc = pm.spaceLocator(n = jnt.replace("jnt", "loc"))
			for axis in "XYZ":
				loc.setAttr("localScale" + axis, 0.3)
				pm.connectAttr(loc + ".rotate" + axis, jnt + ".rotate" + axis)
			loc_grp = self.createGroupAbove(node = loc)
			loc_grp.setTranslation(cv.getPosition())
			POCI_node = pm.shadingNode("pointOnCurveInfo", n = side + "_brow_POCI_" + str(i), asUtility = True)
			POCI_node.setAttr("turnOnPercentage", 1)
			parameterValue = i * (1.0 / float(cv_range - 1))
			POCI_node.setAttr("parameter", parameterValue)
			pm.connectAttr(brow_crv + ".worldSpace[0]", POCI_node + ".inputCurve")
			pm.connectAttr(POCI_node + ".position", jnt + ".translate")
			loc_decoMtx = pm.shadingNode("decomposeMatrix", n = loc + "_decoMtx", asUtility = True)
			pm.connectAttr(loc + ".worldMatrix[0]", loc_decoMtx + ".inputMatrix")
			pm.connectAttr(loc_decoMtx + ".outputTranslate", brow_crv + ".controlPoints[{0}]".format(i))
			cv_list.append(cv)
			jnt_list.append(jnt)
			loc_list.append(loc)

		# making the curve and the locators follow the head
		main_loc_grp = pm.group(n = side + "_brow_loc_grp", em = True)
		for loc in loc_list:
			loc_grp = loc.getParent()
			pm.parent(loc_grp, main_loc_grp)
		self.matrixConstraint(child = main_loc_grp, parent = head_jnt)

		# clean-up
		pm.parent(main_loc_grp, setup_grp)
		pm.parent(brow_crv, setup_grp)
		_logger.info("Built Succesfully")
		self.close()

	def selEgde(self):
		edges = pm.ls(sl = True, fl = True)
		if edges:
			self.sel_edge_le.setText("")
		for edge in edges:
			if edge == edges[-1]:
				self.sel_edge_le.setText(self.sel_edge_le.text() + edge.name())
			else:
				self.sel_edge_le.setText(self.sel_edge_le.text() + edge.name() + ", ")

	def selHeadJnt(self):
		head_jnt = pm.ls(sl = True)[0]
		self.head_jnt_le.setText(head_jnt.name())

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

	def createGroupAbove(self, node):
		node = pm.PyNode(node)
		grp = pm.group(n = node + "_osGrp", em = True)
		node_pos = pm.xform(node, q = True, ws = True, m = True)
		pm.xform(grp, ws = True, m = node_pos)
		pm.parent(grp, node.getParent())
		pm.parent(node, grp)
		return grp


if __name__ == "__main__":
	try:
		brow_setup.close()
		brow_setup.deleteLater()

	except:
		pass

	finally:
		brow_setup = BrowSetup()
		brow_setup.show()