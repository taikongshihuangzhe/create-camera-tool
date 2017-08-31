import main_window

dialog = None

def run():
    global dialog
    dialog = main_window.createCameraWindow()
    dialog.show()
