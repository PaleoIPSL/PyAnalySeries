from resources.qt_compat import *

import sys
import datetime
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import LogLocator, FuncFormatter

from .misc import *
from .interactivePlot import interactivePlot

import pyleoclim as pyleo
matplotlib.rcdefaults()

#=========================================================================================
for key in plt.rcParams.keys():
    if key.startswith('keymap.'):
        plt.rcParams[key] = []

#=========================================================================================
class computePowerSpectrumWindow(QWidget):
    METHOD_PERIOD = 'Periodogram'
    METHOD_WELCH = 'Welch'
    METHOD_MTM = 'MTM'
    METHOD_LOMB = 'Lomb-Scargle'
    METHOD_WWZ = 'Wavelet (WWZ)'

    DOC_PERIOD = "https://pyleoclim-util.readthedocs.io/en/latest/utils/introduction.html#pyleoclim.utils.spectral.periodogram"
    DOC_WELCH = "https://pyleoclim-util.readthedocs.io/en/latest/utils/introduction.html#pyleoclim.utils.spectral.welch"
    DOC_MTM = "https://pyleoclim-util.readthedocs.io/en/latest/utils/introduction.html#pyleoclim.utils.spectral.mtm"
    DOC_LOMB = "https://pyleoclim-util.readthedocs.io/en/latest/utils/introduction.html#pyleoclim.utils.spectral.lomb_scargle"
    DOC_WWZ = "https://pyleoclim-util.readthedocs.io/en/latest/utils/introduction.html#pyleoclim.utils.spectral.wwz_psd"

    #---------------------------------------------------------------------------------------------
    def __init__(self, Id, open_powerSpectrumWindows, item, add_item_tree_widget):
        super().__init__()

        self.Id = Id
        self.open_powerSpectrumWindows = open_powerSpectrumWindows
        self.item = item
        self.add_item_tree_widget = add_item_tree_widget

        self.psd_results = []
        self.seriesDict = None

        title = 'Compute Power Spectrum (PSD) : ' + self.Id
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 1200, 800)
        self.setMinimumSize(900, 650)

        main_layout = QVBoxLayout()

        #----------------------------------------------
        groupbox1 = QGroupBox('Parameters:')
        groupbox1_layout = QVBoxLayout()

        top_row_layout = QHBoxLayout()

        self.method_combo = QComboBox(self)
        self.method_combo.addItems([
            self.METHOD_PERIOD,
            self.METHOD_WELCH,
            self.METHOD_MTM,
            self.METHOD_LOMB,
            self.METHOD_WWZ,
        ])
        self.method_combo.setFixedWidth(180)
        self.method_combo.currentTextChanged.connect(self.update_parameter_page)
        self.method_combo.currentTextChanged.connect(self.update_method_info)

        self.compute_button = QPushButton('Compute', self)
        self.remove_button = QPushButton('Remove last', self)
        self.compute_button.setStyleSheet('padding: 4px 12px;')
        self.remove_button.setStyleSheet('padding: 4px 12px;')

        top_row_layout.addWidget(QLabel('Method:'))
        top_row_layout.addWidget(self.method_combo)
        top_row_layout.addSpacing(20)
        top_row_layout.addWidget(self.compute_button)
        top_row_layout.addWidget(self.remove_button)
        top_row_layout.addStretch()

        groupbox1_layout.addLayout(top_row_layout)

        #----------------------------------------------
        self.method_info_browser = QTextBrowser(self)
        self.method_info_browser.setOpenExternalLinks(True)
        self.method_info_browser.setMinimumHeight(100)
        self.method_info_browser.setStyleSheet("""
            QTextBrowser {
                background: #fafafa;
                border: 1px solid #d0d0d0;
                padding: 6px;
            }
        """)

        groupbox1_layout.addWidget(self.method_info_browser)

        #----------------------------------------------
        self.params_stack = QStackedWidget(self)
        self.params_stack.addWidget(self._build_periodogram_page())
        self.params_stack.addWidget(self._build_welch_page())
        self.params_stack.addWidget(self._build_mtm_page())
        self.params_stack.addWidget(self._build_lomb_page())
        self.params_stack.addWidget(self._build_wwz_page())
        groupbox1_layout.addWidget(self.params_stack)

        groupbox1.setLayout(groupbox1_layout)
        main_layout.addWidget(groupbox1, stretch=1)

        #----------------------------------------------
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.compute_psd)

        #----------------------------------------------
        self.interactive_plot = interactivePlot()
        canvas = FigureCanvas(self.interactive_plot.fig)
        main_layout.addWidget(canvas, stretch=3)

        #----------------------------------------------
        save_layout = QHBoxLayout()

        self.saved_psd_combo = QComboBox(self)
        self.saved_psd_combo.setMinimumWidth(360)

        self.save_button = QPushButton('Save PSD', self)
        self.close_button = QPushButton('Close', self)
        self.save_button.setStyleSheet('padding: 4px 12px;')
        self.close_button.setStyleSheet('padding: 4px 12px;')

        save_layout.addStretch()
        save_layout.addWidget(QLabel('PSD to save:'))
        save_layout.addWidget(self.saved_psd_combo)
        save_layout.addSpacing(12)
        save_layout.addWidget(self.save_button)
        save_layout.addSpacing(40)
        save_layout.addWidget(self.close_button)

        main_layout.addLayout(save_layout)

        #----------------------------------------------
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(20)
        self.status_bar.setSizeGripEnabled(False)

        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        #----------------------------------------------
        self.compute_button.clicked.connect(self.compute_psd)
        self.remove_button.clicked.connect(self.clear_plot)
        self.save_button.clicked.connect(self.save_series)
        self.close_button.clicked.connect(self.close)

        self.method_combo.currentTextChanged.connect(self.delayed_update)
        self.periodogram_window_combo.currentTextChanged.connect(self.delayed_update)
        self.welch_window_combo.currentTextChanged.connect(self.delayed_update)
        self.welch_nperseg_sb.valueChanged.connect(self.delayed_update)
        self.welch_overlap_sb.valueChanged.connect(self.delayed_update)
        self.mtm_nw_sb.valueChanged.connect(self.delayed_update)
        self.lomb_freq_combo.currentTextChanged.connect(self.delayed_update)
        self.wwz_freq_combo.currentTextChanged.connect(self.delayed_update)
        self.wwz_c_sb.valueChanged.connect(self.delayed_update)

        close_shortcut = QShortcut(QKeySequenceClose, self)
        close_shortcut.activated.connect(self.close)

        self.update_parameter_page(self.method_combo.currentText())
        self.update_method_info(self.method_combo.currentText())
        self._initialize_plot()

    #---------------------------------------------------------------------------------------------
    def update_method_info(self, method):

        if method == self.METHOD_PERIOD:
            html = f"""
            <b>Periodogram</b><br>
            Blackman-Tukey / periodogram-based spectral density estimation.<br><br>

            <b>Exposed parameter</b><br>
            <code>window</code>: tapering window applied before PSD estimation.<br><br>

            <b>Backend call</b><br>
            <code>ts.standardize().interp().spectral(method="periodogram", settings={{"window": ...}})</code><br><br>

            <b>Backend defaults not exposed here</b><br>
            <code>nfft=None</code>, <code>return_onesided=True</code>,
            <code>detrend=None</code>, <code>sg_kwargs=None</code>,
            <code>gaussianize=False</code>, <code>standardize=True</code>,
            <code>scaling='density'</code><br><br>

            <b>Documentation</b><br>
            <a href="{self.DOC_PERIOD}">pyleoclim.utils.spectral.periodogram</a>
            """

        elif method == self.METHOD_WELCH:
            html = f"""
            <b>Welch PSD</b><br>
            Spectral density estimated by averaging periodograms computed on overlapping segments.<br><br>

            <b>Exposed parameters</b><br>
            <code>window</code>: tapering window for each segment<br>
            <code>nperseg</code>: segment length<br>
            <code>overlap</code>: overlap between consecutive segments, expressed here in %<br><br>

            <b>Backend call</b><br>
            <code>ts.standardize().interp().spectral(method="welch", settings={{"window": ..., "nperseg": ..., "noverlap": ...}})</code><br><br>

            <b>Backend defaults not exposed here</b><br>
            <code>nfft=None</code>, <code>return_onesided=True</code>,
            <code>detrend=None</code>, <code>sg_kwargs=None</code>,
            <code>gaussianize=False</code>, <code>standardize=True</code>,
            <code>scaling='density'</code>, <code>average='mean'</code><br><br>

            <b>Documentation</b><br>
            <a href="{self.DOC_WELCH}">pyleoclim.utils.spectral.welch</a>
            """

        elif method == self.METHOD_MTM:
            html = f"""
            <b>MTM</b><br>
            Multi-Taper Method for spectral density estimation.<br><br>

            <b>Exposed parameter</b><br>
            <code>NW</code>: time-bandwidth product controlling spectral concentration and number of tapers.<br><br>

            <b>Backend call</b><br>
            <code>ts.standardize().interp().spectral(method="mtm", settings={{"NW": ...}})</code><br><br>

            <b>Backend defaults not exposed here</b><br>
            <code>BW=None</code>, <code>detrend=None</code>,
            <code>sg_kwargs=None</code>, <code>gaussianize=False</code>,
            <code>standardize=True</code>, <code>adaptive=False</code>,
            <code>jackknife=True</code>, <code>low_bias=True</code>,
            <code>sides='default'</code>, <code>nfft=None</code><br><br>

            <b>Backend note</b><br>
            If neither <code>NW</code> nor <code>BW</code> is specified, Pyleoclim uses a bandwidth
            equal to 4 times the fundamental frequency, corresponding to <code>NW = 4</code>.<br><br>

            <b>Documentation</b><br>
            <a href="{self.DOC_MTM}">pyleoclim.utils.spectral.mtm</a>
            """

        elif method == self.METHOD_LOMB:
            html = f"""
            <b>Lomb-Scargle</b><br>
            Periodogram designed for unevenly spaced time series.<br><br>

            <b>Exposed parameter</b><br>
            <code>freq</code>: frequency-grid strategy used by Pyleoclim.<br>

            <b>Backend call</b><br>
            <code>ts.standardize().spectral(method="lomb_scargle", freq=...)</code><br><br>

            <b>Backend defaults not exposed here</b><br>
            <code>freq=None</code>, <code>freq_kwargs=None</code>,
            <code>n50=3</code>, <code>window='hann'</code>,
            <code>detrend=None</code>, <code>sg_kwargs=None</code>,
            <code>gaussianize=False</code>, <code>standardize=True</code>,
            <code>average='mean'</code><br><br>

            <b>Documentation</b><br>
            <a href="{self.DOC_LOMB}">pyleoclim.utils.spectral.lomb_scargle</a>
            """

        elif method == self.METHOD_WWZ:
            html = f"""
            <b>WWZ PSD</b><br>
            Spectral estimation using the <b>Weighted Wavelet Z-transform</b>.<br>
            This method is designed for <b>unevenly spaced time series</b> and does
            <b>not rely on interpolation</b>.<br><br>
        
            <b>Exposed parameters</b><br>
            <code>Frequency-grid method</code>: strategy used to build the frequency vector<br>
            <code>Decay constant (c)</code>: controls the time/frequency resolution trade-off;
            smaller values give sharper spectral peaks<br><br>
        
            <b>Backend call</b><br>
            <code>ts.standardize().spectral(method="wwz", settings={{"freq_method": ..., "c": ...}})</code><br><br>
        
            <b>Backend defaults not exposed here</b><br>
            <code>freq=None</code>, <code>freq_method='log'</code>,
            <code>freq_kwargs=None</code>, <code>tau=None</code>,
            <code>c=0.001</code>, <code>nproc=8</code>,
            <code>detrend=False</code>, <code>sg_kwargs=None</code>,
            <code>gaussianize=False</code>, <code>standardize=True</code>,
            <code>Neff_threshold=3</code>, <code>anti_alias=False</code>,
            <code>avgs=2</code>, <code>method='Kirchner_numba'</code><br><br>
        
            <b>Backend note</b><br>
            Pyleoclim documents <code>c</code> as the main adjustable parameter.
            The default value <code>1e-3</code> is recommended for most spectral-analysis use cases.<br><br>
        
            <b>Documentation</b><br>
            <a href="{self.DOC_WWZ}">pyleoclim.utils.spectral.wwz_psd</a>
            """

        else:
            html = ""

        self.method_info_browser.setHtml(html)

    #---------------------------------------------------------------------------------------------
    def _build_periodogram_page(self):

        page = QWidget()
        layout = QFormLayout(page)

        layout.setFormAlignment(AlignTop | AlignLeft)
        layout.setLabelAlignment(AlignLeft)

        self.periodogram_window_combo = QComboBox(self)
        self.periodogram_window_combo.addItems(['hann', 'boxcar', 'blackman'])
        self.periodogram_window_combo.setFixedWidth(140)

        layout.addRow('Taper window:', self.periodogram_window_combo)
        return page

    #---------------------------------------------------------------------------------------------
    def _build_welch_page(self):

        page = QWidget()
        layout = QFormLayout(page)

        layout.setFormAlignment(AlignTop | AlignLeft)
        layout.setLabelAlignment(AlignLeft)

        self.welch_window_combo = QComboBox(self)
        self.welch_window_combo.addItems(['hann', 'boxcar', 'blackman'])
        self.welch_window_combo.setFixedWidth(140)

        self.welch_nperseg_sb = QSpinBox(self)
        self.welch_nperseg_sb.setRange(8, 1000000)
        self.welch_nperseg_sb.setSingleStep(8)
        self.welch_nperseg_sb.setValue(128)
        self.welch_nperseg_sb.setFixedWidth(120)

        self.welch_overlap_sb = QSpinBox(self)
        self.welch_overlap_sb.setRange(0, 95)
        self.welch_overlap_sb.setSingleStep(5)
        self.welch_overlap_sb.setValue(50)
        self.welch_overlap_sb.setSuffix(' %')
        self.welch_overlap_sb.setFixedWidth(120)

        layout.addRow('Window:', self.welch_window_combo)
        layout.addRow('Segment length (nperseg):', self.welch_nperseg_sb)
        layout.addRow('Overlap:', self.welch_overlap_sb)
        return page

    #---------------------------------------------------------------------------------------------
    def _build_mtm_page(self):

        page = QWidget()
        layout = QFormLayout(page)

        layout.setFormAlignment(AlignTop | AlignLeft)
        layout.setLabelAlignment(AlignLeft)

        self.mtm_nw_sb = QDoubleSpinBox(self)
        self.mtm_nw_sb.setRange(2.0, 4.0)
        self.mtm_nw_sb.setSingleStep(0.5)
        self.mtm_nw_sb.setValue(4.0)
        self.mtm_nw_sb.setDecimals(1)
        self.mtm_nw_sb.setFixedWidth(120)
        self.mtm_nw_sb.setToolTip('Time-bandwidth product. Typical range: 2.0 to 4.0.')

        layout.addRow('Time-bandwidth product (NW):', self.mtm_nw_sb)
        return page

    #---------------------------------------------------------------------------------------------
    def _build_lomb_page(self):

        page = QWidget()
        layout = QFormLayout(page)

        layout.setFormAlignment(AlignTop | AlignLeft)
        layout.setLabelAlignment(AlignLeft)

        self.lomb_freq_combo = QComboBox(self)
        self.lomb_freq_combo.addItems(['log', 'lomb_scargle', 'welch', 'scale', 'nfft'])
        self.lomb_freq_combo.setFixedWidth(160)

        layout.addRow('Frequency-grid method:', self.lomb_freq_combo)
        return page

    #---------------------------------------------------------------------------------------------
    def _build_wwz_page(self):

        page = QWidget()
        layout = QFormLayout(page)

        layout.setFormAlignment(AlignTop | AlignLeft)
        layout.setLabelAlignment(AlignLeft)

        self.wwz_freq_combo = QComboBox()
        self.wwz_freq_combo.addItems(["log", "lomb_scargle", "welch", "scale", "nfft"])
        self.wwz_freq_combo.setFixedWidth(120)
        
        self.wwz_c_sb = QDoubleSpinBox()
        self.wwz_c_sb.setDecimals(4)
        self.wwz_c_sb.setRange(0.0001, 1.0)
        self.wwz_c_sb.setValue(0.001)
        self.wwz_c_sb.setSingleStep(0.001)
        self.wwz_c_sb.setFixedWidth(120)
        
        layout.addRow("Frequency-grid method:", self.wwz_freq_combo)
        layout.addRow("Decay constant (c):", self.wwz_c_sb)
        return page

    #---------------------------------------------------------------------------------------------
    def update_parameter_page(self, method):
    
        mapping = {
            self.METHOD_PERIOD: 0,
            self.METHOD_WELCH: 1,
            self.METHOD_MTM: 2,
            self.METHOD_LOMB: 3,
            self.METHOD_WWZ: 4,
        }
    
        self.params_stack.setCurrentIndex(mapping.get(method, 0))
    
        # reset parameters to default
        if method == self.METHOD_PERIOD:
            self.periodogram_window_combo.setCurrentText('hann')
    
        elif method == self.METHOD_WELCH:
            self.welch_window_combo.setCurrentText('hann')
            self.welch_nperseg_sb.setValue(128)
            self.welch_overlap_sb.setValue(50)
    
        elif method == self.METHOD_MTM:
            self.mtm_nw_sb.setValue(4.0)
    
        elif method == self.METHOD_LOMB:
            self.lomb_freq_combo.setCurrentText('log')
    
        elif method == self.METHOD_WWZ:
            self.wwz_freq_combo.setCurrentText('log')

    #---------------------------------------------------------------------------------------------
    def delayed_update(self):

        self.status_bar.showMessage('Waiting', 1000)
        self.update_timer.start(800)

    #---------------------------------------------------------------------------------------------
    def _get_series(self):

        self.seriesDict = self.item.data(0, Qt.ItemDataRole.UserRole)
        series = self.seriesDict['Series']
        series = series.groupby(series.index).mean()
        series = series.dropna()
        return series.sort_index()

    #---------------------------------------------------------------------------------------------
    def _build_pyleo_series(self, series):

        return pyleo.Series(
            time=series.index.to_numpy(),
            value=series.to_numpy(),
            verbose=False,
        )

    #---------------------------------------------------------------------------------------------
    def _compute_selected_psd(self, ts):

        method_label = self.method_combo.currentText()

        if method_label == self.METHOD_PERIOD:
            window = self.periodogram_window_combo.currentText()
            settings = {'window': window}
            psd = ts.standardize().interp().spectral(
                    method='periodogram', 
                    settings=settings
            )
            label = f'Periodogram | {window}'
            history = f'Spectral estimation: method=Periodogram; window={window}'

        elif method_label == self.METHOD_WELCH:
            window = self.welch_window_combo.currentText()
            nperseg = self.welch_nperseg_sb.value()
            overlap_percent = self.welch_overlap_sb.value()
            noverlap = int(nperseg * overlap_percent / 100)
            if noverlap >= nperseg:
                noverlap = max(0, nperseg - 1)
            settings = {
                'window': window,
                'nperseg': nperseg,
                'noverlap': noverlap,
            }
            psd = ts.standardize().interp().spectral(
                    method='welch', 
                    settings=settings
            )
            label = f'Welch | {window} | nperseg={nperseg} | overlap={overlap_percent}%'
            history = (
                'Spectral estimation: method=Welch; '
                f'window={window}; nperseg={nperseg}; overlap={overlap_percent}%'
            )

        elif method_label == self.METHOD_MTM:
            nw = self.mtm_nw_sb.value()
            settings = {'NW': nw}
            psd = ts.standardize().interp().spectral(
                    method='mtm', 
                    settings=settings
            )
            label = f'MTM | NW={nw:.1f}'
            history = f'Spectral estimation: method=MTM; NW={nw:.1f}'

        elif method_label == self.METHOD_LOMB:
            freq = self.lomb_freq_combo.currentText()
            psd = ts.standardize().spectral(
                    method='lomb_scargle', 
                    freq=freq
            )
            label = f'Lomb-Scargle | freq={freq}'
            history = f'Spectral estimation: method=Lomb-Scargle; freq={freq}'

        elif method_label == self.METHOD_WWZ:
            freq_method = self.wwz_freq_combo.currentText()
            c = self.wwz_c_sb.value()
            psd = ts.standardize().spectral(
                method='wwz',
                settings={
                    'freq_method': freq_method,
                    'c': c
                }
            )
            label = f'Wavelet (WWZ) | freq_method={freq_method} | c={c}'
            history = f'Spectral estimation: method=Wavelet (WWZ); freq_method={freq_method}; c={c}'

        else:
            raise ValueError(f'Unknown spectral method: {method_label}')

        frequency = np.asarray(psd.frequency)
        amplitude = np.asarray(psd.amplitude)

        mask = np.isfinite(frequency) & np.isfinite(amplitude) & (frequency > 0) & (amplitude > 0)
        frequency = frequency[mask]
        amplitude = amplitude[mask]

        if len(frequency) == 0:
            raise ValueError('No valid positive frequencies returned by Pyleoclim.')

        period = 1.0 / frequency
        sorter = np.argsort(period)
        period = period[sorter]
        amplitude = amplitude[sorter]

        return {
            'label': label,
            'history': history,
            'method': method_label,
            'period': period,
            'psd': amplitude,
        }

    #---------------------------------------------------------------------------------------------
    def compute_psd(self):

        try:
            series = self._get_series()
            if len(series) < 8:
                raise ValueError('The series is too short to compute a spectral estimation.')

            self.status_bar.showMessage('Computing...', 0)
            QApplication.processEvents()

            ts = self._build_pyleo_series(series)
            result = self._compute_selected_psd(ts)
            self.psd_results.append(result)
            self.saved_psd_combo.addItem(result['label'])
            self.saved_psd_combo.setCurrentIndex(self.saved_psd_combo.count() - 1)

            self._redraw_plot()

            self.status_bar.showMessage('Done', 1000)
            QApplication.processEvents()

        except Exception as exc:
            self.status_bar.showMessage(f'Error: {exc}', 5000)
            QMessageBox.warning(self, 'Spectral estimation', str(exc))

    #---------------------------------------------------------------------------------------------
    def _initialize_plot(self):

        ax = self.interactive_plot.axs[0]
        ax.clear()
        self.interactive_plot.reset()

        ax.grid(visible=True, which='major', color='lightgray', linestyle='dashed', linewidth=0.5)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.xaxis.set_major_locator(LogLocator(base=10, subs=[1, 2, 5]))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{val:g}"))
        ax.invert_xaxis()
        ax.set_xlabel('Period')
        ax.set_ylabel('PSD')

    #---------------------------------------------------------------------------------------------
    def _redraw_plot(self):
    
        ax = self.interactive_plot.axs[0]
        ax.clear()
        self.interactive_plot.reset()
    
        ax.set_xlabel('Period')
        ax.set_ylabel('PSD')
    
        if self.psd_results:
            ax.grid(visible=True, which='major', color='lightgray', linestyle='dashed', linewidth=0.5)
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.xaxis.set_major_locator(LogLocator(base=10, subs=[1, 2, 5]))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{val:g}"))
            ax.invert_xaxis()
    
            for result in self.psd_results:
                line, = ax.plot(
                    result['period'],
                    result['psd'],
                    linewidth=0.8,
                    label=result['label']
                )
                points = ax.scatter(
                    result['period'],
                    result['psd'],
                    s=6,
                    marker='o',
                    visible=False
                )
                ax.line_points_pairs.append((line, points))
    
            legend = ax.legend()
            for legend_line, ax_line in zip(legend.get_lines(), ax.get_lines()):
                legend_line.set_picker(5)
                ax.map_legend_to_line[legend_line] = ax_line
    
            ax.autoscale()
    
        self.interactive_plot.fig.canvas.draw()
        self.interactive_plot.fig.canvas.setFocus()

    #---------------------------------------------------------------------------------------------
    def clear_plot(self):
    
        if not self.psd_results:
            self.status_bar.showMessage('No PSD to remove', 2000)
            return
    
        self.psd_results.pop()
    
        self.saved_psd_combo.clear()
        for result in self.psd_results:
            self.saved_psd_combo.addItem(result['label'])
    
        self._redraw_plot()
        self.status_bar.showMessage('Last PSD removed', 1500)

    #---------------------------------------------------------------------------------------------
    def save_series(self):

        if not self.psd_results:
            QMessageBox.information(self, 'Save PSD', 'No PSD available to save.')
            return

        index = self.saved_psd_combo.currentIndex()
        if index < 0 or index >= len(self.psd_results):
            QMessageBox.information(self, 'Save PSD', 'Please select a PSD to save.')
            return

        result = self.psd_results[index]
        series_Id = generate_Id()

        history = result['history']
        history += f'<BR>---> series <i><b>{series_Id}</b></i>'

        PSD_seriesDict = {
            'Id': series_Id,
            'Type': 'Series PSD',
            'Name': '',
            'X': 'Period',
            'Y': f'PSD ({result["label"]})',
            'Color': generate_color(exclude_color=self.seriesDict['Color']) if self.seriesDict else generate_color(),
            'Date': datetime.datetime.now().strftime('Created %Y/%m/%d at %H:%M:%S'),
            'History': append_to_htmlText(self.seriesDict['History'], history),
            'Comment': '',
            'Series': pd.Series(result['psd'], index=result['period']),
            'AxisSettings': {
                "xaxis": {"type": "log1-2-5", "invert": True},
                "yaxis": {"type": "log10", "invert": False}
            }
        }

        try:
            position = self.item.parent().indexOfChild(self.item)
            self.add_item_tree_widget(self.item.parent(), PSD_seriesDict, position + 1)
            self.status_bar.showMessage('PSD saved', 2000)
        except Exception as exc:
            QMessageBox.warning(self, 'Save PSD', f'Unable to save PSD: {exc}')

    #---------------------------------------------------------------------------------------------
    def closeEvent(self, event):

        self.open_powerSpectrumWindows.pop(self.Id, None)
        event.accept()


