====================
tf2-hitsound-manager
====================

A simple GUI to browse, set, and store ``Team Fortress 2`` custom sounds.

Credits
=======

This project implements the `TF2 Build`_ typeface, created by Andrea Wicklund.

.. _TF2 Build: https://archive.ph/MFdnM

Further, `this Reddit post`_ was (haphazardly) cited as the list of sounds included in ``data/custom_sounds.txt``.
`This page`_ was cited as a more comprehensive list.

.. _this Reddit post: https://archive.ph/Ho8ae
.. _This page: https://archive.ph/Rwjq7

More official sources will be cited in future versions.

Dependencies
============

* Python 3.8 or higher
* `FFmpeg`_ (add this to your system PATH)

.. _FFmpeg: https://www.ffmpeg.org/download.html

Installation
============

.. code-block:: console

    $ pip install tf2-hitsound-manager

Usage/Configuration
===================

.. code-block:: console

    $ tf2-hitsound-manager

Alternatively, you can install the standalone executable/binary available on the GitHub page.

Unless you have your TF2 directory
(e.g., ``C:\Program Files (x86)\Steam\steamapps\common\Team Fortress 2``)
added to your system PATH, you will be asked to configure your TF2 path
on your first run of the program.

``tf2-hitsound-manager`` will store copies of sounds as they were imported.
Upon setting a custom sound, the program will export a copy, converted accordingly.
These will be exported to ``<TF2 Directory>/tf/custom/TF2 Hitsound Manager/sound``.

Note that ``tf2-hitsound-manager`` does not affect custom sounds stored in directories
other than this; you would have to delete other directories manually.

Further note that once a sound has been set through the manager, it will be assumed
that said custom sound has already been stored, and will be deleted on the next change.
If you intend to use this program, do not change custom sounds without the manager after having used it.

Deleting sounds
***************

You can delete imports by selecting the import you want to delete and keying ``del``.
More sweeping controls to delete imports will be added in a future update.