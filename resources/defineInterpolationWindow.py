from resources.qt_compat import *

from .misc import *
from .interactivePlot import interactivePlot
from .CustomQTableWidget import CustomQTableWidget

import sys
import datetime
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import ConnectionPatch
from matplotlib.lines import Line2D

from scipy import interpolate

#=========================================================================================
for key in plt.rcParams.keys():
    if key.startswith('keymap.'):
        plt.rcParams[key] = []

#=========================================================================================
class defineInterpolationWindow(QWidget):
    #---------------------------------------------------------------------------------------------
    def __init__(self, Id, open_interpolationWindows, itemINTERPOLATION, items, add_item_tree_widget):
        super().__init__()

        self.Id = Id
        self.open_interpolationWindows = open_interpolationWindows
        self.itemINTERPOLATION = itemINTERPOLATION
        self.items = items
        self.add_item_tree_widget = add_item_tree_widget

        self.seriesWidth = 0.8
        self.pointerColor = 'blue'
        self.key_shift = False
        self.key_control = False
        self.key_x = False
        self.mousepress = None
        self.vline1 = None
        self.vline2 = None
        self.vline1List = []
        self.vline2List = []
        self.X1Coords = []
        self.X2Coords = []
        self.artistsList_Dict = {}
        self.artistsList_LastId = None 
        self.artistsList_LastValues = []
        self.interpolationMode = 'Linear'
        self.axsInterp = None
        self.second_xaxis = None
        self.gradientSamplePoints = 100

        title = 'Define INTERPOLATION : ' + self.Id
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 1200, 800)
        self.setMinimumSize(800, 600)

        self.tabs = QTabWidget()

        #----------------------------------------------
        pointers_tab = QWidget()
        pointers_layout = QVBoxLayout()

        self.pointers_table = CustomQTableWidget()

        pointers_layout.addWidget(self.pointers_table)
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

        canvas1 = FigureCanvas(self.interactive_pointersPlot.fig)
        pointersPlot_layout.addWidget(canvas1)

        pointersPlot_tab.setLayout(pointersPlot_layout)

        #----------------------------------------------
        plots_tab = QWidget()
        plots_layout = QVBoxLayout()

        self.interactive_plot = interactivePlot(
            rows=2, 
            cols=1,
            allow_back_x_axis_settings=True,
            allow_back_y_axis_settings=True,
            allow_back_axis_settings=True,
            allow_save_axis_settings=False
        )
        self.interactive_plot.top_margin = 100
        self.interactive_plot.right_margin = 150
        self.axs = self.interactive_plot.axs

        canvas2 = FigureCanvas(self.interactive_plot.fig)
        plots_layout.addWidget(canvas2)

        self.axsInterp = self.axs[0].twinx()
        self.axsInterp.sharey(self.axs[1])
        self.axsInterp.set_zorder(-10)

        plots_tab.setLayout(plots_layout)

        #----------------------------------------------
        gradients_tab = QWidget()
        gradients_layout = QVBoxLayout()
        
        gradients_control_layout = QHBoxLayout()
        
        self.gradientSamplePoints_label = QLabel("Sample points:")
        self.gradientSamplePoints_spin = QSpinBox()
        self.gradientSamplePoints_spin.setMinimum(10)
        self.gradientSamplePoints_spin.setMaximum(10000)
        self.gradientSamplePoints_spin.setValue(self.gradientSamplePoints)
        self.gradientSamplePoints_spin.setSingleStep(10)
        self.gradientSamplePoints_spin.setToolTip(
            "Number of points used to evaluate interpolation gradients"
        )
        
        gradients_control_layout.addWidget(self.gradientSamplePoints_label)
        gradients_control_layout.addWidget(self.gradientSamplePoints_spin)
        gradients_control_layout.addStretch()
        
        self.gradients_table = CustomQTableWidget()
        
        gradients_layout.addLayout(gradients_control_layout)
        gradients_layout.addWidget(self.gradients_table)
        
        gradients_tab.setLayout(gradients_layout)
        
        self.gradientSamplePoints_spin.valueChanged.connect(self.updateGradientViews)

        #----------------------------------------------
        self.tabs.addTab(plots_tab, "Plots")
        self.tabs.addTab(pointers_tab, "Pointers")
        self.tabs.addTab(pointersPlot_tab, "Pointers plot")
        self.tabs.addTab(gradients_tab, "Gradients")
        self.tabs.setCurrentIndex(0)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        #----------------------------------------------
        control_layout1 = QHBoxLayout()
        
        self.selectSeriesRef_combo_label = QLabel("Reference series:")
        self.selectSeriesRef_combo_label.setFixedWidth(120)
        self.selectSeriesRef_combo = QComboBox()
        font = QFont("Courier New")
        self.selectSeriesRef_combo.setFont(font)

        for n,item in enumerate(self.items):
            seriesDict = item.data(0, Qt.ItemDataRole.UserRole)
            XName = seriesDict['X']
            YName = seriesDict['Y']
            Id = seriesDict['Id']
            self.selectSeriesRef_combo.addItem(f'{n+1} with {Id}: {XName} / {YName}')
        self.selectSeriesRef_combo.setCurrentIndex(0)

        control_layout1.addWidget(self.selectSeriesRef_combo_label)
        control_layout1.addWidget(self.selectSeriesRef_combo)
        control_layout1.addStretch()

        main_layout.addLayout(control_layout1)

        self.selectSeriesRef_combo.currentIndexChanged.connect(self.selectSeries_change)

        #----------------------------------------------
        control_layout2 = QHBoxLayout()

        self.selectSeriesDist_combo_label = QLabel("Distorted series:")
        self.selectSeriesDist_combo_label.setFixedWidth(120)
        self.selectSeriesDist_combo = QComboBox()
        font = QFont("Courier New")
        self.selectSeriesDist_combo.setFont(font)

        for n,item in enumerate(self.items):
            seriesDict = item.data(0, Qt.ItemDataRole.UserRole)
            XName = seriesDict['X']
            YName = seriesDict['Y']
            Id = seriesDict['Id']
            self.selectSeriesDist_combo.addItem(f'{n+1} with {Id}: {XName} / {YName}')
        self.selectSeriesDist_combo.setCurrentIndex(1)

        control_layout2.addWidget(self.selectSeriesDist_combo_label)
        control_layout2.addWidget(self.selectSeriesDist_combo)
        control_layout2.addStretch()

        main_layout.addLayout(control_layout2)

        self.selectSeriesDist_combo.currentIndexChanged.connect(self.selectSeries_change)

        #----------------------------------------------
        control_layout3 = QHBoxLayout()

        self.showInterp = QCheckBox("Show interpolated curve")
        self.showInterp.setChecked(True)

        self.removeAddLastConnect_button = QPushButton()
        self.removeAddLastConnect_button.setFixedWidth(210)
        self.removeAddLastConnect_button.setText("Remove last connection")
        self.removeAddLastConnect_button.setShortcut("u")
        self.removeAddLastConnect_button.setEnabled(False)

        self.interp_combo_label = QLabel("Interpolation Method:")
        self.interp_combo_label.setToolTip("Choose between Linear or PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) interpolation")
        self.interp_combo = QComboBox()
        self.interp_combo.addItem("Linear")
        self.interp_combo.addItem("PCHIP")

        style = "padding: 4px 12px; text-align: left;"
        self.saveInterpolation_button = QPushButton("Save interpolation", self)
        self.saveInterpolation_button.setStyleSheet(style)
        self.saveInterpolation_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.saveInterpolationAndSeriesInterpolated_button = QPushButton("Save interpolation and series interpolated", self)
        self.saveInterpolationAndSeriesInterpolated_button.setStyleSheet(style)
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet(style)

        buttonsGroup1_layout = QHBoxLayout()
        buttonsGroup1_layout.addWidget(self.interp_combo_label)
        buttonsGroup1_layout.addWidget(self.interp_combo)
        buttonsGroup1_layout.addWidget(self.showInterp)
        buttonsGroup1_layout.addWidget(self.removeAddLastConnect_button)
        buttonsGroup1_layout.addStretch()
        control_layout3.addLayout(buttonsGroup1_layout)
        
        saveClose_layout = QVBoxLayout()
        saveClose_layout.addWidget(self.saveInterpolation_button)
        saveCloseLine_layout = QHBoxLayout()
        saveCloseLine_layout.addWidget(self.saveInterpolationAndSeriesInterpolated_button)
        saveCloseLine_layout.addWidget(self.close_button)
        saveClose_layout.addLayout(saveCloseLine_layout)
        control_layout3.addLayout(saveClose_layout)
        control_layout3.setAlignment(buttonsGroup1_layout, AlignBottom)
        #control_layout3.setAlignment(saveClose_layout, AlignBottom)

        main_layout.addLayout(control_layout3)

        self.showInterp.stateChanged.connect(self.showInterp_change)
        self.removeAddLastConnect_button.clicked.connect(self.removeAddLastConnect)
        self.interp_combo.currentIndexChanged.connect(self.interpMode_change)
        self.saveInterpolation_button.clicked.connect(self.saveInterpolation)
        self.saveInterpolationAndSeriesInterpolated_button.clicked.connect(self.saveInterpolationAndSeriesInterpolated)
        self.close_button.clicked.connect(self.close)

        #----------------------------------------------
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(20)
        self.status_bar.setSizeGripEnabled(False)

        main_layout.addWidget(self.status_bar)

        #----------------------------------------------
        self.setLayout(main_layout)

        self.myplot()

        menu_bar = QMenuBar(self)
        main_layout.setMenuBar(menu_bar)

        close_shortcut = QShortcut(QKeySequenceClose, self)
        close_shortcut.activated.connect(self.close)

        self.interactive_plot.fig.canvas.setFocus()

    #---------------------------------------------------------------------------------------------
    def removeAddLastConnect(self):

        if not self.artistsList_LastId: return

        connect, vline1, vline2  = self.artistsList_LastValues

        if self.artistsList_LastId in self.artistsList_Dict.keys():
            for artist in self.artistsList_LastValues:
                artist.remove()
            del self.artistsList_Dict[self.artistsList_LastId]
            self.vline1List.remove(vline1)
            self.vline2List.remove(vline2)
            self.removeAddLastConnect_button.setText("Reposition last connection")
            self.removeAddLastConnect_button.setShortcut("u")
        else:
            self.artistsList_Dict[self.artistsList_LastId] = self.artistsList_LastValues
            self.interactive_plot.fig.add_artist(connect)
            self.interactive_plot.axs[0].add_artist(vline1)
            self.interactive_plot.axs[1].add_artist(vline2)
            self.vline1List.append(vline1)
            self.vline2List.append(vline2)
            self.removeAddLastConnect_button.setText("Remove last connection")
            self.removeAddLastConnect_button.setShortcut("u")

        self.updatePointers()
        self.updateInterpPlot()

    #---------------------------------------------------------------------------------------------
    def selectSeries_change(self):

        xlim0 = self.axs[0].get_xlim()      # keep axs[0] range 
        xlim1 = self.axs[1].get_xlim()      # keep axs[1] range 

        if self.second_xaxis is not None:
            self.second_xaxis.remove()
            self.second_xaxis = None

        self.deleteConnections()
        self.axs[0].clear()
        self.axs[1].clear()
        self.axsInterp.clear()
        self.axsInterp.relim()          # reinit range
        self.itemINTERPOLATION = None
        self.myplot()

        self.axs[0].set_xlim(xlim0)
        self.axs[1].set_xlim(xlim1)

        self.updateConnections()

    #---------------------------------------------------------------------------------------------
    def showInterp_change(self):

        if len(self.X1Coords) < 2: 
            msg = 'Warning: interpolation function not defined (not enough pointers)'
            self.status_bar.showMessage(msg, 5000)
            return None

        self.updateInterpPlot()

    #---------------------------------------------------------------------------------------------
    def interpMode_change(self):

        self.interpolationMode = self.interp_combo.currentText()
        self.updateInterpPlot()

    #---------------------------------------------------------------------------------------------
    def readINTERPOLATION(self):

        self.interpolationDict = self.itemINTERPOLATION.data(0, Qt.ItemDataRole.UserRole)
        self.X1Coords = self.interpolationDict['X1Coords']
        self.X2Coords = self.interpolationDict['X2Coords']

    #---------------------------------------------------------------------------------------------
    def myplot(self):

        if self.itemINTERPOLATION:
            self.readINTERPOLATION()

        self.drawPlots()
        self.drawConnections()
        self.updatePointers()
        self.updateInterpPlot()

    #---------------------------------------------------------------------------------------------
    def updateInterpPlot(self):

        if self.second_xaxis is not None:
            self.second_xaxis.remove()
            self.second_xaxis = None

        self.axsInterp.set_visible(False)
        self.axsInterp.clear()
        self.interactive_plot.fig.canvas.draw()
        
        if len(self.X1Coords) < 2: return
        if not self.showInterp.isChecked(): return
        
        self.axsInterp.set_visible(True)

        f_1to2, f_2to1 = self.defineInterpolationFunctions(self.X1Coords, self.X2Coords, interpolationMode=self.interpolationMode)

        if self.second_xaxis: self.second_xaxis.remove()
        self.second_xaxis = self.axsInterp.secondary_xaxis('top', functions=(f_1to2, f_2to1))
        self.second_xaxis.tick_params(labelrotation=30)
        self.second_xaxis.set_xlabel(self.X2Name, color=self.series2Color)
        plt.setp(self.second_xaxis.get_xticklabels(), horizontalalignment='left')

        X2Interp = f_2to1(self.X2)
        self.line2Interp, = self.axsInterp.plot(X2Interp, self.Y2, color=self.series2Color, alpha=0.8, linewidth=self.seriesWidth, label='line2Interp')
        self.axsInterp.set_ylabel(self.Y2Name, color=self.series2Color)
        self.axsInterp.yaxis.set_label_position('right')

        self.updateConnections()
        self.interactive_plot.fig.canvas.draw()
        self.interactive_plot.fig.canvas.setFocus()

    #---------------------------------------------------------------------------------------------
    def updatePointersPlot(self):

        self.pointersPlot_ax.set_visible(True)
        self.pointersPlot_ax.clear()
        for line in self.pointersPlot_axGradient.lines:     # do no use clear() to keep settings
            line.remove()
        self.interactive_pointersPlot.fig.canvas.draw()

        if len(self.X1Coords) < 2: return

        #------------------------------------------------
        legendHandles = []

        line, = self.pointersPlot_ax.plot(self.X2Coords, self.X1Coords, color='steelblue', linewidth=1, label='Pointers')
        points = self.pointersPlot_ax.scatter(self.X2Coords, self.X1Coords, s=10, marker='o', color='steelblue', visible=False)

        self.pointersPlot_ax.patch.set_visible(False)
        self.pointersPlot_ax.grid(visible=True, which='major', color='lightgray', linestyle='dashed', linewidth=1)
        self.pointersPlot_ax.set_xlabel(self.X2Name)
        self.pointersPlot_ax.set_ylabel(self.X1Name, color='steelblue')
        legendHandle = Line2D([0], [0], color='steelblue', label='Pointers')
        legendHandles.append(legendHandle)
        self.pointersPlot_ax.line_points_pairs.append((line, points))

        self.pointersPlot_axGradient.set_ylabel('Gradients (dx/dy)', color='darkorange')
        self.pointersPlot_axGradient.line_points_pairs = []
        self.interactive_pointersPlot.axs.append(self.pointersPlot_axGradient)

        npoints = self.gradientSamplePoints_spin.value()
        X2CoordsValues = np.linspace(self.X2Coords[0], self.X2Coords[-1], npoints)

        f_1to2, f_2to1 = self.defineInterpolationFunctions(self.X1Coords, self.X2Coords, interpolationMode='Linear')
        gradientLinear = np.gradient(X2CoordsValues, f_2to1(X2CoordsValues)).astype(np.float32)      # to avoid unnecessary precision
        line1, = self.pointersPlot_axGradient.plot(X2CoordsValues, gradientLinear, color='darkorange', lw=1, label='Linear')
        legendHandle = Line2D([0], [0], color='darkorange', label='Linear')
        legendHandles.append(legendHandle)

        f_1to2, f_2to1 = self.defineInterpolationFunctions(self.X1Coords, self.X2Coords, interpolationMode='PCHIP')
        gradientPCHIP = np.gradient(X2CoordsValues, f_2to1(X2CoordsValues)).astype(np.float32)       # to avoid unnecessary precision
        line2, = self.pointersPlot_axGradient.plot(X2CoordsValues, gradientPCHIP, color='darkorange', linestyle='dashed', lw=1, label='PCHIP')
        legendHandle = Line2D([0], [0], color='darkorange', linestyle='dashed', label='PCHIP')
        legendHandles.append(legendHandle)

        legend = self.pointersPlot_ax.legend(handles=legendHandles)
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
    def updatePointers(self):

        self.X1Coords = sorted([float(line.get_xdata()[0]) for line in self.vline1List])
        self.X2Coords = sorted([float(line.get_xdata()[0]) for line in self.vline2List])

        self.pointers_table.clearContents()

        self.pointers_table.setRowCount(len(self.X1Coords))
        self.pointers_table.setColumnCount(2)
        self.pointers_table.setHorizontalHeaderLabels([
            f"Distorted: X",
            f"Reference: {self.X1Name}", 
        ])
        for i in range(len(self.X1Coords)):
            self.pointers_table.setItem(i, 0, QTableWidgetItem(str(f'{self.X2Coords[i]:.6f}')))
            self.pointers_table.setItem(i, 1, QTableWidgetItem(str(f'{self.X1Coords[i]:.6f}')))
            background_color = QColor('white') if i % 2 == 0 else QColor('whitesmoke')
            self.pointers_table.item(i, 0).setBackground(background_color)
            self.pointers_table.item(i, 1).setBackground(background_color)
        self.pointers_table.resizeColumnsToContents()
        self.pointers_table.set_italic_headers()

        self.updatePointersPlot()
        self.updateGradients()

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
        f_1to2, f_2to1 = self.defineInterpolationFunctions(
            self.X1Coords,
            self.X2Coords,
            interpolationMode='Linear'
        )
        X1Linear = f_2to1(X2Values)
        gradientLinear = np.gradient(X2Values, X1Linear).astype(np.float32)
    
        # PCHIP
        f_1to2, f_2to1 = self.defineInterpolationFunctions(
            self.X1Coords,
            self.X2Coords,
            interpolationMode='PCHIP'
        )
        X1PCHIP = f_2to1(X2Values)
        gradientPCHIP = np.gradient(X2Values, X1PCHIP).astype(np.float32)
    
        self.gradients_table.setRowCount(npoints)
        self.gradients_table.setColumnCount(3)
        self.gradients_table.setHorizontalHeaderLabels([
            f"Distorted: X",
            "Gradient Linear",
            "Gradient PCHIP",
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
    def drawPlots(self):

        #----------------------------------------------------
        # self.axs[0] --> Reference 
        # self.axs[1] --> Distorted to interpolate

        #----------------------------------------------------
        self.itemRef = self.items[self.selectSeriesRef_combo.currentIndex()]

        self.series1Dict = self.itemRef.data(0, Qt.ItemDataRole.UserRole)
        self.X1Name = self.series1Dict['X']
        self.Y1Name = self.series1Dict['Y']
        self.series1 = self.series1Dict['Series']
        self.series1 = self.series1.groupby(self.series1.index).mean()
        self.X1 = self.series1.index
        self.Y1 = self.series1.values

        self.axs[0].grid(visible=True, which='major', color='lightgray', linestyle='dashed', linewidth=0.5)
        self.axs[0].set_xlabel(self.X1Name)
        self.axs[0].set_ylabel(self.Y1Name)
        self.axs[0].patch.set_alpha(0)
        self.axs[0].line_points_pairs = []

        self.series1Color = self.series1Dict['Color']

        self.line1, = self.axs[0].plot(self.X1, self.Y1, color=self.series1Color, linewidth=self.seriesWidth, label='line1', picker=True, pickradius=20)
        self.points1 = self.axs[0].scatter(self.X1, self.Y1, s=5, marker='o', color=self.series1Color, visible=False, label='points1', picker=True, pickradius=5)
        self.axs[0].line_points_pairs.append((self.line1, self.points1))

        self.linecursor1 = self.axs[0].axvline(color='k', alpha=0.25, linewidth=1)

        axis_settings = self.series1Dict.get("AxisSettings")
        self.interactive_plot.apply_axis_settings(self.axs[0], axis_settings)

        #----------------------------------------------------
        self.itemDist = self.items[self.selectSeriesDist_combo.currentIndex()]

        self.series2Dict = self.itemDist.data(0, Qt.ItemDataRole.UserRole)
        self.X2Name = self.series2Dict['X']
        self.Y2Name = self.series2Dict['Y']
        self.series2 = self.series2Dict['Series']
        self.series2 = self.series2.groupby(self.series2.index).mean()
        self.X2 = self.series2.index
        self.Y2 = self.series2.values

        self.axs[1].grid(visible=True, which='major', color='lightgray', linestyle='dashed', linewidth=0.5)
        self.axs[1].set_xlabel(self.X2Name)
        self.axs[1].set_ylabel(self.Y2Name)
        self.axs[1].patch.set_alpha(0)
        self.axs[1].line_points_pairs = []

        self.series2Color = self.series2Dict['Color']

        self.line2, = self.axs[1].plot(self.X2, self.Y2, color=self.series2Color, linewidth=self.seriesWidth, label='line2', picker=True, pickradius=20)
        self.points2 = self.axs[1].scatter(self.X2, self.Y2, s=5, marker='o', color=self.series2Color, visible=False, label='points2', picker=True, pickradius=5)
        self.axs[1].line_points_pairs.append((self.line2, self.points2))

        self.linecursor2 = self.axs[1].axvline(color='k', alpha=0.25, linewidth=1)

        axis_settings = self.series2Dict.get("AxisSettings")
        self.interactive_plot.apply_axis_settings(self.axs[1], axis_settings)

        #----------------------------------------------------
        self.interactive_plot.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.interactive_plot.fig.canvas.mpl_connect('key_release_event', self.on_key_release)
        self.interactive_plot.fig.canvas.mpl_connect('pick_event', self.on_mouse_pick)
        self.interactive_plot.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)
        self.interactive_plot.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.interactive_plot.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.interactive_plot.fig.canvas.mpl_connect('scroll_event', self.on_mouse_scroll)

        #----------------------------------------------------
        self.interactive_plot.fig.canvas.draw()
        self.interactive_plot.fig.canvas.setFocus()

    #---------------------------------------------------------------------------------------------
    def drawConnections(self):

        redefine_LastId = False
        if self.artistsList_LastId:
            connect, vline1_Last, vline2_Last  = self.artistsList_LastValues
            redefine_LastId = True

        self.artistsList_Dict = {}
        self.vline1List = []
        self.vline2List = []

        found_Last_Id = False
        for i in range(len(self.X1Coords)):
            X1Coord = self.X1Coords[i]
            X2Coord = self.X2Coords[i]
            vline1 = self.axs[0].axvline(X1Coord, color=self.pointerColor, alpha=0.5, linestyle='--', linewidth=1, label='vline1')
            vline2 = self.axs[1].axvline(X2Coord, color=self.pointerColor, alpha=0.5, linestyle='--', linewidth=1, label='vline2')
            connect = ConnectionPatch(color=self.pointerColor, alpha=0.5, linewidth=1, picker=10, clip_on=True, label='connection',
                        xyA=(X1Coord, self.axs[0].get_ylim()[0]), coordsA=self.axs[0].transData,
                        xyB=(X2Coord, self.axs[1].get_ylim()[1]), coordsB=self.axs[1].transData)
            self.interactive_plot.fig.add_artist(connect)
            self.vline1List.append(vline1)
            self.vline2List.append(vline2)
            self.artistsList_Dict[id(connect)] = [connect, vline1, vline2]
    
            if redefine_LastId:
                if (vline1.get_xdata() == vline1_Last.get_xdata()) and (vline2.get_xdata() == vline2_Last.get_xdata()):
                    self.artistsList_LastId = id(connect)
                    self.artistsList_LastValues = [connect, vline1, vline2]
                    self.removeAddLastConnect_button.setEnabled(True)

        self.interactive_plot.fig.canvas.draw()
        self.interactive_plot.fig.canvas.setFocus()

    #---------------------------------------------------------------------------------------------
    def updateConnections(self):

        for artistsList in self.artistsList_Dict.values():
            if isinstance(artistsList[0], ConnectionPatch):
                connect = artistsList[0]
                x1, y1 = connect.xy1
                connect.xy1 = (x1, self.axs[0].get_ylim()[0])
                x2, y2 = connect.xy2
                connect.xy2 = (x2, self.axs[1].get_ylim()[1])
                if ((self.axs[0].get_xlim()[0] < x1 < self.axs[0].get_xlim()[1]) and
                    (self.axs[1].get_xlim()[0] < x2 < self.axs[1].get_xlim()[1])):
                    connect.set_visible(True)
                else:
                    connect.set_visible(False)

        self.interactive_plot.fig.canvas.draw()
        self.interactive_plot.fig.canvas.setFocus()

    #---------------------------------------------------------------------------------------------
    def deleteConnections(self):

        for objectId in self.artistsList_Dict.keys():
            for artist in self.artistsList_Dict[objectId]:
                artist.remove()
        self.artistsList_Dict = {}

        if self.vline1 != None: self.vline1.remove();
        if self.vline2 != None: self.vline2.remove();

        self.vline1List = []
        self.vline2List = []
        self.vline1 = None
        self.vline2 = None

    #---------------------------------------------------------------------------------------------
    def deleteCoords(self):
    
        self.itemINTERPOLATION = None
        self.X1Coords = []
        self.X2Coords = []

    #---------------------------------------------------------------------------------------------
    def on_key_press(self, event):

        sys.stdout.flush()

        #-------------------
        if event.key == 'c':
            if self.vline1 != None and self.vline2 != None :
                X1Coord = float(self.vline1.get_xdata()[0])
                X2Coord = float(self.vline2.get_xdata()[0])
                # current X1Coords, X2Coords. Will be defined later from setInterp
                X1Coords_cur = sorted([float(line.get_xdata()[0]) for line in self.vline1List])
                X2Coords_cur = sorted([float(line.get_xdata()[0]) for line in self.vline2List])
                # Check positions
                if np.searchsorted(X1Coords_cur, X1Coord) != np.searchsorted(X2Coords_cur, X2Coord):
                    msg = 'Error: Connection not possible because it would cross existing connections'
                    self.status_bar.showMessage(msg, 5000)
                    return

                connect = ConnectionPatch(color=self.pointerColor, alpha=0.5, linewidth=1, picker=10, clip_on=True, label='connection',
                            xyA=(X1Coord, self.axs[0].get_ylim()[0]), coordsA=self.axs[0].transData,
                            xyB=(X2Coord, self.axs[1].get_ylim()[1]), coordsB=self.axs[1].transData)
                self.interactive_plot.fig.add_artist(connect)
                self.artistsList_Dict[id(connect)] = [connect, self.vline1, self.vline2]
                self.artistsList_LastId = id(connect)
                self.artistsList_LastValues = [connect, self.vline1, self.vline2]
                self.removeAddLastConnect_button.setEnabled(True)
                self.removeAddLastConnect_button.setText("Remove last connection")
                self.removeAddLastConnect_button.setShortcut("u")
                self.vline1List.append(self.vline1)
                self.vline2List.append(self.vline2)
                self.vline1 = None
                self.vline2 = None

                self.updatePointers()
                self.updateInterpPlot()
                self.interactive_plot.fig.canvas.draw()
                self.interactive_plot.fig.canvas.setFocus()

        #-------------------
        elif event.key == 'a':
            self.updateConnections()

        #-------------------
        elif event.key == 'z':
            #self.selectSeries_change()
            self.showInterp.setChecked(not self.showInterp.isChecked())
            self.showInterp_change()

        #-------------------
        elif event.key == 'Z':
            self.axs[1].set_ylim(self.axs[0].get_ylim())
            self.updateConnections()
            self.showInterp.setChecked(not self.showInterp.isChecked())
            self.showInterp_change()

        #-------------------
        elif event.key == 'x':
            self.key_x = True 

        #-------------------
        elif event.key == 'X':
            reply = QMessageBox.question(
                self, 
                'Confirmation', 
                'Are you sure you want to delete all pointers ?', 
                MessageBoxYes | MessageBoxNo, 
                MessageBoxNo
            )

            if reply == MessageBoxYes:
                self.artistsList_LastId = None
                self.removeAddLastConnect_button.setEnabled(False)
                self.removeAddLastConnect_button.setText("Remove last connection")
                self.removeAddLastConnect_button.setShortcut("u")
                self.deleteConnections()
                self.deleteCoords()
                self.updatePointers()
                self.updateInterpPlot()
                self.interactive_plot.fig.canvas.draw()
                self.interactive_plot.fig.canvas.setFocus()

        #-------------------
        elif event.key == 'shift':
            self.key_shift = True

        #-------------------
        elif event.key == 'control':
            self.key_control = True

    #------------------------------------------------------------------
    def on_key_release(self, event):

        sys.stdout.flush()

        #-------------------
        if event.key == 'x':
            self.key_x = False

        #-------------------
        elif event.key == 'shift':
            self.key_shift = False

        #-------------------
        elif event.key == 'control':
            self.key_control = False 

    #------------------------------------------------------------------
    def on_mouse_press(self, event):

        #if event.inaxes not in self.axs: return

        self.mousepress = None
        if event.button == 1:
            self.mousepress = 'left'

        self.updateConnections()

    #------------------------------------------------------------------
    def on_mouse_release(self, event):

        self.mousepress = None

    #------------------------------------------------------------------
    def on_mouse_scroll(self, event):

        self.updateConnections()

    #------------------------------------------------------------------
    def on_mouse_pick(self, event):
    
        artistLabel = event.artist.get_label()
   
        #-----------------------------------------------
        if artistLabel == 'connection':
            if self.key_x:

                if self.vline1 != None: self.vline1.remove();
                if self.vline2 != None: self.vline2.remove();

                objectId = id(event.artist)
                self.removeAddLastConnect_button.setEnabled(False)

                connect, vline1, vline2  = self.artistsList_Dict[objectId];
                connect.remove()
                self.vline1List.remove(vline1)
                self.vline2List.remove(vline2)
                self.vline1 = vline1
                self.vline2 = vline2

                del self.artistsList_Dict[objectId]

                self.updatePointers()
                self.updateInterpPlot()
                
        #-----------------------------------------------
        if artistLabel in ['line1', 'line2']:
            if self.key_shift:
                coordPoint = [event.mouseevent.xdata, event.mouseevent.ydata]
                if event.artist == self.line1:
                    if self.vline1 != None:
                        self.vline1.set_data([coordPoint[0], coordPoint[0]], [0, 1])
                    else:
                        self.vline1 = self.axs[0].axvline(coordPoint[0], color=self.pointerColor , alpha=0.5, linestyle='--', linewidth=1, label='vline1')
                elif event.artist == self.line2:
                    if self.vline2 != None:
                        self.vline2.set_data([coordPoint[0], coordPoint[0]], [0, 1])
                    else:
                        self.vline2 = self.axs[1].axvline(coordPoint[0], color=self.pointerColor, alpha=0.5, linestyle='--', linewidth=1, label='vline2')
                self.interactive_plot.fig.canvas.draw()
                self.interactive_plot.fig.canvas.setFocus()
   
        #-----------------------------------------------
        elif artistLabel in ['points1', 'points2']:
            if self.key_control:
                ind = event.ind[0]
                if event.artist == self.points1:
                    coordPoint = [self.X1[ind], self.Y1[ind]]
                    if self.vline1 != None:
                        self.vline1.set_data([coordPoint[0], coordPoint[0]], [0, 1])
                    else:
                        self.vline1 = self.axs[0].axvline(coordPoint[0], color=self.pointerColor , alpha=0.5, linestyle='--', linewidth=1, label='vline1')
                elif event.artist == self.points2:
                    coordPoint = [self.X2[ind], self.Y2[ind]]
                    if self.vline2 != None:
                        self.vline2.set_data([coordPoint[0], coordPoint[0]], [0, 1])
                    else:
                        self.vline2 = self.axs[1].axvline(coordPoint[0], color=self.pointerColor, alpha=0.5, linestyle='--', linewidth=1, label='vline2')
                self.interactive_plot.fig.canvas.draw()
                self.interactive_plot.fig.canvas.setFocus()

    #------------------------------------------------------------------
    def on_mouse_motion(self, event):

        #-----------------------------------------------
        found = False
        for artistsList in self.artistsList_Dict.values():
            if isinstance(artistsList[0], ConnectionPatch):
                connect = artistsList[0]
                if connect.contains(event)[0]:
                    connect.set_color('red')
                    found = True 
                else:
                    connect.set_color(self.pointerColor)
        if found:
            self.interactive_plot.fig.canvas.draw()
            self.interactive_plot.fig.canvas.setFocus()
            #self.interactive_plot.fig.canvas.draw_idle()

        #-----------------------------------------------
        if event.inaxes is self.interactive_plot.axs[0]:
            self.linecursor1.set_visible(True)
            self.linecursor2.set_visible(False)
            self.linecursor1.set_xdata([event.xdata])
        elif event.inaxes is self.interactive_plot.axs[1]:
            self.linecursor1.set_visible(False)
            self.linecursor2.set_visible(True)
            self.linecursor2.set_xdata([event.xdata])
        else:
            self.linecursor1.set_visible(False)
            self.linecursor2.set_visible(False)
            self.points1.set_visible(False)
            self.points2.set_visible(False)
        self.interactive_plot.fig.canvas.draw()
        self.interactive_plot.fig.canvas.setFocus()

        #-----------------------------------------------
        if self.mousepress == 'left':
            self.updateConnections()

    #---------------------------------------------------------------------------------------------
    @staticmethod
    def safe_PchipInterpolator(X1Coords, X2Coords):
        f_pchip = interpolate.PchipInterpolator(X1Coords, X2Coords, extrapolate=False)
    
        def extrapolated_func(x):
            if x < X1Coords[0]:
                slope = (X2Coords[1] - X2Coords[0]) / (X1Coords[1] - X1Coords[0])
                return X2Coords[0] + slope * (x - X1Coords[0])
            elif x > X1Coords[-1]:
                slope = (X2Coords[-1] - X2Coords[-2]) / (X1Coords[-1] - X1Coords[-2])
                return X2Coords[-1] + slope * (x - X1Coords[-1])
            else:
                return f_pchip(x)
    
        return np.vectorize(extrapolated_func, otypes=[float])  

    #---------------------------------------------------------------------------------------------
    @staticmethod
    def defineInterpolationFunctions(X1Coords, X2Coords, interpolationMode='Linear'):
        if interpolationMode == 'Linear':
            f_1to2 = interpolate.interp1d(X1Coords, X2Coords, kind='linear', fill_value='extrapolate')
            f_2to1 = interpolate.interp1d(X2Coords, X1Coords, kind='linear', fill_value='extrapolate')
        elif interpolationMode == 'PCHIP':
            #f_1to2 = interpolate.PchipInterpolator(X1Coords, X2Coords, extrapolate=True)
            #f_2to1 = interpolate.PchipInterpolator(X2Coords, X1Coords, extrapolate=True)
            f_1to2 = defineInterpolationWindow.safe_PchipInterpolator(X1Coords, X2Coords)
            f_2to1 = defineInterpolationWindow.safe_PchipInterpolator(X2Coords, X1Coords)

        return (f_1to2, f_2to1)

    #---------------------------------------------------------------------------------------------
    def saveInterpolation(self):

        if len(self.X1Coords) < 2: 
            msg = 'Warning: interpolation function not defined (not enough pointers)'
            self.status_bar.showMessage(msg, 5000)
            return None

        interpolation_Id = generate_Id()
        interpolationDict = {
            'Id': interpolation_Id,
            'Type': 'INTERPOLATION',
            'Name': 'Pointers', 
            'X1Coords': self.X1Coords,
            'X2Coords': self.X2Coords,
            'X1Name': self.X1Name,              # interpolated to reference that is X1
            'Date': datetime.datetime.now().strftime("Created %Y/%m/%d at %H:%M:%S"),
            'History': f'INTERPOLATION <i><b>{interpolation_Id}</i></b>',
            'Comment': ''
        }

        # Fixed sync issue causing stale pointer reload by resetting self.itemINTERPOLATION
        self.itemINTERPOLATION = None

        try:
            self.add_item_tree_widget(self.itemRef.parent(), interpolationDict)
        except:
            pass

        return interpolation_Id

    #---------------------------------------------------------------------------------------------
    def saveInterpolationAndSeriesInterpolated(self):

        interpolation_Id = self.saveInterpolation()
        if interpolation_Id is None:
            return

        f_1to2, f_2to1 = self.defineInterpolationFunctions(self.X1Coords, self.X2Coords, interpolationMode=self.interpolationMode)

        #series_interpolated = pd.Series(self.Y2, index=f_2to1(self.X2))

        # to keep replicates
        series2 = self.series2Dict['Series']
        series_interpolated = pd.Series(series2.values, index=f_2to1(series2.index))

        interpolated_Id = generate_Id()
        interpolated_seriesDict = self.series2Dict | {'Id': interpolated_Id, 
            'Type': 'Series interpolated', 
            'Series': series_interpolated,
            'InterpolationMode': self.interpolationMode,
            'X': self.X1Name,
            'XOriginal': self.X2Name,
            'XOriginalValues': series2.index.to_list(),
            'X1Coords': self.X1Coords,
            'X2Coords': self.X2Coords,
            'Color': generate_color(exclude_color=self.series2Dict['Color']),
            'Date': datetime.datetime.now().strftime("Created %Y/%m/%d at %H:%M:%S"),
            'History': append_to_htmlText(self.series2Dict['History'], 
                f'Series <i><b>{self.series2Dict["Id"]}</i></b> interpolated with INTERPOLATION <i><b>{interpolation_Id}</i></b> with mode {self.interpolationMode}<BR>---> series <i><b>{interpolated_Id}</b></i>'),
            'Comment': ''
        }

        try:
            position = self.itemDist.parent().indexOfChild(self.itemDist)
            self.add_item_tree_widget(self.itemDist.parent(), interpolated_seriesDict, position+1)
        except:
            pass

    #---------------------------------------------------------------------------------------------
    def closeEvent(self, event):
        plt.close()
        self.open_interpolationWindows.pop(self.Id, None)
        event.accept()

#=========================================================================================
# Example usage
if __name__ == "__main__":

    def handle_item(parent, item):
        print('handle', parent, item)

    app = QApplication([])

    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.cos(2*x)+4

    series1 = pd.Series(y1, index=x)
    series1Dict = {'Id': 'abcd', 'X': 'x1Name', 'Y': 'y1Name', 'Series': series1, 
            'Color': 'darkorange',
            'Date': '', 'Comment': 'A text', 'History': 'command1 ; command2'}
    item1 = QTreeWidgetItem()
    item1.setData(0, Qt.ItemDataRole.UserRole, series1Dict)

    series2 = pd.Series(y2, index=x)
    series2Dict = {'Id': 'abcd', 'X': 'x2Name', 'Y': 'y2Name', 'Series': series2, 
            'Color': 'blue',
            'Date': '', 'Comment': 'A text', 'History': 'command1 ; command2'}
    item2 = QTreeWidgetItem()
    item2.setData(0, Qt.ItemDataRole.UserRole, series2Dict)

    series3 = pd.Series(y3, index=x)
    series3Dict = {'Id': 'abcd', 'X': 'x3Name', 'Y': 'y3Name', 'Series': series3, 
            'Color': 'green',
            'Date': '', 'Comment': 'A text', 'History': 'command1 ; command2'}
    item3 = QTreeWidgetItem()
    item3.setData(0, Qt.ItemDataRole.UserRole, series3Dict)

    open_interpolationWindows = {}
    Id_interpolationWindow = '1234'
    interpolationWindow = defineInterpolationWindow(Id_interpolationWindow, open_interpolationWindows, None, 
                            [item1, item2, item3], handle_item)
    open_interpolationWindows[Id_interpolationWindow] = interpolationWindow
    interpolationWindow.show()

    sys.exit(app_exec(app))
