# PiTiVi , Non-linear video editor
#
#       pitivi/elements/thumbnailsink.py
#
# Copyright (c) 2005, Edward Hervey <bilboed@bilboed.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.
"""
GdkPixbuf thumbnail sink
"""

import gobject
import gst
import struct
import time

big_to_cairo_alpha_mask = struct.unpack('=i', '\xFF\x00\x00\x00')[0]
big_to_cairo_red_mask = struct.unpack('=i', '\x00\xFF\x00\x00')[0]
big_to_cairo_green_mask = struct.unpack('=i', '\x00\x00\xFF\x00')[0]
big_to_cairo_blue_mask = struct.unpack('=i', '\x00\x00\x00\xFF')[0]

class CairoSurfaceThumbnailSink(gst.BaseSink):
    """
    GStreamer thumbnailing sink element.

    Can be used in pipelines to generates gtk.gdk.Pixbuf automatically.
    """

    __gsignals__ = {
        "thumbnail": (gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,
                      ([gobject.TYPE_UINT64]))
        }

    __gsttemplates__ = (
        gst.PadTemplate("sink",
                         gst.PAD_SINK,
                         gst.PAD_ALWAYS,
                         gst.Caps("video/x-raw-rgb,"
                                  "bpp = (int) 32, depth = (int) 32,"
                                  "endianness = (int) BIG_ENDIAN,"
                                  "alpha_mask = (int) %i, "
                                  "red_mask = (int)   %i, "
                                  "green_mask = (int) %i, "
                                  "blue_mask = (int)  %i, "
                                  "width = (int) [ 1, max ], "
                                  "height = (int) [ 1, max ], "
                                  "framerate = (fraction) [ 0, 25 ]"
                                  % (big_to_cairo_alpha_mask,
                                     big_to_cairo_red_mask,
                                     big_to_cairo_green_mask,
                                     big_to_cairo_blue_mask)))
        )

    def __init__(self):
        gst.BaseSink.__init__(self)
        self.width = 1
        self.height = 1
        self.set_sync(True)
        self.data = None

    def do_set_caps(self, caps):
        self.log("caps %s" % caps.to_string())
        self.log("padcaps %s" % self.get_pad("sink").get_caps().to_string())
        self.width = caps[0]["width"]
        self.height = caps[0]["height"]
        if not caps[0].get_name() == "video/x-raw-rgb":
            return False
        return True

    def do_render(self, buf):
        self.data = str(buf.data)
        self.emit('thumbnail', buf.timestamp)
        return gst.FLOW_OK
 
    def do_preroll(self, buf):
        print "Pre-roll"
        return self.do_render(buf)

gobject.type_register(CairoSurfaceThumbnailSink)