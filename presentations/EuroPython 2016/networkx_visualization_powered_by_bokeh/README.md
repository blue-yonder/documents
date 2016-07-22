Installation
============

Both, the jupyter notebook and the bokeh app are developed with the use of a **python3** interpreter.
Therefore it is recommend to use python3 to run the notebook and the app.

Create a python virtualenv and source it:

```
virtualenv -p python3 venv
. venv/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```


Notebook
========

To start a notebook server and directly open the bokehx notebook use this command:

```
jupyter notebook bokehx.ipynb
```

A new tab in browser should open or got to [http://localhost:8888/notebooks/bokehx.ipynb](http://localhost:8888/notebooks/bokehx.ipynb).

Bokeh App
=========

To run the Bokeh application type in your shell:

```
bokeh serve bokehx_app.py
```

This will start a bokeh server and the app will be available at [http://localhost:5006/bokehx_app](http://localhost:5006/bokehx_app).
