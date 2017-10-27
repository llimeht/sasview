import json
import os
import functools

from PyQt4 import QtGui
from PyQt4 import QtCore
import sas.sasview
import sas.qtgui.Utilities.LocalConfig as LocalConfig
import sas.qtgui.Utilities.GuiUtils as GuiUtils

from collections import defaultdict
from sas.qtgui.Utilities.CategoryInstaller import CategoryInstaller
from sasmodels.sasview_model import load_standard_models
from sas.qtgui.MainWindow.ViewDelegate import CategoryViewDelegate

from UI.CategoryManagerUI import Ui_CategoryManagerUI

class ToolTippedItemModel(QtGui.QStandardItemModel):

    def __init__(self, parent = None):
        QtGui.QStandardItemModel.__init__(self,parent)

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.ToolTipRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.QString(str(self.header_tooltips[section]))

        return QtGui.QStandardItemModel.headerData(self, section, orientation, role)


class CategoryManager(QtGui.QDialog, Ui_CategoryManagerUI):
    def __init__(self, parent=None):
        super(CategoryManager, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Category Manager")

        self.initializeModels()

        self.addActions()

    def readCategoryInfo(self):
        """
        Reads the categories in from file
        """
        self.master_category_dict = defaultdict(list)
        self.by_model_dict = defaultdict(list)
        self.model_enabled_dict = defaultdict(bool)

        categorization_file = CategoryInstaller.get_user_file()
        if not os.path.isfile(categorization_file):
            categorization_file = CategoryInstaller.get_default_file()
        with open(categorization_file, 'rb') as cat_file:
            self.master_category_dict = json.load(cat_file)
            self.regenerateModelDict()

        # Load the model dict
        models = load_standard_models()
        for model in models:
            self.models[model.name] = model


    def checkboxSelected(self, item):
        # Assure we're dealing with checkboxes
        if not item.isCheckable():
            return
        status = item.checkState()

        def isCheckable(row):
            return self._category_model.item(row, 0).isCheckable()

        # If multiple rows selected - toggle all of them, filtering uncheckable
        rows = [s.row() for s in self.lstParams.selectionModel().selectedRows() if isCheckable(s.row())]

        # Switch off signaling from the model to avoid recursion
        self._category_model.blockSignals(True)
        # Convert to proper indices and set requested enablement
        [self._category_model.item(row, 0).setCheckState(status) for row in rows]
        self._category_model.blockSignals(False)

    def initializeModels(self):
        """
        Set up models and views
        """
        # Set the main models
        # We can't use a single model here, due to restrictions on flattening
        # the model tree with subclassed QAbstractProxyModel...
        self._category_model = ToolTippedItemModel()
        self.lstParams.setModel(self._category_model)
        self.readCategoryInfo()

        # Delegates for custom editing and display
        self.lstParams.setItemDelegate(CategoryViewDelegate(self))

        self.lstParams.setAlternatingRowColors(True)
        stylesheet = """

            QTreeView {
                paint-alternating-row-colors-for-empty-area:0;
            }

            QTreeView::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
                border: 1px solid #bfcde4;
            }

            QTreeView::item:selected {
                border: 1px solid #567dbc;
            }

            QTreeView::item:selected:active{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
            }

            QTreeView::item:selected:!active {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
            }
           """
        self.lstParams.setStyleSheet(stylesheet)
        self.lstParams.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lstParams.customContextMenuRequested.connect(self.showModelDescription)
        self.lstParams.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)

    def regenerateModelDict(self):
        """
        Regenerates self.by_model_dict which has each model name as the
        key and the list of categories belonging to that model
        along with the enabled mapping
        """
        self.by_model_dict = defaultdict(list)
        for category in self.master_category_dict:
            for (model, enabled) in self.master_category_dict[category]:
                self.by_model_dict[model].append(category)
                self.model_enabled_dict[model] = enabled

    def addActions(self):
        """
        Add actions to the logo push buttons
        """

        self.cmdOK.clicked.connect(self.close)

