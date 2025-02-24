from qtpy.QtWidgets import QGraphicsSceneHoverEvent
from nodeeditor.node_graphics_node import QDMGraphicsNode 


class Graphics(QDMGraphicsNode):
    node_hover_effect_callBack = None
    def initSizes(self):
        super().initSizes()  
        self.setNodeSize(self.node.width,self.node.height)
        self.edge_roundness = 10
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10 
         

    def add_node_hover_effect_callBack(self, callBack):
        if callable(callBack):
            self.node_hover_effect_callBack = callBack

    def setNodeSize(self, width, height):
        self.width = width
        self.height = height  
        self.prepareGeometryChange() 
        

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
    
    def onSelected(self):
        """Our event handling when the node was selected"""
        self.node.scene.grScene.itemSelected.emit() 

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()
        if callable(self.node_hover_effect_callBack):
            self.node_hover_effect_callBack(True) 

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()
        if callable(self.node_hover_effect_callBack):
            self.node_hover_effect_callBack(False) 