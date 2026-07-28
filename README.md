## PyAnalySeries

PyAnalySeries Reimagined: A Legacy Tool Reborn

![version](https://img.shields.io/github/v/tag/PBrockmann/PyAnalySeries)  
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21240987.svg)](https://doi.org/10.5281/zenodo.21240987)

**PyAnalySeries** is a Python application built on **matplotlib**, with a **PyQt-based graphical interface**, making it easily portable across platforms including **Linux**, **macOS**, and **Windows**.  
It is designed as a modern continuation of the <a href="https://github.com/PaleoIPSL/AnalySeries" target="_blank">**AnalySeries**</a>, the original application on MacOS, aiming to reproduce its core functionalities within a more robust and portable Python environment.  
Special attention has been given to **ergonomics**, emphasizing **simplicity** and **clarity**, while offering intuitive interactivity such as **zooming**, **panning**, and **scrolling**, with **linked or independent axis**.  
The core design follows a **"Define then Apply"** workflow for data processing operations such as **filtering**, **sampling**, and **interpolation**.  
Documents are read and saved in an **open format** spreadsheet (xlsx) with **multiple worksheets** for organization. It is also possible to import series or pointers directly from the **clipboard**, following a simple **copy (Ctrl+C)** and **paste (Ctrl+V)** operation from an external spreadsheet.  
The application leverages **robust, well-tested modules** for interpolation, notably **SciPy**, and features an **interactive interface** for defining **interpolation pointers** (formerly known as *Linage* and *Splinage*), allowing for **precise placement and manipulation**—either directly on data points or independently.  

PyAnalySeries provides access to insolation computations through the **Insolation** module, including astronomical solutions and derived quantities such as eccentricity, obliquity, precession parameters, and various insolation metrics. It also integrates the **Pyleoclim** package for time series processing, including detrending, frequency filtering, and power spectral density (PSD) estimation.

Based on: numpy, pandas, matplotlib, scipy, shapely, openpyxl, PyQt, Inso, Pyleoclim

Conception and developments : Patrick Brockmann LSCE/CEA - IPSL

This project is distributed under the **CeCILL v2.1** license.  
![CeCILL License](https://img.shields.io/badge/license-CeCILL-blue)

<img src="QRCode.png" alt="QRCode" width="200" />

<hr style="border:2px solid gray">

#### Reference  
Hevia-Cruz, F., Brockmann, P., Govin, A., Michel, E., and Paillard, D. (2025). Reviving AnalySeries: PyAnalySeries, a modern and collaborative open-source tool for time-series analysis. Past Global Changes Magazine, 33(2), 74–75. [https://doi.org/10.22498/pages.33.2.74](https://doi.org/10.22498/pages.33.2.74)

<hr style="border:2px solid gray">

#### PyAnalySeries Demo Tour

<a href="https://paleoipsl.github.io/PyAnalySeries" target="_blank">https://paleoipsl.github.io/PyAnalySeries</a>

<hr style="border:2px solid gray">

#### EGU 2026 Demo Session

A demo session on PyAnalySeries took place during EGU 2026:

**SC2.27 – Processing and visualizing 2-D datasets using the PyAnalySeries software for research and teaching**  
Wednesday, 06 May, 08:30–10:15 (CEST), Room 0.55

<hr style="border:2px solid gray">

#### Documentation 
The use of the application is detailed in the following [Wiki page](https://github.com/PaleoIPSL/PyAnalySeries/wiki).

<hr style="border:2px solid gray">

#### Captures

![ScreenShot1](misc/capture_01.png) 


![ScreenShot2](misc/capture_02.png) 

<hr style="border:2px solid gray">

#### Tutorials
 
Tutorials can be found from the [Wiki page](https://github.com/PaleoIPSL/PyAnalySeries/wiki)

 * [Tutorial 01](https://github.com/PaleoIPSL/PyAnalySeries/wiki/Tutorial-01)
 * [Tutorial 02](https://github.com/PaleoIPSL/PyAnalySeries/wiki/Tutorial-02)

<hr style="border:2px solid gray">

##### Installation and update

See [installation.md](./installation.md) for installation details.


See [update.md](./update.md) for update details.

<hr style="border:2px solid gray">

##### Test

 * `python PyAnalySeries.py`
 * `python PyAnalySeries.py test/ws_ex.xlsx`
 * `python PyAnalySeries.py test/MD95-2042.xlsx test/GeoB3938.xlsx`

<hr style="border:2px solid gray">

##### Shortcuts 

See [shortcuts.md](./shortcuts.md) for shortcut settings.

<hr style="border:2px solid gray">

#### Releases

See [releases.md](./releases.md) for release details.
