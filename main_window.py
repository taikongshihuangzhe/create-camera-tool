import os
import pymel.core as pm
import copy
import math
from PySide import QtCore, QtGui
from pyside_utils import loadUiType
from data import Data

form_class, base_class = loadUiType(os.path.join(os.path.dirname(__file__), 'create_camera.ui'))
lock_icon = QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'pics', 'lock.png'))

class ProtectedData:
    """A Wrapper class used to prevent PySide from automatically converting
     OrderedDict to python dict."""
    def __init__(self, ord_dict):
        self.data = ord_dict

    def get(self):
        return self.data


class createCameraWindow(base_class, form_class):
    """UI Window Object."""
    green = QtGui.QBrush(QtGui.QColor(0, 255, 0))
    genericLens = False
    Generic_lens = ProtectedData({'name': 'Generic', 'focal_length_sets':['Custom'], 'anamorphic': False})
    def __init__(self, parent=None):
        super(createCameraWindow, self).__init__(parent)
        self.setupUi(self)
        self.initUi()
        self.manufacturer = None
        self.model = None
        self.setting = None
        self.film_back = None
        self.img_res = None
        self.lens = None
        self.focal_length = None

    def initUi(self):
        """Initialize UI."""
        self.data_sheet = Data()
        self.data_sheet.load_yaml()
        self.empty_item = QtGui.QTableWidgetItem()

        # Populate Manufacturer list
        self.init_manufacturer_list()

        # Set up UI
        self.project_name.setText('Default')

        self.focalField.setValidator(QtGui.QIntValidator())
        self.focalField.hide()
        self.lockFOV.setIcon(lock_icon)
        self.lockFOV.setToolTip('Lock the current FOV value and show the corresponding focal length to mantain the FOV.')
        self.lockFOV.setIconSize(QtCore.QSize(15, 15))
        self.lockFOV.setEnabled(False)
        self.rec_lens.hide()
        self.rec_lens_label.hide()

        # Set up Info table
        cat = QtGui.QTableWidgetItem('Manufacturer: ')
        cat.setTextAlignment(QtCore.Qt.AlignRight |
        QtCore.Qt.AlignVCenter)
        self.bodyInfo.setItem(0, 0, cat)
        cat = QtGui.QTableWidgetItem('Model: ')
        cat.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.bodyInfo.setItem(1, 0, cat)
        cat = QtGui.QTableWidgetItem('Setting: ')
        cat.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.bodyInfo.setItem(2, 0, cat)
        filmsize_cat = QtGui.QTableWidgetItem('Film Back Size (mm): ')
        filmsize_cat.setTextAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        imgrez_cat = QtGui.QTableWidgetItem('Image Resolution: ')
        imgrez_cat.setTextAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.bodyInfo.setItem(3, 0, filmsize_cat)
        self.bodyInfo.setItem(4, 0, imgrez_cat)
        name_cat = QtGui.QTableWidgetItem('Name: ')
        name_cat.setTextAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        focal_cat = QtGui.QTableWidgetItem('Focal Length (mm): ')
        focal_cat.setTextAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        anamorphic_cat = QtGui.QTableWidgetItem('Anamorphic: ')
        anamorphic_cat.setTextAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.lensInfo.setItem(0, 0, name_cat)
        self.lensInfo.setItem(1, 0, anamorphic_cat)
        self.lensInfo.setItem(2, 0, focal_cat)

        self.connect()

    def connect(self):
        """Connecting UI signal to methods."""
        self.manufacturerList.itemClicked.connect(self.update_model)

        self.modelList.itemClicked.connect(self.update_setting)
        self.modelList.itemClicked.connect(self.update_lens)

        self.lensList.itemClicked.connect(self.update_focal_length)
        self.lensList.itemClicked.connect(self.update_info)

        self.settingList.itemClicked.connect(self.update_info)
        self.settingSearch.textChanged.connect(self.filter_setting)
        self.focalList.currentIndexChanged.connect(self.update_info)
        self.focalField.editingFinished.connect(self.update_info)
        self.lockFOV.released.connect(self.update_info)

        self.create.clicked.connect(self.create_camera)
        self.apply.clicked.connect(self.apply_camera)

    def init_manufacturer_list(self):
        """Initialize Manufacturer list."""
        for i in self.data_sheet.body:
            item = QtGui.QListWidgetItem(i, self.manufacturerList)
            item.setData(QtCore.Qt.UserRole, ProtectedData(self.data_sheet.body[i]))

    def update_model(self, sel_manu=None):
        """Update *Model* list."""
        self.modelList.clear()
        if sel_manu:
            item_data = sel_manu.data(QtCore.Qt.UserRole).get()
            for i in item_data:
                item = QtGui.QListWidgetItem(i, self.modelList)
                item.setData(QtCore.Qt.UserRole, ProtectedData(item_data[i]))

        self.update_setting()
        self.update_lens()

    def update_setting(self, sel_mod=None):
        """Update *Setting* List based on model selection."""
        self.settingSearch.clear()
        self.update_setting_table(sel_mod)
        if sel_mod:
            self.settingSearch.setEnabled(True)
        else:
            self.settingSearch.setEnabled(False)

    def update_setting_table(self, sel_mod=None, search=None):
        """Update *Setting* List."""
        self.settingList.clear()
        if sel_mod:
            setting_data = sel_mod.data(QtCore.Qt.UserRole).get()['settings']
            for i in setting_data:
                if not search or search.lower() in i.lower():
                    item = QtGui.QListWidgetItem(i, self.settingList)
                    item.setData(QtCore.Qt.UserRole, ProtectedData(setting_data[i]))

    def update_lens(self, sel_mod=None):
        """Update *Lens* List."""
        self.lensList.clear()
        if sel_mod:
            lens_data = sel_mod.data(QtCore.Qt.UserRole).get()['lenses']
            # Insert Generic lens
            item = QtGui.QListWidgetItem('GENERIC', self.lensList)
            item.setForeground(self.green)
            item.setData(QtCore.Qt.UserRole, self.Generic_lens)
            for i in lens_data:
                lens_obj = self.data_sheet.lens[i]
                lens_data = lens_obj
                item = QtGui.QListWidgetItem(lens_data['name'], self.lensList)
                item.setData(QtCore.Qt.UserRole, ProtectedData(lens_data))
        self.update_focal_length()
        self.update_info()

    def filter_setting(self, text):
        """Called once the content of *Search* field changes."""
        selected_model = self.modelList.currentItem()
        self.update_setting_table(selected_model, text)

    def update_focal_length(self, sel_len=None):
        """Update *Focal Length* Combobox"""
        # Block indexChanged signal while updating combobox
        self.focalList.blockSignals(True)
        self.focalList.clear()
        self.focalField.clear()

        self.genericLens = False
        self.focalList.show()
        self.focalField.hide()
        if sel_len:
            if sel_len.text() == 'GENERIC':
                self.genericLens = True
                self.focalList.hide()
                self.focalField.show()
            else:
                lens_data = sel_len.data(QtCore.Qt.UserRole).get()
                self.focalList.addItems(map(str, lens_data['focal_length_sets']))
        self.focalList.blockSignals(False)

    def update_info_table(self):
        """Update the content in *Info* table."""
        # Clear content
        for row in range(self.bodyInfo.rowCount()):
            self.bodyInfo.setItem(row, 1, QtGui.QTableWidgetItem())

        for row in range(self.lensInfo.rowCount()):
            self.lensInfo.setItem(row, 1, QtGui.QTableWidgetItem())

        # Set display
        if self.manufacturer:
            val = QtGui.QTableWidgetItem(self.manufacturer)
            self.bodyInfo.setItem(0, 1, val)

        if self.model:
            val = QtGui.QTableWidgetItem(self.model)
            self.bodyInfo.setItem(1, 1, val)

        if self.setting:
            val = QtGui.QTableWidgetItem(self.setting)
            self.bodyInfo.setItem(2, 1, val)

            if self.lens and self.lens['anamorphic']:
                self.film_back['width'] *= 2

            film_w = self.film_back['width']
            film_h = self.film_back['height']
            img_w = self.img_res['width']
            img_h = self.img_res['height']

            filmsize_val = QtGui.QTableWidgetItem(str(film_w) + ' x ' + str(film_h))
            imgrez_val = QtGui.QTableWidgetItem(str(img_w) + ' x ' + str(img_h))

            self.bodyInfo.setItem(3, 1, filmsize_val)
            self.bodyInfo.setItem(4, 1, imgrez_val)

        if self.lens:
            name_val = QtGui.QTableWidgetItem(self.lens['name'])
            name_val.setTextAlignment(QtCore.Qt.AlignTop)

            focal_val = QtGui.QTableWidgetItem(', '.join(map(str, self.lens['focal_length_sets'])))
            focal_val.setTextAlignment(QtCore.Qt.AlignTop)

            ana_val = QtGui.QTableWidgetItem('Yes' if self.lens['anamorphic'] else 'No')
            ana_val.setTextAlignment(QtCore.Qt.AlignTop)

            self.lensInfo.setItem(0, 1, name_val)
            self.lensInfo.setItem(1, 1, ana_val)
            self.lensInfo.setItem(2, 1, focal_val)
            self.lensInfo.resizeRowsToContents()

        if not self.lockFOV.isChecked():
            self.FOV.clear()
            self.rec_lens.hide()
            self.rec_lens_label.hide()
            if self.setting and self.lens and self.focal_length:
                fov = 114.592 * math.atan(film_w/self.focal_length/2)
                self.FOV.setText(str(round(fov, 2)))
                self.lockFOV.setEnabled(True)
            else:
                self.lockFOV.setEnabled(False)
        else:
            self.rec_lens.clear()
            self.rec_lens.show()
            self.rec_lens_label.show()
            if self.setting:
                locked_fov = float(self.FOV.text())
                rec_lens = film_w / (2 * math.tan(locked_fov / 114.592))
                self.rec_lens.setText(str(round(rec_lens, 2)))

    def update_info(self):
        """Update attribute and display based on the current camera body and lens
         selection."""

        # Update data
        current_manufacturer = self.manufacturerList.currentItem()
        current_model = self.modelList.currentItem()
        current_setting = self.settingList.currentItem()
        current_lens = self.lensList.currentItem()
        if self.genericLens:
            current_focal_length = self.focalField.text()
        else:
            current_focal_length = self.focalList.currentText()

        self.manufacturer = current_manufacturer.text() if current_manufacturer else None
        self.model = current_model.text() if current_model else None
        self.lens = current_lens.data(QtCore.Qt.UserRole).get() if current_lens else None
        self.focal_length = float(current_focal_length) if current_setting and current_focal_length else None
        if current_setting:
            self.setting = current_setting.text()
            self.film_back = copy.deepcopy(current_setting.data(QtCore.Qt.UserRole).get()['film_back'])
            self.img_res = copy.deepcopy(current_setting.data(QtCore.Qt.UserRole).get()['image_size'])
        else:
            self.setting = None
            self.film_back = None
            self.img_res = None

        self.update_info_table()

    def ui_selection_check(self):
        """Check selections before creating or updating cameras."""
        self.update_info()
        cam_selected = self.settingList.selectedItems()
        lens_selected = self.lensList.selectedItems()
        if not cam_selected:
            msg = QtGui.QMessageBox(parent=self)
            msg.setText('Please select a Format.')
            msg.setWindowTitle('Warning')
            msg.exec_()
            return False

        if not lens_selected:
            msg = QtGui.QMessageBox(parent=self)
            msg.setText('Please select a Lens.')
            msg.setWindowTitle('Warning')
            msg.exec_()
            return False

        if self.genericLens:
            focal_length = self.focalField.text()
            if not focal_length.isdigit():
                msg = QtGui.QMessageBox(parent=self)
                msg.setText('Focal length is not valid.')
                msg.setWindowTitle('Warning')
                msg.exec_()
                return False

        return True

    def create_camera(self):
        """Create Camera."""
        if not self.ui_selection_check():
            return

        cam_transfrom, cam_shape = pm.camera(hfa=self.film_back['width'] * 0.03937,
            vfa=self.film_back['height'] * 0.03937, focalLength=self.focal_length, ncp=1, fcp=90000)
        cam_transfrom.rename('shotCam')
        cam_shape.setAttr('locatorScale', 3)
        cam_shape.setAttr('displayGateMaskColor', [0,0,0])
        cam_shape.setAttr('displayFilmGate', 1)
        cam_shape.setAttr('cameraAperture', l=True)
        cam_shape.setAttr('focalLength', l=True)

        pm.xform(cam_transfrom, roo=self.rotOrder.currentText())

    def apply_camera(self):
        """Update selected cameras."""
        cameras_selected = pm.ls(sl=True, dag=True, leaf=True, cameras=True)

        if len(cameras_selected) == 0:
            msg = QtGui.QMessageBox(parent=self)
            msg.setText('Please select a camera in the scene.')
            msg.setWindowTitle('Warning')
            msg.exec_()
            return

        if not self.ui_selection_check():
            return

        for cam in cameras_selected:
            cam_transform = pm.listRelatives(cam, parent=True)[0]
            # Unlock attributes
            cam.setAttr('cameraAperture', l=False)
            cam.setAttr('focalLength', l=False)

            cam.setHorizontalFilmAperture(self.film_back['width'] * 0.03937)
            cam.setVerticalFilmAperture(self.film_back['height'] * 0.03937)
            cam.setFocalLength(self.focal_length)

            cam.setAttr('cameraAperture', l=True)
            cam.setAttr('focalLength', l=True)

            pm.xform(cam_transform, roo=self.rotOrder.currentText())