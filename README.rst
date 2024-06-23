.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/python_refactor_tool_box.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/python_refactor_tool_box
    .. image:: https://readthedocs.org/projects/python_refactor_tool_box/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://python_refactor_tool_box.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/python_refactor_tool_box/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/python_refactor_tool_box
    .. image:: https://img.shields.io/pypi/v/python_refactor_tool_box.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/python_refactor_tool_box/
    .. image:: https://img.shields.io/conda/vn/conda-forge/python_refactor_tool_box.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/python_refactor_tool_box
    .. image:: https://pepy.tech/badge/python_refactor_tool_box/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/python_refactor_tool_box
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/python_refactor_tool_box
.. image:: https://img.shields.io/pypi/v/python_refactor_tool_box.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/python_refactor_tool_box/

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

=====================
python_refactor_tool_box
=====================


    A set of tools helping to refactor python code


python_refactor_tool_box help to refactor python code by moving all existing classes to dedicated module


Installation
============

.. code-block:: bash

    pip install python_refactor_tool_box

Quick start
===========

.. code-block:: python

    from python_refactor_tool_box.SourceDirectory import SourceDirectory
    from tests.helper import (
        create_samples,
        expected_samples_directory,
        input_samples_directory,
        samples_directory,
    )

    create_samples(samples_directory)

    input_source_directory = SourceDirectory(input_samples_directory)

    input_source_directory.refactor()

Examples
========

Take a look at quick_start.py to see how to use the library.

Note
====

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.

Licence
=======

ffbb_api_client is distributed under the Apache 2.0 license.

Dev notes
=========

Command used to create this project:

.. code-block:: bash

    putup FFBBApiClient_Python -p ffbb_api_client -l Apache-2.0 -d "Allow to interact with FFBB apis" -u "https://github.com/Rinzler78/FFBBApiClient_Python" -v --github-actions --venv .venv
