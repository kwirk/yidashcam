=========================
YI Dashcam python library
=========================
An unofficial python library for interfacing with the Xiaomi YI Dash Cam.

Disclaimer
==========
USE AT YOUR OWN RISK! This is an unofficial software library which may cause
permanent damage to your dash camera and permanent loss of data.

Requirements
============
The main library requires:

* `Python >= 3.4 <http://www.python.org/>`_
* `Requests <http://docs.python-requests.org/en/master/>`_


The web application requires:

* Flask_


.. _Flask: http://flask.pocoo.org/

Usage
=====
To use, you must connect to your dash camera via WiFi first.

An example of using `yidashcam` (sync emergency clips to current
folder):

.. code-block:: python

    import os
    import yidashcam

    with yidashcam.YIDashcam() as yi:
        print("Serial number: {}".format(yi.serial_number))
        for emr_file in yi.emergency_list:
            if not os.path.exists(emr_file.name):
                print("Fetching {}...".format(emr_file.path))
                with open(emr_file.name, 'wb') as local_file:
                    for data in yi.get_file(emr_file):
                        local_file.write(data)


Also included is two applications:

* ``python -m yidashcam`` puts the dash camera in a mode to allow live
  streaming from the dash camera.
* ``python -m webapp`` hosts a local web app to allow browsing of dash
  camera's stored video (requires Flask_).


License
=======
MIT License

Copyright (c) 2016 Steven Hiscocks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
