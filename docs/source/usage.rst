=====
Usage
=====

Command Line
------------


.. code-block:: console

    $ mlca "C:\PatientDicom"


To enable multi-threading, indicate the max number of parallel threads allowed
with the ``--processes`` flag (or ``-n`` for short). The example below allows
up to 8 parallel processes. This applies to checking for DICOM modality and
beam analysis.

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



Plan Summary
------------
A simple example is below. Check out the module references for details about
every method and property available.

.. code-block:: python

    >>> from mlca.mlc_analyzer import Plan
    >>> plan = Plan('rtplan.dcm')
    >>> plan


Output will look like:

.. code-block:: console

    Patient Name:        ANON11264
    Patient MRN:         ANON11264
    Study Instance UID:  2.16.840.1.114362.1.6.7.4.17517.7693757184.462857971.1073.8123
    TPS:                 ADAC Pinnacle3
    Plan name:           ANON
    # of Fx Group(s):    3
    Plan MUs:            776.1, 659.2, 512.3
    Beam Count(s):       9, 9, 8
    Control Point(s):    140, 120, 100
    Complexity Score(s): 1.274, 1.290, 1.127


Beam Data
---------
You can access specific beam information. Some examples are shown below.

.. code-block:: python

    >>> beam = plan.fx_group[0].beam[0]
    >>> beam.area
        [16172.0, 16172.0, 13398.0, 13398.0, 428.0, 428.0, 787.0, 787.0, 582.0,
        582.0, 1728.0, 1728.0, 3479.0, 3479.0, 502.0, 502.0, 8587.0, 8587.0]
    >>> beam.gantry_angle
        [200.0]
    >>> beam.meter_set
        90.199996948242
    >>> beam.younge_complexity_scores
        array([0.0081077 , 0.        , 0.00878864, 0.        , 0.01600782,
               0.        , 0.02859258, 0.        , 0.02102578, 0.        ,
               0.01606121, 0.        , 0.01505108, 0.        , 0.01389648,
               0.        , 0.0075811 , 0.        ])

