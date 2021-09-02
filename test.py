import bpy
import shutil
import os
import threading

from bpy.props import IntProperty, FloatProperty

src = r"D:\Start_IceCream_Park_River_005.mp4"
dst = r'D:\Temp\Start_IceCream_Park_River_005.mp4'


class ModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"

    _timer = None

    def modal(self, context, event):        
        if event.type == 'TIMER':
            if not os.path.exists(dst):
                progress = 0
            else:
                progress = int((float(os.path.getsize(dst))/float(os.path.getsize(src))) * 100)
                bpy.context.scene.progress = progress

                for area in bpy.context.screen.areas:
                    if area.type == "VIEW_3D":
                        for region in area.regions:
                            if region.type == "UI":
                                region.tag_redraw()
        if os.path.getsize(src) == os.path.getsize(dst) or event.type in {'ESC'}:
            return {"CANCELLED"}
        
        return {'PASS_THROUGH'}

    def execute(self, context):    
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(ModalOperator)


if __name__ == "__main__":
    
    register()
    
    def copying_file(source_path, destination_path):
        print("Copying......")
        shutil.copy2(source_path, destination_path)

        if os.path.exists(destination_path):
            print("Done....")
            return True

        print("Filed...")
        return False
    

    
    t = threading.Thread(name='copying', target=copying_file, args=(src, dst))
    t.start()
    
    bpy.ops.object.modal_operator('INVOKE_DEFAULT')
