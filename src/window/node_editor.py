
from qtpy.QtGui import   QWheelEvent
from qtpy.QtWidgets import QWidget,QStyledItemDelegate 
from nodeeditor.node_editor_widget import NodeEditorWidget   
from nodeeditor.node_graphics_view import QDMGraphicsView as OriginalQDMGraphicsView
from nodeeditor.node_scene import Scene as OriginalScene
from nodeeditor.utils import dumpException
from nodeeditor.node_graphics_scene import QDMGraphicsScene
class Scene(OriginalScene):
    parent_app = None 
    def deserialize(self, data: dict, hashmap: dict={}, restore_id: bool=True, *args, **kwargs) -> bool:
        try:
            hashmap = {}

            if restore_id: self.id = data['id']

            # -- deserialize NODES

            ## Instead of recreating all the nodes, reuse existing ones...
            # get list of all current nodes:
            all_nodes = self.nodes.copy()

            # go through deserialized nodes:
            for node_data in data['nodes']:
                # can we find this node in the scene?
                found = False
                for node in all_nodes:
                    if node.id == node_data['id']:
                        found = node
                        break

                if not found:
                    try:
                        new_node = self.getNodeClassFromData(node_data)(self,parent=self.parent_app)
                        new_node.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                        new_node.onDeserialized(node_data)
                        # print("New node for", node_data['title'])
                    except:
                        dumpException()
                else:
                    try:
                        found.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                        found.onDeserialized(node_data)
                        all_nodes.remove(found)
                        # print("Reused", node_data['title'])
                    except: dumpException()

            # remove nodes which are left in the scene and were NOT in the serialized data!
            # that means they were not in the graph before...
            while all_nodes != []:
                node = all_nodes.pop()
                node.remove()


            # -- deserialize EDGES


            ## Instead of recreating all the edges, reuse existing ones...
            # get list of all current edges:
            all_edges = self.edges.copy()

            # go through deserialized edges:
            for edge_data in data['edges']:
                # can we find this node in the scene?
                found = False
                for edge in all_edges:
                    if edge.id == edge_data['id']:
                        found = edge
                        break

                if not found:
                    new_edge = self.getEdgeClass()(self).deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                    # print("New edge for", edge_data)
                else:
                    found.deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                    all_edges.remove(found)

            # remove nodes which are left in the scene and were NOT in the serialized data!
            # that means they were not in the graph before...
            while all_edges != []:
                edge = all_edges.pop()
                edge.remove()


            return True
        except Exception as e:
            print(f"Deserializasyon hatası: {str(e)}") 
            
class QDMGraphicsView(OriginalQDMGraphicsView):
    def __init__(self, grScene: 'QDMGraphicsScene', parent: 'QWidget'=None): 
        super().__init__(grScene,parent)
        self.parent = parent

    def wheelEvent(self, event: QWheelEvent): 
        if self.parent.parent.getWeelStatus(): 
            """overridden Qt's ``wheelEvent``. This handles zooming"""
            # calculate our zoom Factor
            zoomOutFactor = 1 / self.zoomInFactor

            # calculate zoom
            if event.angleDelta().y() > 0:
                zoomFactor = self.zoomInFactor
                self.zoom += self.zoomStep
            else:
                zoomFactor = zoomOutFactor
                self.zoom -= self.zoomStep


            clamped = False
            if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
            if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

            # set scene scale
            if not clamped or self.zoomClamp is False:
                self.scale(zoomFactor, zoomFactor)
        else:
            delta = event.angleDelta()
            self.parent.parent.wheelEvent(event)


class NodeEditorWidget(NodeEditorWidget): 
    GraphicsView_class = QDMGraphicsView
    Scene_class = Scene 
    



class NoMarginDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        # Adjust the size hint to remove margins
        size = super().sizeHint(option, index)
        size.setWidth(size.width() - option.rect.left())  # Remove left margin
        return size