
try:
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtWidgets import *

    QT_API = "PyQt6"
    IS_QT6 = True
    IS_QT5 = False

except ImportError:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *

    QT_API = "PyQt5"
    IS_QT6 = False
    IS_QT5 = True

#print(QT_API)

#========================================================================================
if IS_QT6:
    AlignLeft = Qt.AlignmentFlag.AlignLeft
    AlignCenter = Qt.AlignmentFlag.AlignCenter
    AlignVCenter = Qt.AlignmentFlag.AlignVCenter
    AlignTop = Qt.AlignmentFlag.AlignTop
    AlignBottom = Qt.AlignmentFlag.AlignBottom

    ToolTip = Qt.WindowType.ToolTip

    TextSelectableByMouse = Qt.TextInteractionFlag.TextSelectableByMouse
    TextBrowserInteraction = Qt.TextInteractionFlag.TextBrowserInteraction

    ItemIsEditable = Qt.ItemFlag.ItemIsEditable
    ItemIsSelectable = Qt.ItemFlag.ItemIsSelectable
    ItemIsEnabled = Qt.ItemFlag.ItemIsEnabled
    ItemIsDropEnabled = Qt.ItemFlag.ItemIsDropEnabled

    CustomContextMenu = Qt.ContextMenuPolicy.CustomContextMenu
    WA_Hover = Qt.WidgetAttribute.WA_Hover

    MessageBoxYes = QMessageBox.StandardButton.Yes
    MessageBoxNo = QMessageBox.StandardButton.No
    MessageBoxCancel = QMessageBox.StandardButton.Cancel
    MessageBoxDiscard = QMessageBox.StandardButton.Discard
    MessageBoxAcceptRole = QMessageBox.ButtonRole.AcceptRole

    HoverMove = QEvent.Type.HoverMove
    HoverEnter = QEvent.Type.HoverEnter
    Leave = QEvent.Type.Leave
    FocusOut = QEvent.Type.FocusOut

    KeepAspectRatio = Qt.AspectRatioMode.KeepAspectRatio
    SmoothTransformation = Qt.TransformationMode.SmoothTransformation
    Expanding = QSizePolicy.Policy.Expanding
    Minimum = QSizePolicy.Policy.Minimum

    SP_DialogApplyButton = QStyle.StandardPixmap.SP_DialogApplyButton

    QKeySequenceClose = QKeySequence.StandardKey.Close
    QKeySequenceCopy = QKeySequence.StandardKey.Copy

#----------------------------------------------
else:
    AlignLeft = Qt.AlignLeft
    AlignCenter = Qt.AlignCenter
    AlignVCenter = Qt.AlignVCenter
    AlignTop = Qt.AlignTop
    AlignBottom = Qt.AlignBottom

    ToolTip = Qt.ToolTip

    TextSelectableByMouse = Qt.TextSelectableByMouse
    TextBrowserInteraction = Qt.TextBrowserInteraction

    ItemIsEditable = Qt.ItemIsEditable
    ItemIsSelectable = Qt.ItemIsSelectable
    ItemIsEnabled = Qt.ItemIsEnabled
    ItemIsDropEnabled = Qt.ItemIsDropEnabled

    CustomContextMenu = Qt.CustomContextMenu
    WA_Hover = Qt.WA_Hover

    MessageBoxYes = QMessageBox.Yes
    MessageBoxNo = QMessageBox.No
    MessageBoxCancel = QMessageBox.Cancel
    MessageBoxDiscard = QMessageBox.Discard
    MessageBoxAcceptRole = QMessageBox.AcceptRole

    HoverMove = QEvent.HoverMove
    HoverEnter = QEvent.HoverEnter
    Leave = QEvent.Leave
    FocusOut = QEvent.FocusOut

    KeepAspectRatio = Qt.KeepAspectRatio
    SmoothTransformation = Qt.SmoothTransformation
    Expanding = QSizePolicy.Expanding
    Minimum = QSizePolicy.Minimum

    SP_DialogApplyButton = QStyle.SP_DialogApplyButton

    QKeySequenceClose = QKeySequence.Close
    QKeySequenceCopy = QKeySequence.Copy

#========================================================================================
def app_exec(app):
    if IS_QT6:
        return app.exec()
    return app.exec_()

#========================================================================================
def event_pos(event):
    if hasattr(event, "position"):
        p = event.position()
        return p.x(), p.y()
    p = event.pos()
    return p.x(), p.y()

#========================================================================================
def event_global_pos(event):
    """
    Return the global (screen) position of a Qt or Matplotlib event.

    This function transparently handles differences between:
    - PyQt5 (`globalPos()`)
    - PyQt6 (`globalPosition().toPoint()`)

    It also supports Matplotlib events by accessing the underlying Qt event
    via the `guiEvent` attribute when present.

    Parameters
    ----------
    event : object
        Qt event or Matplotlib event with a `guiEvent` attribute.

    Returns
    -------
    QPoint or None
        Global position in screen coordinates, or None if unavailable.
    """
    gui_event = getattr(event, "guiEvent", event)
    if gui_event is None:
        return None

    if hasattr(gui_event, "globalPosition"):
        return gui_event.globalPosition().toPoint()

    if hasattr(gui_event, "globalPos"):
        return gui_event.globalPos()

    return None

#========================================================================================