#=========================================================================================
# Example usage
if __name__ == '__main__':

    def handle_item(parent, item, position=None):
        print('handle', parent, item, position)

    app = QApplication([])

    x = np.linspace(1, 200, 400)
    y = np.sin(2 * np.pi * x / 20) + 0.4 * np.sin(2 * np.pi * x / 50)
    series = pd.Series(y, index=x)

    seriesDict = {
        'Id': 'abcd',
        'Type': 'Serie',
        'Name': 'Test',
        'X': 'Time',
        'Y': 'Signal',
        'Series': series,
        'Color': generate_color(),
        'Date': datetime.datetime.now().strftime('Created %Y/%m/%d at %H:%M:%S'),
        'Comment': '',
        'History': ''
    }
    item = QTreeWidgetItem()
    item.setData(0, Qt.ItemDataRole.UserRole, seriesDict)

    parent_item = QTreeWidgetItem()
    parent_item.addChild(item)

    Id_powerSpectrumWindow = '1234'
    open_powerSpectrumWindows = {}

    powerSpectrumWindow = computePowerSpectrumWindow(
        Id_powerSpectrumWindow,
        open_powerSpectrumWindows,
        item,
        handle_item,
    )
    open_powerSpectrumWindows[Id_powerSpectrumWindow] = powerSpectrumWindow
    powerSpectrumWindow.show()

    sys.exit(app_exec(app))
