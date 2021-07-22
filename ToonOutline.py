"""
This tool has been written by Eliran Magen.
it allows you to easily create a toon outline for your meshes.
works best with low-poly meshes and can be used with game-engines as well.
"""

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import logging

# creating a logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def maya_main_window():
	main_window_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class ToonOutline(QtWidgets.QDialog):
	def __init__(self, parent = maya_main_window()):
		super(ToonOutline, self).__init__(parent)

		self.setWindowTitle("Toon Outline")
		self.setMinimumSize(320, 200)
		self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint)

		self.create_actions()
		self.create_widgets()
		self.create_layouts()
		self.create_connections()

	def create_actions(self):
		self.about_action = QtWidgets.QAction("About", self)

	def create_widgets(self):
		self.menu_bar = QtWidgets.QMenuBar()
		self.help_menu = self.menu_bar.addMenu("Help")
		self.help_menu.addAction(self.about_action)

		self.selected_mesh_le = QtWidgets.QLineEdit()
		self.selected_mesh_btn = QtWidgets.QPushButton("<")
		self.selected_mesh_btn.setToolTip("Click to insert selected mesh")

		self.generate_btn = QtWidgets.QPushButton("Generate")
		self.generate_btn.setToolTip("Click to generate toon outline")

		self.thickness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		self.thickness_slider.setRange(0, 150)
		self.thickness_slider.setSingleStep(10)
		self.thickness_slider.setValue(30)
		self.thickness_sb = QtWidgets.QDoubleSpinBox()
		self.thickness_sb.setSingleStep(0.1)
		self.thickness_sb.setMinimum(0)
		self.thickness_sb.setValue(0.3)

		#self.color_box = QtWidgets.QColorDialog()
		self.color_box = QtWidgets.QComboBox()
		self.color_box.addItems(["Black", "White", "Red", "Green", "Blue", "Yellow"])

		self.isSkinned_cb = QtWidgets.QCheckBox("do skin")
		self.isSkinned_cb.setChecked(True)
		self.isSkinned_cb.setToolTip("Check True if your selected mesh is already skinned")
		self.topJntGrp_le = QtWidgets.QLineEdit("Top Joint Group")
		self.select_topJntGrp_btn = QtWidgets.QPushButton("<")
		self.select_topJntGrp_btn.setToolTip("Click to insert selected top joint group or node")

		self.apply_btn = QtWidgets.QPushButton("Apply")
		self.cancel_btn = QtWidgets.QPushButton("Cancel")


	def create_layouts(self):
		selected_mesh_layout = QtWidgets.QHBoxLayout()
		selected_mesh_layout.addWidget(self.selected_mesh_le)
		selected_mesh_layout.addWidget(self.selected_mesh_btn)

		thickness_layout = QtWidgets.QHBoxLayout()
		thickness_layout.addWidget(self.thickness_slider)
		thickness_layout.addWidget(self.thickness_sb)

		doSkin_layout = QtWidgets.QHBoxLayout()
		doSkin_layout.addWidget(self.topJntGrp_le)
		doSkin_layout.addWidget(self.select_topJntGrp_btn)

		form_layout = QtWidgets.QFormLayout()
		form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
		form_layout.addRow("Mesh:", selected_mesh_layout)
		form_layout.addRow("", self.generate_btn)
		form_layout.addRow("Thickness:", thickness_layout)
		form_layout.addRow("Outline Color:", self.color_box)
		form_layout.addRow("", self.isSkinned_cb)
		form_layout.addRow("", doSkin_layout)

		apply_cancel_layout = QtWidgets.QHBoxLayout()
		apply_cancel_layout.addWidget(self.apply_btn)
		apply_cancel_layout.addWidget(self.cancel_btn)

		main_layout = QtWidgets.QVBoxLayout(self)
		main_layout.setSpacing(2)
		main_layout.setMenuBar(self.menu_bar)
		main_layout.addLayout(form_layout)
		main_layout.addLayout(apply_cancel_layout)

	def create_connections(self):
		self.about_action.triggered.connect(self.about)

		self.selected_mesh_btn.clicked.connect(self.input_mesh)

		self.generate_btn.clicked.connect(self.generate_outline_mesh)

		self.thickness_slider.sliderReleased.connect(self.slide_thickness)
		self.thickness_sb.valueChanged.connect(self.input_thickness)

		self.color_box.activated.connect(self.assign_color)

		self.isSkinned_cb.toggled.connect(self.update_topJntGrp_visibility)
		self.select_topJntGrp_btn.clicked.connect(self.select_top_joint_group)

		self.apply_btn.clicked.connect(self.delete_history)
		self.cancel_btn.clicked.connect(self.close)

	def input_mesh(self):
		try:
			sel_mesh = cmds.ls(sl = True)
			if len(sel_mesh) < 1:
				om.MGlobal.displayWarning("Please select a mesh")
			elif len(sel_mesh) > 1:
				om.MGlobal.displayWarning("Please select only one mesh")
			else:
				sel_mesh = sel_mesh[0]
				self.selected_mesh_le.setText(sel_mesh)

		except:
			om.MGlobal.displayWarning("Please select a mesh")

	def generate_outline_mesh(self):
		# querrying the selected mesh
		sel_mesh = self.selected_mesh_le.text()

		if self.selected_mesh_le.text() == "":
			om.MGlobal.displayWarning("Please select a mesh")

		else:
			# duplicate the selected mesh
			duplicated_mesh = cmds.duplicate(n = "{0}_ToonOutline_geo".format(sel_mesh))
			duplicated_mesh = duplicated_mesh[0]

			# reversing the normals and deselecting the double-sided attribute
			cmds.polyNormal(duplicated_mesh, normalMode = 0, userNormalMode = 0, ch = True)
			cmds.setAttr("{0}.doubleSided".format(duplicated_mesh), 0)

			# creating and connecting the new shader
			if cmds.objExists("{0}_ToonOutline_SHD".format(sel_mesh)):
				cmds.delete("{0}_ToonOutline_SHD".format(sel_mesh))
			else:
				pass
			toon_outline_SHD = cmds.shadingNode("lambert", n = "{0}_ToonOutline_SHD".format(sel_mesh), asShader = True)
			toon_outline_SG = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, n = "{0}SG".format(toon_outline_SHD))
			cmds.connectAttr("{0}.outColor".format(toon_outline_SHD), "{0}.surfaceShader".format(toon_outline_SG), force = True)
			cmds.select(duplicated_mesh, replace = True)
			cmds.sets(edit = True, forceElement = toon_outline_SG)
			cmds.setAttr("{0}.color".format(toon_outline_SHD), 0, 0, 0, type = "double3")

			# creating the "thickness"
			toon_outline_PMV = cmds.polyMoveVertex(duplicated_mesh, ch = True)
			cmds.rename(toon_outline_PMV, "ToonOutline_PMV")
			cmds.select(cl = 1)
			thickness_value = self.thickness_sb.value()
			thickness_value = "-{0}".format(thickness_value)
			thickness_value = float(thickness_value)
			cmds.setAttr("ToonOutline_PMV.localTranslateZ", thickness_value)

	def slide_thickness(self):
		original_value = self.thickness_slider.value()
		original_value = float(original_value)
		new_value = original_value / 100
		self.thickness_sb.setValue(new_value)

	def input_thickness(self):
		original_value = self.thickness_sb.value()
		new_value = "-{0}".format(original_value)
		new_value = float(new_value)
		self.thickness_slider.setSliderPosition(int(original_value * 100))

		try:
			cmds.setAttr("ToonOutline_PMV.localTranslateZ", new_value)

		except:
			om.MGlobal.displayWarning("Please Generate")

	def assign_color(self, index):
		sel_mesh = self.selected_mesh_le.text()
		ToonOutline_SHD = "{0}_ToonOutline_SHD".format(sel_mesh)
		if index == 0:
			try:
				cmds.setAttr("{0}.color".format(ToonOutline_SHD), 0, 0, 0, type = "double3")
			except:
				om.MGlobal.displayWarning("Please Generate")

		if index == 1:
			try:
				cmds.setAttr("{0}.color".format(ToonOutline_SHD), 1, 1, 1, type = "double3")
			except:
				om.MGlobal.displayWarning("Please Generate")

		if index == 2:
			try:
				cmds.setAttr("{0}.color".format(ToonOutline_SHD), 1, 0, 0, type = "double3")
			except:
				om.MGlobal.displayWarning("Please Generate")

		if index == 3:
			try:
				cmds.setAttr("{0}.color".format(ToonOutline_SHD), 0, 1, 0, type = "double3")
			except:
				om.MGlobal.displayWarning("Please Generate")

		if index == 4:
			try:
				cmds.setAttr("{0}.color".format(ToonOutline_SHD), 0, 0, 1, type = "double3")
			except:
				om.MGlobal.displayWarning("Please Generate")

		if index == 5:
			try:
				cmds.setAttr("{0}.color".format(ToonOutline_SHD), 1, 1, 0, type = "double3")
			except:
				om.MGlobal.displayWarning("Please Generate")

	def update_topJntGrp_visibility(self, checked):
		self.topJntGrp_le.setVisible(checked)
		self.select_topJntGrp_btn.setVisible(checked)

	def select_top_joint_group(self):
		try:
			top_jnt_grp = cmds.ls(sl = 1)
			if len(top_jnt_grp) < 1:
				om.MGlobal.displayWarning("Please select a top joints group or node")
			elif len(top_jnt_grp) > 1:
				om.MGlobal.displayWarning("Please select only one top joints group or node")
			else:
				top_jnt_grp = top_jnt_grp[0]
				self.topJntGrp_le.setText(top_jnt_grp)

		except:
			om.MGlobal.displayWarning("Please select a valid top joints group or node")

	def delete_history(self):
		if self.selected_mesh_le.text() == "":
			om.MGlobal.displayWarning("Please select a mesh and generate")

		else:
			sel_mesh = "{0}_ToonOutline_geo".format(self.selected_mesh_le.text())
			cmds.delete(sel_mesh, ch = True)
			if self.isSkinned_cb.isChecked():
				try:
					top_jnt_grp = self.topJntGrp_le.text()
					cmds.select(top_jnt_grp, replace = True)
					cmds.select(hi = True, add = True)
					cmds.select("{0}_ToonOutline_geo".format(self.selected_mesh_le.text()), add = True)
					cmds.skinCluster(toSelectedBones = True, skinMethod = 0, bindMethod = 0)
					cmds.select(self.selected_mesh_le.text(), replace = True)
					cmds.select("{0}_ToonOutline_geo".format(self.selected_mesh_le.text()), add = True)
					cmds.copySkinWeights(noMirror = True, surfaceAssociation = "closestPoint", influenceAssociation = "closestJoint")
					cmds.select("{0}_ToonOutline_geo".format(self.selected_mesh_le.text()), add = True)
					mel.eval("removeUnusedInfluences;")
					toon_outline.close()

				except:
					om.MGlobal.displayWarning("Please select a valid top joints group or node")

			else:
				toon_outline.close()

			cmds.select(cl = True)

	def about(self):
		msg = QtWidgets.QMessageBox()
		msg.setIcon(QtWidgets.QMessageBox.Information)
		msg.setWindowTitle("About Toon Outline")
		msg.setText("This tool is used to create a simple toon outline\naround your object to give it a more cartoony look\n\nCreated by Eliran Magen")
		msg.exec_()


if __name__ == "__main__":
	try:
		toon_outline.close()
		toon_outline.deleteLater()

	except:
		pass

	finally:
		toon_outline = ToonOutline()
		toon_outline.show()