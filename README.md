# DVHA MLC Analyzer (DVHA-MLCA)
Batch analyze DICOM-RT Plan files to calculate complexity scores

[DVH Analytics](https://github.com/cutright/DVH-Analytics) (DVHA) is a software application for building a local 
database of radiation oncology treatment planning data. It imports data from DICOM-RT files (i.e., plan, dose, and 
structure), creates a SQL database, provides customizable plots, and provides tools for generating linear, 
multi-variable, and machine learning regressions.

DVHA-MLCA is a stand-alone command-line script to batch analyze DICOM-RT Plans using the MLC Analyzer code from DVHA.

Complexity score based on:  
Younge KC, Matuszak MM, Moran JM, McShan DL, Fraass BA, Roberts DA. Penalization of aperture
complexity in inversely planned volumetric modulated arc therapy. Med Phys. 2012;39(11):7160–70.

<a href="https://pypi.org/project/dvha-mlca/">
        <img src="https://img.shields.io/pypi/v/dvha-mlca.svg" alt="PyPi Version" /></a>

Installation
---------
To install via pip:
```
pip install dvha-mlca
```
If you've installed via pip or setup.py, launch from your terminal with:
```
mlca <init-scanning-directory>
```
If you've cloned the project, but did not run the setup.py installer, launch DVHA with:
```
python mlca/main.py <init-scanning-directory>
```

### Command line usage
~~~~
usage: mlca [-h] [-of OUTPUT_FILE] [-xw COMPLEXITY_WEIGHT_X]
            [-yw COMPLEXITY_WEIGHT_Y] [-xs MAX_FIELD_SIZE_X]
            [-ys MAX_FIELD_SIZE_Y] [-ver]
            [init_dir]

Command line DVHA MLC Analyzer

positional arguments:
  init_dir              Directory containing DICOM-RT Plan files

optional arguments:
  -h, --help            show this help message and exit
  -of OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output will be saved as
                        dvha_mlca_<version>_results_<time-stamp>.csv by
                        default.
  -xw COMPLEXITY_WEIGHT_X, --x-weight COMPLEXITY_WEIGHT_X
                        Complexity coefficient for x-dimension: default = 1.0
  -yw COMPLEXITY_WEIGHT_Y, --y-weight COMPLEXITY_WEIGHT_Y
                        Complexity coefficient for y-dimension: default = 1.0
  -xs MAX_FIELD_SIZE_X, --x-max-field-size MAX_FIELD_SIZE_X
                        Maximum field size in the x-dimension: default = 400.0
                        (mm)
  -ys MAX_FIELD_SIZE_Y, --y-max-field-size MAX_FIELD_SIZE_Y
                        Maximum field size in the y-dimension: default = 400.0
                        (mm)
  -ver, --version       Print the DVHA-MLCA version

~~~~

Dependencies
---------
* [Python](https://www.python.org) >3.5
* [Pydicom](https://github.com/darcymason/pydicom)
* [NumPy](http://numpy.org)
* [Shapely](https://github.com/Toblerity/Shapely)

Support
---------  
If you like DVHA-MLCA and would like to support our mission, all we ask is that you cite us if we helped your 
publication, or help the DVHA community by submitting bugs, issues, feature requests, or solutions on the 
[issues page](https://github.com/cutright/DVHA-MLCA/issues).

Cite
---------  
DOI: [https://doi.org/10.1002/acm2.12401](https://doi.org/10.1002/acm2.12401)  
Cutright D, Gopalakrishnan M, Roy A, Panchal A, and Mittal BB. "DVH Analytics: A DVH database for clinicians and 
researchers." Journal of Applied Clinical Medical Physics 19.5 (2018): 413-427.