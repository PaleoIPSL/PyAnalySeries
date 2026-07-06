 * 6.36
   * Add Gradients tab to interpolation windows (defineInterpolationWindow and displayInterpolationWindow) with Linear/PCHIP gradient values, configurable sampling resolution, and spreadsheet export via copy/paste
   * Fix typo: 'Distorded' to 'Distorted'
 * 6.35
   * Add persistent axis settings (scale type and inversion state) saved in worksheets
   * Add per-feature configuration of interactivePlot context menu actions depending on display window type and shared-axis configuration
   * Change define to create for createInsolationAstroSeriesWindow, createSinusoidalSeriesWindow, createRandomSeriesWindow.
 * 6.34
   * Fix saving of original-axis values (including replicates) for interpolated series
   * Add original-axis values column to the Data tab of displaySingleSeriesWindow for interpolated series
 * 6.33
   * Fix custom tooltip text visibility with dark/inverted color themes
 * 6.32
   * Increase numerical precision in statistics display from .2f to .6
 * 6.31
   * Fix angular wrap for true longitudes when computing integrated insolation (support intervals crossing 0°)
   * Fix shortcut 'z' in defineInterpolationWindow
 * 6.30
   * Fix incorrect time sign handling (Past > 0) introduced by astro/insolation code refactoring
   * Update images in defineInsolationAstroSeriesWindow
 * 6.29
   * Fix issue with secondary axis not properly removed in defineInterpolationWindow
   * Fix issue with secondary axis not properly removed in defineInterpolationWindow
   * Add season_length.ipynb notebook (need inso 1.2.0, `pip install --ugrade inso`)
   * Add images in defineInsolationAstroSeriesWindow
   * Additionnal Qt compatibilities (QKeySequence.StandardKey.Close, ...)
 * 6.28
   * Update inso to v1.2.0 in conda environments
   * Update inso to v1.2.0 in conda environments
   * Preserve replicate variability when compute Detrend
 * 6.27
   * Add Qt compatibility layer (PyQt5 / PyQt6)
   * Add Qt compatibility layer (PyQt5 / PyQt6)
 * 6.26
   * Fix in defineInsolation, Eccentricity and Precession parameter are dimensionless
   * Factorize astro/insolation computations from defineInsolationAstroSeriesWindow into a shared module insolationAstroSeries.py
   * Add a notebook example using insolationAstroSeries.py (interactive with ipywidgets)
 * 6.25
   * Fix XOriginalValues format to list in defineInterpolation
 values are converted to lists on save to avoid ambiguous comparisons
 * 6.24
   * Fix alignement of parameters
   * Unified UI with Fusion style for consistent cross-platform rendering
   * Standardized keyboard shortcuts (platform conventions):
     * Close window: Ctrl+W / Cmd+W
     * Quit application: Ctrl+Q / Cmd+Q
 * 6.23
   * Add window parameter in FIR Frequency Filter
 * 6.22
   * Fix history in Detrend, Frequency, Aggregate, Power Spectrum (PSD) 
   * Shortcut on Windows
 * 6.21
   * Remove synchronisation from tree to windows (sync_with_item, sync_window_with_item)
 * 6.20
   * Add Transforms / Detrend based on Pyleoclim
   * Add Transforms / Detrend based on Pyleoclim
   * Add Frequency-Domain Filter / Frequency Filter based on Pyleoclim
   * Add Spectral Estimation / Power Spectrum (PSD) based on Pyleoclim
   * Add Edit / Aggregate / Clean
   * Improve numeric import: automatic detection of . or , as decimal separators
   * Improve replicate detection: use duplicated(keep=False) so all replicated values are highlighted
   * Change SAMPLE to SAMPLING in interface, dialogs and code
   * Align series import with pointers import: use displayed column order instead of fixed indices
 * 6.10
   * Fix defineInterpolation gradients plot update by removing lines instead of clearing
 * 6.09
   * Fix sync issue causing stale pointer reload by resetting self.itemINTERPOLATION before save
   * Disable SizeGrid in StatusBar
   * Pointers plot now allows independent vertical zooming of pointers and gradients on the secondary axis
   * Fix History text rendering so it correctly follows application font size changes
   * Change application icon now as SVG
   * Swap Type, Id columns in the tree 
 * 6.08
   * Simplify icons
   * Add numba and llvmlite to environment.yml to avoid pip build issues when installing pyleoclim
 * 6.07
   * Fix series color button rendering in tree
 * 6.06
   * Fix series reading: length now determined from X column only, preventing X/Y misalignment caused by separate trailing trimming
 * 6.05
   * Fix keep replicates in apply Filter
 * 6.04
   * Implement per-plot horizontal axis grouping in displayStackedSeriesWindow
 * 6.03
   * Keep replicates in interpolation, filter
 * 6.02
   * Rename replicates formerly referred to as duplicates in displaySingleSeriesWindow
   * Add quantiles and other stats in displaySingleSeriesWindow
   * Fix reading WS with trim trailing NaNs when interpolation
 * 6.01
   * Fix PyQt6 breaking change: update key and modifier enums (Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier).
 * 6.00 
   * Fix remaining windows not closing on application exit.
   * Add Pyleoclim
   * New conda environment
   * PyQt5 to PyQt6 (macOS ≥ 13 required; older macOS systems unsupported)
 * 5.45
   * Typo fix in defineSinusoidalSeriesWindow
 * 5.44
   * Move display actions into a dedicated Display menu
   * Add a Preferences menu to control font size (persisted via QSettings)
   * Add a Preferences option to control tooltip visibility (persisted via QSettings)
 * 5.43
   * Remove Y-axis inverted (now available via the context menu)
   * Fix missing Date in various examples from resource classes
   * Fix worksheet saving when items are removed in overwrite mode
 * 5.42
   * Add local and global autoscale
   * Fix exit handling
 * 5.41
   * Ensure correct file extension based on selected save format
 * 5.40
   * Change Serie to Series in interface, dialogs and code
   * Fix read of boolean values (in define sampling)
 * 5.32
   * Tag before deep change (5.40)
 * 5.31.2
   * Add missing icons
   * Fix Date missing in apply filter, sample, interpolation
 * 5.31.1
   * Fix History in define Interpolation
 * 5.31
   * Add Date as field for items (save in WS, handle existing or not)
   * Improve History texts
   * Add Date as field for items (save in WS, handle existing or not)
   * Improve History texts
   * Modify interactivePlot :  
       - to add context menu on axis to choose invert, linear, log display
       - to add context menu on plot to save figure
   * Handle missing values when import serie
 * 5.30
   * Add timestamp when saving
   * Fix synchronisation item lost from 5.26 
   * Allow readonly on ID column
   * Keep existing sheetnames when saving WS
 * 5.29
   * Fix import data when number of columns is not consistent.
 * 5.28
   * Add 'Create / Sinusoidal Serie' with the defineSinusoidalSeriesWindow class
   * Change some parameters input as float in defineInsolationAstroSeriesWindow
 * 5.27
   * Fix saved status when items are modified
 * 5.26
   * Issue #18 Control saving WorkSheet individually
   * Issue #17 Exit sequence with control of unsaved worksheets
   * Issue #16 Align vertical axis in defineInterpolationWindown with Z
   * Fix saved status when items are pasted
 * 5.25
   * Fix alternating row colors and selections
   * Use last dir when creating new worksheet
   * Fix height of parameters in defineSampleWindow
 * 5.24
   * Alternating row colors in main window
   * Fix when no WS exist and display windows ask to update item
   * Issue #15 Add 'Save ...' in addition to 'Save and ...'  
   * Issue #14 Change removing connection keeps pointers
 * 5.23
   * Fix save WS when paste an item. 
   * Fix multiple drop items. Not allowed.
 * 5.22
   * Add 'Astronomical solution' in History in defineInsolationAstroSeriesWindow 
 * 5.21
   * Issue #10 change to handle the order in the choosen series in Define Samping
   * Issue #9 Fix on zoom behaviour
   * Issue #8 Fix on keeping zoom position in Define Interpolation
   * Issue #7 Add on Wiki a paragraph to detail exporting plots and possible use of Inkscape
 * 5.20
   * inso as standalone module to be installed by a `pip install inso`
   * Add a Shuffle button in defineRandomSeriesWindow
 * 5.19
   * Fix omission of Precession parameter when Import serie
 * 5.18
   * Fix in sampling when x values are used (XCoords were not saved)
 * 5.17
   * Force sorting on serie index when import, display data and save
 * 5.16
   * Fix \r when clipboard (copy/paste) is produced from Mac
 * 5.15
   * Fix Display Together and Display Stacked to disallow INTERPOLATION
   * Fix test on monotonic increasing and unique when import pointers
   * Fix colors order (missing, duplicates) with displaySingleSeriesWindow
 * 5.14
   * Fix style for buttons
   * Allow empty cells in 1st column when importing series
   * Set headers of QTableWidget
   * Blend colors in QTableWidget
 * 5.13
   * Add last recent dir when open worksheets
   * Fix when xlsx file has no item detected
   * Fix html files
   * Add href links in references for insolation
 * 5.12
   * Fix hide of tooltip when not focus.
   * Add encoding utf-8 for reading html files
 * 5.11
   * Add padding on various buttons.
   * Fix sampling intervals (start and end were missing).
 * 5.1
   * Alpha release 
 * 5.0
   * Beta realease 
