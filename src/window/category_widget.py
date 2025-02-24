from .node_editor import NoMarginDelegate
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
 
from .list_widget import ListWidget 

from src.node_editor.constants import NODES
from src.node_editor.collector import get_class_from_opcode
def get_all_nodes():
    items = {}
    keys = list(NODES.keys())
    keys.sort()
    for key in keys:
        node = get_class_from_opcode(key)  
        if node.category in items:
            pass
        else:
            items[node.category] = list() 
        items[node.category].append([node.op_title, node.icon, node.op_code,node.category]) 
    return items

class CategoryTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self): 
        self.setHeaderHidden(True)
        nodes = get_all_nodes()
        node_keys = dict(nodes).keys()
        index = 0 
        for key in node_keys:
            self.createCategory(key,nodes[key],index) 
            index += 1 
        self.setIndentation(0) 
        #self.expandAll()

    def createCategory(self,name,items,index): 
        self.setItemDelegate(NoMarginDelegate(self))
        group = QTreeWidgetItem(self)
        group.setText(0, name)   
        first_child = QTreeWidgetItem(group) 
        list_box = ListWidget()
        list_box = list_box.addItems(items)
        list_box.setStyleSheet("margin: 0px; padding: 0px;") 
        item_widget = QWidget()
        layout = QVBoxLayout(item_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.addWidget(list_box)
        item_widget.setLayout(layout) 
        self.setItemWidget(first_child, 0, item_widget)
        if index == 0 : 
            group.setExpanded(True)
        else:
            group.setExpanded(False)