DVHA MLC Analyzer
=================
|logo|

|build| |Docs| |pypi| |python-version| |lgtm| |lgtm-cq| |Codecov| |lines| |repo-size| |code-style|

Batch analyze DICOM-RT Plan files to calculate complexity scores

`DVH Analytics <https://github.com/cutright/DVH-Analytics>`__ (DVHA) is a software application for building a local
database of radiation oncology treatment planning data. It imports data from DICOM-RT files (i.e., plan, dose, and 
structure), creates a SQL database, provides customizable plots, and provides tools for generating linear, 
multi-variable, and machine learning regressions.

DVHA-MLCA is a stand-alone command-line script to batch analyze DICOM-RT Plans using the MLC Analyzer code from DVHA.

Complexity score based on:  
Younge KC, Matuszak MM, Moran JM, McShan DL, Fraass BA, Roberts DA. Penalization of aperture
complexity in inversely planned volumetric modulated arc therapy. Med Phys. 2012;39(11):7160–70.

Installation
------------

To install via pip:

.. code-block:: console

    $ pip install dvha-mlca


If you've installed via pip or setup.py, launch from your terminal with:

.. code-block:: console

    $ mlca <init-scanning-directory>


If you've cloned the project, but did not run the setup.py installer, launch DVHA-MLCA with:

.. code-block:: console

    $ python mlca/main.py <init-scanning-directory>


Command line usage
------------------

.. code-block:: console

    usage: mlca [-h] [-of OUTPUT_FILE] [-xw COMPLEXITY_WEIGHT_X]
                [-yw COMPLEXITY_WEIGHT_Y] [-xs MAX_FIELD_SIZE_X]
                [-ys MAX_FIELD_SIZE_Y] [-ver] [-v] [-n PROCESSES]
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
      -v, --verbose         Print final results and plan summaries as they are
                            analyzed
      -n PROCESSES, --processes PROCESSES
                            Enable multiprocessing, set number of parallel
                            processes


For example:

.. code-block:: console

    $ mlca "C:\PatientDicom" -n 8
    Directory: C:\PatientDicom
    Begin file tree scan ...
    File tree scan complete
    Searching for DICOM-RT Plan files ...
         100%|██████████████████████████████| 9087/9087 [00:59<00:00, 153.52it/s]
    1650 DICOM-RT Plan file(s) found
    Analyzing 1650 file(s) ...
          10%|███                           | 169/1650 [02:02<13:35,  1.82it/s]


Dependencies
------------
* `Python <https://www.python.org>`__ >3.5
* `Pydicom <https://github.com/darcymason/pydicom>`__
* `NumPy <http://numpy.org>`__
* `Shapely <https://github.com/Toblerity/Shapely>`__

Support
-------
If you like DVHA-MLCA and would like to support our mission, all we ask is that you cite us if we helped your 
publication, or help the DVHA community by submitting bugs, issues, feature requests, or solutions on the 
`issues page <https://github.com/cutright/DVHA-MLCA/issues>`__.

Cite
----
DOI: `https://doi.org/10.1002/acm2.12401 <https://doi.org/10.1002/acm2.12401>`__
Cutright D, Gopalakrishnan M, Roy A, Panchal A, and Mittal BB. "DVH Analytics: A DVH database for clinicians and 
researchers." Journal of Applied Clinical Medical Physics 19.5 (2018): 413-427.

.. |build| image:: https://github.com/cutright/DVHA-MLCA/workflows/build/badge.svg
   :target: https://github.com/cutright/DVHA-MLCA/actions
   :alt: build

.. |pypi| image:: https://img.shields.io/pypi/v/dvha-mlca.svg
   :target: https://pypi.org/project/dvha-mlca
   :alt: PyPI

.. |python-version| image:: https://img.shields.io/pypi/pyversions/dvha-mlca.svg
   :target: https://pypi.org/project/dvha-mlca
   :alt: PyPI

.. |lgtm-cq| image:: https://img.shields.io/lgtm/grade/python/g/cutright/DVHA-MLCA.svg?logo=lgtm&label=code%20quality
   :target: https://lgtm.com/projects/g/cutright/DVHA-MLCA/context:python
   :alt: lgtm code quality

.. |lgtm| image:: https://img.shields.io/lgtm/alerts/g/cutright/DVHA-MLCA.svg?logo=lgtm
   :target: https://lgtm.com/projects/g/cutright/DVHA-MLCA/alerts
   :alt: lgtm

.. |Codecov| image:: https://codecov.io/gh/cutright/DVHA-MLCA/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/cutright/DVHA-MLCA
   :alt: Codecov

.. |Docs| image:: https://readthedocs.org/projects/dvha-mlca/badge/?version=latest
   :target: https://dvha-mlca.readthedocs.io/
   :alt: Documentation Status

.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. |lines| image:: https://img.shields.io/tokei/lines/github/cutright/dvha-mlca
   :target: https://img.shields.io/tokei/lines/github/cutright/dvha-mlca
   :alt: Lines of code

.. |repo-size| image:: https://img.shields.io/github/languages/code-size/cutright/dvha-mlca
   :target: https://img.shields.io/github/languages/code-size/cutright/dvha-mlca
   :alt: Repo Size

.. |logo| raw:: html

    <a>
      <img src="https://user-images.githubusercontent.com/4778878/92505112-351c7780-f1c9-11ea-9b5c-0de1ad2d131d.png" width='400' alt="DVHA logo"/>
    </a>