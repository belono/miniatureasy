# MiniaturEasy
Extract miniatures from your images in a few clicks.

.. image:: https://www.quantifiedcode.com/api/v1/project/a55e32706c144305b03b966d3594bd29/badge.svg
  :target: https://www.quantifiedcode.com/app/project/a55e32706c144305b03b966d3594bd29
  :alt: Code issues

Description
-----------

MiniaturEasy is a multiplatform GUI app for fast and easy miniature extraction from image files,
allowing the user to multiload, view, rotate, crop and save a high quality thumbnail, in just a few clicks.

Can load all image formats supported by PIL/Pillow and save thumbnails in JPEG or PNG formats.

Dependencies
------------

This app makes use of Python and the following dependencies:

    * wxPython GUI toolkit
    * Pillow for image manipulation

Usage
-----

The basic usage is:

    To create a thumbnail:
    
    1 - Load an image file.
    2 - (Optional) If you want to save a thumb from a portion of the image:
        Drag mouse over the image to draw an adjustable RubberBand.
    3 - Click on Save button, check out the miniature preview,
        set a pathname and size for the thumb and then click OK.
        
    A high quality miniature will be created.


Contributing
------------

This project is open for any contribution.

Oxygen KDE icons
------------

This project makes use of a selection of icons from the Oxygen KDE icons theme.
https://www.kde.org/
https://github.com/KDE/oxygen-icons

Testing
-------

Succesfully tested under this platforms:
    
    - Linux
      Python v.2.7, v.3.5
      wxPython v.2.8, v.3.0.2, v.3.0.3(Phoenix)
      PIL v.1.1.7, Pillow v.2.8, v.2.9, v.3.1.2
      
    - Win32 (XP)
      Python v.2.7
      wxPython v.2.8, v.3.0.2
      Pillow v.4.0.0
