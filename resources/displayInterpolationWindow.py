from resources.qt_compat import *

import sys
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

from .misc import *
from .CustomQTableWidget import CustomQTableWidget 
from .interactivePlot import interactivePlot
from .defineInterpolationWindow import defineInterpolationWindow

#=========================================================================================
class displayInterpolationWindow(QWidget):

    #---------------------------------------------------------------------------------------------
    def updatePointersPlot(self):
    
        self.pointersPlot_ax.clear()
        for line in self.pointersPlot_axGradient.lines:
            line.remove()
    
        legendHandles = []
    
        line, = self.pointersPlot_ax.plot(
            self.X2Coords,
            self.X1Coords,
            color='steelblue',
            linewidth=1,
            label='Pointers'
        )
        points = self.pointersPlot_ax.scatter(
            self.X2Coords,
            self.X1Coords,
            s=10,
            marker='o',
            color='steelblue'
        )
    
        self.pointersPlot_ax.patch.set_visible(False)
        self.pointersPlot_ax.grid(
            visible=True,
            which='major',
            color='lightgray',
            linestyle='dashed',
            linewidth=1
        )
        self.pointersPlot_ax.set_xlabel('X')
        self.pointersPlot_ax.set_ylabel(self.X1Name, color='steelblue')
    
        legendHandles.append(Line2D([0], [0], color='steelblue', label='Pointers'))
        self.pointersPlot_ax.line_points_pairs = []
        self.pointersPlot_ax.line_points_pairs.append((line, points))
    
        self.pointersPlot_axGradient.set_ylabel(
            'Distorted / Reference gradient',
            color='darkorange'
        )
        self.pointersPlot_axGradient.line_points_pairs = []
    
        npoints = self.gradientSamplePoints_spin.value()
        X2CoordsValues = np.linspace(self.X2Coords[0], self.X2Coords[-1], npoints)
    
        f_1to2, f_2to1 = defineInterpolationWindow.defineInterpolationFunctions(
            self.X1Coords,
            self.X2Coords,
            interpolationMode='Linear'
        )
        gradientLinear = np.gradient(
            X2CoordsValues,
            f_2to1(X2CoordsValues)
        ).astype(np.float32)
    
        line1, = self.pointersPlot_axGradient.plot(
            X2CoordsValues,
            gradientLinear,
            color='darkorange',
            lw=1,
            label='Linear'
        )
        legendHandles.append(Line2D([0], [0], color='darkorange', label='Linear'))
    
        f_1to2, f_2to1 = defineInterpolationWindow.defineInterpolationFunctions(
            self.X1Coords,
            self.X2Coords,
            interpolationMode='PCHIP'
        )
        gradientPCHIP = np.gradient(
            X2CoordsValues,
            f_2to1(X2CoordsValues)
        ).astype(np.float32)
    
        line2, = self.pointersPlot_axGradient.plot(
            X2CoordsValues,
            gradientPCHIP,
            color='darkorange',
            linestyle='dashed',
            lw=1,
            label='PCHIP'
        )
        legendHandles.append(
            Line2D([0], [0], color='darkorange', linestyle='dashed', label='PCHIP')
        )
    
        legend = self.pointersPlot_ax.legend(handles=legendHandles)
    
        self.pointersPlot_ax.map_legend_to_line = {}
        line_map = {
            "Pointers": line,
            "Linear": line1,
            "PCHIP": line2,
        }
    
        for legend_line in legend.get_lines():
            label = legend_line.get_label()
            legend_line.set_picker(5)
            self.pointersPlot_ax.map_legend_to_line[legend_line] = line_map[label]
    
        self.interactive_pointersPlot.fig.canvas.draw()

    #---------------------------------------------------------------------------------------------
    def updateGradients(self):
    
        self.gradients_table.clearContents()
    
        if len(self.X1Coords) < 2:
            self.gradients_table.setRowCount(0)
            self.gradients_table.setColumnCount(0)
            return
    
        npoints = self.gradientSamplePoints_spin.value()
    
        X2Values = np.linspace(self.X2Coords[0], self.X2Coords[-1], npoints)
    
        # Linear
        f_1to2, f_2to1 = defineInterpolationWindow.defineInterpolationFunctions(
            self.X1Coords,
            self.X2Coords,
            interpolationMode='Linear'
        )
        X1Linear = f_2to1(X2Values)
        gradientLinear = np.gradient(X2Values, X1Linear).astype(np.float32)
    
        # PCHIP
        f_1to2, f_2to1 = defineInterpolationWindow.defineInterpolationFunctions(
            self.X1Coords,
            self.X2Coords,
            interpolationMode='PCHIP'
        )
        X1PCHIP = f_2to1(X2Values)
        gradientPCHIP = np.gradient(X2Values, X1PCHIP).astype(np.float32)
    
        self.gradients_table.setRowCount(npoints)
        self.gradients_table.setColumnCount(3)
        self.gradients_table.setHorizontalHeaderLabels([
            "Distorted: X",
            "Gradient (Linear)",
            "Gradient (PCHIP)",
        ])
    
        for i in range(npoints):
            self.gradients_table.setItem(i, 0, QTableWidgetItem(f'{X2Values[i]:.6f}'))
            self.gradients_table.setItem(i, 1, QTableWidgetItem(f'{gradientLinear[i]:.6f}'))
            self.gradients_table.setItem(i, 2, QTableWidgetItem(f'{gradientPCHIP[i]:.6f}'))
    
            background_color = QColor('white') if i % 2 == 0 else QColor('whitesmoke')
            for j in range(3):
                self.gradients_table.item(i, j).setBackground(background_color)
    
        self.gradients_table.resizeColumnsToContents()
        self.gradients_table.set_italic_headers()

    #---------------------------------------------------------------------------------------------
    def updateGradientViews(self):
        self.updatePointersPlot()
        self.updateGradients()

    #---------------------------------------------------------------------------------------------
    def __init__(self, Id, open_displayWindows, item):
        super().__init__()

        self.Id = Id
        self.open_displayWindows = open_displayWindows
        self.item = item

        self.interpolationDict = self.item.data(0, Qt.ItemDataRole.UserRole)

        self.X1Coords = self.interpolationDict['X1Coords']
        self.X2Coords = self.interpolationDict['X2Coords']
        self.X1Name = self.interpolationDict['X1Name']
        self.gradientSamplePoints = 100

        title = 'Display INTERPOLATION : ' + self.Id
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 1000, 600)
        
        self.tabs = QTabWidget()
       
        #----------------------------------------------
        pointers_tab = QWidget()
        pointers_layout = QVBoxLayout()
        pointers_table = CustomQTableWidget()
        pointers_table.setRowCount(len(self.X1Coords))
        pointers_table.setColumnCount(2)
        pointers_table.setHorizontalHeaderLabels([
            f"Distorted: X",
            f"Reference: {self.X1Name}", 
        ])

        for i in range(len(self.X1Coords)):
            pointers_table.setItem(i, 0, QTableWidgetItem(str(f'{self.X2Coords[i]:.6f}')))
            pointers_table.setItem(i, 1, QTableWidgetItem(str(f'{self.X1Coords[i]:.6f}')))
            background_color = QColor('white') if i % 2 == 0 else QColor('whitesmoke')
            pointers_table.item(i, 0).setBackground(background_color)
            pointers_table.item(i, 1).setBackground(background_color)
        pointers_table.resizeColumnsToContents()
        pointers_table.set_italic_headers()

        pointers_layout.addWidget(pointers_table)
        pointers_tab.setLayout(pointers_layout)

        #----------------------------------------------
        pointersPlot_tab = QWidget()
        pointersPlot_layout = QVBoxLayout()

        self.interactive_pointersPlot = interactivePlot()
        self.interactive_pointersPlot.left_margin = 200 
        self.pointersPlot_ax = self.interactive_pointersPlot.axs[0]
        self.pointersPlot_ax.twins = []
        self.pointersPlot_ax.twins_orientation = 'vertical'
        self.pointersPlot_axGradient = self.pointersPlot_ax.twinx()
        self.pointersPlot_axGradient.spine_left_position = -100
        self.pointersPlot_axGradient.yaxis.set_label_position('left')
        self.pointersPlot_axGradient.yaxis.set_ticks_position('left')
        self.pointersPlot_axGradient.spines['right'].set_visible(False)
        self.pointersPlot_axGradient.spines['top'].set_visible(False)
        self.pointersPlot_axGradient.spines['bottom'].set_visible(False)
        self.pointersPlot_axGradient.set_zorder(-10)

        self.interactive_pointersPlot.axs.append(self.pointersPlot_axGradient)
        
        canvas = FigureCanvas(self.interactive_pointersPlot.fig)
        pointersPlot_layout.addWidget(canvas)
        
        pointersPlot_tab.setLayout(pointersPlot_layout)

        #----------------------------------------------
        gradients_tab = QWidget()
        gradients_layout = QVBoxLayout()
        
        gradients_control_layout = QHBoxLayout()
        
        self.gradientSamplePoints_label = QLabel("Sample points:")
        
        self.gradientSamplePoints_spin = QSpinBox()
        self.gradientSamplePoints_spin.setMinimum(10)
        self.gradientSamplePoints_spin.setMaximum(10000)
        self.gradientSamplePoints_spin.setSingleStep(10)
        self.gradientSamplePoints_spin.setValue(self.gradientSamplePoints)
        
        gradients_control_layout.addWidget(self.gradientSamplePoints_label)
        gradients_control_layout.addWidget(self.gradientSamplePoints_spin)
        gradients_control_layout.addStretch()
        
        self.gradients_table = CustomQTableWidget()
        
        gradients_layout.addLayout(gradients_control_layout)
        gradients_layout.addWidget(self.gradients_table)
        
        gradients_tab.setLayout(gradients_layout)
       
        self.gradientSamplePoints_spin.valueChanged.connect(self.updateGradientViews)
        self.updateGradientViews()

        #----------------------------------------------
        info_tab = QWidget()
        info_layout = QVBoxLayout()

        self.textName = QLabel(f"Name : <b>{self.interpolationDict['Name']}</b>")

        self.textDate = QLabel(f"Date : {self.interpolationDict['Date']}")

        labelHistory = QLabel("History :")
        self.textHistory = QTextEdit()
        self.textHistory.setFixedHeight(self.textHistory.fontMetrics().lineSpacing() * 10)
        self.textHistory.setText(self.interpolationDict['History'])
        self.textHistory.setReadOnly(True)
        self.textHistory.setFont(QFont("Courier New"))

        labelComment = QLabel("Comment :")
        self.textComment = QTextEdit()
        self.textComment.setFixedHeight(self.textComment.fontMetrics().lineSpacing() * 10)
        self.textComment.setText(self.interpolationDict['Comment'])

        info_layout.addWidget(self.textName)
        info_layout.addWidget(self.textDate)
        info_layout.addWidget(labelHistory)
        info_layout.addWidget(self.textHistory)
        info_layout.addWidget(labelComment)
        info_layout.addWidget(self.textComment)
        info_layout.addStretch()

        info_tab.setLayout(info_layout)

        #----------------------------------------------
        self.tabs.addTab(pointers_tab, "Pointers")
        self.tabs.addTab(pointersPlot_tab, "Pointers plot")
        self.tabs.addTab(gradients_tab, "Gradients")
        self.tabs.addTab(info_tab, "Info")
        self.tabs.setCurrentIndex(1)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        #----------------------------------------------
        button_layout = QHBoxLayout()

        self.close_button = QPushButton("Close", self)
        button_layout.addStretch()

        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

        self.close_button.clicked.connect(self.close)

        #----------------------------------------------
        self.setLayout(main_layout)

        menu_bar = QMenuBar(self)
        main_layout.setMenuBar(menu_bar)

        close_shortcut = QShortcut(QKeySequenceClose, self)
        close_shortcut.activated.connect(self.close)

    #---------------------------------------------------------------------------------------------
    def closeEvent(self, event):
        plt.close()
        self.interpolationDict['Comment'] = self.textComment.toPlainText()
        # if WS has been removed while a Display is active 
        try:
            self.item.setData(0, Qt.ItemDataRole.UserRole, self.interpolationDict)
        except:
            #print("item not available to be updated")
            pass 
        self.open_displayWindows.pop(self.Id, None)
        event.accept()

#=========================================================================================
# Example usage
if __name__ == "__main__":

    app = QApplication([])

    X1Coords = [20,40,45,60,80]
    X2Coords = [30,50,65,80,90]

    itemDict = {
        'Id': 'abcd',
        'Name': 'A name',
        'Type': 'INTERPOLATION', 
        'interpolationMode': 'Linear',
        'X1Coords': X1Coords, 
        'X2Coords': X2Coords, 
        'X1Name': 'X1Name', 
        'Date': '',
        'Comment': 'A text',
        'History': 'command1 ; command2'
    }

    item = QTreeWidgetItem()
    item.setData(0, Qt.ItemDataRole.UserRole, itemDict)

    open_displayWindows = {}
    Id_displayWindow = '1234'
    displayWindow = displayInterpolationWindow(Id_displayWindow, open_displayWindows, item)
    open_displayWindows[Id_displayWindow] = displayWindow
    displayWindow.show()

    sys.exit(app_exec(app))
