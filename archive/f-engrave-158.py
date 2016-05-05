#!/usr/bin/python
"""
    f-engrave G-Code Generator
    
    Copyright (C) <2016>  <Scorch>
    Source was used from the following works:
              engrave-11.py G-Code Generator -- Lawrence Glaister --
              GUI framework from arcbuddy.py -- John Thornton  --
              cxf2cnc.py v0.5 font parsing code --- Ben Lipkowitz(fenn) --
              dxf.py DXF Viewer (http://code.google.com/p/dxf-reader/)
              DXF2GCODE (http://code.google.com/p/dfxf2gcode/)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    To make it a menu item in Ubuntu use the Alacarte Menu Editor and add
    the command python YourPathToThisFile/ThisFilesName.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at:
    http://wiki.linuxcnc.org/cgi-bin/emcinfo.pl?Simple_EMC_G-Code_Generators

    Version 0.1 Initial code

    Version 0.2 - Added V-Carve code
                - Fixed potential inf loop
                - Added pan and zoom
                - Moved Font file read out of calculation loop (increased speed)

    Version 0.3 - Bug fix for flip normals and flip text
                - Moved depth scalar calc out of for loop

    Version 0.4 - Added importing for DXF files
                - Added import True Type fonts using the ttf2cxf_stream helper program
                - Fixed line thickness display when zooming

    Version 0.5 - Added support for more DXF entity types POLYLINE and LEADER (leaders won't have arrow heads)
                - Added global accuracy setting
                - Added straight line detection in v-carve output (reduces number of G1 commands and output file size)
                - Improved handling of closed loops in v-carving
                - Added global variable named "Zero" for non-zero checks

    Version 0.6 - Added import Portable BitMap (PBM) images using Potrace as a helper program
                - Default directory for opening PBM and DXF files is now set to the current font directory
                - Default directory for and saving is now set to the users home directory
                - Helper programs should now be found if they are in the global search path or F-Engrave
                    script folder (Previously the helper programs needed to be in f-engrave script folder)

    Version 0.7 - Increased speed of v-carve calculation for large designs.  Approximately 20 times faster now.
                - Added window that displays status and contains a stop button for v-carve calculations
                - Fixed display so that it no longer freezes during long calculations
                - Fixed divide by zero error for certain fonts (Bug in Versions 0.5 and 0.6)

    Version 0.8 - Changed interface when working with image (DXF or PBM) files.
                - Added post processing logic to reduce number and distance of rapid moves
                - Fixed bug in DXF code that caused failure to import some DXF files.
                - Changed settings dialogs to allow recalculation and v-carving from the dialog window to preview settings
                - Added some logic for determining default .ngc names and directory when saving
                - Remove option for steps around corner (now internally calculated based on step length and bit geometry)

    Version 0.9 - Added arc fitting to g-code output
                - Fixed extended characters up to 255 (now uses numbers for the font index rather than the character)
                - Added option for a second operation g-code output file to clean-up islands and adjacent areas of a v-carving
                - Cleaned up some GUI bugs introduced in Version 0.8
                - Remove flip border normals option
                - Default to check "all" instead of current character "chr"
                - Changed the percent complete calculation to use the % of the total segment length rather than the segment count

    Version 0.91 - Fixed bug that caused Radius setting from text mode to affect image mode
                 - Fixed bug that caused some DXF files to fail erroneously

    Version 0.92 - Fixed bug that caused some buttons on the v-carve setting to not show up.

    Version 0.93 - Fixed bug that caused bad g-code in some cases.

    Version 1.00 - Added support for DXF polyline entity "bulges" (CamBam uses polyline bulges in DXF exports)
                 - Modified code to be compatible with Python 3.  (F-Engrave now works with Python 2.5 through 3.3)
                 - Removed stale references to grid the grid geometry manager
                 - Made minor user interface changes

    Version 1.01 - Fixed bug importing text information from g-code file in Python 3
                 - Put additional restriction on arc fitting to prevent arcing straight lines

    Version 1.02 - Put more restrictions on arc fitting to prevent huge erroneous circles
                 - Added key binding for CTRL-g to copy g-code to clipboard

    Version 1.10 - Added Command line option to set the default directory
                 - Added setting option for disabling the use of variable in the g-code output
                 - Added option for b-carving (using a ball end mill in v-carve mode)
                 - Added the text to be engraved to the top of the ngc file
                 - Added max depth to the v-carve settings
                 - Eliminated failure to save g-code file when the  image file name contains extended characters.
                 - Changed the default .ngc/.svg file name when saving. Now it always uses the base of the image file name.
                 - Changed the default behavior for v-carve step size. now the default in or mm value is always
                   reset (0.010in or 0.25mm) when switching between unit types.  This will ensure that metric users
                   will start with a good default step size setting.

    Version 1.11 - Fixed error when saving clean up g-code.
                 - Removed Extra spaces from beginning of g-code preamble and post-amble
                 - Added arc fitting to the variables that are saved to and read from the g-code output file

    Version 1.12 - Added logic to add newline to g-code preamble and g-code post-amble whenever a pipe character "|" is input

    Version 1.13 - Fixed bug preventing clean up tool-paths when the "Cut Depth Limit" variable is used.

    Version 1.14 - Fixed bug preventing the use of the Cut Depth Limit when b-carving
                 - Updated website info in help menu

    Version 1.20 - Added option to enable extended (Unicode) characters
                 - Also made a small change to the v-carve algorithm to fix a special case.

    Version 1.21 - Added more command line options including a batch mode with no GUI

    Version 1.22 - Fixed three bugs associated with importing dxf files
                 - Fixed bug associated with clean up calculations
                 - Changed minimum allowable line spacing from one to zero

    Version 1.30 - When importing DXF files F-Engrave no longer relies on the direction of the
                   loop (clockwise/counter-clockwise) to determines which side to cut.  Now F-Engrave
                   determines which loops are inside of other loops and flips the directions automatically.
                 - Added a new option for "V-Carve Loop Accuracy" in v-carve settings.  This setting
                   tells F-Engrave to ignore features smaller than the set value.  This allows F-Engrave
                   to ignore small DXF imperfections that resulted in bad tool paths.

    Version 1.31 - Fixed bug that was preventing batch mode from working in V1.30

    Version 1.32 - Added limit to the length of the engraved text included in g-code file
                   comment (to prevent error with long engraved text)
                 - Changed number of decimal places output when in mm mode to 3 (still 4 places for inches)
                 - Changed g-code format for G2/G3 arcs to center format arcs (generally preferred format)
                 - Hard coded G90 and G91.1 into g-code output to make sure the output will be interpreted
                   correctly by g-code interpreters.

    Version 1.33 - Added option to scale original input image size rather than specify a image height

    Version 1.34 - Eliminated G91.1 code when arc fitting is disabled.  When arc fitting is disabled
                   the code (G91.1) is not needed and it may cause problems for interpretors that do not
                   support that code (i.e. ShapeOko)

    Version 1.35 - Fixed importing of ellipse features from DXF files. Ellipse end overlapped the beginning
                   of the ellipse.
                 - Fixed saving long text to .ncg files.  Long text was truncated when a .ngc file was opened.

    Version 1.36 - Fixed major bug preventing saving .ncg files when the text was not a long string.

    Version 1.37 - Added logic to ignore very small line segments that caused problems v-carving some graphic input files.

    Version 1.38 - Changed default origin to the DXF input file origin when height is set by percentage of DXF image size.

    Version 1.39 - Fixed bug in v-carving routine resulting in failed v-carve calculation. (Bug introduced in Version 1.37)

    Version 1.40 - Added code to increased v-carving speed (based on input from geo01005)
                 - Windows executable file now generated from Python 2.5 with Psyco support (significant speed increase)
                 - Changed Default Origin behavior (for DXF/Image files) to be the origin of the DXF file or lower left
                   corner of the input image.
                 - Added automatic scaling of all linear dimensions values when changing between units (in/mm)
                 - Fixed bug in clean up function in the v-carve menu.  (the bug resulted in excessive Z motions in some cases)
                 - Fixed bug resulting in the last step of v-carving for any given loop to be skipped/incorrect.

    Version 1.41 - Adjusted global Zero value (previous value resulted in rounding errors in some cases)
                 - Removed use of accuracy (Acc) in the v-carve circle calculation

    Version 1.42 - Changed default to disable variables in g-code output.

    Version 1.43 - Fixed bug in v-carve cleanup routing that caused some areas to not be cleaned up.

    Version 1.44 - Fixed really bad bug in v-carve cleanup for bitmap images introduced in V1.43

    Version 1.45 - Added multi-pass cutting for v-carving
                 - Removed "Inside Corner Angle" and "Outside Corner Angle" options

    Version 1.46 - Fixed bug which cause double cutting of v-carve pattern when multi-pass cutting was disabled

    Version 1.47 - Added ability to read more types of DXF files (files using BLOCKS with the INSERT command)
                 - Fixed errors when running batch mode for v-carving.
                 - Added .tap to the drop down list of file extensions in the file save dialog

    Version 1.48 - Fixed another bug in the multi-pass code resulting in multi-pass cutting when multi-pass cutting was disabled.

    Version 1.49 - Added option to suppress option recovery comments in the g-code output
                 - Added button in "General Settings" to automatically save a configuration (config.ngc) file

    Version 1.50 - Modified helper program (ttf2cxf_stream) and F-Engrave interaction with it to better control the line
	           segment approximation of arcs.
                 - Added straight cutter support
                 - Added option to create prismatic cuts (inverse of v-carve).  This option opens the
                   possibility of making v-carve inlays.
                 - Fixed minor bug in the v-bit cleanup tool-path generation
                 - Changed the behavior when using inverting normals for v-carving.  Now a box is automatically
                   generated to bound the cutting on the outside of the design/lettering.  The size of the box is
                   controlled by the Box/Circle Gap setting in the general settings.
                 - Removed v-carve accuracy setting
                 - Added option for radius format g-code arcs when arc fitting.  This will help compatibility
                   with g-code interpreters that are missing support for center format arcs.

    Version 1.51 - Added Plunge feed rate setting (if set to zero the normal feed rate applies)
                 - Removed default coolant start/stop M codes for the header and footer
                 - Changed default footer to include a newline character between the M codes another Shapeoko/GRBL problem.
                 - Fixed some Python 3 incompatibilities with reading configuration files

    Version 1.52 - Fixed potential divide by zero error in DXF reader
                 - Text mode now includes space for leading carriage returns (i.e. Carriage returns before text characters)                 

    Version 1.53 - Changed space for leading carriage returns to only apply at 0,90,270 and 180 degree rotations.
                 - Added floating tool tips to the options on the main window (hover over the option labels to see the tool tip text)

    Version 1.54 - Fixed bug that resulted in errors if the path to a file contained the text of an F-Engrave setting variable
                 - Reduced time to open existing g-code files by eliminating unnecessary recalculation calls.
                 - Added configuration variable to remember the last. Folder location used when a configuration file is saved.
                 - Added support for most jpg, gif, tif and png files (it is still best to use Bitmaps)
                 - After saving a new configuration file the settings menu will now pop back to the top (sometimes it would get buried under other windows)
                 - Now searches current folder and home folder for image files when opening existing g-code files.
                   previously the image file needed to be in the exact path location as when the file was saved

    Version 1.55 - Fixed error in line/curve fitting that resulted in bad output with high Accuracy settings
                 - Fixed missing parentheses on file close commands (resulted in problems when using PyPy
                 - Suppress comments in g-code should now suppress all full line g-code comments
                 - Fixed error that resulted in cutting outside the lines with large Accuracy settings 

    Version 1.56 - Changed line/curve fitting to use Douglas-Peucker curve fitting routine originally from LinuxCNC image2gcode
                 - Re-enabled the use of #2 variable when engraving with variable enabled (was broken in previous version)
                 - Fixed SVG export (was broken in previous version)
                 
    Version 1.57 - Fixed feed rate. Changes in 1.56 resulted in feed rate not being written to g-code file.
                     
    Version 1.58 - Fixed some special cases which resulted in errors being thrown (v-carve single lines)
                 - Changed the default settings to be more compatable with incomplete g-code interpretors like GRBL
    """

version = '1.58'
#Setting QUIET to True will stop almost all console messages
QUIET = False

import sys
VERSION = sys.version_info[0]

if VERSION == 3:
    from tkinter import *
    from tkinter.filedialog import *
    import tkinter.messagebox
    MAXINT = sys.maxsize
else:
    from Tkinter import *
    from tkFileDialog import *
    import tkMessageBox
    MAXINT = sys.maxint

if VERSION < 3 and sys.version_info[1] < 6:
    def next(item):
        return item.next()

try:
    import psyco
    psyco.full()
    sys.stdout.write("(Psyco loaded: You have the fastest F-Engrave.)\n")
except:
    pass


PIL = True
if PIL == True:
    try:
        from PIL import Image
        from PIL import ImageTk
        from PIL import ImageOps
        import _imaging
    except:
        try:
            from PIL.Image import core as _imaging # for debian jessie
        except:
            PIL = False


from math import *
from time import time
import os
import re
import binascii
import getopt
from subprocess import Popen, PIPE
import webbrowser

IN_AXIS   = "AXIS_PROGRESS_BAR" in os.environ

Zero       = 0.00001  #Changed from 0.0000001 to 0.00001 V1.41
STOP_CALC = 0

#raw_input("PAUSED: Press ENTER to continue")
################################################################################
#             Function for outputting messages to different locations          #
#            depending on what options are enabled                             #
################################################################################
def fmessage(text,newline=True):
    global IN_AXIS, QUIET
    if (not IN_AXIS and not QUIET):
        if newline==True:
            try:
                sys.stdout.write(text)
                sys.stdout.write("\n")
            except:
                pass
        else:
            try:
                sys.stdout.write(text)
            except:
                pass

def message_box(title,message):
    if VERSION == 3:
        tkinter.messagebox.showinfo(title,message)
    else:
        tkMessageBox.showinfo(title,message)
        pass

def message_ask_ok_cancel(title, mess):
    if VERSION == 3:
        result=tkinter.messagebox.askokcancel(title, mess)
    else:
        result=tkMessageBox.askokcancel(title, mess)
    return result

############################################################################
# routine takes an x and a y coords and does a coordinate transformation   #
# to a new coordinate system at angle from the initial coordinate system   #
# Returns new x,y tuple                                                    #
############################################################################
def Transform(x,y,angle):
    newx = x * cos(angle) - y * sin(angle)
    newy = x * sin(angle) + y * cos(angle)
    return newx,newy

############################################################################
# routine takes an sin and cos and returns the angle (between 0 and 360)   #
############################################################################
def Get_Angle(s,c):
    if   (s >= 0.0 and c >= 0.0):
        angle = degrees( acos(c) )
    elif (s >= 0.0 and c < 0.0):
        angle = degrees( acos(c) )
    elif (s < 0.0 and c <= 0.0):
        angle = 360-degrees( acos(c) )
    elif (s < 0.0 and c > 0.0):
        angle = 360-degrees( acos(c) )
    else:
        pass
    if angle < 0.001 and s < 0:
        angle == 360.0
    if angle > 359.999 and s >= 0:
        angle == 0.0
    return angle

################################################################################
# This routine parses the .cxf font file and builds a font dictionary of       #
# line segment strokes required to cut each character.                         #
# Arcs (only used in some fonts) are converted to a number of line             #
# segments based on the angular length of the arc. Since the idea of           #
# this font description is to make it support independent x and y scaling,     #
# we do not use native arcs in the g-code.                                      #
################################################################################
def parse(file,segarc):
    font = {}
    key = None
    stroke_list = []
    xmax, ymax = 0, 0
    for text_in in file:
        text = text_in+" "
        # format for a typical letter (lower-case r):
        # #comment, with a blank line after it
        #
        # [r] 3  (or "[0072] r" where 0072 is the HEX value of the character)
        # L 0,0,0,6
        # L 0,6,2,6
        # A 2,5,1,0,90
        #
        end_char = len(text)
        if end_char and key: #save the character to our dictionary
            font[key] = Character(key)
            font[key].stroke_list = stroke_list
            font[key].xmax = xmax

        new_cmd = re.match('^\[(.*)\]\s', text)
        if new_cmd: #new character
            key_tmp = new_cmd.group(1)
            if len(new_cmd.group(1)) == 1:
                key = ord(key_tmp)
            else:
                if len(key_tmp) == 5:
                    key_tmp = key_tmp[1:]
                if len(key_tmp) == 4:
                    try:
                        key=int(key_tmp,16)
                    except:
                        key = None
                        stroke_list = []
                        xmax, ymax = 0, 0
                        continue
                else:
                    key = None
                    stroke_list = []
                    xmax, ymax = 0, 0
                    continue
            stroke_list = []
            xmax, ymax = 0, 0

        line_cmd = re.match('^L (.*)', text)
        if line_cmd:
            coords = line_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            stroke_list += [Line(coords)]
            xmax = max(xmax, coords[0], coords[2])

        arc_cmd = re.match('^A (.*)', text)
        if arc_cmd:
            coords = arc_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            xcenter, ycenter, radius, start_angle, end_angle = coords

            # since font defn has arcs as ccw, we need some font foo
            if ( end_angle < start_angle ):
                start_angle -= 360.0

            # approximate arc with line seg every "segarc" degrees
            segs = int((end_angle - start_angle) / segarc)+1
            angleincr = (end_angle - start_angle)/segs
            xstart = cos( radians(start_angle) ) * radius + xcenter
            ystart = sin( radians(start_angle) ) * radius + ycenter
            angle = start_angle
            for i in range(segs):
                angle += angleincr
                xend = cos( radians(angle) ) * radius + xcenter
                yend = sin( radians(angle) ) * radius + ycenter
                coords = [xstart,ystart,xend,yend]
                stroke_list += [Line(coords)]
                xmax = max(xmax, coords[0], coords[2])
                ymax = max(ymax, coords[1], coords[3])
                xstart = xend
                ystart = yend
    return font

################################################################################
def parse_dxf(dxf_file,segarc,new_origin=True):
    # Initialize / reset
    font = {}
    key = None
    stroke_list = []
    xmax, ymax = -1e10, -1e10
    xmin, ymin =  1e10,  1e10
    dxf_import=DXF_CLASS()
    dxf_import.GET_DXF_DATA(dxf_file,tol_deg=segarc)
    dxfcoords=dxf_import.DXF_COORDS_GET(new_origin)

    ##save the character to our dictionary
    key = ord("F")
    stroke_list=[]
    for line in dxfcoords:
        XY=line
        stroke_list += [ Line([ XY[0],XY[1],XY[2],XY[3] ]) ]
        xmax=max(xmax,XY[0],XY[2])
        ymax=max(ymax,XY[1],XY[3])
        xmin=min(xmin,XY[0],XY[2])
        ymin=min(ymin,XY[1],XY[3])

    font[key] = Character(key)
    font[key].stroke_list = stroke_list
    font[key].xmax = xmax
    font[key].ymax = ymax
    font[key].xmin = xmin
    font[key].ymin = ymin

    return font
################################################################################

class Character:
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%%s" % (self.stroke_list)

    def get_xmax(self):
        try: return max([s.xmax for s in self.stroke_list[:]])
        except ValueError: return 0

    def get_ymax(self):
        try: return max([s.ymax for s in self.stroke_list[:]])
        except ValueError: return 0

    def get_ymin(self):
        try: return min([s.ymin for s in self.stroke_list[:]])
        except ValueError: return 0

################################################################################
class Line:

    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords
        self.xmax = max(self.xstart, self.xend)
        self.ymax = max(self.ystart, self.yend)
        self.ymin = min(self.ystart, self.yend)

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" % (self.xstart, self.ystart, self.xend, self.yend)
################################################################################
####################################################
##     PointClass from dxf2gcode_b02_point.py     ##
####################################################
class PointClass:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y
    def __str__(self):
        return ('X ->%6.3f  Y ->%6.3f' %(self.x,self.y))

####################################################
##  Begin Excerpts from dxf2gcode_b02_nurbs_calc  ##
####################################################
class NURBSClass:
    def __init__(self,degree=0,Knots=[],Weights=None,CPoints=None):
        self.degree=degree              #Spline degree
        self.Knots=Knots                #Knot Vector
        self.CPoints=CPoints            #Control points of splines [2D]
        self.Weights=Weights            #Weighting of the individual points

        #Initializing calculated variables
        self.HCPts=[]                   #Homogeneous points vectors [3D]

        #Convert Points in Homogeneous points
        self.CPts_2_HCPts()

        #Creating the BSplineKlasse to calculate the homogeneous points
        self.BSpline=BSplineClass(degree=self.degree,\
                                  Knots=self.Knots,\
                                  CPts=self.HCPts)

    #Calculate a number of evenly distributed points
    def calc_curve_old(self,n=0, cpts_nr=20):
        #Initial values for step and u
        u=0; Points=[]
        step=self.Knots[-1]/(cpts_nr-1)
        while u<=self.Knots[-1]:
            Pt=self.NURBS_evaluate(n=n,u=u)
            Points.append(Pt)
            u+=step
        return Points


    #Calculate a number points using error limiting
    def calc_curve(self,n=0, tol_deg=20):
        #Initial values for step and u
        u=0; Points=[]

        tol = radians(tol_deg)
        i=1
        while self.Knots[i]==0:
            i=i+1
        step=self.Knots[i]/3

        Pt1=self.NURBS_evaluate(n=n,u=0.0)
        Points.append(Pt1)
        while u<self.Knots[-1]:
            if (u+step > self.Knots[-1]):
                step = self.Knots[-1]-u

            Pt2=self.NURBS_evaluate(n=n,u=u+step)
            Pt_test=self.NURBS_evaluate(n=n,u=u + step/2)

            ###
            DX = Pt2.x-Pt1.x
            DY = Pt2.y-Pt1.y
            cord = sqrt(DX*DX + DY*DY)
            DXtest = Pt_test.x-(Pt1.x+Pt2.x)/2
            DYtest = Pt_test.y-(Pt1.y+Pt2.y)/2
            t = sqrt(DXtest*DXtest + DYtest*DYtest)
            if (abs(t) > Zero):
                R = (cord*cord/4 + t*t)/(2*t)
            else:
                R = 0

            dx1 = (Pt_test.x - Pt1.x)
            dy1 = (Pt_test.y - Pt1.y)
            L1 = sqrt(dx1*dx1 + dy1*dy1)

            dx2 = (Pt2.x - Pt_test.x)
            dy2 = (Pt2.y - Pt_test.y)
            L2 = sqrt(dx2*dx2 + dy2*dy2)

            if L1 > Zero and L2 > Zero and R > Zero:
                angle = 2 * asin((cord/2)/R)
            else:
                angle=0.0

            if angle > tol:
                step = step/2
            else:
                u+=step
                Points.append(Pt2)
                step = step*2
                Pt1=Pt2
        return Points


    #Calculate a point of NURBS
    def NURBS_evaluate(self,n=0,u=0):

        #Calculate the homogeneous points to the n th derivative
        HPt=self.BSpline.bspline_ders_evaluate(n=n,u=u)

        #Point back to normal coordinates transform
        Point=self.HPt_2_Pt(HPt[0])
        return Point

    #Convert the NURBS control points and weight in a homogeneous vector
    def CPts_2_HCPts(self):
        for P_nr in range(len(self.CPoints)):
            HCPtVec=[self.CPoints[P_nr].x*self.Weights[P_nr],\
                       self.CPoints[P_nr].y*self.Weights[P_nr],\
                       self.Weights[P_nr]]
            self.HCPts.append(HCPtVec[:])

    #Convert a homogeneous vector point in a point
    def HPt_2_Pt(self,HPt):
        return PointClass(x=HPt[0]/HPt[-1],y=HPt[1]/HPt[-1])

class BSplineClass:
    def __init__(self,degree=0,Knots=[],CPts=[]):
        self.degree=degree
        self.Knots=Knots
        self.CPts=CPts

        self.Knots_len=len(self.Knots)
        self.CPt_len=len(self.CPts[0])
        self.CPts_len=len(self.CPts)

        # Incoming inspection, fit the upper node number, etc.
        if  self.Knots_len< self.degree+1:
            fmessage("SPLINE: degree greater than number of control points.")
        if self.Knots_len != (self.CPts_len + self.degree+1):
            fmessage("SPLINE: Knot/Control Point/degree number error.")

    #Modified Version of Algorithm A3.2 from "THE NURBS BOOK" pg.93
    def bspline_ders_evaluate(self,n=0,u=0):
        #Calculating the position of the node vector
        span=self.findspan(u)

        #Compute the basis function up to the n th derivative at the point u
        dN=self.ders_basis_functions(span,u,n)

        p=self.degree
        du=min(n,p)

        CK=[]
        dPts=[]
        for i in range(self.CPt_len):
            dPts.append(0.0)
        for k in range(n+1):
            CK.append(dPts[:])

        for k in range(du+1):
            for j in range(p+1):
                for i in range(self.CPt_len):
                    CK[k][i]+=dN[k][j]*self.CPts[span-p+j][i]
        return CK

    #Algorithm A2.1 from "THE NURBS BOOK" pg.68
    def findspan(self,u):
        #Special case when the value is == Endpoint
        if(u==self.Knots[-1]):
            return self.Knots_len-self.degree-2

        # Binary search
        # (The interval from high to low is always halved by
        # [mid: mi +1] value lies between the interval of Knots)
        low=self.degree
        high=self.Knots_len
        mid=int((low+high)/2)
        while ((u<self.Knots[mid])or(u>=self.Knots[mid+1])):
            if (u<self.Knots[mid]):
                high=mid
            else:
                low=mid
            mid=int((low+high)/2)
        return mid

    #Algorithm A2.3 from "THE NURBS BOOK" pg.72
    def ders_basis_functions(self,span,u,n):
        d=self.degree

        #Initialize the a matrix
        a=[]
        zeile=[]
        for j in range(d+1):
            zeile.append(0.0)
        a.append(zeile[:]); a.append(zeile[:])

        #Initialize the ndu matrix
        ndu=[]
        zeile=[]
        for i in range(d+1):
            zeile.append(0.0)
        for j in range(d+1):
            ndu.append(zeile[:])

        #Initialize the ders matrix
        ders=[]
        zeile=[]
        for i in range(d+1):
            zeile.append(0.0)
        for j in range(n+1):
            ders.append(zeile[:])

        ndu[0][0]=1.0
        left=[0]
        right=[0]

        for j in range(1,d+1):
            left.append(u-self.Knots[span+1-j])
            right.append(self.Knots[span+j]-u)
            saved=0.0
            for r in range(j):
                #Lower Triangle
                ndu[j][r]=right[r+1]+left[j-r]
                temp=ndu[r][j-1]/ndu[j][r]
                #Upper Triangle
                ndu[r][j]=saved+right[r+1]*temp
                saved=left[j-r]*temp
            ndu[j][j]=saved

        #Load the basis functions
        for j in range(d+1):
            ders[0][j]=ndu[j][d]

        #This section computes the derivatives (Eq. [2.9])
        for r in range(d+1): #Loop over function index
            s1=0; s2=1  #Alternate rows in array a
            a[0][0]=1.0
            for k in range(1,n+1):
                der=0.0
                rk=r-k; pk=d-k
                if(r>=k):
                    a[s2][0]=a[s1][0]/ndu[pk+1][rk]
                    der=a[s2][0]*ndu[rk][pk]
                if (rk>=-1):
                    j1=1
                else:
                    j1=-rk
                if (r-1<=pk):
                    j2=k-1
                else:
                    j2=d-r

                #Here he is not in the first derivative of pure
                for j in range(j1,j2+1):
                    a[s2][j]=(a[s1][j]-a[s1][j-1])/ndu[pk+1][rk+j]
                    der+=a[s2][j]*ndu[rk+j][pk]

                if(r<=pk):
                    a[s2][k]=-a[s1][k-1]/ndu[pk+1][r]
                    der+=a[s2][k]*ndu[r][pk]

                ders[k][r]=der
                j=s1; s1=s2; s2=j #Switch rows

        #Multiply through by the the correct factors
        r=d
        for k in range(1,n+1):
            for j in range(d+1):
                ders[k][j] *=r
            r*=(d-k)
        return ders

####################################################
##  End Excerpts from dxf2gcode_b02_nurbs_calc.py ##
####################################################

class Header:
    def __init__(self):
        self.variables = dict()
        self.last_var = None
    def new_var(self, kw):
        self.variables.update({kw: dict()})
        self.last_var = self.variables[kw]
    def new_val(self, val):
        self.last_var.update({ str(val[0]) : val[1] })

class Entity:
    def __init__(self, _type):
        self.type = _type
        self.data = dict()
    def update(self, value):
        key = str(value[0])
        val = value[1]
        if key in self.data:
            if type(self.data[key]) != list:
                self.data[key] = [self.data[key]]
            self.data[key].append(val)
        else:
            self.data.update({key:val})

class Entities:
    def __init__(self):
        self.entities = []
        self.last = None
    def new_entity(self, _type):
        e = Entity(_type)
        self.entities.append(e)
        self.last = e
    def update(self, value):
        self.last.update(value)

class Block:
    def __init__(self, master):
        self.master = master
        self.data = dict()
        self.entities = []
        self.le = None
    def new_entity(self, value):
        self.le = Entity(value)
        self.entities.append(self.le)
    def update(self, value):
        if self.le == None:
            val = str(value[0])
            self.data.update({val:value[1]})
            if val == "2":
                self.master.blocks[value[1]] = self
        else:
            self.le.update(value)

class Blocks:
    def __init__(self):
        self.blocks = dict()
        self.last_var = None
    def new_block(self):
        b = Block(self)
        self.last_block = b
        self.last_var = b
    def new_entity(self, value):
        self.last_block.new_entity(value)
    def update(self, value):
        self.last_block.update(value)

class DXF_CLASS:
    def __init__(self):
        self.coords = []
        strings = []
        floats = []
        ints = []

        strings += list(range(0, 10))     #String (255 characters maximum; less for Unicode strings)
        floats += list(range(10, 60))     #Double precision 3D point
        ints += list(range(60, 80))       #16-bit integer value
        ints += list(range(90,100))       #32-bit integer value
        strings += [100]            #String (255 characters maximum; less for Unicode strings)
        strings += [102]            #String (255 characters maximum; less for Unicode strings
        strings += [105]            #String representing hexadecimal (hex) handle value
        floats += list(range(140, 148))   #Double precision scalar floating-point value
        ints += list(range(170, 176))     #16-bit integer value
        ints += list(range(280, 290))     #8-bit integer value
        strings += list(range(300, 310))  #Arbitrary text string
        strings += list(range(310, 320))  #String representing hex value of binary chunk
        strings += list(range(320, 330))  #String representing hex handle value
        strings += list(range(330, 369))  #String representing hex object IDs
        strings += [999]            #Comment (string)
        strings += list(range(1000, 1010))#String (255 characters maximum; less for Unicode strings)
        floats += list(range(1010, 1060)) #Floating-point value
        ints += list(range(1060, 1071))   #16-bit integer value
        ints += [1071]              #32-bit integer value

        self.funs = []
        for i in range(0,1072):
            self.funs.append(self.read_none)

        for i in strings:
            self.funs[i] = self.read_string

        for i in floats:
            self.funs[i] = self.read_float

        for i in ints:
            self.funs[i] = self.read_int

    def read_int(self,data):
        return int(float(data))

    def read_float(self,data):
        return float(data)

    def read_string(self,data):
        return str(data)

    def read_none(self,data):
        return None

###    def read_dxf_file(self, name, data):
###        fd = file(name)
###        Skip = True
###        for line in fd:
###            group_code = int(line)
###
###            value = fd.next().replace('\r', '')
###            value = value.replace('\n', '')
###            value = value.lstrip(' ')
###            value = value.rstrip(' ')
###            value = self.funs[group_code](value)
###            if (value != "SECTION") and Skip:
###                continue
###            else:
###                Skip = False
###            data.append((group_code, value))
###        fd.close()

    def read_dxf_data(self, fd, data):
        self.comment="None"
        Skip = True
        fd_iter = iter(fd)
        for line in fd_iter:
            try:
                group_code = int(line)
                value = next(fd_iter).replace('\r', '')
                value = value.replace('\n', '')
                value = value.lstrip(' ')
                value = value.rstrip(' ')
                value = self.funs[group_code](value)
                if (value != "SECTION") and Skip:
                    if group_code==999:
                        self.comment=value
                    continue
                else:
                    Skip = False
                data.append((group_code, value))
            except:
                pass

    def bulge_coords(self,x0,y0,x1,y1,bulge,tol_deg=20):
        global Zero
        bcoords=[]
        if bulge < 0.0:
            sign = 1
            bulge=abs(bulge)
        else:
            sign = -1

        dx      = x1-x0
        dy      = y1-y0
        c       = sqrt(dx**2 + dy**2)
        alpha   = 2.0 * (atan(bulge))
        R       = c / (2*sin(alpha))
        L       = R * cos(alpha)
        steps   = ceil(2*alpha / radians(tol_deg))

        if abs(c) < Zero:
            phi = 0
            bcoords.append([x0,y0,x1,y1])
            return bcoords

        seg_sin =  dy/c
        seg_cos =  dx/c
        phi = Get_Angle(seg_sin,seg_cos)

        d_theta = 2*alpha / steps
        theta = alpha - d_theta

        xa = x0
        ya = y0
        for i in range(1,int(steps)):
            xp = c/2 - R*sin(theta)
            yp = R*cos(theta) - L
            xb,yb = Transform(xp,yp*sign,radians(phi))
            xb=xb+x0
            yb=yb+y0

            bcoords.append([xa,ya,xb,yb])
            xa = xb
            ya = yb
            theta = theta -d_theta
        bcoords.append([xa,ya,x1,y1])
        return bcoords

    def add_coords(self,line,offset,scale,rotate):
        x0s = line[0]*scale[0]
        y0s = line[1]*scale[1]
        x1s = line[2]*scale[0]
        y1s = line[3]*scale[1]

        if abs(rotate) > Zero:
            rad = radians(rotate)
            x0r = x0s*cos(rad) - y0s*sin(rad)
            y0r = x0s*sin(rad) + y0s*cos(rad)
            x1r = x1s*cos(rad) - y1s*sin(rad)
            y1r = x1s*sin(rad) + y1s*cos(rad)
        else:
            x0r = x0s
            y0r = y0s
            x1r = x1s
            y1r = y1s

        x0 = x0r + offset[0]
        y0 = y0r + offset[1]
        x1 = x1r + offset[0]
        y1 = y1r + offset[1]

        self.coords.append([x0,y0,x1,y1])

    def eval_entity(self,e,bl,tol_deg=20,offset=[0,0],scale=[1,1],rotate=0):
        ############# LINE ############
        if e.type == "LINE":
            x0 = e.data["10"]
            y0 = e.data["20"]
            x1 = e.data["11"]
            y1 = e.data["21"]
            self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
        ############# ARC #############
        elif e.type == "ARC":
            x     = e.data["10"]
            y     = e.data["20"]
            r     = e.data["40"]
            start = e.data["50"]
            end   = e.data["51"]

            if end < start:
                end=end+360.0
            delta  = end-start
            angle_steps = max(floor(delta/tol_deg),2)

            start_r = radians(start)
            end_r   = radians(end)

            step_phi = radians( delta/angle_steps )
            x0 = x + r * cos(start_r)
            y0 = y + r * sin(start_r)
            pcnt = 1
            while pcnt < angle_steps+1:
                phi = start_r + pcnt*step_phi
                x1 = x + r * cos(phi)
                y1 = y + r * sin(phi)
                self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
                x0=x1
                y0=y1
                pcnt += 1

        ######### LWPOLYLINE ##########
        elif e.type == "LWPOLYLINE":
            flag=0
            lpcnt=-1
            for x,y in zip(e.data["10"], e.data["20"]):
                x1 = x
                y1 = y
                lpcnt=lpcnt+1
                try:
                    bulge1 = e.data["42"][lpcnt]
                except:
                    bulge1 = 0

                if flag==0:
                    x0=x1
                    y0=y1
                    bulge0=bulge1
                    flag=1
                else:
                    if bulge0 != 0:
                        bcoords = self.bulge_coords(x0,y0,x1,y1,bulge0,tol_deg)
                        for line in bcoords:
                            self.add_coords(line,offset,scale,rotate)
                    else:
                        self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
                    x0     = x1
                    y0     = y1
                    bulge0 = bulge1

            if (e.data["70"]!=0):
                x1 = e.data["10"][0]
                y1 = e.data["20"][0]
                if bulge0 != 0:
                    bcoords = self.bulge_coords(x0,y0,x1,y1,bulge1,tol_deg)
                    for line in bcoords:
                        self.add_coords(line,offset,scale,rotate)
                else:
                    self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
        ########### CIRCLE ############
        elif e.type == "CIRCLE":
            x = e.data["10"]
            y = e.data["20"]
            r = e.data["40"]

            start = 0
            end   = 360
            if end < start:
                end=end+360.0
            delta  = end-start
            angle_steps = max(floor(delta)/tol_deg,2)

            start_r = radians( start )
            end_r   = radians( end )

            step_phi = radians( delta/angle_steps)
            x0 = x + r * cos(start_r)
            y0 = y + r * sin(start_r)
            pcnt = 1
            while pcnt < angle_steps+1:
                phi = start_r + pcnt*step_phi
                x1 = x + r * cos(phi)
                y1 = y + r * sin(phi)
                self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
                x0=x1
                y0=y1
                pcnt += 1

        ############ SPLINE ###########
        elif e.type == "SPLINE":
            self.Spline_flag=[]
            self.degree=1
            self.Knots=[]
            self.Weights=[]
            self.CPoints=[]

            self.Spline_flag = int(e.data["70"])
            self.degree      = int(e.data["71"])
            self.Knots       =     e.data["40"]
            try:
                self.Weights = e.data["41"]
            except:
                for K in self.Knots:
                    self.Weights.append(1)
                pass

            for x,y in zip(e.data["10"], e.data["20"]):
                self.CPoints.append(PointClass(float(x), float(y)))

            self.MYNURBS=NURBSClass(degree=self.degree, \
                                     Knots=self.Knots,  \
                                   Weights=self.Weights,\
                                   CPoints=self.CPoints)

            mypoints=self.MYNURBS.calc_curve(n=0, tol_deg=tol_deg)
            flag = 0
            for XY in mypoints:
                x1 = XY.x
                y1 = XY.y
                if flag==0:
                    x0=x1
                    y0=y1
                    flag=1
                else:
                    self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
                    x0=x1
                    y0=y1

        ########### ELLIPSE ###########
        elif e.type == "ELLIPSE":
            #X and Y center points
            xcp = e.data["10"]
            ycp = e.data["20"]

            #X and Y of major axis end point
            xma = e.data["11"]
            yma = e.data["21"]

            #Ratio of minor axis to major axis
            ratio = e.data["40"]

            #Start and end angles (in radians 0 and 2pi for full ellipse)
            start = degrees( e.data["41"] )
            end   = degrees( e.data["42"] )

            rotation = atan2(yma, xma)
            a = sqrt(xma**2 + yma**2)
            b = a * ratio

            ##################
            if end < start:
                end=end+360.0
            delta  = end-start


            start_r = radians( start )
            end_r   = radians( end )

            tol = radians( tol_deg )

            phi = start_r
            x1 = xcp + ( a*cos(phi) * cos(rotation) - b*sin(phi) * sin(rotation) );
            y1 = ycp + ( a*cos(phi) * sin(rotation) + b*sin(phi) * cos(rotation) );
            step=tol
            while phi < end_r:
                if (phi+step > end_r):
                    step = end_r-phi

                x2 = xcp + ( a*cos(phi+step) * cos(rotation) - b*sin(phi+step) * sin(rotation) );
                y2 = ycp + ( a*cos(phi+step) * sin(rotation) + b*sin(phi+step) * cos(rotation) );

                x_test = xcp + ( a*cos(phi+step/2) * cos(rotation) - b*sin(phi+step/2) * sin(rotation) );
                y_test = ycp + ( a*cos(phi+step/2) * sin(rotation) + b*sin(phi+step/2) * cos(rotation) );

                dx1 = (x_test - x1)
                dy1 = (y_test - y1)
                L1 = sqrt(dx1*dx1 + dy1*dy1)

                dx2 = (x2 - x_test)
                dy2 = (y2 - y_test)
                L2 = sqrt(dx2*dx2 + dy2*dy2)

                angle=acos( dx1/L1 * dx2/L2 + dy1/L1 * dy2/L2)

                if angle > tol:
                    step = step/2
                else:
                    phi+=step
                    self.add_coords([x1,y1,x2,y2],offset,scale,rotate)
                    step = step*2
                    x1=x2
                    y1=y2
        ########### ELLIPSE ###########
        elif e.type == "OLD_ELLIPSE":
            #X and Y center points
            xcp = e.data["10"]
            ycp = e.data["20"]
            #X and Y of major axis end point
            xma = e.data["11"]
            yma = e.data["21"]
            #Ratio of minor axis to major axis
            ratio = e.data["40"]
            #Start and end angles (in radians 0 and 2pi for full ellipse)
            start = degrees( e.data["41"] )
            end   = degrees( e.data["42"] )

            rotation = atan2(yma, xma)
            a = sqrt(xma**2 + yma**2)
            b = a * ratio

            ##################
            if end < start:
                end=end+360.0
            delta  = end-start
            angle_steps = max(floor(delta/tol_deg),2)

            start_r = radians( start )
            end_r   = radians( end )

            step_phi = radians( delta/angle_steps )
            x0 = xcp + ( a*cos(start_r) * cos(rotation) - b*sin(start_r) * sin(rotation) );
            y0 = ycp + ( a*cos(start_r) * sin(rotation) + b*sin(start_r) * cos(rotation) );
            pcnt = 1
            while pcnt < angle_steps+1:
                phi = start_r + pcnt*step_phi
                x1 = xcp + ( a*cos(phi) * cos(rotation) - b*sin(phi) * sin(rotation) );
                y1 = ycp + ( a*cos(phi) * sin(rotation) + b*sin(phi) * cos(rotation) );
                self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
                x0=x1
                y0=y1
                pcnt += 1

        ########### LEADER ###########
        elif e.type == "LEADER":
            flag=0
            for x,y in zip(e.data["10"], e.data["20"]):
                x1 = x
                y1 = y
                if flag==0:
                    x0=x1
                    y0=y1
                    flag=1
                else:
                    self.add_coords([x0,y0,x1,y1],offset,scale,rotate)
                    x0=x1
                    y0=y1

        ########### POLYLINE ###########
        elif e.type == "POLYLINE":
            self.POLY_CLOSED =  0
            self.POLY_FLAG   = -1
            try:
                TYPE=e.data["70"]
                if (TYPE==0 or TYPE==8):
                    pass
                elif (TYPE==1):
                    self.POLY_CLOSED=1
                else:
                    fmessage("DXF Import Ignored: - %s - Entity" %(e.type))
                    self.POLY_FLAG = 0
            except:
                pass

        ########### SEQEND ###########
        elif e.type == "SEQEND":
            if (self.POLY_FLAG != 0):
                self.POLY_FLAG=0
                if (self.POLY_CLOSED==1):
                    self.POLY_CLOSED==0
                    x0 = self.PX
                    y0 = self.PY
                    x1 = self.PX0
                    y1 = self.PY0

                    if self.bulge != 0:
                        bcoords = self.bulge_coords(x0,y0,x1,y1,self.bulge,tol_deg)
                        for line in bcoords:
                            self.add_coords(line,offset,scale,rotate)
                    else:
                        self.add_coords([x0,y0,x1,y1],offset,scale,rotate)

            else:
                fmessage("DXF Import Ignored: - %s - Entity" %(e.type))

        ########### VERTEX ###########
        elif e.type == "VERTEX":

            if (self.POLY_FLAG==-1):
                self.PX  = e.data["10"]
                self.PY  = e.data["20"]
                self.PX0 = self.PX
                self.PY0 = self.PY
                try:
                    self.bulge = e.data["42"]
                except:
                    self.bulge = 0

                self.POLY_FLAG = 1
            elif (self.POLY_FLAG == 1):
                x0 = self.PX
                y0 = self.PY
                x1 = e.data["10"]
                y1 = e.data["20"]
                self.PX=x1
                self.PY=y1

                if self.bulge != 0:
                    bcoords = self.bulge_coords(x0,y0,x1,y1,self.bulge,tol_deg)
                    for line in bcoords:
                        self.add_coords(line,offset,scale,rotate)
                else:
                    self.add_coords([x0,y0,x1,y1],offset,scale,rotate)

                try:
                    self.bulge = e.data["42"]
                except:
                    self.bulge = 0
            else:
                fmessage("DXF Import Ignored: - %s - Entity" %(e.type))
                pass
        ########### END VERTEX ###########
        ########### INSERT ###########
        elif e.type == "INSERT":
            key = e.data["2"]
            xoff = e.data["10"]+offset[0]
            yoff = e.data["20"]+offset[1]

            try:
                xscale = e.data["41"]
            except:
                xscale = 1
            try:
                yscale = e.data["42"]
            except:
                yscale = 1
            try:
                rotate = e.data["50"]
            except:
                rotate = 0

            for e in bl.blocks[key].entities:
                self.eval_entity(e,bl,tol_deg,offset=[xoff,yoff],scale=[xscale,yscale],rotate=rotate)

        ########### END INSERT ###########
        elif e.type == "HATCH":
            #quietly ignore HATCH
            pass
        else:
            fmessage("DXF Import Ignored: %s Entity" %(e.type))
            pass



    def GET_DXF_DATA(self,fd, tol_deg=20):
        data = []
        try:
            self.read_dxf_data(fd, data)
        except:
            fmessage("\nUnable to read input DXF data!")
            return 1
        data = iter(data)
        g_code, value = None, None
        sections = dict()

        he = Header()
        bl = Blocks()
        while value != "EOF":
            g_code, value = next(data)
            if value == "SECTION":
                g_code, value = next(data)
                sections[value] = []

                while value != "ENDSEC":
                    if value == "HEADER":
                        while True:
                            g_code, value = next(data)
                            if value == "ENDSEC":
                                break
                            elif g_code == 9:
                                he.new_var(value)
                            else:
                                he.new_val((g_code, value))

                    elif value == "BLOCKS":
                        while True:
                            g_code, value = next(data)
                            if value == "ENDSEC":
                                break
                            elif value == "ENDBLK":
                                continue
                            elif value == "BLOCK":
                                bl.new_block()
                            elif g_code == 0 and value != "BLOCK":
                                bl.new_entity(value)
                            else:
                                bl.update((g_code, value))

                    elif value == "ENTITIES":
                        TYPE=""
                        en = Entities()
                        while True:
                            g_code, value = next(data)

                            ###################################
                            if g_code==0:
                                TYPE = value
                            if TYPE == "LWPOLYLINE" and g_code==10 and g_code_last==20:
                                # Add missing code 42
                                en.update((42, 0.0))
                            g_code_last = g_code
                            ###################################

                            if value == "ENDSEC":
                                break
                            elif g_code == 0 and value != "ENDSEC":
                                en.new_entity(value)
                            else:
                                en.update((g_code, value))
                    try:
                        g_code, value = next(data)
                    except:
                        break

        for e in en.entities:
            self.eval_entity(e,bl,tol_deg)


    def DXF_COORDS_GET(self,new_origin=True):
        if (new_origin==True):
            ymin=99999
            xmin=99999
            for line in self.coords:
                XY=line
                if XY[0] < xmin:
                        xmin = XY[0]
                if XY[1] < ymin:
                        ymin = XY[1]
                if XY[2] < xmin:
                        xmin = XY[2]
                if XY[3] < ymin:
                        ymin = XY[3]
        else:
            xmin=0
            ymin=0

        coords_out=[]
        for line in self.coords:
            XY=line
            coords_out.append([XY[0]-xmin, XY[1]-ymin, XY[2]-xmin, XY[3]-ymin])
        return coords_out



## Making a "ToolTip" in Tkinter
'''
http://tkinter.unpythonic.net/wiki/ToolTip

Michael Lange <klappnase (at) freakmail (dot) de>
The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
module which unfortunately seems to be broken (at least the version I saw).
INITIALIZATION OPTIONS:
anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
                default is 
bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
                entered the parent widget; default is 1500
fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
                outside of the parent widget; this may be useful if you want to use tooltips for
                large widgets like listboxes or canvases; default is 0
font :          font to use for the widget; default is system specific
justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
padx :          extra space added to the left and right within the widget; default is 4
pady :          extra space above and below the text; default is 2
relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
text :          the text that is displayed inside the widget
textvariable :  if set to an instance of Tkinter.StringVar() the variable's value will be used as text for the widget
width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
wraplength :    limits the number of characters in each line; default is 150

WIDGET METHODS:
configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
                    next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

Other widget methods that might be useful if you want to subclass ToolTip:
enter() :           callback when the mouse pointer enters the parent widget
leave() :           called when the mouse pointer leaves the parent widget
motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
                    tooltip has shown up to continually update the coordinates of the tooltip window
coords() :          calculates the screen coordinates of the tooltip window
create_contents() : creates the contents of the tooltip window (by default a Tkinter.Label)

# Ideas gleaned from PySol
'''
class ToolTip:
    def __init__(self, master, text='Your text here', delay=100, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
                      'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
                      'width':0, 'wraplength':150}
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1
    
    def configure(self, **opts):
        for key in opts:
            if self._opts.has_key(key):
                self._opts[key] = opts[key]
            else:
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError
    
    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##
    
    def enter(self, event=None):
        self._schedule()
        
    def leave(self, event=None):
        self._unschedule()
        self._hide()
    
    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))
    
    ##------the methods that do the work:---------------------------------------------------------##
    
    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()
    
    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()
                
    ##----these methods might be overridden in derived classes:----------------------------------##
    
    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = Label(self._tipwindow, **opts)
        label.pack()

# End making a "ToolTip" in tkinter

############################################################################
class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.w = 780
        self.h = 490
        frame = Frame(master, width= self.w, height=self.h)
        self.master = master
        self.x = -1
        self.y = -1
        self.initComplete = 0
        self.delay_calc = 0

        #if PIL == False:
        #    fmessage("Python Imaging Library (PIL) was not found...Bummer")
        #    fmessage("    PIL enables more image file formats.")

        cmd = ["ttf2cxf_stream","TEST","STDOUT"]
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if VERSION == 3:
                stdout = bytes.decode(stdout)
            if str.find(stdout.upper(),'TTF2CXF') != -1:
                self.TTF_AVAIL = TRUE
            else:
                self.TTF_AVAIL = FALSE
                fmessage("ttf2cxf_stream is not working...Bummer")
        except:
            fmessage("ttf2cxf_stream executable is not present/working...Bummer")
            self.TTF_AVAIL = FALSE

        cmd = ["potrace","-v"]
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if VERSION == 3:
                stdout = bytes.decode(stdout)
            if str.find(stdout.upper(),'POTRACE') != -1:
                self.POTRACE_AVAIL = TRUE
                if str.find(stdout.upper(),'1.1') == -1:
                    fmessage("F-Engrave Requires Potrace Version 1.10 or Newer.")
            else:
                self.POTRACE_AVAIL = FALSE
                fmessage("potrace is not working...Bummer")
        except:
            fmessage("potrace executable is not present/working...Bummer")
            self.POTRACE_AVAIL = FALSE

        self.createWidgets()

    def f_engrave_init(self):
        self.master.update()
        self.initComplete = 1
        self.delay_calc   = 0
        self.menu_Mode_Change()

    def createWidgets(self):
        self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind('<Escape>', self.KEY_ESC)
        self.master.bind('<F1>', self.KEY_F1)
        self.master.bind('<F2>', self.KEY_F2)
        self.master.bind('<F3>', self.KEY_F3)
        self.master.bind('<F4>', self.KEY_F4)
        self.master.bind('<F5>', self.KEY_F5) #self.Recalculate_Click)
        self.master.bind('<Control-Up>'  , self.Listbox_Key_Up)
        self.master.bind('<Control-Down>', self.Listbox_Key_Down)
        self.master.bind('<Prior>', self.KEY_ZOOM_IN) # Page Up
        self.master.bind('<Next>', self.KEY_ZOOM_OUT) # Page Down
        self.master.bind('<Control-g>', self.KEY_CTRL_G)

        self.batch      = BooleanVar()
        self.show_axis  = BooleanVar()
        self.show_box   = BooleanVar()
        self.show_thick = BooleanVar()
        self.flip       = BooleanVar()
        self.mirror     = BooleanVar()
        self.outer      = BooleanVar()
        self.upper      = BooleanVar()
        self.fontdex    = BooleanVar()
        self.v_flop     = BooleanVar()
        self.v_pplot    = BooleanVar()
        self.inlay      = BooleanVar()
        self.no_comments= BooleanVar()
        self.ext_char   = BooleanVar()
        self.var_dis    = BooleanVar()
        self.useIMGsize = BooleanVar()

        self.clean_P    = BooleanVar()
        self.clean_X    = BooleanVar()
        self.clean_Y    = BooleanVar()
        self.v_clean_P  = BooleanVar()
        self.v_clean_X  = BooleanVar()
        self.v_clean_Y  = BooleanVar()

        self.arc_fit    = StringVar()
        self.YSCALE     = StringVar()
        self.XSCALE     = StringVar()
        self.LSPACE     = StringVar()
        self.CSPACE     = StringVar()
        self.WSPACE     = StringVar()
        self.TANGLE     = StringVar()
        self.TRADIUS    = StringVar()
        self.ZSAFE      = StringVar()
        self.ZCUT       = StringVar()
        self.STHICK     = StringVar()
        self.origin     = StringVar()
        self.justify    = StringVar()
        self.units      = StringVar()

        self.xorigin    = StringVar()
        self.yorigin    = StringVar()
        self.segarc     = StringVar()
        self.accuracy   = StringVar()

        self.funits     = StringVar()
        self.FEED       = StringVar()
        self.PLUNGE     = StringVar()
        self.fontfile   = StringVar()
        self.H_CALC     = StringVar()
        self.plotbox    = StringVar()
        self.boxgap     = StringVar()
        self.fontdir    = StringVar()
        self.cut_type   = StringVar()
        self.input_type = StringVar()


        self.bit_shape  = StringVar()
        self.v_bit_angle= StringVar()
        self.v_bit_dia  = StringVar()
        self.v_depth_lim= StringVar()
        self.v_drv_crner= StringVar()
        self.v_stp_crner= StringVar()
        self.v_step_len = StringVar()
        self.allowance  = StringVar()
        self.v_check_all= StringVar()
        self.v_max_cut  = StringVar()
        self.v_rough_stk= StringVar()

        self.clean_dia  = StringVar()
        self.clean_step = StringVar()
        self.clean_v    = StringVar()
        self.clean_name = StringVar()

        self.gpre        = StringVar()
        self.gpost       = StringVar()

        self.bmp_turnpol      = StringVar()
        self.bmp_turdsize     = StringVar()
        self.bmp_alphamax     = StringVar()
        self.bmp_opttolerance = StringVar()
        self.bmp_longcurve    = BooleanVar()

        self.maxcut             = StringVar()
        self.current_input_file = StringVar()
        self.bounding_box       = StringVar()

        ###########################################################################
        #                         INITILIZE VARIABLES                             #
        #    if you want to change a default setting this is the place to do it   #
        ###########################################################################
        self.batch.set(0)
        self.show_axis.set(1)
        self.show_box.set(1)
        self.show_thick.set(1)
        self.flip.set(0)
        self.mirror.set(0)
        self.outer.set(1)
        self.upper.set(1)
        self.fontdex.set(0)
        self.useIMGsize.set(0)

        self.v_flop.set(0)
        self.v_pplot.set(0)
        self.inlay.set(0)
        self.no_comments.set(1)
        self.ext_char.set(0)
        self.var_dis.set(1)

        self.clean_P.set(1)
        self.clean_X.set(1)
        self.clean_Y.set(0)
        self.v_clean_P.set(0)
        self.v_clean_Y.set(1)
        self.v_clean_X.set(0)

        self.arc_fit.set("none") #"none", "center", "radius"
        self.YSCALE.set("2.0")
        self.XSCALE.set("100")
        self.LSPACE.set("1.1")
        self.CSPACE.set("25")
        self.WSPACE.set("100")
        self.TANGLE.set("0.0")
        self.TRADIUS.set("0.0")
        self.ZSAFE.set("0.25")
        self.ZCUT.set("-0.005")
        self.STHICK.set("0.01")
        self.origin.set("Default")      # Options are "Default",
                                        #             "Top-Left", "Top-Center", "Top-Right",
                                        #             "Mid-Left", "Mid-Center", "Mid-Right",
                                        #             "Bot-Left", "Bot-Center", "Bot-Right"

        self.justify.set("Left")        # Options are "Left", "Right", "Center"
        self.units.set("in")            # Options are "in" and "mm"
        self.FEED.set("5.0")
        self.PLUNGE.set("0.0")
        self.fontfile.set(" ")
        self.H_CALC.set("max_use")
        self.plotbox.set("no_box")
        self.boxgap.set("0.25")
        self.fontdir.set("fonts")
        self.cut_type.set("engrave")    # Options are "engrave" and "v-carve"
        self.input_type.set("text")     # Options are "text" and "image"

        self.bit_shape.set("VBIT")
        self.v_bit_angle.set("60")
        self.v_bit_dia.set("0.5")
        self.v_depth_lim.set("0.0")
        self.v_drv_crner.set("135")
        self.v_stp_crner.set("200")
        self.v_step_len.set("0.01")
        self.allowance.set("0.0")
        self.v_check_all.set("all")      # Options are "chr" and "all"
        self.v_rough_stk.set("0.0")
        self.v_max_cut.set("-1.0")

        self.bmp_turnpol.set("minority") # options: black, white, right, left, minority, majority, or random
        self.bmp_turdsize.set("2")       # default 2
        self.bmp_alphamax.set("1")       # default 1
        self.bmp_opttolerance.set("0.2") # default 0.2
        self.bmp_longcurve.set(1)        # default 1 (True)

        self.xorigin.set("0.0")
        self.yorigin.set("0.0")
        self.segarc.set("5.0")
        self.accuracy.set("0.001")

        self.segID   = []
        self.gcode   = []
        self.svgcode = []
        self.coords  = []
        self.vcoords = []
        self.clean_coords=[]
        self.clean_segment=[]
        self.clean_coords_sort=[]
        self.v_clean_coords_sort=[]

        self.clean_v.set("0.05")
        self.clean_dia.set(".25")      # Diameter of clean-up bit
        self.clean_step.set("50")      # Clean-up step-over as percent of clean-up bit diameter
        self.clean_name.set("_clean")

        self.font    = {}
        self.RADIUS_PLOT = 0
        self.MAXX    = 0
        self.MINX    = 0
        self.MAXY    = 0
        self.MINY    = 0

        self.Xzero = float(0.0)
        self.Yzero = float(0.0)
        self.default_text = "F-Engrave"
        self.HOME_DIR     =  os.path.expanduser("~")
        self.NGC_FILE     = (self.HOME_DIR+"/None")
        self.IMAGE_FILE   = (self.HOME_DIR+"/None")
        self.current_input_file.set(" ")
        self.bounding_box.set(" ")

        self.pscale = 0
        # PAN and ZOOM STUFF
        self.panx = 0
        self.panx = 0
        self.lastx = 0
        self.lasty = 0

        # Derived variables
        self.calc_depth_limit()

        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.units.set('mm')
            self.funits.set('mm/min')

        ##########################################################################
        #                         G-Code Default Preamble                        #
        ##########################################################################
        # G17        ; sets XY plane                                             #
        # G64 P0.003 ; G64 P- (motion blending tolerance set to 0.003) This is   #
        #              the default in engrave.py                                 #
        # G64        ; G64 without P option keeps the best speed possible, no    #
        #              matter how far away from the programmed point you end up. #
        # M3 S3000   ; Spindle start at 3000                                     #
        ##########################################################################
        self.gpre.set("G17 G64 P0.001 M3 S3000")

        ##########################################################################
        #                        G-Code Default Postamble                        #
        ##########################################################################
        # M5 ; Stop Spindle                                                      #
        # M9 ; Turn all coolant off                                              #
        # M2 ; End Program                                                       #
        ##########################################################################
        self.gpost.set("M5|M2")

        ##########################################################################
        ###                     END INITILIZING VARIABLES                      ###
        ##########################################################################
        config_file = "config.ngc"
        home_config1 = self.HOME_DIR + "/" + config_file
        config_file2 = ".fengraverc"
        home_config2 = self.HOME_DIR + "/" + config_file2
        if ( os.path.isfile(config_file) ):
            self.Open_G_Code_File(config_file)
        elif ( os.path.isfile(home_config1) ):
            self.Open_G_Code_File(home_config1)
        elif ( os.path.isfile(home_config2) ):
            self.Open_G_Code_File(home_config2)

        opts, args = None, None
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hbg:f:d:t:",["help","batch","gcode_file","fontdir=","defdir=","text="])
        except:
            fmessage('Unable interpret command line options')
            sys.exit()
        for option, value in opts:
            if option in ('-h','--help'):
                fmessage(' ')
                fmessage('Usage: python f-engrave.py [-g file | -f fontdir | -d directory | -t text | -b ]')
                fmessage('-g    : f-engrave gcode output file to read (also --gcode_file)')
                fmessage('-f    : path to font file, directory or image file (also --fontdir)')
                fmessage('-d    : default directory (also --defdir)')
                fmessage('-t    : engrave text (also --text)')
                fmessage('-b    : batch mode (also --batch)')
                fmessage('-h    : print this help (also --help)\n')
                sys.exit()
            if option in ('-g','--gcode_file'):
                self.Open_G_Code_File(value)
                self.NGC_FILE = value
            if option in ('-f','--fontdir'):
                if os.path.isdir(value):
                    self.fontdir.set(value)
                elif os.path.isfile(value):
                    dirname = os.path.dirname(value)
                    fileName, fileExtension = os.path.splitext(value)
                    TYPE=fileExtension.upper()
                    if TYPE=='.CXF' or TYPE=='.TTF':
                        self.input_type.set("text")
                        self.fontdir.set(dirname)
                        self.fontfile.set(os.path.basename(fileName)+fileExtension)
                    else:
                        self.input_type.set("image")
                        self.IMAGE_FILE = value
                else:
                    fmessage("File/Directory Not Found:\t%s" %(value) )

            if option in ('-d','--defdir'):
                self.HOME_DIR = value
                if str.find(self.NGC_FILE,'/None') != -1:
                    self.NGC_FILE = (self.HOME_DIR+"/None")
                if str.find(self.IMAGE_FILE,'/None') != -1:
                    self.IMAGE_FILE = (self.HOME_DIR+"/None")
            if option in ('-t','--text'):
                value = value.replace('|', '\n')

                self.default_text = value
            if option in ('-b','--batch'):
                self.batch.set(1)

        if self.batch.get():
            fmessage('(F-Engrave Batch Mode)')

            if self.input_type.get() == "text":
                self.Read_font_file()
            else:
                self.Read_image_file()

            self.DoIt()
            if self.cut_type.get() == "v-carve":
                self.V_Carve_It()
            self.WriteGCode()

            for line in self.gcode:
                try:
                    sys.stdout.write(line+'\n')
                except:
                    sys.stdout.write('(skipping line)\n')
            sys.exit()

        ##########################################################################

        # make a Status Bar
        self.statusMessage = StringVar()
        self.statusMessage.set("")
        self.statusbar = Label(self.master, textvariable=self.statusMessage, \
                                   bd=1, relief=SUNKEN , height=1)
        self.statusbar.pack(anchor=SW, fill=X, side=BOTTOM)
        self.statusMessage.set("Welcome to F-Engrave")

        # Buttons
        self.Recalculate = Button(self.master,text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

        # Canvas
        lbframe = Frame( self.master )
        self.PreviewCanvas_frame = lbframe
        self.PreviewCanvas = Canvas(lbframe, width=self.w-525, \
                                        height=self.h-200, background="grey")
        self.PreviewCanvas.pack(side=LEFT, fill=BOTH, expand=1)
        self.PreviewCanvas_frame.place(x=230, y=10)

        self.PreviewCanvas.bind("<Button-4>" , self._mouseZoomIn)
        self.PreviewCanvas.bind("<Button-5>" , self._mouseZoomOut)
        self.PreviewCanvas.bind("<2>"        , self.mousePanStart)
        self.PreviewCanvas.bind("<B2-Motion>", self.mousePan)
        self.PreviewCanvas.bind("<1>"        , self.mouseZoomStart)
        self.PreviewCanvas.bind("<B1-Motion>", self.mouseZoom)
        self.PreviewCanvas.bind("<3>"        , self.mousePanStart)
        self.PreviewCanvas.bind("<B3-Motion>", self.mousePan)

        # Left Column #
        self.Label_font_prop = Label(self.master,text="Text Font Properties:", anchor=W)
        
        self.Label_Yscale = Label(self.master,text="Text Height", anchor=CENTER)
        self.Label_Yscale_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Yscale = Entry(self.master,width="15")
        self.Entry_Yscale.configure(textvariable=self.YSCALE)
        self.Entry_Yscale.bind('<Return>', self.Recalculate_Click)
        self.YSCALE.trace_variable("w", self.Entry_Yscale_Callback)
        self.Label_Yscale_ToolTip = ToolTip(self.Label_Yscale, text= \
        'Character height of a single line of text.')
        #or the height of an imported image. (DXF, BMP, etc.)')
        
        
        self.NormalColor =  self.Entry_Yscale.cget('bg')

        self.Label_Sthick = Label(self.master,text="Line Thickness")
        self.Label_Sthick_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Sthick = Entry(self.master,width="15")
        self.Entry_Sthick.configure(textvariable=self.STHICK)
        self.Entry_Sthick.bind('<Return>', self.Recalculate_Click)
        self.STHICK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(self.Label_Sthick, text= \
        'Thickness or width of engraved lines. Set this to your engraving cutter diameter.  This setting only affects the displayed lines not the g-code output.')

        self.Label_Xscale = Label(self.master,text="Text Width", anchor=CENTER )
        self.Label_Xscale_u = Label(self.master,text="%", anchor=W)
        self.Entry_Xscale = Entry(self.master,width="15")
        self.Entry_Xscale.configure(textvariable=self.XSCALE)
        self.Entry_Xscale.bind('<Return>', self.Recalculate_Click)
        self.XSCALE.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(self.Label_Xscale, text= \
        'Scaling factor for the width of characters.')

        self.Label_useIMGsize = Label(self.master,text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_useIMGsize.configure(variable=self.useIMGsize, command = self.useIMGsize_var_Callback)

        self.Label_Cspace = Label(self.master,text="Char Spacing", anchor=CENTER )
        self.Label_Cspace_u = Label(self.master,text="%", anchor=W)
        self.Entry_Cspace = Entry(self.master,width="15")
        self.Entry_Cspace.configure(textvariable=self.CSPACE)
        self.Entry_Cspace.bind('<Return>', self.Recalculate_Click)
        self.CSPACE.trace_variable("w", self.Entry_Cspace_Callback)
        self.Label_Cspace_ToolTip = ToolTip(self.Label_Cspace, text= \
        'Character spacing as a percent of character width.')

        self.Label_Wspace = Label(self.master,text="Word Spacing", anchor=CENTER )
        self.Label_Wspace_u = Label(self.master,text="%", anchor=W)
        self.Entry_Wspace = Entry(self.master,width="15")
        self.Entry_Wspace.configure(textvariable=self.WSPACE)
        self.Entry_Wspace.bind('<Return>', self.Recalculate_Click)
        self.WSPACE.trace_variable("w", self.Entry_Wspace_Callback)
        self.Label_Wspace_ToolTip = ToolTip(self.Label_Wspace, text= \
        'Width of the space character. This is determined as a percentage of the maximum width of the characters in the currently selected font.')

        self.Label_Lspace = Label(self.master,text="Line Spacing", anchor=CENTER )
        self.Entry_Lspace = Entry(self.master,width="15")
        self.Entry_Lspace.configure(textvariable=self.LSPACE)
        self.Entry_Lspace.bind('<Return>', self.Recalculate_Click)
        self.LSPACE.trace_variable("w", self.Entry_Lspace_Callback)
        self.Label_Lspace_ToolTip = ToolTip(self.Label_Lspace, text= \
        'The vertical spacing between lines of text. This is a multiple of the text height previously input. A vertical spacing of 1.0 could result in consecutive lines of text touching each other if the maximum height character is directly below a character that extends the lowest (like a "g").')

        self.Label_pos_orient = Label(self.master,text="Text Position and Orientation:",\
                                          anchor=W)

        self.Label_Tangle = Label(self.master,text="Text Angle", anchor=CENTER )
        self.Label_Tangle_u = Label(self.master,text="deg", anchor=W)
        self.Entry_Tangle = Entry(self.master,width="15")
        self.Entry_Tangle.configure(textvariable=self.TANGLE)
        self.Entry_Tangle.bind('<Return>', self.Recalculate_Click)
        self.TANGLE.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(self.Label_Tangle, text= \
        'Rotation of the text or image from horizontal.')


        self.Label_Justify      = Label(self.master,text="Justify", anchor=CENTER )
        self.Justify_OptionMenu = OptionMenu(root, self.justify, "Left","Center",\
                                                 "Right", command=self.Recalculate_RQD_Click)
        self.Label_Justify_ToolTip = ToolTip(self.Label_Justify, text= \
        'Justify determins how to align multiple lines of text. Left side, Right side or Centered.')

        self.Label_Origin      = Label(self.master,text="Origin", anchor=CENTER )
        self.Origin_OptionMenu = OptionMenu(root, self.origin,
                                            "Top-Left",
                                            "Top-Center",
                                            "Top-Right",
                                            "Mid-Left",
                                            "Mid-Center",
                                            "Mid-Right",
                                            "Bot-Left",
                                            "Bot-Center",
                                            "Bot-Right",
                                            "Default", command=self.Recalculate_RQD_Click)
        self.Label_Origin_ToolTip = ToolTip(self.Label_Origin, text= \
        'Origin determins where the X and Y zero position is located relative to the engraving.')

        self.Label_flip = Label(self.master,text="Flip Text")
        self.Checkbutton_flip = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=self.flip)
        self.flip.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_flip_ToolTip = ToolTip(self.Label_flip, text= \
        'Selecting Flip Text/Image mirrors the design about a horizontal line')

        self.Label_mirror = Label(self.master,text="Mirror Text")
        self.Checkbutton_mirror = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=self.mirror)
        self.mirror.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_mirror_ToolTip = ToolTip(self.Label_mirror, text= \
        'Selecting Mirror Text/Image mirrors the design about a vertical line.')

        self.Label_text_on_arc = Label(self.master,text="Text on Circle Properties:",\
                                           anchor=W)

        self.Label_Tradius = Label(self.master,text="Circle Radius", anchor=CENTER )
        self.Label_Tradius_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Tradius = Entry(self.master,width="15")
        self.Entry_Tradius.configure(textvariable=self.TRADIUS)
        self.Entry_Tradius.bind('<Return>', self.Recalculate_Click)
        self.TRADIUS.trace_variable("w", self.Entry_Tradius_Callback)
        self.Label_Tradius_ToolTip = ToolTip(self.Label_Tradius, text= \
        'Circle radius is the radius of the circle that the text in the input box is placed on. If the circle radius is set to 0.0 the text is not placed on a circle.')

        self.Label_outer = Label(self.master,text="Outside circle")
        self.Checkbutton_outer = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=self.outer)
        self.outer.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_outer_ToolTip = ToolTip(self.Label_outer, text= \
        'Select whether the text is placed so that is falls on the inside of the circle radius or the outside of the circle radius.')

        self.Label_upper = Label(self.master,text="Top of Circle")
        self.Checkbutton_upper = Checkbutton(self.master,text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=self.upper)
        self.upper.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_upper_ToolTip = ToolTip(self.Label_upper, text= \
        'Select whether the text is placed on the top of the circle of on the bottom of the circle (i.e. concave down or concave up).')

        self.separator1 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(height=2, bd=1, relief=SUNKEN)

        # End Left Column #

        # Right Column #
        self.Label_gcode_opt = Label(self.master,text="Gcode Properties:", anchor=W)

        self.Label_Feed = Label(self.master,text="Feed Rate")
        self.Label_Feed_u = Label(self.master,textvariable=self.funits, anchor=W)
        self.Entry_Feed = Entry(self.master,width="15")
        self.Entry_Feed.configure(textvariable=self.FEED)
        self.Entry_Feed.bind('<Return>', self.Recalculate_Click)
        self.FEED.trace_variable("w", self.Entry_Feed_Callback)
        self.Label_Feed_ToolTip = ToolTip(self.Label_Feed, text= \
        'Specify the tool feed rate that is output in the g-code output file.')
        

        self.Label_Plunge = Label(self.master,text="Plunge Rate")
        self.Label_Plunge_u = Label(self.master,textvariable=self.funits, anchor=W)
        self.Entry_Plunge = Entry(self.master,width="15")
        self.Entry_Plunge.configure(textvariable=self.PLUNGE)
        self.Entry_Plunge.bind('<Return>', self.Recalculate_Click)
        self.PLUNGE.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(self.Label_Plunge, text= \
        'Plunge Rate sets the feed rate for vertical moves into the material being cut.\n\nWhen Plunge Rate is set to zero plunge feeds are equal to Feed Rate.')
        

        self.Label_Zsafe = Label(self.master,text="Z Safe")
        self.Label_Zsafe_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Zsafe = Entry(self.master,width="15")
        self.Entry_Zsafe.configure(textvariable=self.ZSAFE)
        self.Entry_Zsafe.bind('<Return>', self.Recalculate_Click)
        self.ZSAFE.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(self.Label_Zsafe, text= \
        'Z location that the tool will be sent to prior to any rapid moves.')

        self.Label_Zcut = Label(self.master,text="Cut Depth")
        self.Label_Zcut_u = Label(self.master,textvariable=self.units, anchor=W)
        self.Entry_Zcut = Entry(self.master,width="15")
        self.Entry_Zcut.configure(textvariable=self.ZCUT)
        self.Entry_Zcut.bind('<Return>', self.Recalculate_Click)
        self.ZCUT.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(self.Label_Zcut, text= \
        'Depth of the engraving cut. This setting has no effect when the v-carve option is selected.')

        self.Checkbutton_fontdex = Checkbutton(self.master,text="Show All Font Characters",\
                                                   anchor=W)
        self.fontdex.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Checkbutton_fontdex.configure(variable=self.fontdex)
        self.Label_fontfile = Label(self.master,textvariable=self.current_input_file, anchor=W,\
                                        foreground='grey50')
        self.Label_List_Box = Label(self.master,text="Font Files:", foreground="#101010",\
                                        anchor=W)
        lbframe = Frame( self.master )
        self.Listbox_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Listbox_1 = Listbox(lbframe, selectmode="single", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.Listbox_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Listbox_1.pack(side=LEFT, fill=BOTH, expand=1)

        self.Listbox_1.bind("<ButtonRelease-1>", self.Listbox_1_Click)
        self.Listbox_1.bind("<Up>",   self.Listbox_Key_Up)
        self.Listbox_1.bind("<Down>", self.Listbox_Key_Down)

        try:
            font_files=os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files=" "
        for name in font_files:
            if str.find(name.upper(),'.CXF') != -1 \
            or (str.find(name.upper(),'.TTF') != -1 and self.TTF_AVAIL ):
                self.Listbox_1.insert(END, name)
        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")

        self.fontdir.trace_variable("w", self.Entry_fontdir_Callback)

        self.V_Carve_Calc = Button(self.master,text="Calc V-Carve", command=self.V_Carve_Calc_Click)

        self.Radio_Cut_E = Radiobutton(self.master,text="Engrave", value="engrave", anchor=W)
        self.Radio_Cut_E.configure(variable=self.cut_type )
        self.Radio_Cut_V = Radiobutton(self.master,text="V-Carve", value="v-carve", anchor=W)
        self.Radio_Cut_V.configure(variable=self.cut_type )
        self.cut_type.trace_variable("w", self.Entry_recalc_var_Callback)
        # End Right Column #

        # Text Box
        self.Input_Label = Label(self.master,text="Input Text:",anchor=W)

        lbframe = Frame( self.master)
        self.Input_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Input = Text(lbframe, width="40", height="12", yscrollcommand=scrollbar.set,\
                              bg='white')
        self.Input.insert(END, self.default_text)
        scrollbar.config(command=self.Input.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Input.pack(side=LEFT, fill=BOTH, expand=1)
        self.Input.bind("<Key>", self.Recalculate_RQD_Nocalc)
        ## self.master.unbind("<Alt>")

        #GEN Setting Window Entry initialization
        self.Entry_Xoffset=Entry()
        self.Entry_Yoffset=Entry()
        self.Entry_BoxGap = Entry()
        self.Entry_ArcAngle = Entry()
        self.Entry_Accuracy = Entry()
        #Bitmap Setting Window Entry initialization
        self.Entry_BMPturdsize = Entry()
        self.Entry_BMPalphamax = Entry()
        self.Entry_BMPoptTolerance = Entry()
        #V-Carve Setting Window Entry initialization
        self.Entry_Vbitangle = Entry()
        self.Entry_Vbitdia = Entry()
        self.Entry_VDepthLimit = Entry()
        self.Entry_InsideAngle = Entry()
        self.Entry_OutsideAngle = Entry()
        self.Entry_StepSize = Entry()
        self.Entry_Allowance = Entry()
        self.Entry_W_CLEAN = Entry()
        self.Entry_CLEAN_DIA = Entry()
        self.Entry_STEP_OVER = Entry()
        self.Entry_V_CLEAN = Entry()

        # Make Menu Bar
        self.menuBar = Menu(self.master, relief = "raised", bd=2)

        top_File = Menu(self.menuBar, tearoff=0)
        top_File.add("command", label = "Open F-engrave G-Code File", \
                         command = self.menu_File_Open_G_Code_File)
        if self.POTRACE_AVAIL == TRUE:
            top_File.add("command", label = "Open DXF/Bitmap File", \
                             command = self.menu_File_Open_DXF_File)
        else:
            top_File.add("command", label = "Open DXF File", \
                             command = self.menu_File_Open_DXF_File)

        top_File.add("command", label = "Save G-Code File", \
                         command = self.menu_File_Save_G_Code_File)
        top_File.add("command", label = "Save SVG File",    \
                         command = self.menu_File_Save_SVG_File)
        if IN_AXIS:
            top_File.add("command", label = "Write To Axis and Exit", \
                             command = self.WriteToAxis)
        else:
            top_File.add("command", label = "Exit", command = self.menu_File_Quit)
        self.menuBar.add("cascade", label="File", menu=top_File)

        top_Edit = Menu(self.menuBar, tearoff=0)
        top_Edit.add("command", label = "Copy G-Code Data to Clipboard", \
                         command = self.CopyClipboard_GCode)
        top_Edit.add("command", label = "Copy SVG Data to Clipboard", \
                         command = self.CopyClipboard_SVG  )
        self.menuBar.add("cascade", label="Edit", menu=top_Edit)

        top_View = Menu(self.menuBar, tearoff=0)
        top_View.add("command", label = "Recalculate", command = self.menu_View_Recalculate)
        top_View.add_separator()

        top_View.add("command", label = "Zoom In <Page Up>", command = self.menu_View_Zoom_in)
        top_View.add("command", label = "Zoom Out <Page Down>", command = self.menu_View_Zoom_out)
        top_View.add("command", label = "Zoom Fit <F5>", command = self.menu_View_Refresh)

        top_View.add_separator()

        top_View.add_checkbutton(label = "Show Thickness" ,   variable=self.show_thick, \
                                     command= self.menu_View_Refresh)
        top_View.add_checkbutton(label = "Show Origin Axis",  variable=self.show_axis , \
                                     command= self.menu_View_Refresh)
        top_View.add_checkbutton(label = "Show Bounding Box", variable=self.show_box  , \
                                     command= self.menu_View_Refresh)
        self.menuBar.add("cascade", label="View", menu=top_View)

        top_Settings = Menu(self.menuBar, tearoff=0)
        top_Settings.add("command", label = "General Settings", \
                             command = self.GEN_Settings_Window)
        top_Settings.add("command", label = "V-Carve Settings", \
                             command = self.VCARVE_Settings_Window)
        if self.POTRACE_AVAIL == TRUE:
            top_Settings.add("command", label = "Bitmap Import Settings", \
                                 command = self.PBM_Settings_Window)

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label = "Engrave Mode" ,   variable=self.cut_type, value="engrave")
        top_Settings.add_radiobutton(label = "V-Carve Mode" ,   variable=self.cut_type, value="v-carve")

        top_Settings.add_separator()
        top_Settings.add_radiobutton(label = "Text Mode (CXF/TTF)" ,   variable=self.input_type, value="text", \
                                         command= self.menu_Mode_Change)
        top_Settings.add_radiobutton(label = "Image Mode (DXF/Bitmap)" ,   variable=self.input_type, value="image", \
                                         command= self.menu_Mode_Change)

        self.menuBar.add("cascade", label="Settings", menu=top_Settings)

        top_Help = Menu(self.menuBar, tearoff=0)
        top_Help.add("command", label = "About", command = self.menu_Help_About)
        top_Help.add("command", label = "Help (Web Page)", command = self.menu_Help_Web)
        self.menuBar.add("cascade", label="Help", menu=top_Help)

        self.master.config(menu=self.menuBar)

################################################################################
    def entry_set(self, val2, calc_flag=0, new=0):
        if calc_flag == 0 and new==0:
            try:
                self.statusbar.configure( bg = 'yellow' )
                val2.configure( bg = 'yellow' )
                self.statusMessage.set(" Recalculation required.")
            except:
                pass
        elif calc_flag == 3:
            try:
                val2.configure( bg = 'red' )
                self.statusbar.configure( bg = 'red' )
                self.statusMessage.set(" Value should be a number. ")
            except:
                pass
        elif calc_flag == 2:
            try:
                self.statusbar.configure( bg = 'red' )
                val2.configure( bg = 'red' )
            except:
                pass
        elif (calc_flag == 0 or calc_flag == 1) and new==1 :
            try:
                self.statusbar.configure( bg = 'white' )
                self.statusMessage.set(self.bounding_box.get())
                val2.configure( bg = 'white' )
            except:
                pass
        elif (calc_flag == 1) and new==0 :
            try:
                self.statusbar.configure( bg = 'white' )
                self.statusMessage.set(self.bounding_box.get())
                val2.configure( bg = 'white' )
            except:
                pass

        elif (calc_flag == 0 or calc_flag == 1) and new==2:
            return 0
        return 1

################################################################################
    def Sort_Paths(self,ecoords,i_loop=2):
        ##########################
        ###   find loop ends   ###
        ##########################
        Lbeg=[]
        Lend=[]
        if len(ecoords)>0:
            Lbeg.append(0)
            loop_old=ecoords[0][i_loop]
            for i in range(1,len(ecoords)):
                loop = ecoords[i][i_loop]
                if loop != loop_old:
                    Lbeg.append(i)
                    Lend.append(i-1)
                loop_old=loop
            Lend.append(i)

        #######################################################
        # Find new order based on distance to next beg or end #
        #######################################################
        order_out = []
        use_beg=0
        if len(ecoords)>0:
            order_out.append([Lbeg[0],Lend[0]])
        inext = 0
        total=len(Lbeg)
        for i in range(total-1):
            if use_beg==1:
                ii=Lbeg.pop(inext)
                Lend.pop(inext)
            else:
                ii=Lend.pop(inext)
                Lbeg.pop(inext)

            Xcur = ecoords[ii][0]
            Ycur = ecoords[ii][1]

            dx = Xcur - ecoords[ Lbeg[0] ][0]
            dy = Ycur - ecoords[ Lbeg[0] ][1]
            min_dist = dx*dx + dy*dy

            dxe = Xcur - ecoords[ Lend[0] ][0]
            dye = Ycur - ecoords[ Lend[0] ][1]
            min_diste = dxe*dxe + dye*dye

            inext=0
            inexte=0
            for j in range(1,len(Lbeg)):
                dx = Xcur - ecoords[ Lbeg[j] ][0]
                dy = Ycur - ecoords[ Lbeg[j] ][1]
                dist = dx*dx + dy*dy
                if dist < min_dist:
                    min_dist=dist
                    inext=j
                ###
                dxe = Xcur - ecoords[ Lend[j] ][0]
                dye = Ycur - ecoords[ Lend[j] ][1]
                diste = dxe*dxe + dye*dye
                if diste < min_diste:
                    min_diste=diste
                    inexte=j
                ###
            if min_diste < min_dist:
                inext=inexte
                order_out.append([Lend[inexte],Lbeg[inexte]])
                use_beg=1
            else:
                order_out.append([Lbeg[inext],Lend[inext]])
                use_beg=0
        ###########################################################
        return order_out

    def Write_Config_File(self, event):
        self.WriteGCode(config_file=True)
        config_file = "config.ngc"
        configname_full = self.HOME_DIR + "/" + config_file


        win_id=self.grab_current()
        if ( os.path.isfile(configname_full) ):
            if not message_ask_ok_cancel("Replace", "Replace Exiting Configuration File?\n"+configname_full):
                try:
                    win_id.withdraw()
                    win_id.deiconify()
                except:
                    pass
                return
            
        try:
            fout = open(configname_full,'w')
        except:
            self.statusMessage.set("Unable to open file for writing: %s" %(configname_full))
            self.statusbar.configure( bg = 'red' )
            return
        for line in self.gcode:
            try:
                fout.write(line+'\n')
            except:
                fout.write('(skipping line)\n')
        fout.close()
        self.statusMessage.set("Configuration File Saved: %s" %(configname_full))
        self.statusbar.configure( bg = 'white' )
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass


    ################################################################################
    def WriteGCode(self,config_file=False):
        global Zero
        self.gcode = []
        SafeZ  =   float(self.ZSAFE.get())
        Depth  =   float(self.ZCUT.get())


        if self.batch.get():
            String = self.default_text
        else:
            String = self.Input.get(1.0,END)

        String_short = String
        max_len = 40
        if len(String)  >  max_len:
            String_short = String[0:max_len] + '___'

        Acc    =   float(self.accuracy.get())
        
        if (self.no_comments.get() != True) or (config_file == True):
            self.gcode.append('( Code generated by f-engrave-'+version+'.py )')
            self.gcode.append('( by Scorch - 2016 )')
        
            self.gcode.append('(Settings used in f-engrave when this file was created)')
            if self.input_type.get() == "text":
                self.gcode.append("(Engrave Text:" + re.sub(r'\W+', ' ', String_short) + " )" )
            self.gcode.append("(=========================================================)")

            # BOOL
            self.gcode.append('(fengrave_set show_axis   %s )' %( int(self.show_axis.get())     ))
            self.gcode.append('(fengrave_set show_box    %s )' %( int(self.show_box.get())      ))
            self.gcode.append('(fengrave_set show_thick  %s )' %( int(self.show_thick.get())    ))
            self.gcode.append('(fengrave_set flip        %s )' %( int(self.flip.get())          ))
            self.gcode.append('(fengrave_set mirror      %s )' %( int(self.mirror.get())        ))
            self.gcode.append('(fengrave_set outer       %s )' %( int(self.outer.get())         ))
            self.gcode.append('(fengrave_set upper       %s )' %( int(self.upper.get())         ))
            self.gcode.append('(fengrave_set v_flop      %s )' %( int(self.v_flop.get())        ))
            self.gcode.append('(fengrave_set v_pplot     %s )' %( int(self.v_pplot.get())       ))
            self.gcode.append('(fengrave_set inlay       %s )' %( int(self.inlay.get())       ))
            self.gcode.append('(fengrave_set bmp_long    %s )' %( int(self.bmp_longcurve.get()) ))
            self.gcode.append('(fengrave_set var_dis     %s )' %( int(self.var_dis.get())       ))
            self.gcode.append('(fengrave_set ext_char    %s )' %( int(self.ext_char.get())      ))
            self.gcode.append('(fengrave_set useIMGsize  %s )' %( int(self.useIMGsize.get())    ))
            self.gcode.append('(fengrave_set no_comments %s )' %( int(self.no_comments.get())   ))


            # STRING.get()
            self.gcode.append('(fengrave_set arc_fit    %s )' %( self.arc_fit.get()    ))
            self.gcode.append('(fengrave_set YSCALE     %s )' %( self.YSCALE.get()     ))
            self.gcode.append('(fengrave_set XSCALE     %s )' %( self.XSCALE.get()     ))
            self.gcode.append('(fengrave_set LSPACE     %s )' %( self.LSPACE.get()     ))
            self.gcode.append('(fengrave_set CSPACE     %s )' %( self.CSPACE.get()     ))
            self.gcode.append('(fengrave_set WSPACE     %s )' %( self.WSPACE.get()     ))
            self.gcode.append('(fengrave_set TANGLE     %s )' %( self.TANGLE.get()     ))
            self.gcode.append('(fengrave_set TRADIUS    %s )' %( self.TRADIUS.get()    ))
            self.gcode.append('(fengrave_set ZSAFE      %s )' %( self.ZSAFE.get()      ))
            self.gcode.append('(fengrave_set ZCUT       %s )' %( self.ZCUT.get()       ))
            self.gcode.append('(fengrave_set STHICK     %s )' %( self.STHICK.get()     ))
            self.gcode.append('(fengrave_set origin     %s )' %( self.origin.get()     ))
            self.gcode.append('(fengrave_set justify    %s )' %( self.justify.get()    ))
            self.gcode.append('(fengrave_set units      %s )' %( self.units.get()      ))

            self.gcode.append('(fengrave_set xorigin    %s )' %( self.xorigin.get()    ))
            self.gcode.append('(fengrave_set yorigin    %s )' %( self.yorigin.get()    ))
            self.gcode.append('(fengrave_set segarc     %s )' %( self.segarc.get()     ))
            self.gcode.append('(fengrave_set accuracy   %s )' %( self.accuracy.get()   ))

            self.gcode.append('(fengrave_set FEED       %s )' %( self.FEED.get()       ))
            self.gcode.append('(fengrave_set PLUNGE     %s )' %( self.PLUNGE.get()     ))
            self.gcode.append('(fengrave_set fontfile   \042%s\042 )' %( self.fontfile.get() ))
            self.gcode.append('(fengrave_set H_CALC     %s )' %( self.H_CALC.get()     ))
            self.gcode.append('(fengrave_set plotbox    %s )' %( self.plotbox.get()    ))
            self.gcode.append('(fengrave_set boxgap     %s )' %( self.boxgap.get()    ))
            self.gcode.append('(fengrave_set cut_type    %s )' %( self.cut_type.get()    ))
            self.gcode.append('(fengrave_set bit_shape   %s )' %( self.bit_shape.get() ))
            self.gcode.append('(fengrave_set v_bit_angle %s )' %( self.v_bit_angle.get() ))
            self.gcode.append('(fengrave_set v_bit_dia   %s )' %( self.v_bit_dia.get()   ))
            self.gcode.append('(fengrave_set v_drv_crner %s )' %( self.v_drv_crner.get() ))
            self.gcode.append('(fengrave_set v_stp_crner %s )' %( self.v_stp_crner.get() ))
            self.gcode.append('(fengrave_set v_step_len  %s )' %( self.v_step_len.get()  ))
            self.gcode.append('(fengrave_set allowance   %s )' %( self.allowance.get()       ))

            self.gcode.append('(fengrave_set v_max_cut   %s )' %( self.v_max_cut.get()   ))
            self.gcode.append('(fengrave_set v_rough_stk %s )' %( self.v_rough_stk.get() ))

            self.gcode.append('(fengrave_set v_depth_lim  %s )' %( self.v_depth_lim.get() ))

            self.gcode.append('(fengrave_set v_check_all %s )' %( self.v_check_all.get() ))
            self.gcode.append('(fengrave_set bmp_turnp   %s )' %( self.bmp_turnpol.get()      ))
            self.gcode.append('(fengrave_set bmp_turds   %s )' %( self.bmp_turdsize.get()     ))
            self.gcode.append('(fengrave_set bmp_alpha   %s )' %( self.bmp_alphamax.get()     ))
            self.gcode.append('(fengrave_set bmp_optto   %s )' %( self.bmp_opttolerance.get() ))

            self.gcode.append('(fengrave_set fontdir    \042%s\042 )' %( self.fontdir.get()  ))
            self.gcode.append('(fengrave_set gpre        %s )' %( self.gpre.get()         ))
            self.gcode.append('(fengrave_set gpost       %s )' %( self.gpost.get()        ))

            self.gcode.append('(fengrave_set imagefile   \042%s\042 )' %( self.IMAGE_FILE ))
            self.gcode.append('(fengrave_set input_type  %s )' %( self.input_type.get() ))

            self.gcode.append('(fengrave_set clean_dia   %s )' %( self.clean_dia.get()  ))
            self.gcode.append('(fengrave_set clean_step  %s )' %( self.clean_step.get() ))
            self.gcode.append('(fengrave_set clean_v     %s )' %( self.clean_v.get()    ))
            clean_out = ("%d,%d,%d,%d,%d,%d" %(self.clean_P.get(),self.clean_X.get(),self.clean_Y.get(),\
                self.v_clean_P.get(),self.v_clean_Y.get(),self.v_clean_X.get()) )
            self.gcode.append('(fengrave_set clean_paths  %s )' %( clean_out ))
            
            str_data=''
            cnt = 0
            for char in String:
               if cnt > 10:
                   str_data = str_data + ')'
                   self.gcode.append('(fengrave_set TCODE   %s' %(str_data))
                   str_data=''
                   cnt=0
               str_data = str_data + ' %03d ' %( ord(char) )
               cnt = cnt + 1
            str_data = str_data + ')'
            self.gcode.append('(fengrave_set TCODE   %s' %(str_data))


            self.gcode.append('(fengrave_set NGC_DIR  \042%s\042 )' %( os.path.dirname(self.NGC_FILE) ))
            self.gcode.append('( Fontfile: %s )' %(self.fontfile.get()))

            self.gcode.append("(#########################################################)")


        

        if self.units.get() == "in":
            dp=4
            dpfeed=2
        else:
            dp=3
            dpfeed=1
            
        g_target = lambda s: sys.stdout.write(s + "\n")
        g = Gcode(safetyheight = SafeZ,
                 tolerance=Acc,
                 target=lambda s: self.gcode.append(s),
                 arc_fit = self.arc_fit.get())

        g.dp     = dp
        g.dpfeed = dpfeed
        g.set_plane(17)

        if not self.var_dis.get():
            FORMAT = '#1 = %%.%df  ( Safe Z )' %(dp)
            self.gcode.append(FORMAT %(SafeZ))
            FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' %(dp)
            self.gcode.append(FORMAT %(Depth))
            safe_val  = '#1'
            depth_val = '#2'
        else:
            FORMAT = '%%.%df' %(dp)
            safe_val  = FORMAT %(SafeZ)
            depth_val = FORMAT %(Depth)

        # G90        ; Sets absolute distance mode
        self.gcode.append('G90')
        # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
        if (self.arc_fit.get()=="center"):
            self.gcode.append('G91.1')
        if self.units.get() == "in":
            # G20 ; sets units to inches
            self.gcode.append('G20')
        else:
            # G21 ; sets units to mm
            self.gcode.append('G21')

        for line in self.gpre.get().split('|'):
            self.gcode.append(line)

        FORMAT = '%%.%df' %(dpfeed)
        feed_str     = FORMAT %(float(self.FEED.get()))
        plunge_str   = FORMAT %(float(self.PLUNGE.get()))
        zero_feed    = FORMAT %(float(0.0))

        #Set Feed rate
        self.gcode.append("F%s" %feed_str)
        
        if plunge_str==zero_feed:
            plunge_str = feed_str

        oldx = oldy = -99990.0
        first_stroke = True
        #Set up variables for multipass cutting
        maxDZ       =  float(self.v_max_cut.get())
        rough_stock =  float(self.v_rough_stk.get())
        zmin        =  0.0
        roughing    = True
        rough_again = False

        if self.cut_type.get() == "engrave" or self.bit_shape.get() == "FLAT":
            #print "engraving...."
            ecoords = []
            if (self.bit_shape.get() == "FLAT") and (self.cut_type.get() != "engrave"):
                Acc = float(self.v_step_len.get())*1.5
                ###################################
                ###   Create Flat Cut ECOORDS   ###
                ###################################
                if len(self.vcoords)>0:
                    rbit      = self.calc_vbit_dia()/2.0
                    loopa_old = self.vcoords[0][3]
                    loop=0
                    for i in range(1,len(self.vcoords)):
                        xa    = self.vcoords[i][0]
                        ya    = self.vcoords[i][1]
                        ra    = self.vcoords[i][2]
                        loopa = self.vcoords[i][3]

                        if (loopa_old != loopa):
                            loop = loop + 1
                        if ra >= rbit:
                            ecoords.append([xa,ya,loop])
                            loopa_old = loopa
                        else:
                            loop = loop + 1
                Depth = float(self.maxcut.get())
                if (rough_stock > 0):
                    rough_again = True
                if ((rough_stock > 0) and(-maxDZ < rough_stock)):
                    rough_stock = -maxDZ
                    
            else:
                ##########################
                ###   Create ECOORDS   ###
                ##########################
                loop=0
                for line in self.coords:
                    XY = line
                    x1 = XY[0]
                    y1 = XY[1]
                    x2 = XY[2]
                    y2 = XY[3]
                    dx = oldx - x1
                    dy = oldy - y1
                    dist = sqrt(dx*dx + dy*dy)
                    # check and see if we need to move to a new discontinuous start point
                    if (dist > Acc) or first_stroke:
                        loop = loop+1
                        first_stroke = False
                        ecoords.append([x1,y1,loop])
                    ecoords.append([x2,y2,loop])
                    oldx, oldy = x2, y2

            order_out=self.Sort_Paths(ecoords)
            ###########################
            
            while (rough_again == True or roughing == True):
                if (rough_again == False):
                    roughing = False
                    maxDZ = -99999
                rough_again = False
                zmin = zmin + maxDZ

                z1   = Depth
                if ( roughing ):
                    z1 = z1 + rough_stock
                if ( z1 < zmin):
                    z1 = zmin
                    rough_again = True
                zmax = zmin - maxDZ

                if (self.bit_shape.get() == "FLAT") and (self.cut_type.get() != "engrave"):
                    FORMAT = '%%.%df' %(dp)
                    depth_val = FORMAT %(z1)
                
                dist = 999
                lastx=-999
                lasty=-999
                lastz= 0
                z1   = 0
                nextz= 0
                
                #self.gcode.append("G0 Z%s" %(safe_val))
                for line in order_out:
                    temp=line
                    if temp[0] > temp[1]:
                        step = -1
                    else:
                        step = 1

                    R_last         = 999
                    x_center_last  = 999
                    y_center_last  = 999
                    FLAG_arc = 0
                    FLAG_line = 0
                    code=" "

                    loop_old = -1
                    
                    for i in range(temp[0],temp[1]+step,step):
                        x1   = ecoords[i][0]
                        y1   = ecoords[i][1]
                        loop = ecoords[i][2]

                        if ( i+1 < temp[1]+step ):
                            nextx    = ecoords[i+1][0]
                            nexty    = ecoords[i+1][1]
                            nextloop = ecoords[i+1][2]
                        else:
                            nextx    =  0
                            nexty    =  0
                            nextloop =  -99 #don't change this dummy number it is used below

                        # check and see if we need to move to a new discontinuous start point
                        if (loop != loop_old):
                            g.flush()
                            dx = x1-lastx
                            dy = y1-lasty
                            dist = sqrt(dx*dx + dy*dy)
                            if dist > Acc:
                                # lift engraver
                                self.gcode.append("G0 Z%s" %(safe_val))
                                # rapid to current position

                                FORMAT = 'G0 X%%.%df Y%%.%df'%(dp,dp)
                                self.gcode.append(FORMAT %(x1,y1))
                                # drop cutter
                                if (feed_str == plunge_str):
                                    self.gcode.append('G1 Z%s' %(depth_val))
                                else:
                                    self.gcode.append('G1 Z%s F%s' %(depth_val, plunge_str))
                                    g.set_feed(feed_str)
                                lastx = x1
                                lasty = y1
                                g.cut(x1,y1)
                        else:
                            g.cut(x1,y1)
                            lastx = x1
                            lasty = y1
                            
                        loop_old = loop
                    g.flush()
                g.flush()
            g.flush()
        #END engraving
        else:
            # V-carve stuff
            plunge_str = feed_str
            ##########################
            ###   find loop ends   ###
            ##########################
            Lbeg=[]
            Lend=[]
            Lbeg.append(0)
            if len(self.vcoords) > 0:
                loop_old=self.vcoords[0][3]
                for i in range(1,len(self.vcoords)):
                    loop = self.vcoords[i][3]
                    if loop != loop_old:
                        Lbeg.append(i)
                        Lend.append(i-1)
                    loop_old=loop
                Lend.append(i)
                #####################################################
                # Find new order based on distance to next begining #
                #####################################################
                order_out = []
                order_out.append([Lbeg[0],Lend[0]])
                inext = 0
                total=len(Lbeg)
                for i in range(total-1):
                    ii=Lend.pop(inext)
                    Lbeg.pop(inext)
                    Xcur = self.vcoords[ii][0]
                    Ycur = self.vcoords[ii][1]

                    dx = Xcur - self.vcoords[ Lbeg[0] ][0]
                    dy = Ycur - self.vcoords[ Lbeg[0] ][1]
                    min_dist = dx*dx + dy*dy

                    inext=0
                    for j in range(1,len(Lbeg)):
                        dx = Xcur - self.vcoords[ Lbeg[j] ][0]
                        dy = Ycur - self.vcoords[ Lbeg[j] ][1]
                        dist = dx*dx + dy*dy
                        if dist < min_dist:
                            min_dist=dist
                            inext=j
                    order_out.append([Lbeg[inext],Lend[inext]])
                #####################################################
                new_coords=[]
                for line in order_out:
                    temp=line
                    for i in range(temp[0],temp[1]+1):
                        new_coords.append(self.vcoords[i])

                half_angle = radians( float(self.v_bit_angle.get())/2.0 )
                bit_radius = float(self.v_bit_dia.get())/2.0

                ################################
                # V-carve stuff
                #maxDZ       =  float(self.v_max_cut.get())
                #rough_stock =  float(self.v_rough_stk.get())
                #zmin        =  0.0
                #roughing    = True
                #rough_again = False
                if (rough_stock > 0):
                    rough_again = True
                ################################
                if ((rough_stock > 0) and(-maxDZ < rough_stock)):
                    rough_stock = -maxDZ
                while (rough_again == True or roughing == True):
                    if (rough_again == False):
                        roughing = False
                        maxDZ = -99999
                    rough_again = False
                    zmin = zmin + maxDZ

                    loop_old = -1
                    R_last         = 999
                    x_center_last  = 999
                    y_center_last  = 999
                    FLAG_arc = 0
                    FLAG_line = 0
                    code=" "

                    v_index=-1

                    while v_index < len(new_coords)-1:
                        v_index = v_index + 1
                        x1   = new_coords[v_index][0]
                        y1   = new_coords[v_index][1]
                        r1   = new_coords[v_index][2]
                        loop = new_coords[v_index][3]

                        if ( v_index+1 < len(new_coords) ):
                            nextx    = new_coords[v_index+1][0]
                            nexty    = new_coords[v_index+1][1]
                            nextr    = new_coords[v_index+1][2]
                            nextloop = new_coords[v_index+1][3]
                        else:
                            nextx    =  0
                            nexty    =  0
                            nextr    =  0
                            nextloop =  -99 #don't change this dummy number it is used below

                        if   self.bit_shape.get() == "VBIT":
                            z1    = -r1   /tan(half_angle)
                            nextz = -nextr/tan(half_angle)
                            if self.inlay.get():
                                inlay_depth = self.calc_r_inlay_depth()
                                z1    = z1 + inlay_depth
                                nextz = nextz + inlay_depth

                        elif self.bit_shape.get() == "BALL":
                            theta =  acos(r1 / bit_radius)
                            z1    = -bit_radius*(1- sin(theta))

                            next_theta =  acos(nextr / bit_radius)
                            nextz      = -bit_radius*(1- sin(next_theta))
                        elif self.bit_shape.get() == "FLAT":
                            # This case should have been caught in the
                            # engraving section above
                            pass
                        else:
                            pass

                        if ( roughing ):
                            z1    = z1    + rough_stock
                            nextz = nextz + rough_stock
                        if (   z1 < zmin):
                            z1    = zmin
                            rough_again = True
                        if (nextz < zmin):
                            nextz = zmin
                            rough_again = True

                        zmax = zmin - maxDZ #+ rough_stock
                        if ((z1 > zmax) and (nextz > zmax)) and (roughing):
                            loop_old = -1
                            continue
                        # check and see if we need to move to a new discontinuous start point
                        if (loop != loop_old):
                            g.flush()
                            # lift engraver
                            self.gcode.append("G0 Z%s" %(safe_val))
                            # rapid to current position
                            FORMAT = 'G0 X%%.%df Y%%.%df' %(dp,dp)
                            self.gcode.append(FORMAT %(x1,y1))
                            # drop cutter to z depth
                            FORMAT = 'G1 Z%%.%df'  %(dp)
                            self.gcode.append(FORMAT %(z1))
                                
                            lastx = x1
                            lasty = y1
                            lastz = z1
                            g.cut(x1,y1,z1)
                        else:
                            g.cut(x1,y1,z1)
                            lastx = x1
                            lasty = y1
                            lastz = z1
                        loop_old = loop
                    g.flush()
                g.flush()
            g.flush()
            # End V-carve stuff
        # Make Circle
        XOrigin    =  float(self.xorigin.get())
        YOrigin    =  float(self.yorigin.get())
        Radius_plot=  float(self.RADIUS_PLOT)
        if Radius_plot != 0 and self.cut_type.get() == "engrave":
            self.gcode.append('G0 Z%s' %(safe_val))

            FORMAT = 'G0 X%%.%df Y%%.%df' %(dp,dp)
            self.gcode.append(FORMAT  %(-Radius_plot - self.Xzero + XOrigin, YOrigin - self.Yzero))

            
            if (feed_str == plunge_str):
                FEED_STRING = ""
            else:
                FEED_STRING = " F" + plunge_str
                g.set_feed(feed_str)
                
            self.gcode.append('G1 Z%s' %(depth_val) + FEED_STRING)

            if (feed_str == plunge_str):
                FEED_STRING = ""
            else:
                FEED_STRING = " F" + feed_str
            
            FORMAT = 'G2 I%%.%df J%%.%df' %(dp,dp)
            self.gcode.append(FORMAT %( Radius_plot, 0.0) + FEED_STRING)
        # End Circle

        self.gcode.append( 'G0 Z%s' %(safe_val))  # final engraver up

        for line in self.gpost.get().split('|'):
            self.gcode.append(line)

    ################################################################################

    #############################
    # Write Cleanup G-code File #
    #############################
    def WRITE_CLEAN_UP(self,bit_type="straight"):
        global Zero
        self.gcode = []
        SafeZ  =   float(self.ZSAFE.get())
        BitDia =   float(self.clean_dia.get())

        self.calc_depth_limit()
        Depth = float(self.maxcut.get())
        if self.inlay.get():
            Depth = Depth + float(self.allowance.get())

        Acc    =   float(self.accuracy.get())
        Units  =   self.units.get()


        if bit_type == "straight":
            coords_out = self.clean_coords_sort
        else:
            coords_out = self.v_clean_coords_sort
            
        if (self.no_comments.get() != True):
            self.gcode.append('( Code generated by f-engrave-'+version+'.py )')
            self.gcode.append('( by Scorch - 2016 )')
            self.gcode.append('( This file is a secondary operation for )')
            self.gcode.append('( cleaning up a V-carve. )')

            if bit_type == "straight":
                self.gcode.append('( The tool paths were calculated based )')
                self.gcode.append('( on using a bit with a )')
                self.gcode.append('( Diameter of %.4f %s)' %(BitDia, Units))
            else:
                self.gcode.append('( The tool paths were calculated based )')
                self.gcode.append('( on using a v-bit with a)')
                self.gcode.append('( angle of %.4f Degrees)' %(float(self.v_bit_angle.get())) )

            self.gcode.append("(==========================================)")


        if self.units.get() == "in":
            dp=4
            dpfeed=2
        else:
            dp=3
            dpfeed=1
        

        if not self.var_dis.get():
            FORMAT = '#1 = %%.%df  ( Safe Z )' %(dp)
            self.gcode.append(FORMAT %(SafeZ))
            safe_val  = '#1'
        else:
            FORMAT = '%%.%df' %(dp)
            safe_val  = FORMAT %(SafeZ)
            depth_val = FORMAT %(Depth)

        self.gcode.append("(##########################################)")
        # G90        ; Sets absolute distance mode
        self.gcode.append('G90')
        # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
        if (self.arc_fit.get()=="center"):
            self.gcode.append('G91.1')
        if self.units.get() == "in":
            # G20 ; sets units to inches
            self.gcode.append('G20')
        else:
            # G21 ; sets units to mm
            self.gcode.append('G21')

        for line in self.gpre.get().split('|'):
            self.gcode.append(line)
            
        #self.gcode.append( 'G0 Z%s' %(safe_val))
        
        FORMAT = '%%.%df' %(dp)
        feed_str     = FORMAT %(float(self.FEED.get()))    
        plunge_str   = FORMAT %(float(self.PLUNGE.get()))
        feed_current = FORMAT %(float(0.0))
        #fmessage(feed_str +" "+plunge_str)
        if plunge_str==feed_current:
            plunge_str = feed_str

        # Multipass stuff
        ################################
        # Cleanup
        maxDZ       =  float(self.v_max_cut.get())
        rough_stock =  float(self.v_rough_stk.get())
        zmin        =  0.0
        roughing    = True
        rough_again = False
        if (rough_stock > 0):
            rough_again = True
        ################################
        if ((rough_stock > 0) and(-maxDZ < rough_stock)):
            rough_stock = -maxDZ
        while (rough_again == True or roughing == True):
            if (rough_again == False):
                roughing = False
                maxDZ = -99999
            rough_again = False
            zmin = zmin + maxDZ

            #self.gcode.append( 'G0 Z%s' %(safe_val))
            oldx = oldy = -99990.0
            first_stroke = True
            ########################################################################
            # The clean coords have already been sorted so we can just write them  #
            ########################################################################

            order_out=self.Sort_Paths(coords_out,3)
            new_coords=[]
            for line in order_out:
                temp=line
                if (temp[0] < temp[1]):
                    step=1
                else:
                    step=-1
                for i in range(temp[0],temp[1]+step,step):
                    new_coords.append(coords_out[i])
            coords_out=new_coords

            if len(coords_out) > 0:
                loop_old = -1
                FLAG_arc = 0
                FLAG_line = 0
                code=" "
                v_index=-1
                while v_index < len(coords_out)-1:
                    v_index = v_index + 1
                    x1   = coords_out[v_index][0]
                    y1   = coords_out[v_index][1]
                    r1   = coords_out[v_index][2]
                    loop = coords_out[v_index][3]

                    if ( v_index+1 < len(coords_out) ):
                        nextx    = coords_out[v_index+1][0]
                        nexty    = coords_out[v_index+1][1]
                        nextr    = coords_out[v_index+1][2]
                        nextloop = coords_out[v_index+1][3]
                    else:
                        nextx    =  0
                        nexty    =  0
                        nextr    =  0
                        nextloop =  -99

                    # check and see if we need to move to a new discontinuous start point
                    if (loop != loop_old):
                        # lift engraver
                        self.gcode.append("G0 Z%s" %(safe_val))
                        # rapid to current position
                        FORMAT = 'G0 X%%.%df Y%%.%df' %(dp,dp)
                        self.gcode.append(FORMAT %(x1,y1))

                        z1 = Depth;
                        if ( roughing ):
                            z1    = Depth + rough_stock #Depth
                        if (   z1 < zmin):
                            z1    = zmin
                            rough_again = True

                        FORMAT = '%%.%df' %(dp)
                        depth_val = FORMAT %(z1)

                        if (feed_current == plunge_str):
                            FEED_STRING = ""
                        else:
                            FEED_STRING = " F" + plunge_str
                            feed_current = plunge_str
                            
                        self.gcode.append("G1 Z%s" %(depth_val) + FEED_STRING)

                        lastx=x1
                        lasty=y1
                    else:
                        if (feed_str == feed_current):
                            FEED_STRING = ""
                        else:
                            FEED_STRING = " F" + feed_str
                            feed_current = feed_str
                        
                        FORMAT = 'G1 X%%.%df Y%%.%df' %(dp,dp)
                        self.gcode.append(FORMAT %(x1,y1) + FEED_STRING)
                        lastx=x1
                        lasty=y1
                    loop_old = loop

        #End multipass loop

        self.gcode.append( 'G0 Z%s' %(safe_val))  # final engraver up

        for line in self.gpost.get().split('|'):
            self.gcode.append(line)
        ###################################

    def WriteSVG(self):
        if self.cut_type.get() == "v-carve":
            Thick = 0.001
        else:
            Thick   = float(self.STHICK.get())

        dpi=100

        maxx = -99919.0
        maxy = -99929.0
        maxa = -99939.0
        mina =  99949.0
        miny =  99959.0
        minx =  99969.0
        for line in self.coords:
            XY = line
            maxx = max(maxx, XY[0],XY[2])
            minx = min(minx, XY[0],XY[2])
            miny = min(miny, XY[1],XY[3])
            maxy = max(maxy, XY[1],XY[3])

        XOrigin    =  float(self.xorigin.get())
        YOrigin    =  float(self.yorigin.get())
        Radius_plot=  float(self.RADIUS_PLOT)
        if Radius_plot != 0:
            maxx = max(maxx, XOrigin+Radius_plot - self.Xzero)
            minx = min(minx, XOrigin-Radius_plot - self.Xzero)
            miny = min(miny, YOrigin-Radius_plot - self.Yzero)
            maxy = max(maxy, YOrigin+Radius_plot - self.Yzero)

        maxx = maxx + Thick/2
        minx = minx - Thick/2
        miny = miny - Thick/2
        maxy = maxy + Thick/2

        width_in  = maxx-minx
        height_in = maxy-miny
        width  = ((maxx-minx)*dpi)
        height = ((maxy-miny)*dpi)

        self.svgcode = []
        self.svgcode.append('<?xml version="1.0" standalone="no"?>')
        self.svgcode.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"  ')
        self.svgcode.append('  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">  ')
        self.svgcode.append('<svg width="%f%s" height="%f%s" viewBox="0 0 %f %f"  ' \
                            %(width_in,self.units.get(),height_in,self.units.get(),width,height) )
        self.svgcode.append('     xmlns="http://www.w3.org/2000/svg" version="1.1">')
        self.svgcode.append('  <title> F-engrave Output </title>')
        self.svgcode.append('  <desc>SVG File Created By F-Engrave</desc>')

        # Make Circle
        if Radius_plot != 0 and self.cut_type.get() == "engrave":
            self.svgcode.append('  <circle cx="%f" cy="%f" r="%f"' %(
                        ( XOrigin-self.Xzero-minx)*dpi,
                        (-YOrigin+self.Yzero+maxy)*dpi,
                        ( Radius_plot            )*dpi) )
            self.svgcode.append('        fill="none" stroke="blue" stroke-width="%f"/>' %(Thick*dpi))
        # End Circle

        for line in self.coords:
            XY = line
            self.svgcode.append('  <path d="M %f %f L %f %f"' %(
                    ( XY[0]-minx)*dpi,
                    (-XY[1]+maxy)*dpi,
                    ( XY[2]-minx)*dpi,
                    (-XY[3]+maxy)*dpi) )
            self.svgcode.append('        fill="none" stroke="blue" stroke-width="%f" stroke-linecap="round" stroke-linejoin="round"/>' %(Thick*dpi))

        if self.input_type.get() == "text":
            Radius_in =  float(self.TRADIUS.get())
        else:
            Radius_in = 0.0

        Thick     =  float(self.STHICK.get() )
        if self.plotbox.get() != "no_box":
            if Radius_in != 0:
                Delta = Thick/2 + float(self.boxgap.get())
        self.svgcode.append('</svg>')

    def CopyClipboard_GCode(self):
        self.clipboard_clear()
        if (self.Check_All_Variables() > 0):
            return
        self.WriteGCode()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def CopyClipboard_SVG(self):
        self.clipboard_clear()
        self.WriteSVG()
        for line in self.svgcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        if (self.Check_All_Variables() > 0):
            return
        self.WriteGCode()
        for line in self.gcode:
            try:
                sys.stdout.write(line+'\n')
            except:
                pass
        self.Quit_Click(None)

    def Quit_Click(self, event):
        self.statusMessage.set("Exiting!")
        root.destroy()

    def ZOOM_ITEMS(self,x0,y0,z_factor):
        all = self.PreviewCanvas.find_all()
        for i in all:
            self.PreviewCanvas.scale(i, x0, y0, z_factor, z_factor)
            w=self.PreviewCanvas.itemcget(i,"width")
            self.PreviewCanvas.itemconfig(i, width=float(w)*z_factor)
        self.PreviewCanvas.update_idletasks()

    def ZOOM(self,z_inc):
        all = self.PreviewCanvas.find_all()
        x = int(self.PreviewCanvas.cget("width" ))/2.0
        y = int(self.PreviewCanvas.cget("height"))/2.0
        for i in all:
            self.PreviewCanvas.scale(i, x, y, z_inc, z_inc)
            w=self.PreviewCanvas.itemcget(i,"width")
            self.PreviewCanvas.itemconfig(i, width=float(w)*z_inc)
        self.PreviewCanvas.update_idletasks()

    def menu_View_Zoom_in(self):
        x = int(self.PreviewCanvas.cget("width" ))/2.0
        y = int(self.PreviewCanvas.cget("height"))/2.0
        self.ZOOM_ITEMS(x, y, 2.0)

    def menu_View_Zoom_out(self):
        x = int(self.PreviewCanvas.cget("width" ))/2.0
        y = int(self.PreviewCanvas.cget("height"))/2.0
        self.ZOOM_ITEMS(x, y, 0.5)

    def _mouseZoomIn(self,event):
        self.ZOOM_ITEMS(event.x, event.y, 1.25)

    def _mouseZoomOut(self,event):
        self.ZOOM_ITEMS(event.x, event.y, 0.75)

    def mouseZoomStart(self,event):
        self.zoomx0 = event.x
        self.zoomy  = event.y
        self.zoomy0 = event.y

    def mouseZoom(self,event):
        dy = event.y-self.zoomy
        if dy < 0.0:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 1.15)
        else:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 0.85)
        self.lasty = self.lasty + dy
        self.zoomy = event.y

    def mousePanStart(self,event):
        self.panx = event.x
        self.pany = event.y

    def mousePan(self,event):
        all = self.PreviewCanvas.find_all()
        dx = event.x-self.panx
        dy = event.y-self.pany
        for i in all:
            self.PreviewCanvas.move(i, dx, dy)
        self.lastx = self.lastx + dx
        self.lasty = self.lasty + dy
        self.panx = event.x
        self.pany = event.y

    def Recalculate_Click(self, event):
        self.DoIt()

    def Settings_ReLoad_Click(self, event, arg1="", arg2=""):
        win_id=self.grab_current()
        if self.input_type.get() == "text":
            self.Read_font_file()
        else:
            self.Read_image_file()
        self.DoIt()
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def VCARVE_Recalculate_Click(self):
        win_id=self.grab_current()
        self.V_Carve_Calc_Click()
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def CLEAN_Recalculate_Click(self):
        win_id=self.grab_current()
        if self.clean_segment == []:
            mess = "Calculate V-Carve must be executed\n"
            mess = mess + "prior to Calculating Cleanup"
            message_box("Cleanup Info",mess)
        else:
            stop = self.Clean_Calc_Click("straight")
            if stop != 1:
                self.Clean_Calc_Click("v-bit")
            self.Plot_Data()

        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_Clean_Click(self):
        win_id=self.grab_current()
        if (self.clean_P.get() + \
            self.clean_X.get() + \
            self.clean_Y.get() + \
            self.v_clean_P.get() + \
            self.v_clean_Y.get() + \
            self.v_clean_X.get()) != 0:
            if self.clean_coords_sort == []:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message_box("Cleanup Info",mess)
            else:
                self.menu_File_Save_clean_G_Code_File("straight")
        else:
            mess =        "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no V Cleanup paths were found)"
            message_box("Cleanup Info",mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_V_Clean_Click(self):
        win_id=self.grab_current()
        if (self.clean_P.get() + \
            self.clean_X.get() + \
            self.clean_Y.get() + \
            self.v_clean_P.get() + \
            self.v_clean_Y.get() + \
            self.v_clean_X.get()) != 0:
            if self.v_clean_coords_sort == []:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving V Cleanup G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message_box("Cleanup Info",mess)
            else:
                self.menu_File_Save_clean_G_Code_File("v-bit")
        else:
            mess =        "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no Cleanup paths were found)"
            message_box("Cleanup Info",mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    ######################

    def Close_Current_Window_Click(self):
        win_id=self.grab_current()
        win_id.destroy()

    def Stop_Click(self, event):
        global STOP_CALC
        STOP_CALC=1

    def calc_clean_width(self):
        xLength = self.MAXX-self.MINX
        yLength = self.MAXY-self.MINY
        bit_dia = self.calc_vbit_dia()
        clean_w = min(xLength,yLength)/2.0 + bit_dia
        return clean_w

    def calc_vbit_dia(self):
        bit_dia   = float(self.v_bit_dia.get())
        depth_lim = float(self.v_depth_lim.get())
        half_angle = radians( float(self.v_bit_angle.get())/2.0 )

        if self.inlay.get() and (self.bit_shape.get() == "VBIT"):
            allowance = float(self.allowance.get())
            bit_dia = -2*allowance*tan(half_angle)
            bit_dia = max(bit_dia, 0.001)
            #bit_dia = 0.001
            return bit_dia

        if depth_lim < 0.0:
            if   self.bit_shape.get() == "VBIT":
                bit_dia    = -2*depth_lim*tan(half_angle)
            elif self.bit_shape.get() == "BALL":
                R = bit_dia / 2.0
                bit_dia = 2*sqrt( R**2 - (R+depth_lim)**2)
            elif self.bit_shape.get() == "FLAT":
                R = bit_dia / 2.0
            else:
                pass
        return bit_dia

    def calc_depth_limit(self):
        try:
            if  self.bit_shape.get() == "VBIT":
                half_angle = radians( float(self.v_bit_angle.get())/2.0 )
                bit_depth = -float(self.v_bit_dia.get())/2.0 /tan(half_angle)
            elif self.bit_shape.get() == "BALL":
                bit_depth = -float( self.v_bit_dia.get()) / 2.0
            elif self.bit_shape.get() == "FLAT":
                bit_depth = -float( self.v_bit_dia.get()) / 2.0
            else:
                pass

            depth_lim = float(self.v_depth_lim.get())
            if self.bit_shape.get() != "FLAT":
                if depth_lim < 0.0:
                    self.maxcut.set("%.3f" %(max(bit_depth, depth_lim)))
                else:
                    self.maxcut.set("%.3f" %(bit_depth))
            else:
                if depth_lim < 0.0:
                    self.maxcut.set("%.3f" %(depth_lim))
                else:
                    self.maxcut.set("%.3f" %(bit_depth))
        except:
            self.maxcut.set("error")

    def calc_r_inlay_top(self):
        half_angle  = radians( float(self.v_bit_angle.get())/2.0 )
        inlay_depth = self.calc_r_inlay_depth()
        r_inlay_top = tan(half_angle)*inlay_depth
        return r_inlay_top

    def calc_r_inlay_depth(self):
        inlay_depth = float(self.maxcut.get())
        return inlay_depth


    # Left Column #
    #############################
    def Entry_Yscale_Check(self):
        try:
            value = float(self.YSCALE.get())
            if  value <= 0.0:
                self.statusMessage.set(" Height should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Yscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check() )
    #############################
    def Entry_Xscale_Check(self):
        try:
            value = float(self.XSCALE.get())
            if  value <= 0.0:
                self.statusMessage.set(" Width should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Xscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check() )
    #############################
    def Entry_Sthick_Check(self):
        try:
            value = float(self.STHICK.get())
            if  value < 0.0:
                self.statusMessage.set(" Thickness should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Sthick_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check() )
    #############################
    def Entry_Lspace_Check(self):
        try:
            value = float(self.LSPACE.get())
            if  value < 0.0:
                self.statusMessage.set(" Line space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Lspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check() )
    #############################
    def Entry_Cspace_Check(self):
        try:
            value = float(self.CSPACE.get())
            if  value < 0.0:
                self.statusMessage.set(" Character space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Cspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check() )
    #############################
    def Entry_Wspace_Check(self):
        try:
            value = float(self.WSPACE.get())
            if  value < 0.0:
                self.statusMessage.set(" Word space should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Wspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check() )
    #############################
    def Entry_Tangle_Check(self):
        try:
            value = float(self.TANGLE.get())
            if  value <= -360.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between -360 and 360 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Tangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check() )
    #############################
    def Entry_Tradius_Check(self):
        try:
            value = float(self.TRADIUS.get())
            if  value < 0.0:
                self.statusMessage.set(" Radius should be greater than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Tradius_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() )
    # End Left Column #

    # Right Column #
    #############################
    def Entry_Feed_Check(self):
        try:
            value = float(self.FEED.get())
            if  value <= 0.0:
                self.statusMessage.set(" Feed should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Feed_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Feed,self.Entry_Feed_Check())
    #############################
    def Entry_Plunge_Check(self):
        try:
            value = float(self.PLUNGE.get())
            if  value < 0.0:
                self.statusMessage.set(" Plunge rate should be greater than or equal to 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Plunge_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Plunge,self.Entry_Plunge_Check())
    #############################
    def Entry_Zsafe_Check(self):
        try:
            value = float(self.ZSAFE.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Zsafe_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zsafe,self.Entry_Zsafe_Check())
    #############################
    def Entry_Zcut_Check(self):
        try:
            value = float(self.ZCUT.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Zcut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zcut,self.Entry_Zcut_Check())
    #############################
    # End Right Column #


    ######################################
    #    Settings Window Call Backs      #
    ######################################
    def Entry_Xoffset_Check(self):
        try:
            value = float(self.xorigin.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Xoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check())
    #############################
    def Entry_Yoffset_Check(self):
        try:
            value = float(self.yorigin.get())
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Yoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yoffset,self.Entry_Yoffset_Check())
    #############################
    def Entry_ArcAngle_Check(self):
        try:
            value = float(self.segarc.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_ArcAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check())
    #############################
    def Entry_Accuracy_Check(self):
        try:
            value = float(self.accuracy.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Accuracy_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check())
    #############################
    def Entry_BoxGap_Check(self):
        try:
            value = float(self.boxgap.get())
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_BoxGap_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BoxGap,self.Entry_BoxGap_Check())
    #############################
    def Fontdir_Click(self, event):
        win_id=self.grab_current()
        newfontdir = askdirectory(mustexist=1,initialdir=self.fontdir.get() )
        if newfontdir != "" and newfontdir != ():
            self.fontdir.set(newfontdir.encode("utf-8"))
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass
    ######################################
    #    V-Carve Settings Call Backs     #
    ######################################
    def Entry_Vbitangle_Check(self):
        try:
            value = float(self.v_bit_angle.get())
            if  value < 0.0 or value > 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_Vbitangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check() )
        self.calc_depth_limit()

    #############################
    def Entry_Vbitdia_Check(self):
        try:
            value = float(self.v_bit_dia.get())
            if  value <= 0.0:
                self.statusMessage.set(" Diameter should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Vbitdia_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check() )
        self.calc_depth_limit()
    #############################
    def Entry_VDepthLimit_Check(self):
        try:
            value = float(self.v_depth_lim.get())
            if  value > 0.0:
                self.statusMessage.set(" Depth should be less than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_VDepthLimit_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() )
        self.calc_depth_limit()
    #############################
    def Entry_InsideAngle_Check(self):
        try:
            value = float(self.v_drv_crner.get())
            if  value <= 0.0 or value >= 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_InsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() )
    #############################
    def Entry_OutsideAngle_Check(self):
        try:
            value = float(self.v_stp_crner.get())
            if  value <= 180.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between 180 and 360 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_OutsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check() )
    #############################
    def Entry_StepSize_Check(self):
        try:
            value = float(self.v_step_len.get())
            if  value <= 0.0:
                self.statusMessage.set(" Step size should be greater than 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_StepSize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check() )
    #############################
    def Entry_Allowance_Check(self):
        try:
            value = float(self.allowance.get())
            if  value > 0.0:
                self.statusMessage.set(" Allowance should be less than or equal to 0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_Allowance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check() )

    #############################
    def Entry_Prismatic_Callback(self, varName, index, mode):
        try:
            if not bool(self.inlay.get()):
                self.Label_Allowance.configure(state="disabled")
                self.Entry_Allowance.configure(state="disabled")
                self.Label_Allowance_u.configure(state="disabled")
            else:
                self.Label_Allowance.configure(state="normal")
                self.Entry_Allowance.configure(state="normal")
                self.Label_Allowance_u.configure(state="normal")
        except:
            pass
        self.Recalc_RQD()
        
    #############################
    def Entry_v_max_cut_Check(self):
        try:
            value = float(self.v_max_cut.get())
            if  value >= 0.0:
                self.statusMessage.set(" Max Depth per Pass should be less than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 1         # Value is a valid number changes do not require recalc
    def Entry_v_max_cut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check() )
    #############################
    def Entry_v_rough_stk_Check(self):
        try:
            value = float(self.v_rough_stk.get())
            if  value < 0.0:
                self.statusMessage.set(" Finish Pass Stock should be positive or zero (Zero disables multi-pass)")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        try:
            if float(self.v_rough_stk.get()) == 0.0:
                self.Label_v_max_cut.configure(state="disabled")
                self.Label_v_max_cut_u.configure(state="disabled")
                self.Entry_v_max_cut.configure(state="disabled")
            else:
                self.Label_v_max_cut.configure(state="normal")
                self.Label_v_max_cut_u.configure(state="normal")
                self.Entry_v_max_cut.configure(state="normal")
        except:
            pass
        return 1         # Value is a valid number changes do not require recalc
    def Entry_v_rough_stk_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check() )

    #############################
    def Entry_V_CLEAN_Check(self):
        try:
            value = float(self.clean_v.get())
            if  value < 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_V_CLEAN_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check() )
    #############################
    def Entry_CLEAN_DIA_Check(self):
        try:
            value = float(self.clean_dia.get())
            if  value <= 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_CLEAN_DIA_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check() )
    #############################
    def Entry_STEP_OVER_Check(self):
        try:
            value = float(self.clean_step.get())
            if  value <= 0.0:
                self.statusMessage.set(" Step Over should be between 0% and 100% ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_STEP_OVER_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check() )
    #############################

    def Entry_Bit_Shape_Check(self):
        self.calc_depth_limit()

        try:
            if   self.bit_shape.get() == "VBIT":
                self.Label_Vbitangle.configure(state="normal")
                self.Label_Vbitangle_u.configure(state="normal")
                self.Entry_Vbitangle.configure(state="normal")
                self.Label_photo.configure(state="normal")
                self.Label_Vbitdia.configure(text="V-Bit Diameter")
            elif self.bit_shape.get() == "BALL":
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_Vbitdia.configure(text="Ball Nose Bit Diameter")
            elif self.bit_shape.get() == "FLAT":
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_Vbitdia.configure(text="Straight Bit Diameter")
            else:
                pass
        except:
            pass

    def Entry_Bit_Shape_var_Callback(self, varName, index, mode):
        self.Entry_Bit_Shape_Check()

    ######################################
    # Bitmap Settings Window Call Backs  #
    ######################################
    def Entry_BMPturdsize_Check(self):
        try:
            value = float(self.bmp_turdsize.get())
            if  value < 1.0:
                self.statusMessage.set(" Step size should be greater or equal to 1.0 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_BMPturdsize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check() )
    #############################
    def Entry_BMPalphamax_Check(self):
        try:
            value = float(self.bmp_alphamax.get())
            if  value < 0.0 or value > 4.0/3.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number
    def Entry_BMPalphamax_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check() )
    #############################
    def Entry_BMPoptTolerance_Check(self):
        try:
            value = float(self.bmp_opttolerance.get())
            if  value < 0.0:
                self.statusMessage.set(" Alpha Max should be between 0.0 and 1.333 ")
                return 2 # Value is invalid number
        except:
            return 3     # Value not a number
        return 0         # Value is a valid number

    def Entry_BMPoptTolerance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check() )
    #############################

    ##########################################################################
    ##########################################################################
    def Check_All_Variables(self):
        if self.batch.get():
            return 0
        MAIN_error_cnt= \
        self.entry_set(self.Entry_Yscale,  self.Entry_Yscale_Check()  ,2) +\
        self.entry_set(self.Entry_Xscale,  self.Entry_Xscale_Check()  ,2) +\
        self.entry_set(self.Entry_Sthick,  self.Entry_Sthick_Check()  ,2) +\
        self.entry_set(self.Entry_Lspace,  self.Entry_Lspace_Check()  ,2) +\
        self.entry_set(self.Entry_Cspace,  self.Entry_Cspace_Check()  ,2) +\
        self.entry_set(self.Entry_Wspace,  self.Entry_Wspace_Check()  ,2) +\
        self.entry_set(self.Entry_Tangle,  self.Entry_Tangle_Check()  ,2) +\
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() ,2) +\
        self.entry_set(self.Entry_Feed,    self.Entry_Feed_Check()    ,2) +\
        self.entry_set(self.Entry_Plunge,  self.Entry_Plunge_Check()  ,2) +\
        self.entry_set(self.Entry_Zsafe,   self.Entry_Zsafe_Check()   ,2) +\
        self.entry_set(self.Entry_Zcut,    self.Entry_Zcut_Check()    ,2)

        GEN_error_cnt= \
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check() ,2) +\
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check() ,2) +\
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),2) +\
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),2) +\
        self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,2) +\
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check() ,2) +\
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check() ,2) +\
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),2) +\
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),2) +\
        self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,2)

        VCARVE_error_cnt= \
        self.entry_set(self.Entry_Vbitangle,   self.Entry_Vbitangle_Check()   ,2) +\
        self.entry_set(self.Entry_Vbitdia,     self.Entry_Vbitdia_Check()     ,2) +\
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() ,2) +\
        self.entry_set(self.Entry_OutsideAngle,self.Entry_OutsideAngle_Check(),2) +\
        self.entry_set(self.Entry_StepSize,    self.Entry_StepSize_Check()    ,2) +\
        self.entry_set(self.Entry_CLEAN_DIA,   self.Entry_CLEAN_DIA_Check()   ,2) +\
        self.entry_set(self.Entry_STEP_OVER,   self.Entry_STEP_OVER_Check()   ,2) +\
        self.entry_set(self.Entry_Allowance,   self.Entry_Allowance_Check()   ,2) +\
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), 2)

        PBM_error_cnt= \
        self.entry_set(self.Entry_BMPoptTolerance,self.Entry_BMPoptTolerance_Check(),2) +\
        self.entry_set(self.Entry_BMPturdsize,    self.Entry_BMPturdsize_Check()    ,2) +\
        self.entry_set(self.Entry_BMPalphamax,    self.Entry_BMPalphamax_Check()    ,2)

        ERROR_cnt = MAIN_error_cnt + GEN_error_cnt + VCARVE_error_cnt +PBM_error_cnt

        if (ERROR_cnt > 0):
            self.statusbar.configure( bg = 'red' )
        if (PBM_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in PBM Settings Window ")
        if (VCARVE_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in V-Carve Settings Window ")
        if (GEN_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in General Settings Window ")
        if (MAIN_error_cnt > 0):
            self.statusMessage.set(\
                " Entry Error Detected: Check Entry Values in Main Window ")

        return ERROR_cnt

    ##########################################################################
    ##########################################################################
    def V_Carve_Calc_Click(self):
        if (self.Check_All_Variables() > 0):
            return

        vcalc_status = Toplevel(width=525, height=60)
        # Use grab_set to prevent user input in the main window during calculations
        vcalc_status.grab_set()

        self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT , height=1, anchor=W)
        self.statusbar2.place(x=130+12+12, y=6, width=350, height=30)
        self.statusMessage.set("Starting Calculation")
        self.statusbar.configure( bg = 'yellow' )

        self.stop_button = Button(vcalc_status,text="Stop Calculation")
        self.stop_button.place(x=12, y=17, width=130, height=30)
        self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

        self.Checkbutton_v_pplot = Checkbutton(vcalc_status,text="Plot During V-Carve Calculation", anchor=W)
        self.Checkbutton_v_pplot.place(x=130+12+12, y=34, width=300, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)

        vcalc_status.resizable(0,0)
        vcalc_status.title('Executing V-Carve')
        vcalc_status.iconname("F-Engrave")

        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            vcalc_status.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            fmessage("Unable to create temporary icon file.")

        self.V_Carve_It()
        self.menu_View_Refresh()
        vcalc_status.grab_release()
        try:
            vcalc_status.destroy()
        except:
            pass

    ##########################################################################
    ##########################################################################
    def Clean_Calc_Click(self,bit_type="straight"):
        if (self.Check_All_Variables() > 0):
            return 1

        if self.clean_coords == []:
            vcalc_status = Toplevel(width=525, height=50)
            # Use grab_set to prevent user input in the main window during calculations
            vcalc_status.grab_set()

            self.statusbar2 = Label(vcalc_status, textvariable=self.statusMessage, bd=1, relief=FLAT , height=1)
            self.statusbar2.place(x=130+12+12, y=12, width=350, height=30)
            self.statusMessage.set("Starting Clean Calculation")
            self.statusbar.configure( bg = 'yellow' )

            self.stop_button = Button(vcalc_status,text="Stop Calculation")
            self.stop_button.place(x=12, y=12, width=130, height=30)
            self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

            vcalc_status.resizable(0,0)
            vcalc_status.title('Executing Clean Area Calculation')
            vcalc_status.iconname("F-Engrave")

            try: #Attempt to create temporary icon bitmap file
                f = open("f_engrave_icon",'w')
                f.write("#define f_engrave_icon_width 16\n")
                f.write("#define f_engrave_icon_height 16\n")
                f.write("static unsigned char f_engrave_icon_bits[] = {\n")
                f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
                f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
                f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
                f.close()
                vcalc_status.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                fmessage("Unable to create temporary icon file.")

            clean_cut = 1
            self.V_Carve_It(clean_cut)
            vcalc_status.grab_release()
            try:
                vcalc_status.destroy()
            except:
                pass

        self.Clean_Path_Calc(bit_type)

        if self.clean_coords == []:
            return 1
        else:
            return 0

    def Entry_recalc_var_Callback(self, varName, index, mode):
        self.Recalc_RQD()

    def Entry_units_var_Callback(self):
        if (self.units.get() == 'in') and (self.funits.get()=='mm/min'):
            self.Scale_Linear_Inputs(1/25.4)
            self.funits.set('in/min')
        elif (self.units.get() == 'mm') and (self.funits.get()=='in/min'):
            self.Scale_Linear_Inputs(25.4)
            self.funits.set('mm/min')
        self.Recalc_RQD()

    def Scale_Linear_Inputs(self, factor=1.0):
        try:
            self.YSCALE.set(     '%.3g' %(float(self.YSCALE.get()     )*factor) )
            self.TRADIUS.set(    '%.3g' %(float(self.TRADIUS.get()    )*factor) )
            self.ZSAFE.set(      '%.3g' %(float(self.ZSAFE.get()      )*factor) )
            self.ZCUT.set(       '%.3g' %(float(self.ZCUT.get()       )*factor) )
            self.STHICK.set(     '%.3g' %(float(self.STHICK.get()     )*factor) )
            self.FEED.set(       '%.3g' %(float(self.FEED.get()       )*factor) )
            self.PLUNGE.set(     '%.3g' %(float(self.PLUNGE.get()     )*factor) )
            self.boxgap.set(     '%.3g' %(float(self.boxgap.get()     )*factor) )
            self.v_bit_dia.set(  '%.3g' %(float(self.v_bit_dia.get()  )*factor) )
            self.v_depth_lim.set('%.3g' %(float(self.v_depth_lim.get())*factor) )
            self.v_step_len.set( '%.3g' %(float(self.v_step_len.get() )*factor) )
            self.allowance.set(  '%.3g' %(float(self.allowance.get()  )*factor) )
            self.v_max_cut.set(  '%.3g' %(float(self.v_max_cut.get()  )*factor) )
            self.v_rough_stk.set('%.3g' %(float(self.v_rough_stk.get())*factor) )
            self.xorigin.set(    '%.3g' %(float(self.xorigin.get()    )*factor) )
            self.yorigin.set(    '%.3g' %(float(self.yorigin.get()    )*factor) )
            self.accuracy.set(   '%.3g' %(float(self.accuracy.get()   )*factor) )
            self.clean_v.set(    '%.3g' %(float(self.clean_v.get()    )*factor) )
            self.clean_dia.set(  '%.3g' %(float(self.clean_dia.get()  )*factor) )
        except:
            pass

    def useIMGsize_var_Callback(self):
        if self.input_type.get() != "text":
            self.Read_image_file()
        try:
            ymx = max(self.font[key].get_ymax() for key in self.font)
            ymn = min(self.font[key].get_ymin() for key in self.font)
            image_height = ymx-ymn
        except:
            if self.units.get() == 'in':
                image_height = 2
            else:
                image_height = 50
        if (self.useIMGsize.get()):
            self.YSCALE.set('%.3g' %(100 * float(self.YSCALE.get()) / image_height ))
        else:
            self.YSCALE.set('%.3g' %(float(self.YSCALE.get()) / 100 * image_height ))

        self.menu_View_Refresh()
        self.Recalc_RQD()

    def Listbox_1_Click(self, event):
        labelL = []
        for i in self.Listbox_1.curselection():
            labelL.append( self.Listbox_1.get(i))
        try:
            self.fontfile.set(labelL[0])
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Listbox_Key_Up(self, event):
        try:
            select_new = int(self.Listbox_1.curselection()[0])-1
        except:
            select_new = self.Listbox_1.size()-2
        self.Listbox_1.selection_clear(0,END)
        self.Listbox_1.select_set(select_new)
        try:
            self.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Listbox_Key_Down(self, event):
        try:
            select_new = int(self.Listbox_1.curselection()[0])+1
        except:
            select_new = 1
        self.Listbox_1.selection_clear(0,END)
        self.Listbox_1.select_set(select_new)
        try:
            self.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Entry_fontdir_Callback(self, varName, index, mode):
        self.Listbox_1.delete(0, END)
        self.Listbox_1.configure( bg = self.NormalColor )
        try:
            font_files=os.listdir(self.fontdir.get())
            font_files.sort()
        except:
            font_files=" "
        for name in font_files:
            if str.find(name.upper(),'.CXF') != -1 \
            or (str.find(name.upper(),'.TTF') != -1 and self.TTF_AVAIL ):
                self.Listbox_1.insert(END, name)
        if len(self.fontfile.get()) < 4:
            try:
                self.fontfile.set(self.Listbox_1.get(0))
            except:
                self.fontfile.set(" ")
        self.Read_font_file()
        self.Recalc_RQD()
    # End General Settings Callbacks

    def menu_File_Open_G_Code_File(self):
        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR
        fileselect = askopenfilename(filetypes=[("F-Engrave G-code Files","*.ngc"),\
                                                ("All Files","*")],\
                                                 initialdir=init_dir)

        if fileselect != '' and fileselect != ():
            self.Open_G_Code_File(fileselect)

    def menu_File_Open_DXF_File(self):
        init_dir = os.path.dirname(self.IMAGE_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        if self.POTRACE_AVAIL == TRUE:
            if PIL:
                fileselect = askopenfilename(filetypes=[("DXF/Bitmap Files", ("*.dxf","*.bmp","*.pbm","*.ppm","*.pgm","*.pnm")),
                                                    ("DXF Files","*.dxf"),\
                                                    ("Bitmap Files",("*.bmp","*.pbm","*.ppm","*.pgm","*.pnm")),\
                                                    ("Slower Image Files",("*.jpg","*.png","*.gif","*.tif")),\
                                                    ("All Files","*")],\
                                                     initialdir=init_dir)
            else:
                fileselect = askopenfilename(filetypes=[("DXF/Bitmap Files", ("*.dxf","*.bmp","*.pbm","*.ppm","*.pgm","*.pnm")),
                                                    ("DXF Files","*.dxf"),\
                                                    ("Bitmap Files",("*.bmp","*.pbm","*.ppm","*.pgm","*.pnm")),\
                                                    ("All Files","*")],\
                                                     initialdir=init_dir)

            
        else:
            fileselect = askopenfilename(filetypes=[("DXF Files","*.dxf"),\
                                                    ("All Files","*")],\
                                                    initialdir=init_dir)

        if fileselect != '' and fileselect != ():
            self.IMAGE_FILE=fileselect
            self.Read_image_file()
            self.DoIt()

    def Open_G_Code_File(self,filename):
        self.delay_calc = 1
        boxsize = "0"
        try:
            fin = open(filename,'r')
        except:
            fmessage("Unable to open file: %s" %(filename))
            return
        text_codes=[]
        ident = "fengrave_set"
        for line in fin:
            if ident in line:

                input_code =  line.split(ident)[1].split()[0] 
                
                if "TCODE" in input_code:
                    code_list = line[line.find("TCODE"):].split()
                    for char in code_list:
                        try:
                            text_codes.append(int(char))
                        except:
                            pass
                # BOOL
                elif "show_axis"  in input_code:
                    self.show_axis.set(line[line.find("show_axis"):].split()[1])
                elif "show_box"   in input_code:
                    self.show_box.set(line[line.find("show_box"):].split()[1])
                elif "show_thick" in input_code:
                    self.show_thick.set(line[line.find("show_thick"):].split()[1])
                elif "flip"       in input_code:
                    self.flip.set(line[line.find("flip"):].split()[1])
                elif "mirror"     in input_code:
                    self.mirror.set(line[line.find("mirror"):].split()[1])
                elif "outer"  in input_code:
                    self.outer.set(line[line.find("outer"):].split()[1])
                elif "upper"      in input_code:
                   self.upper.set(line[line.find("upper"):].split()[1])
                elif "v_flop"      in input_code:
                   self.v_flop.set(line[line.find("v_flop"):].split()[1])
                elif "v_pplot"      in input_code:
                   self.v_pplot.set(line[line.find("v_pplot"):].split()[1])
                elif "inlay"      in input_code:
                   self.inlay.set(line[line.find("inlay"):].split()[1])
                elif "bmp_long"      in input_code:
                   self.bmp_longcurve.set(line[line.find("bmp_long"):].split()[1])
                elif "ext_char"   in input_code:
                   self.ext_char.set(line[line.find("ext_char"):].split()[1])
                elif "useIMGsize"   in input_code:
                   self.useIMGsize.set(line[line.find("useIMGsize"):].split()[1])
                elif "no_comments"   in input_code:
                   self.no_comments.set(line[line.find("no_comments"):].split()[1])

                # STRING
                elif "fontdir"    in input_code:
                    self.fontdir.set(line[line.find("fontdir"):].split("\042")[1])
                elif "gpre"       in input_code:
                    gpre_tmp = ""
                    for word in line[line.find("gpre"):].split():
                        if word != ")" and word != "gpre":
                            gpre_tmp = gpre_tmp + word + " "
                    self.gpre.set(gpre_tmp)
                elif "gpost"      in input_code:
                    gpost_tmp = ""
                    for word in line[line.find("gpost"):].split():
                        if word != ")" and word != "gpost":
                            gpost_tmp = gpost_tmp + word + " "
                    self.gpost.set(gpost_tmp)

                # STRING.set()
                elif "arc_fit"   in input_code:
                   self.arc_fit.set(line[line.find("arc_fit"):].split()[1])
                elif "YSCALE"     in input_code:
                    self.YSCALE.set(line[line.find("YSCALE"):].split()[1])
                elif "XSCALE"     in input_code:
                    self.XSCALE.set(line[line.find("XSCALE"):].split()[1])
                elif "LSPACE"     in input_code:
                    self.LSPACE.set(line[line.find("LSPACE"):].split()[1])
                elif "CSPACE"     in input_code:
                    self.CSPACE.set(line[line.find("CSPACE"):].split()[1])
                elif "WSPACE"     in input_code:
                    self.WSPACE.set(line[line.find("WSPACE"):].split()[1])
                elif "TANGLE"     in input_code:
                    self.TANGLE.set(line[line.find("TANGLE"):].split()[1])
                elif "TRADIUS"    in input_code:
                    self.TRADIUS.set(line[line.find("TRADIUS"):].split()[1])
                elif "ZSAFE"      in input_code:
                    self.ZSAFE.set(line[line.find("ZSAFE"):].split()[1])
                elif "ZCUT"       in input_code:
                    self.ZCUT.set(line[line.find("ZCUT"):].split()[1])
                elif "STHICK"     in input_code:
                    self.STHICK.set(line[line.find("STHICK"):].split()[1])

                elif "xorigin"    in input_code:
                    self.xorigin.set(line[line.find("xorigin"):].split()[1])
                elif "yorigin"    in input_code:
                    self.yorigin.set(line[line.find("yorigin"):].split()[1])
                elif "segarc"     in input_code:
                    self.segarc.set(line[line.find("segarc"):].split()[1])
                elif "accuracy"   in input_code:
                    self.accuracy.set(line[line.find("accuracy"):].split()[1])

                elif "origin"     in input_code:
                    self.origin.set(line[line.find("origin"):].split()[1])
                elif "justify"    in input_code:
                    self.justify.set(line[line.find("justify"):].split()[1])
                elif "units"      in input_code:
                    self.units.set(line[line.find("units"):].split()[1])
                elif "FEED"       in input_code:
                    self.FEED.set(line[line.find("FEED"):].split()[1])
                elif "PLUNGE"       in input_code:
                    self.PLUNGE.set(line[line.find("PLUNGE"):].split()[1])
                elif "fontfile"   in input_code:
                    self.fontfile.set(line[line.find("fontfile"):].split("\042")[1])
                elif "H_CALC"     in input_code:
                    self.H_CALC.set(line[line.find("H_CALC"):].split()[1])
                elif "plotbox"    in input_code:
                    self.plotbox.set(line[line.find("plotbox"):].split()[1])
                elif "boxgap"    in input_code:
                    self.boxgap.set(line[line.find("boxgap"):].split()[1])
                elif "boxsize"    in input_code:
                    boxsize = line[line.find("boxsize"):].split()[1]
                elif "cut_type"    in input_code:
                    self.cut_type.set(line[line.find("cut_type"):].split()[1])
                elif "bit_shape"    in input_code:
                    self.bit_shape.set(line[line.find("bit_shape"):].split()[1])
                elif "v_bit_angle"    in input_code:
                    self.v_bit_angle.set(line[line.find("v_bit_angle"):].split()[1])
                elif "v_bit_dia"    in input_code:
                    self.v_bit_dia.set(line[line.find("v_bit_dia"):].split()[1])
                elif "v_drv_crner"    in input_code:
                    self.v_drv_crner.set(line[line.find("v_drv_crner"):].split()[1])
                elif "v_stp_crner"    in input_code:
                    self.v_stp_crner.set(line[line.find("v_stp_crner"):].split()[1])
                elif "v_step_len"    in input_code:
                    self.v_step_len.set(line[line.find("v_step_len"):].split()[1])
                elif "allowance"    in input_code:
                    self.allowance.set(line[line.find("allowance"):].split()[1])
                elif "v_max_cut"    in input_code:
                    self.v_max_cut.set(line[line.find("v_max_cut"):].split()[1])
                elif "v_rough_stk"    in input_code:
                    self.v_rough_stk.set(line[line.find("v_rough_stk"):].split()[1])
                elif "var_dis"    in input_code:
                    self.var_dis.set(line[line.find("var_dis"):].split()[1])
                elif "v_depth_lim"    in input_code:
                    self.v_depth_lim.set(line[line.find("v_depth_lim"):].split()[1])
                elif "v_check_all"    in input_code:
                    self.v_check_all.set(line[line.find("v_check_all"):].split()[1])
                elif "bmp_turnp"    in input_code:
                    self.bmp_turnpol.set(line[line.find("bmp_turnp"):].split()[1])
                elif "bmp_turds"    in input_code:
                    self.bmp_turdsize.set(line[line.find("bmp_turds"):].split()[1])
                elif "bmp_alpha"    in input_code:
                    self.bmp_alphamax.set(line[line.find("bmp_alpha"):].split()[1])
                elif "bmp_optto"    in input_code:
                    self.bmp_opttolerance.set(line[line.find("bmp_optto"):].split()[1])
                elif "imagefile"    in input_code:
                    self.IMAGE_FILE = (line[line.find("imagefile"):].split("\042")[1])
                elif "input_type"    in input_code:
                    self.input_type.set(line[line.find("input_type"):].split()[1])
                elif "clean_dia"     in input_code:
                    self.clean_dia.set(line[line.find("clean_dia"):].split()[1])
                elif "clean_step"    in input_code:
                    self.clean_step.set(line[line.find("clean_step"):].split()[1])
                elif "clean_v"       in input_code:
                    self.clean_v.set(line[line.find("clean_v"):].split()[1])
                elif "clean_paths"    in input_code:
                    clean_paths=(line[line.find("clean_paths"):].split()[1])
                    clean_split = [float(n) for n in clean_paths.split(',')]
                    if len(clean_split) > 5:
                        self.clean_P.set(bool(clean_split[0]))
                        self.clean_X.set(bool(clean_split[1]))
                        self.clean_Y.set(bool(clean_split[2]))
                        self.v_clean_P.set(bool(clean_split[3]))
                        self.v_clean_Y.set(bool(clean_split[4]))
                        self.v_clean_X.set(bool(clean_split[5]))
                elif "NGC_DIR"    in input_code:
                    NGC_DIR = (line[line.find("NGC_DIR"):].split("\042")[1])
                    self.NGC_FILE     = (NGC_DIR+"/None")

        fin.close()

        file_full = self.fontdir.get() + "/" + self.fontfile.get()
        fileName, fileExtension = os.path.splitext(file_full)
        TYPE=fileExtension.upper()

        if TYPE!='.CXF' and TYPE!='.TTF' and TYPE!='':
            if ( os.path.isfile(file_full) ):
                self.input_type.set("image")

        if boxsize!="0":
            self.boxgap.set( float(boxsize) * float(self.STHICK.get()) )

        if (self.arc_fit.get()=="0"):
            self.arc_fit.set("none")
        elif (self.arc_fit.get()=="1"):
            self.arc_fit.set("center")

        if (self.arc_fit.get()!="none" and self.arc_fit.get()!="center" and self.arc_fit.get()!="radius"):
            self.arc_fit.set("center")

        if text_codes != []:
            try:
                self.Input.delete(1.0,END)
                for Ch in text_codes:
                    try:
                        self.Input.insert(END, "%c" %( unichr(int(Ch))))
                    except:
                        self.Input.insert(END, "%c" %( chr(int(Ch))))
            except:
                self.default_text = ''
                for Ch in text_codes:
                    try:
                        self.default_text = self.default_text + "%c" %( unichr(int(Ch)))
                    except:
                        self.default_text = self.default_text + "%c" %( chr(int(Ch)))

        if self.units.get() == 'in':
            self.funits.set('in/min')
        else:
            self.units.set('mm')
            self.funits.set('mm/min')

        self.calc_depth_limit()

        temp_name, fileExtension = os.path.splitext(filename)
        file_base=os.path.basename(temp_name)

        self.delay_calc = 0
        if self.initComplete == 1:
            self.NGC_FILE = filename
            self.menu_Mode_Change()
            
        

    def menu_File_Save_G_Code_File(self):
        if (self.Check_All_Variables() > 0):
            return

        if self.vcoords == [] and self.cut_type.get() == "v-carve":
            mess = "V-carve path data does not exist.  "
            mess = mess + "Only settings will be saved.\n\n"
            mess = mess + "To generate V-Carve path data Click on the"
            mess = mess + "\"Calculate V-Carve\" button on the main window."
            if not message_ask_ok_cancel("Continue", mess ):
                return

        self.WriteGCode()
        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file=os.path.basename(fileName)

        if self.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file=os.path.basename(fileName)
        else:
            init_file="text"

        filename = asksaveasfilename(defaultextension='.ngc', \
                                     filetypes=[("G-Code File","*.ngc"),("TAP File","*.tap"),("All Files","*")],\
                                     initialdir=init_dir,\
                                     initialfile= init_file )

        if filename != '' and filename != ():
            self.NGC_FILE = filename
            try:
                fout = open(filename,'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" %(filename))
                self.statusbar.configure( bg = 'red' )
                return
            for line in self.gcode:
                try:
                    fout.write(line+'\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" %(filename))
            self.statusbar.configure( bg = 'white' )


    def menu_File_Save_clean_G_Code_File(self, bit_type="straight"):
        if (self.Check_All_Variables() > 0):
            return

        self.WRITE_CLEAN_UP(bit_type)

        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file=os.path.basename(fileName)
        
        if self.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file=os.path.basename(fileName)
            fileName_tmp, fileExtension = os.path.splitext(init_file)
            init_file = fileName_tmp
        else:
            init_file="text"

        if bit_type == "v-bit":
            init_file = init_file + "_v" + self.clean_name.get()
        else:
            init_file = init_file +        self.clean_name.get()


        filename = asksaveasfilename(defaultextension='.ngc', \
                                     filetypes=[("G-Code File","*.ngc"),("TAP File","*.tap"),("All Files","*")],\
                                     initialdir=init_dir,\
                                     initialfile= init_file )

        if filename != '' and filename != ():
            try:
                fout = open(filename,'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" %(filename))
                self.statusbar.configure( bg = 'red' )
                return
            for line in self.gcode:
                try:
                    fout.write(line+'\n')
                except:
                    fout.write('(skipping line)\n')
            fout.close()
            self.statusMessage.set("File Saved: %s" %(filename))
            self.statusbar.configure( bg = 'white' )

    def menu_File_Save_SVG_File(self):
        self.WriteSVG()

        init_dir = os.path.dirname(self.NGC_FILE)
        if ( not os.path.isdir(init_dir) ):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file=os.path.basename(fileName)
        if self.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file=os.path.basename(fileName)
        else:
            init_file="text"

        filename = asksaveasfilename(defaultextension='.svg', \
                                     filetypes=[("SVG File"  ,"*.svg"),("All Files","*")],\
                                     initialdir=init_dir,\
                                     initialfile= init_file )

        if filename != '' and filename != ():
            try:
                fout = open(filename,'w')
            except:
                self.statusMessage.set("Unable to open file for writing: %s" %(filename))
                self.statusbar.configure( bg = 'red' )
                return
            for line in self.svgcode:
                try:
                    fout.write(line+'\n')
                except:
                    pass
            fout.close()
            
            self.statusMessage.set("File Saved: %s" %(filename))
            self.statusbar.configure( bg = 'white' )
    def menu_File_Quit(self):
        if message_ask_ok_cancel("Exit", "Exiting F-Engrave...."):
            self.Quit_Click(None)

    def menu_View_Refresh_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_View_Refresh(self):
        if ( (not self.batch.get()) and (self.initComplete == 1) and (self.delay_calc!=1) ):
            dummy_event = Event()
            dummy_event.widget=self.master
            self.Master_Configure(dummy_event,1)
            self.Plot_Data()

    def menu_Mode_Change_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_Mode_Change(self):
        dummy_event = Event()
        dummy_event.widget=self.master
        self.Master_Configure(dummy_event,1)

        if self.input_type.get() == "text":
            self.Read_font_file()
        else:
            self.Read_image_file()
        self.DoIt()

    def menu_View_Recalculate(self):
        self.DoIt()

    def menu_Help_About(self):
        about = "F-Engrave by Scorch.\n\n"
        about = about + "\163\143\157\162\143\150\100\163\143\157\162"
        about = about + "\143\150\167\157\162\153\163\056\143\157\155\n"
        about = about + "http://www.scorchworks.com/"
        message_box("About F-Engrave",about)

    def menu_Help_Web(self):
        webbrowser.open_new(r"http://www.scorchworks.com/Fengrave/fengrave_doc.html")


    def KEY_ESC(self, event):
        pass #A stop calculation command may go here

    def KEY_F1(self, event):
        self.menu_Help_About()

    def KEY_F2(self, event):
        self.GEN_Settings_Window()

    def KEY_F3(self, event):
        self.VCARVE_Settings_Window()

    def KEY_F4(self, event):
        self.PBM_Settings_Window()

    def KEY_F5(self, event):
        self.menu_View_Refresh()

    def KEY_ZOOM_IN(self, event):
        self.menu_View_Zoom_in()

    def KEY_ZOOM_OUT(self, event):
        self.menu_View_Zoom_out()

    def KEY_CTRL_G(self, event):
        self.CopyClipboard_GCode()

    def Master_Configure(self, event, update=0):
        if event.widget != self.master:
            return

        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        if (self.x, self.y) == (-1,-1):
            self.x, self.y = x,y
        if abs(self.w-w)>10 or abs(self.h-h)>10 or update==1:
            ###################################################
            #  Form changed Size (resized) adjust as required #
            ###################################################
            self.w=w
            self.h=h
            #canvas
            if self.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)


            if self.input_type.get() == "text":
                self.Label_font_prop.configure(text="Text Font Properties:")
                self.Label_Yscale.configure(text="Text Height")
                self.Label_Xscale.configure(text="Text Width")
                self.Label_pos_orient.configure(text="Text Position and Orientation:")
                self.Label_Tangle.configure(text="Text Angle")
                self.Label_flip.configure(text="Flip Text")
                self.Label_mirror.configure(text="Mirror Text")
                self.Label_Yscale_u = Label(self.master,textvariable=self.units, anchor=W)

                self.Label_useIMGsize.place_forget()
                self.Checkbutton_useIMGsize.place_forget()

                # Left Column #
                w_label=90
                w_entry=60
                w_units=35

                x_label_L=10
                x_entry_L=x_label_L+w_label+10
                x_units_L=x_entry_L+w_entry+5

                Yloc=6
                self.Label_font_prop.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)
                Yloc=Yloc+24
                self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Yscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Yscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Sthick.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Sthick_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Sthick.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                if self.cut_type.get() != "engrave":
                    self.Entry_Sthick.configure(state="disabled")
                    self.Label_Sthick.configure(state="disabled")
                    self.Label_Sthick_u.configure(state="disabled")
                else:
                    self.Entry_Sthick.configure(state="normal")
                    self.Label_Sthick.configure(state="normal")
                    self.Label_Sthick_u.configure(state="normal")

                Yloc=Yloc+24
                self.Label_Xscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Xscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Xscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Cspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Cspace_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Cspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Wspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Wspace_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Wspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Lspace.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Entry_Lspace.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24+12
                self.separator1.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_Justify.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Justify_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24+12
                self.separator2.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_text_on_arc.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Label_Tradius.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Tradius_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Tradius.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_outer.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_outer.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_upper.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_upper.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24+12
                self.separator3.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)

                # End Left Column #

                # Start Right Column
                w_label=90
                w_entry=60
                w_units=35

                x_label_R=self.w - 220
                x_entry_R=x_label_R+w_label+10
                x_units_R=x_entry_R+w_entry+5

                Yloc=6
                self.Label_gcode_opt.place(x=x_label_R, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Entry_Feed.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Feed.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Feed_u.place(x=x_units_R, y=Yloc, width=w_units+15, height=21)

                Yloc=Yloc+24
                self.Entry_Plunge.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Plunge.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Plunge_u.place(x=x_units_R, y=Yloc, width=w_units+15, height=21)

                Yloc=Yloc+24
                self.Entry_Zsafe.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Zsafe.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zsafe_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)


                Yloc=Yloc+24
                self.Label_Zcut.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zcut_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)
                self.Entry_Zcut.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)

                if self.cut_type.get() != "engrave":
                    self.Entry_Zcut.configure(state="disabled")
                    self.Label_Zcut.configure(state="disabled")
                    self.Label_Zcut_u.configure(state="disabled")
                else:
                    self.Entry_Zcut.configure(state="normal")
                    self.Label_Zcut.configure(state="normal")
                    self.Label_Zcut_u.configure(state="normal")

                Yloc=Yloc+24+6
                self.Label_List_Box.place(x=x_label_R+0, y=Yloc, width=113, height=22)

                Yloc=Yloc+24
                self.Listbox_1_frame.place(x=x_label_R+0, y=Yloc, width=160+25, height = self.h-324)
                self.Label_fontfile.place(x=x_label_R, y=self.h-165, width=w_label+75, height=21)
                self.Checkbutton_fontdex.place(x=x_label_R, y=self.h-145, width=185, height=23)

                # Buttons etc.

                Ybut=self.h-60
                self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

                Ybut=self.h-60
                self.V_Carve_Calc.place(x=x_label_R, y=Ybut, width=100, height=30)

                Ybut=self.h-105
                self.Radio_Cut_E.place(x=x_label_R, y=Ybut, width=185, height=23)
                Ybut=self.h-85
                self.Radio_Cut_V.place(x=x_label_R, y=Ybut, width=185, height=23)

                self.PreviewCanvas.configure( width = self.w-455, height = self.h-160 )
                self.PreviewCanvas_frame.place(x=220, y=10)
                self.Input_Label.place(x=222, y=self.h-130, width=112, height=21, anchor=W)
                self.Input_frame.place(x=222, y=self.h-110, width=self.w-455, height=75)

            else:
                self.Label_font_prop.configure(text="Image Properties:")
                self.Label_Yscale.configure(text="Image Height")
                self.Label_Xscale.configure(text="Image Width")
                self.Label_pos_orient.configure(text="Image Position and Orientation:")
                self.Label_Tangle.configure(text="Image Angle")
                self.Label_flip.configure(text="Flip Image")
                self.Label_mirror.configure(text="Mirror Image")
                if (self.useIMGsize.get()):
                    self.Label_Yscale_u = Label(self.master,text="%", anchor=W)
                else:
                    self.Label_Yscale_u = Label(self.master,textvariable=self.units, anchor=W)

                # Left Column #
                w_label=90
                w_entry=60
                w_units=35

                x_label_L=10
                x_entry_L=x_label_L+w_label+10
                x_units_L=x_entry_L+w_entry+5

                Yloc=6
                self.Label_font_prop.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)
                Yloc=Yloc+24
                self.Label_Yscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Yscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Yscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                Yloc=Yloc+24
                self.Label_useIMGsize.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_useIMGsize.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_Sthick.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Sthick_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Sthick.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)
                if self.cut_type.get() != "engrave":
                    self.Entry_Sthick.configure(state="disabled")
                    self.Label_Sthick.configure(state="disabled")
                    self.Label_Sthick_u.configure(state="disabled")
                else:
                    self.Entry_Sthick.configure(state="normal")
                    self.Label_Sthick.configure(state="normal")
                    self.Label_Sthick_u.configure(state="normal")



                Yloc=Yloc+24
                self.Label_Xscale.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Xscale_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Xscale.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                self.Label_Cspace.place_forget()
                self.Label_Cspace_u.place_forget()
                self.Entry_Cspace.place_forget()

                self.Label_Wspace.place_forget()
                self.Label_Wspace_u.place_forget()
                self.Entry_Wspace.place_forget()

                self.Label_Lspace.place_forget()
                self.Entry_Lspace.place_forget()

                Yloc=Yloc+24+12
                self.separator1.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_pos_orient.place(x=x_label_L, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Label_Tangle.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Label_Tangle_u.place(x=x_units_L, y=Yloc, width=w_units, height=21)
                self.Entry_Tangle.place(x=x_entry_L, y=Yloc, width=w_entry, height=23)

                self.Label_Justify.place_forget()
                self.Justify_OptionMenu.place_forget()

                Yloc=Yloc+24
                self.Label_Origin.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Origin_OptionMenu.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_flip.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_flip.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                Yloc=Yloc+24
                self.Label_mirror.place(x=x_label_L, y=Yloc, width=w_label, height=21)
                self.Checkbutton_mirror.place(x=x_entry_L, y=Yloc, width=w_entry+40, height=23)

                self.Label_text_on_arc.place_forget()
                self.Label_Tradius.place_forget()
                self.Label_Tradius_u.place_forget()
                self.Entry_Tradius.place_forget()
                self.Label_outer.place_forget()
                self.Checkbutton_outer.place_forget()
                self.Label_upper.place_forget()
                self.Checkbutton_upper.place_forget()

                # End Left Column #
                # Start Right Column Items
                x_label_R=x_label_L
                x_entry_R=x_entry_L
                x_units_R=x_units_L

                Yloc=Yloc+24+12
                self.separator2.place(x=x_label_R, y=Yloc,width=w_label+75+40, height=2)

                Yloc=Yloc+6
                self.Label_gcode_opt.place(x=x_label_R, y=Yloc, width=w_label*2, height=21)

                Yloc=Yloc+24
                self.Entry_Feed.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Feed.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Feed_u.place(x=x_units_R, y=Yloc, width=w_units+15, height=21)

                Yloc=Yloc+24
                self.Entry_Plunge.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Plunge.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Plunge_u.place(x=x_units_R, y=Yloc, width=w_units+15, height=21)

                Yloc=Yloc+24
                self.Entry_Zsafe.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)
                self.Label_Zsafe.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zsafe_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)


                Yloc=Yloc+24
                self.Label_Zcut.place(  x=x_label_R, y=Yloc, width=w_label, height=21)
                self.Label_Zcut_u.place(x=x_units_R, y=Yloc, width=w_units, height=21)
                self.Entry_Zcut.place(  x=x_entry_R, y=Yloc, width=w_entry, height=23)

                if self.cut_type.get() != "engrave":
                    self.Entry_Zcut.configure(state="disabled")
                    self.Label_Zcut.configure(state="disabled")
                    self.Label_Zcut_u.configure(state="disabled")
                else:
                    self.Entry_Zcut.configure(state="normal")
                    self.Label_Zcut.configure(state="normal")
                    self.Label_Zcut_u.configure(state="normal")

                self.Label_List_Box.place_forget()
                self.Listbox_1_frame.place_forget()
                self.Checkbutton_fontdex.place_forget()

                Yloc=Yloc+24+12
                self.separator3.place(x=x_label_L, y=Yloc,width=w_label+75+40, height=2)
                Yloc=Yloc+6
                self.Label_fontfile.place(x=x_label_R, y=Yloc, width=w_label+75, height=21)

                # Buttons etc.
                offset_R=100
                Ybut=self.h-60
                self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

                Ybut=self.h-60
                self.V_Carve_Calc.place(x=x_label_R+offset_R, y=Ybut, width=100, height=30)

                Ybut=self.h-105
                self.Radio_Cut_E.place(x=x_label_R+offset_R, y=Ybut, width=w_label, height=23)
                Ybut=self.h-85
                self.Radio_Cut_V.place(x=x_label_R+offset_R, y=Ybut, width=w_label, height=23)

                self.PreviewCanvas.configure( width = self.w-240, height = self.h-45 )
                self.PreviewCanvas_frame.place(x=230, y=10)
                self.Input_Label.place_forget()
                self.Input_frame.place_forget()

            ###########################################################
            if self.cut_type.get() == "v-carve":
                pass
            else:
                pass
            ###########################################################
            self.Plot_Data()

    ############################################################################
    # routine takes an x and y the point is rotated by angle returns new x,y   #
    ############################################################################
    def Rotn(self,x,y,angle,radius):
        if radius > 0.0:
            alpha = x / radius
            xx = ( radius + y ) * sin(alpha)
            yy = ( radius + y ) * cos(alpha)
        elif radius < 0.0:
            alpha = x / radius
            xx = ( radius + y ) * sin(alpha)
            yy = ( radius + y ) * cos(alpha)
        else: #radius is 0
            alpha = 0
            xx = x
            yy = y

        rad = sqrt(xx * xx + yy * yy)
        theta = atan2(yy,xx)
        newx=rad * cos(theta + radians(angle) )
        newy=rad * sin(theta + radians(angle) )
        return newx,newy,alpha

    ############################################################################
    # routine takes an x and a y scales are applied and returns new x,y tuple  #
    ############################################################################
    def CoordScale(self,x,y,xscale,yscale):
        newx = x * xscale
        newy = y * yscale
        return newx,newy

    def Plot_Line(self,XX1,YY1,XX2,YY2,midx,midy,cszw,cszh,PlotScale,col,radius=0):
        x1 =  cszw/2 + (XX1-midx) / PlotScale
        x2 =  cszw/2 + (XX2-midx) / PlotScale
        y1 =  cszh/2 - (YY1-midy) / PlotScale
        y2 =  cszh/2 - (YY2-midy) / PlotScale
        if radius==0:
            thick=0
        else:
            thick  =  radius*2 / PlotScale
        self.segID.append( self.PreviewCanvas.create_line(x1,y1,x2,y2,fill = col, capstyle="round", width=thick))

    def Plot_Circ(self,XX1,YY1,midx,midy,cszw,cszh,PlotScale,color,Rad,fill):
        dd=Rad
        x1 =  cszw/2 + (XX1-dd-midx) / PlotScale
        x2 =  cszw/2 + (XX1+dd-midx) / PlotScale
        y1 =  cszh/2 - (YY1-dd-midy) / PlotScale
        y2 =  cszh/2 - (YY1+dd-midy) / PlotScale
        if fill ==0:
            self.segID.append( self.PreviewCanvas.create_oval(x1,y1,x2,y2, outline=color, fill=None, width=1 ))
        else:
            self.segID.append( self.PreviewCanvas.create_oval(x1,y1,x2,y2, outline=color, fill=color, width=0 ))

    ############################################################################
    # Routine finds the maximum radius that can be placed in the position      #
    # xpt,ypt witout interfearing with other line segments (rmin is max R LOL) #
    ############################################################################
    #def find_max_circle(self,xpt,ypt,rmin,char_num,seg_sin,seg_cos,corner,Acc_delete,CHK_STRING):
    def find_max_circle(self,xpt,ypt,rmin,char_num,seg_sin,seg_cos,corner,CHK_STRING):
        global Zero
        rtmp = rmin

        xIndex = int((xpt-self.MINX)/self.xPartitionLength)
        yIndex = int((ypt-self.MINY)/self.yPartitionLength)

        self.coords_check=[]
        R_A = abs(rmin)
        Bcnt=-1
        ############################################################
        # Loop over active partitions for the current line segment #
        ############################################################
        for line_B in self.partitionList[xIndex][yIndex]:
            Bcnt=Bcnt+1
            X_B = line_B[len(line_B)-3]
            Y_B = line_B[len(line_B)-2]
            R_B = line_B[len(line_B)-1]
            GAP = sqrt( (X_B-xpt)*(X_B-xpt) + (Y_B-ypt)*(Y_B-ypt)  )
            if GAP < abs(R_A + R_B):
                self.coords_check.append(line_B)

        for linec in self.coords_check:
            XYc = linec
            xmaxt=max(XYc[0],XYc[2]) + rmin*2
            xmint=min(XYc[0],XYc[2]) - rmin*2
            ymaxt=max(XYc[1],XYc[3]) + rmin*2
            ymint=min(XYc[1],XYc[3]) - rmin*2
            if (xpt >= xmint and  ypt >= ymint and xpt <= xmaxt and  ypt <= ymaxt):
                logic_full = True
            else:
                logic_full = False
                continue

            if (CHK_STRING == "chr"):
                logic_full = logic_full and (char_num == int(XYc[5]))

            if corner==1:
                logic_full = logic_full and                                                 \
                             ( (fabs(xpt-XYc[0]) > Zero) or (fabs(ypt-XYc[1]) > Zero) ) and \
                             ( (fabs(xpt-XYc[2]) > Zero) or (fabs(ypt-XYc[3]) > Zero) )

            if logic_full:
                xc1 = (XYc[0]-xpt) * seg_cos - (XYc[1]-ypt) * seg_sin
                yc1 = (XYc[0]-xpt) * seg_sin + (XYc[1]-ypt) * seg_cos
                xc2 = (XYc[2]-xpt) * seg_cos - (XYc[3]-ypt) * seg_sin
                yc2 = (XYc[2]-xpt) * seg_sin + (XYc[3]-ypt) * seg_cos

                if fabs(xc2-xc1) < Zero and fabs(yc2-yc1) > Zero:
                    rtmp=fabs(xc1)
                    if max(yc1,yc2) >= rtmp and min(yc1,yc2) <= rtmp:
                        rmin = min(rmin,rtmp)

                elif fabs(yc2-yc1) < Zero and fabs(xc2-xc1) > Zero:
                    if max(xc1,xc2) >= 0.0 and min(xc1,xc2) <= 0.0 and yc1 > Zero:
                        rtmp=yc1/2.0
                        rmin = min(rmin,rtmp)

                if fabs(yc2-yc1) > Zero and fabs(xc2-xc1) > Zero:
                    m = (yc2-yc1)/(xc2-xc1)
                    b = yc1 - m*xc1
                    sq = m+1/m
                    A = 1 + m*m - 2*m*sq
                    B = -2*b*sq
                    C = -b*b
                    try:
                        sq_root = sqrt(B*B-4*A*C)
                        xq1 = (-B + sq_root)/(2*A)

                        if xq1 >= min(xc1,xc2) and xq1 <= max(xc1,xc2):
                            rtmp = xq1*sq + b
                            if rtmp >= 0.0:
                                rmin=min(rmin,rtmp)

                        xq2 = (-B - sq_root)/(2*A)
                        yq2 = m*xq2+b

                        if xq2 >= min(xc1,xc2) and xq2 <= max(xc1,xc2):
                            rtmp = xq2*sq + b
                            if rtmp >= 0.0:
                                rmin=min(rmin,rtmp)
                    except:
                        pass

                if yc1 > Zero:
                    rtmp = (xc1*xc1 + yc1*yc1) / (2*yc1)
                    rmin=min(rmin,rtmp)

                if yc2 > Zero:
                    rtmp = (xc2*xc2 + yc2*yc2) / (2*yc2)
                    rmin=min(rmin,rtmp)

                ###### NEW V1.20 #######
                if abs(yc1) < Zero and abs(xc1) < Zero:
                    if yc2 > Zero:
                        rmin = 0.0
                if abs(yc2) < Zero and abs(xc2) < Zero:
                    if yc1 > Zero:
                        rmin = 0.0
                ### END NEW V1.20 #####

        return rmin

    def Recalculate_RQD_Nocalc(self, event):
        self.statusbar.configure( bg = 'yellow' )
        self.Input.configure( bg = 'yellow' )
        self.statusMessage.set(" Recalculation required.")

    def Recalculate_RQD_Click(self, event):
        self.statusbar.configure( bg = 'yellow' )
        self.statusMessage.set(" Recalculation required.")
        self.DoIt()

    def Recalc_RQD(self):
        self.statusbar.configure( bg = 'yellow' )
        self.statusMessage.set(" Recalculation required.")
        self.DoIt()

    ##########################################
    #          Read Font File                #
    ##########################################
    def Read_font_file(self):
        if (self.delay_calc==1):
            return
        
        self.font = {}
        file_full = self.fontdir.get() + "/" + self.fontfile.get()
        if ( not os.path.isfile(file_full) ):
            return
        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set("Reading Font File.........")
            self.master.update_idletasks()

        fileName, fileExtension = os.path.splitext(file_full)
        self.current_input_file.set( os.path.basename(file_full) )

        SegArc    =  float(self.segarc.get())
        TYPE=fileExtension.upper()
        if TYPE=='.CXF':
            try:
                file = open(file_full)
            except:
                self.statusMessage.set("Unable to Open CXF File: %s" %(file_full))
                self.statusbar.configure( bg = 'red' )
                return
            self.font = parse(file,SegArc)  # build stroke lists from font file
            file.close()

        elif TYPE=='.TTF':
            option = ""
            if self.ext_char.get():
                option = option + "-e"
            else:
                option = ""
            cmd = ["ttf2cxf_stream",
                   option,
                   "-s",self.segarc.get(),
                   file_full,"STDOUT"]
            try:
                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                if VERSION == 3:
                    file=bytes.decode(stdout).split("\n")
                else:
                    file=stdout.split("\n")

                self.font = parse(file,SegArc)  # build stroke lists from font file
                self.input_type.set("text")
            except:
                fmessage("Unable To open True Type (TTF) font file: %s" %(file_full))
        else:
            pass

        if (not self.batch.get()):
            self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),1)
            self.menu_View_Refresh()

    ##########################################
    #          Read Font File                #
    ##########################################
    def Read_image_file(self):
        if (self.delay_calc==1):
            return
        
        self.font = {}
        file_full = self.IMAGE_FILE
        file_name = os.path.basename(file_full)
        if ( not os.path.isfile(file_full) ):
            file_full = file_name
            if ( not os.path.isfile( file_full ) ):
                file_full = self.HOME_DIR+"/"+file_name
                if ( not os.path.isfile( file_full ) ):
                    file_full = os.path.dirname(self.NGC_FILE)+"/"+file_name
                    if ( not os.path.isfile( file_full ) ):
                        return
        self.IMAGE_FILE = file_full
        
        
        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set(" Reading Image File.........")
            self.master.update_idletasks()

        fileName, fileExtension = os.path.splitext(file_full)
        self.current_input_file.set( os.path.basename(file_full) )


        new_origin = False
        SegArc    =  float(self.segarc.get())
        TYPE=fileExtension.upper()
        if TYPE=='.DXF':
            try:
                fd = open(file_full)
                self.font = parse_dxf(fd,SegArc,new_origin)  # build stroke lists from font file
                fd.close()
                self.input_type.set("image")
            except:
                fmessage("Unable To open Drawing Exchange File (DXF) file.")

        elif TYPE=='.BMP' or TYPE=='.PBM' or TYPE=='.PPM' or TYPE=='.PGM' or TYPE=='.PNM':
            try:
                #cmd = ["potrace","-b","dxf",file_full,"-o","-"]
                if self.bmp_longcurve.get() == 1:
                    cmd = ["potrace",
                       "-z", self.bmp_turnpol.get(),
                       "-t", self.bmp_turdsize.get(),
                       "-a",self.bmp_alphamax.get(),
                       "-O",self.bmp_opttolerance.get(),
                       "-b","dxf",file_full,"-o","-"]
                else:
                    cmd = ["potrace",
                       "-z", self.bmp_turnpol.get(),
                       "-t", self.bmp_turdsize.get(),
                       "-a",self.bmp_alphamax.get(),
                       "-n",
                       "-b","dxf",file_full,"-o","-"]

                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                if VERSION == 3:
                    fd=bytes.decode(stdout).split("\n")
                else:
                    fd=stdout.split("\n")
                #self.font,self.DXF_source = parse_dxf(fd,SegArc,new_origin)  # build stroke lists from font file
                self.font = parse_dxf(fd,SegArc,new_origin)  # build stroke lists from font file
                self.input_type.set("image")
            except:
                fmessage("Unable To create path data from bitmap File.")

        elif TYPE=='.JPG' or TYPE=='.PNG' or TYPE=='.GIF' or TYPE=='.TIF':
            ###########################################################################################################
            #VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV#
            if PIL:
                try:
                    PIL_im = Image.open(file_full)
                    PIL_im = PIL_im.convert("1")
                    file_full_tmp=self.HOME_DIR + "/fengrave_tmp.bmp"
                    PIL_im.save(file_full_tmp,"bmp")
                
                    #cmd = ["potrace","-b","dxf",file_full,"-o","-"]
                    if self.bmp_longcurve.get() == 1:
                        cmd = ["potrace",
                           "-z", self.bmp_turnpol.get(),
                           "-t", self.bmp_turdsize.get(),
                           "-a",self.bmp_alphamax.get(),
                           "-O",self.bmp_opttolerance.get(),
                           "-b","dxf",file_full_tmp,"-o","-"]
                    else:
                        cmd = ["potrace",
                           "-z", self.bmp_turnpol.get(),
                           "-t", self.bmp_turdsize.get(),
                           "-a",self.bmp_alphamax.get(),
                           "-n",
                           "-b","dxf",file_full_tmp,"-o","-"]

                    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = p.communicate()
                    if VERSION == 3:
                        fd=bytes.decode(stdout).split("\n")
                    else:
                        fd=stdout.split("\n")
                    self.font = parse_dxf(fd,SegArc,new_origin)  # build stroke lists from font file
                    self.input_type.set("image")
                    try:
                        os.remove(file_full_tmp)
                    except:
                        pass
                except:
                    fmessage("PIL encountered an error. Unable To create path data from the selected image File.")
                    fmessage("Converting the image file to a BMP file may resolve the issue.")
                    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
            else:
                fmessage("PIL is required for reading JPG, PNG, GIF and TIF files.")
            ###########################################################################################################  
        else:
            pass

        #Reset Entry Fields in Bitmap Settings
        if (not self.batch.get()):
            self.entry_set(self.Entry_BMPoptTolerance,self.Entry_BMPoptTolerance_Check(),1)
            self.entry_set(self.Entry_BMPturdsize,    self.Entry_BMPturdsize_Check()    ,1)
            self.entry_set(self.Entry_BMPalphamax,    self.Entry_BMPalphamax_Check()    ,1)
            self.entry_set(self.Entry_ArcAngle,       self.Entry_ArcAngle_Check()       ,1)
            self.menu_View_Refresh()


    ##########################################
    #        CANVAS PLOTTING STUFF           #
    ##########################################
    def Plot_Data(self):
        if (self.delay_calc==1) or (self.delay_calc == 1):
            return
        self.master.update_idletasks()
        # erase old segs/display objects
        self.PreviewCanvas.delete(ALL)
        self.segID = []

        cszw = int(self.PreviewCanvas.cget("width"))
        cszh = int(self.PreviewCanvas.cget("height"))
        buff=10

        maxx = self.MAXX
        minx = self.MINX
        maxy = self.MAXY
        miny = self.MINY
        midx=(maxx+minx)/2
        midy=(maxy+miny)/2

        if self.cut_type.get() == "v-carve":
            Thick = 0.0
        else:
            Thick   = float(self.STHICK.get())

        if self.input_type.get() == "text":
            Radius_in =  float(self.TRADIUS.get())
        else:
            Radius_in = 0.0

        PlotScale = max((maxx-minx+Thick)/(cszw-buff), (maxy-miny+Thick)/(cszh-buff))
        if PlotScale <= 0:
            PlotScale=1.0
        self.pscale = PlotScale

        Radius_plot = 0
        if self.plotbox.get() != "no_box" and self.cut_type.get() == "engrave":
            if Radius_in != 0:
                Radius_plot=  float(self.RADIUS_PLOT)

        x_lft = cszw/2 + (minx-midx) / PlotScale
        x_rgt = cszw/2 + (maxx-midx) / PlotScale
        y_bot = cszh/2 + (maxy-midy) / PlotScale
        y_top = cszh/2 + (miny-midy) / PlotScale

        if self.show_box.get() == True:
            self.segID.append( self.PreviewCanvas.create_rectangle(
                    x_lft, y_bot, x_rgt, y_top, fill="gray80", outline="gray80", width = 0) )

        if Radius_in != 0:
            Rx_lft = cszw/2 + ( -Radius_in-midx)  / PlotScale
            Rx_rgt = cszw/2 + (  Radius_in-midx)  / PlotScale
            Ry_bot = cszh/2 + (  Radius_in+midy)  / PlotScale
            Ry_top = cszh/2 + ( -Radius_in+midy)  / PlotScale
            self.segID.append( self.PreviewCanvas.create_oval(Rx_lft, Ry_bot, Rx_rgt, Ry_top, outline="gray90", width = 0, dash=3) )

        if self.show_thick.get() == True:
            plot_width = Thick / PlotScale
        else:
            plot_width = 1.0

        # Plot circle radius with radius equal to Radius_plot
        if Radius_plot != 0:
            Rpx_lft = cszw/2 + ( -Radius_plot-midx)  / PlotScale
            Rpx_rgt = cszw/2 + (  Radius_plot-midx)  / PlotScale
            Rpy_bot = cszh/2 + (  Radius_plot+midy)  / PlotScale
            Rpy_top = cszh/2 + ( -Radius_plot+midy)  / PlotScale
            self.segID.append( self.PreviewCanvas.create_oval(Rpx_lft, Rpy_bot, Rpx_rgt, Rpy_top, outline="black", width = plot_width) )

        for line in self.coords:
            XY = line
            x1 =  cszw/2 + (XY[0]-midx) / PlotScale
            x2 =  cszw/2 + (XY[2]-midx) / PlotScale
            y1 =  cszh/2 - (XY[1]-midy) / PlotScale
            y2 =  cszh/2 - (XY[3]-midy) / PlotScale
            self.segID.append( self.PreviewCanvas.create_line(x1,y1,x2,y2,fill = 'black', \
                                                                  width=plot_width , \
                                                                  capstyle='round' ))
        XOrigin   =  float(self.xorigin.get())
        YOrigin   =  float(self.yorigin.get())
        axis_length=(maxx-minx)/4
        axis_x1 =  cszw/2 + (-midx             + XOrigin ) / PlotScale
        axis_x2 =  cszw/2 + ( axis_length-midx + XOrigin ) / PlotScale
        axis_y1 =  cszh/2 - (-midy             + YOrigin ) / PlotScale
        axis_y2 =  cszh/2 - ( axis_length-midy + YOrigin ) / PlotScale


        #########################################
        # V-carve Ploting Stuff
        #########################################
        if self.cut_type.get() == "v-carve":
            loop_old = -1
            r_inlay_top = self.calc_r_inlay_top()

            for line in self.vcoords:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                color = "black"

                rbit = self.calc_vbit_dia()/2.0
                if self.bit_shape.get() == "FLAT":
                    if r >= rbit:
                        self.Plot_Circ(x1,y1,midx,midy,cszw,cszh,PlotScale,color,r,1)
                else:
                    if self.inlay.get():
                        self.Plot_Circ(x1,y1,midx,midy,cszw,cszh,PlotScale,color,r-r_inlay_top,1)
                    else:
                        self.Plot_Circ(x1,y1,midx,midy,cszw,cszh,PlotScale,color,r,1)

            loop_old = -1
            rold     = -1
            for line in self.vcoords:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                loop  = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                plot_flat = False
                if self.bit_shape.get() == "FLAT":
                    if (r == rold) and (r >= rbit):
                        plot_flat = True
                else:
                    plot_flat = True

                if (loop == loop_old) and plot_flat:
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color)
                loop_old = loop
                rold=r
                xold=x1
                yold=y1

        ########################################
        # Plot cleanup data
        ########################################
        if self.cut_type.get() == "v-carve":
            loop_old = -1
            for line in self.clean_coords_sort:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                loop  = XY[3]
                color = "brown"
                if (loop == loop_old):
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color,r)
                loop_old = loop
                xold=x1
                yold=y1

            loop_old = -1
            for line in self.clean_coords_sort:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                loop  = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous start point
                if (loop == loop_old):
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color)
                loop_old = loop
                xold=x1
                yold=y1

            loop_old = -1
            for line in self.v_clean_coords_sort:
                XY    = line
                x1    = XY[0]
                y1    = XY[1]
                r     = XY[2]
                loop  = XY[3]
                color = "yellow"
                if (loop == loop_old):
                    self.Plot_Line(xold, yold, x1, y1, midx,midy,cszw,cszh,PlotScale,color)
                loop_old = loop
                xold=x1
                yold=y1


        #########################################
        # End V-carve Plotting Stuff
        #########################################

        if self.show_axis.get() == True:
            # Plot coordinate system origin
            self.segID.append( self.PreviewCanvas.create_line(axis_x1,axis_y1,\
                                                                  axis_x2,axis_y1,\
                                                                  fill = 'red'  , width = 0))
            self.segID.append( self.PreviewCanvas.create_line(axis_x1,axis_y1,\
                                                                  axis_x1,axis_y2,\
                                                                  fill = 'green', width = 0))

    ############################################################################
    #                         Perform  Calculations                            #
    ############################################################################
    def DoIt(self):
        if ((self.delay_calc==1) or (self.delay_calc == 1)):
            return
        
        self.menu_View_Refresh()
        
        if (not self.batch.get):
            if self.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)

        if (self.Check_All_Variables() > 0):
            return

        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set(" Calculating.........")
            self.master.update_idletasks()
            self.PreviewCanvas.delete(ALL)

        # erase old data
        self.segID = []
        self.gcode   = []
        self.svgcode = []
        self.coords  = []
        self.vcoords = []
        self.clean_coords = []
        self.clean_segment=[]
        self.clean_coords_sort=[]
        self.v_clean_coords_sort=[]

        self.RADIUS_PLOT = 0


        if len(self.font) == 0 and (not self.batch.get()):
            self.statusbar.configure( bg = 'red' )
            if self.input_type.get() == "text":
                self.statusMessage.set("No Font Characters Loaded")
            else:
                self.statusMessage.set("No Image Loaded")
            return

        if self.input_type.get() == "text":
            if (not self.batch.get()):
                String    =  self.Input.get(1.0,END)
            else:
                String    =  self.default_text

            Radius_in =  float(self.TRADIUS.get())
        else:
            String    = "F"
            Radius_in =  0.0
        try:
            SegArc    =  float(self.segarc.get())
            YScale_in =  float(self.YSCALE.get() )
            CSpaceP   =  float(self.CSPACE.get() )
            WSpaceP   =  float(self.WSPACE.get() )
            LSpace    =  float(self.LSPACE.get() )
            Angle     =  float(self.TANGLE.get() )
            Thick     =  float(self.STHICK.get() )
            XOrigin   =  float(self.xorigin.get())
            YOrigin   =  float(self.yorigin.get())
            v_flop    =  bool(self.v_flop.get())
        except:
            self.statusMessage.set(" Unable to create paths.  Check Settings Entry Values.")
            self.statusbar.configure( bg = 'red' )
            return

        if self.cut_type.get() == "v-carve":
            Thick = 0.0

        line_maxx = []
        line_maxy = []
        line_maxa = []
        line_mina = []
        line_miny = []
        line_minx = []

        maxx_tmp = -99991.0
        maxy_tmp = -99992.0
        maxa_tmp = -99993.0
        mina_tmp =  99993.0
        miny_tmp =  99994.0
        minx_tmp =  99995.0

        font_word_space  = 0
        font_line_height = -1e10
        font_char_width =  -1e10
        font_used_height = -1e10
        font_used_width  = -1e10
        font_used_depth  =  1e10

        ################################
        ##      Font Index Preview    ##
        ################################
        if self.fontdex.get() == True:
            Radius_in = 0.0
            String = ""
            for key in self.font:
                if self.ext_char:
                    String = String + unichr(key)
                elif int(key) < 256:
                    String = String + unichr(key)

            Strings = sorted(String)
            mcnt = 0
            String = ""

            if self.ext_char.get():
                pcols = int(1.5*sqrt(float(len(self.font))))
            else:
                pcols = 15

            for char in Strings:
                mcnt = mcnt+1
                String = String + char
                if mcnt > pcols:
                    String = String + '\n'
                    mcnt = 0

        ##################################
        ## Font Height/Width Calculation #
        ##################################
        for char in String:
            try:
                font_used_height = max( self.font[ord(char)].get_ymax(), font_used_height )
                font_used_width  = max( self.font[ord(char)].get_xmax(), font_used_width  )
                font_used_depth  = min( self.font[ord(char)].get_ymin(), font_used_depth  )
            except:
                pass

        if self.H_CALC.get() == "max_all":
            font_line_height = max(self.font[key].get_ymax() for key in self.font)
            font_line_depth  = min(self.font[key].get_ymin() for key in self.font)
        elif self.H_CALC.get() == "max_use":
            font_line_height = font_used_height
            font_line_depth  = font_used_depth

        if font_line_height > 0:
            if (self.useIMGsize.get() and self.input_type.get()=="image"):
                YScale = YScale_in/100.0
            else:
                try:
                    YScale = (YScale_in-Thick)/(font_line_height-font_line_depth)
                except:
                    YScale=.1
                if YScale <= Zero:
                    YScale = .1
        else:
            if (not self.batch.get()): self.statusbar.configure( bg = 'red' )
            if self.H_CALC.get() == "max_all":
                if (not self.batch.get()):
                    self.statusMessage.set("No Font Characters Found")
                else:
                    fmessage("(No Font Characters Found)")
            elif self.H_CALC.get() == "max_use":
                if self.input_type.get()=="image":
                    error_text = "Image contains no design information. (Empty DXF File)"
                else:
                    error_text = "Input Characters Were Not Found in the Current Font"
                    
                if (not self.batch.get()):
                    self.statusMessage.set(error_text)
                else:
                    fmessage("("+error_text+")")
            return
        font_char_width  = max(self.font[key].get_xmax() for key in self.font)
        font_word_space =  font_char_width * (WSpaceP/100.0)

        XScale = float(self.XSCALE.get())  * YScale / 100
        font_char_space =  font_char_width * (CSpaceP /100.0)

        if Radius_in != 0.0:
            if self.outer.get() == True:
                if self.upper.get() == True:
                    Radius =  Radius_in + Thick/2 + YScale*(-font_line_depth)
                else:
                    Radius = -Radius_in - Thick/2 - YScale*(font_line_height)
            else:
                if self.upper.get() == True:
                    Radius =  Radius_in - Thick/2 - YScale*(font_line_height)
                else:
                    Radius = -Radius_in + Thick/2 + YScale*(-font_line_depth)
        else:
            Radius =  Radius_in

        font_line_space = (font_line_height - font_line_depth + Thick/YScale) * LSpace

        max_vals=[]

        xposition  = 0.0
        yposition  = 0.0
        line_cnt = 0.0
        char_cnt = 0
        no_font_record = []
        message2 = ""
        for char in String:
            char_cnt = char_cnt + 1

            if char == ' ':
                xposition += font_word_space
                continue
            if char == '\t':
                xposition += 3*font_word_space
                continue
            if char == '\n':
                xposition = 0
                yposition += font_line_space
                line_cnt = line_cnt+1
                line_minx.append(minx_tmp)
                line_miny.append(miny_tmp)
                line_maxx.append(maxx_tmp)
                line_maxy.append(maxy_tmp)
                line_maxa.append(maxa_tmp)
                line_mina.append(mina_tmp)
                maxx_tmp = -99919.0
                maxy_tmp = -99929.0
                maxa_tmp = -99939.0
                mina_tmp =  99949.0
                miny_tmp =  99959.0
                minx_tmp =  99969.0
                continue

            first_stroke = True
            try:
                font_line_height = self.font[ord(char)].get_ymax()
            except:
                flag=0
                for norec in no_font_record:
                    if norec == char:
                        flag=1
                if flag == 0:
                    no_font_record.append(char)
                    message2 = ", CHECK OUTPUT! Some characters not found in font file."
                continue
            for stroke in self.font[ord(char)].stroke_list:
                x1 = stroke.xstart + xposition
                y1 = stroke.ystart - yposition
                x2 = stroke.xend   + xposition
                y2 = stroke.yend   - yposition

                # Perform scaling
                x1,y1 = self.CoordScale(x1,y1,XScale,YScale)
                x2,y2 = self.CoordScale(x2,y2,XScale,YScale)

                self.coords.append([x1,y1,x2,y2,line_cnt,char_cnt])

                maxx_tmp = max(maxx_tmp, x1, x2)
                minx_tmp = min(minx_tmp, x1, x2)
                miny_tmp = min(miny_tmp, y1, y2)
                maxy_tmp = max(maxy_tmp, y1, y2)

            char_width = self.font[ord(char)].get_xmax() # move over for next character
            xposition += font_char_space + char_width
        #END Char in String

        maxx = maxy = -99999.0
        miny = minx =  99999.0
        cnt=0

        for maxx_val in line_maxx:
            maxx = max( maxx, line_maxx[cnt] )
            minx = min( minx, line_minx[cnt] )
            miny = min( miny, line_miny[cnt] )
            maxy = max( maxy, line_maxy[cnt] )
            cnt=cnt+1
        ##########################################
        #      TEXT LEFT JUSTIFY STUFF           #
        ##########################################
        if self.justify.get() == "Left":
            pass
        ##########################################
        #          TEXT CENTERING STUFF          #
        ##########################################
        if self.justify.get() == "Center":
            cnt=0
            for line in self.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    self.coords[cnt][0]=XY[0] + (maxx - line_maxx[line_num])/2
                    self.coords[cnt][2]=XY[2] + (maxx - line_maxx[line_num])/2
                except:
                    pass
                cnt=cnt+1

        ##########################################
        #        TEXT RIGHT JUSTIFY STUFF        #
        ##########################################
        if self.justify.get() == "Right":
            for line in self.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    XY[0]=XY[0] + (maxx - line_maxx[line_num])
                    XY[2]=XY[2] + (maxx - line_maxx[line_num])
                except:
                    pass
                cnt=cnt+1

        ##########################################
        #         TEXT ON RADIUS STUFF           #
        ##########################################
        mina =  99996.0
        maxa = -99993.0
        if Radius != 0.0:
            for line in self.coords:
                XY = line
                XY[0],XY[1],A1 = self.Rotn(XY[0],XY[1],0,Radius)
                XY[2],XY[3],A2 = self.Rotn(XY[2],XY[3],0,Radius)
                maxa = max(maxa, A1, A2)
                mina = min(mina, A1, A2)
            mida = (mina+maxa)/2
            ##########################################
            #         TEXT LEFT JUSTIFY STUFF        #
            ##########################################
            if self.justify.get() == "Left":
                pass
            ##########################################
            #          TEXT CENTERING STUFF          #
            ##########################################
            if self.justify.get() == "Center":
                for line in self.coords:
                    XY = line
                    XY[0],XY[1] = Transform(XY[0],XY[1],mida)
                    XY[2],XY[3] = Transform(XY[2],XY[3],mida)
            ##########################################
            #        TEXT RIGHT JUSTIFY STUFF        #
            ##########################################
            if self.justify.get() == "Right":
                for line in self.coords:
                    XY = line
                    if self.upper.get() == True:
                        XY[0],XY[1] = Transform(XY[0],XY[1],maxa)
                        XY[2],XY[3] = Transform(XY[2],XY[3],maxa)
                    else:
                        XY[0],XY[1] = Transform(XY[0],XY[1],mina)
                        XY[2],XY[3] = Transform(XY[2],XY[3],mina)

        ##########################################
        #    TEXT FLIP / MIRROR STUFF / ANGLE    #
        ##########################################
        mirror_flag = self.mirror.get()
        flip_flag   = self.flip.get()
            
        maxx  = -99991.0
        maxy  = -99992.0
        miny  =  99994.0
        minx  =  99995.0

        if Angle == 0.0:
            if flip_flag:
                miny  =  -font_line_height*YScale
            else:
                maxy  =  font_line_height*YScale
                
        elif (Angle == 90.0) or (Angle == -270.0):
            if not mirror_flag:
                minx  =  -font_line_height*YScale
            else:
                maxx  =  font_line_height*YScale

        elif (Angle == 270.0) or (Angle == -90.0):
            if not mirror_flag:
                maxx  =   font_line_height*YScale
            else:
                minx  =  -font_line_height*YScale

        elif (Angle == 180.0) or (Angle == -180.0):
            if flip_flag:
                maxy  = font_line_height*YScale
            else:
                miny  = -font_line_height*YScale

        maxr2 =  0.0
        for line in self.coords:
            XY = line
            if Angle != 0.0:
                XY[0],XY[1],A1 = self.Rotn(XY[0],XY[1],Angle,0)
                XY[2],XY[3],A2 = self.Rotn(XY[2],XY[3],Angle,0)

            if mirror_flag == True:
                XY[0] = -XY[0]
                XY[2] = -XY[2]
                v_flop  = not(v_flop)

            if flip_flag == True:
                XY[1] = -XY[1]
                XY[3] = -XY[3]
                v_flop = not(v_flop)

            maxx  = max(maxx,  XY[0], XY[2])
            maxy  = max(maxy,  XY[1], XY[3])

            minx  = min(minx,  XY[0], XY[2])
            miny  = min(miny,  XY[1], XY[3])

            maxr2 = max(maxr2, float(XY[0]*XY[0]+XY[1]*XY[1]), float(XY[2]*XY[2]+XY[3]*XY[3]))


        maxx = maxx + Thick/2
        maxy = maxy + Thick/2
        minx = minx - Thick/2
        miny = miny - Thick/2

        midx = (minx+maxx)/2
        midy = (miny+maxy)/2

        #############################
        #   Engrave Box or circle   #
        #############################
        Delta = 0
        Radius_plot = 0
        Thick_Border  =  float(self.STHICK.get() )
        Delta = Thick/2 + float(self.boxgap.get())
        if self.plotbox.get() != "no_box"  and self.cut_type.get() != "v-carve":

            if Radius_in == 0:
                self.coords.append([ minx-Delta, miny-Delta, maxx+Delta, miny-Delta, 0, 0])
                self.coords.append([ maxx+Delta, miny-Delta, maxx+Delta, maxy+Delta, 0, 0])
                self.coords.append([ maxx+Delta, maxy+Delta, minx-Delta, maxy+Delta, 0, 0])
                self.coords.append([ minx-Delta, maxy+Delta, minx-Delta, miny-Delta, 0, 0])
                Delta = Delta + Thick/2
                minx = minx - Delta
                maxx = maxx + Delta
                miny = miny - Delta
                maxy = maxy + Delta
            else:
                Radius_plot = sqrt(maxr2) + Thick + float(self.boxgap.get())
                minx = -Radius_plot - Thick/2
                maxx = -minx
                miny =  minx
                maxy =  maxx
                midx =  0
                midy =  0
                self.RADIUS_PLOT = Radius_plot
                # Don't create the circle coords here a g-code circle command
                # is generated later when not v-carving

        # The ^ operator used on the next line bitwise is XOR
        if (bool(self.v_flop.get()) ^ bool(self.inlay.get())) and (self.cut_type.get() == "v-carve"):

            if (bool(self.mirror.get()) ^ bool(self.flip.get())):
                self.coords.append([ minx-Delta, miny-Delta, minx-Delta, maxy+Delta, 0, 0])
                self.coords.append([ minx-Delta, maxy+Delta, maxx+Delta, maxy+Delta, 0, 0])
                self.coords.append([ maxx+Delta, maxy+Delta, maxx+Delta, miny-Delta, 0, 0])
                self.coords.append([ maxx+Delta, miny-Delta, minx-Delta, miny-Delta, 0, 0])
            else:
                self.coords.append([ minx-Delta, miny-Delta, maxx+Delta, miny-Delta, 0, 0])
                self.coords.append([ maxx+Delta, miny-Delta, maxx+Delta, maxy+Delta, 0, 0])
                self.coords.append([ maxx+Delta, maxy+Delta, minx-Delta, maxy+Delta, 0, 0])
                self.coords.append([ minx-Delta, maxy+Delta, minx-Delta, miny-Delta, 0, 0])


            Delta = Delta + Thick/2
            minx = minx - Delta
            maxx = maxx + Delta
            miny = miny - Delta
            maxy = maxy + Delta

        ##########################################
        #         ORIGIN LOCATING STUFF          #
        ##########################################
        CASE = str(self.origin.get())
        if     CASE == "Top-Left":
            x_zero = minx
            y_zero = maxy
        elif   CASE == "Top-Center":
            x_zero = midx
            y_zero = maxy
        elif   CASE == "Top-Right":
            x_zero = maxx
            y_zero = maxy
        elif   CASE == "Mid-Left":
            x_zero = minx
            y_zero = midy
        elif   CASE == "Mid-Center":
            x_zero = midx
            y_zero = midy
        elif   CASE == "Mid-Right":
            x_zero = maxx
            y_zero = midy
        elif   CASE == "Bot-Left":
            x_zero = minx
            y_zero = miny
        elif   CASE == "Bot-Center":
            x_zero = midx
            y_zero = miny
        elif   CASE == "Bot-Right":
            x_zero = maxx
            y_zero = miny
        elif   CASE == "Arc-Center":
            x_zero = 0
            y_zero = 0
        else:          #"Default"
            x_zero = 0
            y_zero = 0

        cnt=0
        for line in self.coords:
            XY = line
            self.coords[cnt][0] = XY[0] - x_zero + XOrigin
            self.coords[cnt][1] = XY[1] - y_zero + YOrigin
            self.coords[cnt][2] = XY[2] - x_zero + XOrigin
            self.coords[cnt][3] = XY[3] - y_zero + YOrigin
            cnt=cnt+1

        self.MAXX=maxx - x_zero + XOrigin
        self.MINX=minx - x_zero + XOrigin
        self.MAXY=maxy - y_zero + YOrigin
        self.MINY=miny - y_zero + YOrigin


        self.Xzero = x_zero
        self.Yzero = y_zero

        if (not self.batch.get()):
            # Reset Status Bar and Entry Fields
            self.Input.configure(         bg = 'white' )
            self.entry_set(self.Entry_Yscale,  self.Entry_Yscale_Check()  ,1)
            self.entry_set(self.Entry_Xscale,  self.Entry_Xscale_Check()  ,1)
            self.entry_set(self.Entry_Sthick,  self.Entry_Sthick_Check()  ,1)
            self.entry_set(self.Entry_Lspace,  self.Entry_Lspace_Check()  ,1)
            self.entry_set(self.Entry_Cspace,  self.Entry_Cspace_Check()  ,1)
            self.entry_set(self.Entry_Wspace,  self.Entry_Wspace_Check()  ,1)
            self.entry_set(self.Entry_Tangle,  self.Entry_Tangle_Check()  ,1)
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check() ,1)
            self.entry_set(self.Entry_Feed,    self.Entry_Feed_Check()    ,1)
            self.entry_set(self.Entry_Plunge,  self.Entry_Plunge_Check()  ,1)
            self.entry_set(self.Entry_Zsafe,   self.Entry_Zsafe_Check()   ,1)
            self.entry_set(self.Entry_Zcut,    self.Entry_Zcut_Check()    ,1)
            self.entry_set(self.Entry_BoxGap,  self.Entry_BoxGap_Check()  ,1)
            self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),1)

            self.bounding_box.set("Bounding Box (WxH) = "    +
                                   "%.3g" % (maxx-minx)      +
                                   " %s " % self.units.get() +
                                   " x " +
                                   "%.3g" % (maxy-miny)      +
                                   " %s " % self.units.get() +
                                   " %s" % message2)
            self.statusMessage.set(self.bounding_box.get())

        if no_font_record != []:
            if (not self.batch.get()):
                self.statusbar.configure( bg = 'orange' )
            fmessage('Characters not found in font file:',FALSE)
            fmessage("(",FALSE)
            for entry in no_font_record:
                fmessage( "%s," %(entry),FALSE)
            fmessage(")")

        if (not self.batch.get()):
            self.Plot_Data()
        ################
        #   End DoIt   #
        ################

    ##################################################
    def record_v_carve_data(self,x1,y1,phi,rout,loop_cnt, clean_flag):
        rbit = self.calc_vbit_dia() / 2.0

        Lx, Ly = Transform(0,rout,-phi)
        xnormv = x1+Lx
        ynormv = y1+Ly
        need_clean = 0

        if int(clean_flag) != 1:
            self.vcoords.append([xnormv, ynormv, rout, loop_cnt])
            if abs(rout - rbit) < Zero:
                need_clean = 1
        else:
            if rout > rbit:
                self.clean_coords.append([xnormv, ynormv, rout, loop_cnt])

        return xnormv,ynormv,rout,need_clean


    #####################################################
    # determine if a point is inside a given polygon or not
    # Polygon is a list of (x,y) pairs.
    # http://www.ariel.com.au/a/python-point-int-poly.html
    #####################################################
    def point_inside_polygon(self,x,y,poly):
        n = len(poly)
        inside = -1
        p1x = poly[0][0]
        p1y = poly[0][1]
        for i in range(n+1):
            p2x = poly[i%n][0]
            p2y = poly[i%n][1]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = inside * -1
            p1x,p1y = p2x,p2y

        return inside

    def V_Carve_It(self,clean_flag=0):
        global STOP_CALC
        self.master.unbind("<Configure>")
        STOP_CALC=0

        if self.units.get() == "mm":
            if float( self.v_step_len.get() ) <= .01:
                fmessage("v_step_len is very small setting to default metric value of .25 mm")
                self.v_step_len.set("0.25")

        if (self.Check_All_Variables() > 0):
            return
        if (clean_flag != 1 ):
            self.DoIt()
            self.clean_coords = []
            self.clean_coords_sort=[]
            self.v_clean_coords_sort=[]
            self.clean_segment=[]
        elif self.clean_coords_sort != [] or self.v_clean_coords_sort != []:
            # If there is existing cleanup data clear the screen before computing.
            self.clean_coords = []
            self.clean_coords_sort=[]
            self.v_clean_coords_sort=[]
            self.Plot_Data()

        if (not self.batch.get()):
            self.statusbar.configure( bg = 'yellow' )
            self.statusMessage.set('Preparing for V-Carve Calculations')
            self.master.update()

        #########################################
        # V-Carve Stuff
        #########################################
        if self.cut_type.get() == "v-carve" and self.fontdex.get() == False:

            if self.input_type.get() == "text":
                v_flop    =  bool(self.v_flop.get())

                mirror_flag = self.mirror.get()
                flip_flag   = self.flip.get()

                if self.inlay.get() == True:
                    v_flop  = not(v_flop)
                if mirror_flag == True:
                    v_flop  = not(v_flop)
                if flip_flag == True:
                    v_flop = not(v_flop)
            else:
                v_flop = False

            if (not self.batch.get()):
                cszw = int(self.PreviewCanvas.cget("width"))
                cszh = int(self.PreviewCanvas.cget("height"))
                if (self.v_pplot.get() == 1):
                    self.Plot_Data()

            PlotScale = self.pscale
            maxx = self.MAXX
            minx = self.MINX
            maxy = self.MAXY
            miny = self.MINY
            midx=(maxx+minx)/2
            midy=(maxy+miny)/2

            dline       = float(self.v_step_len.get())
            ###############################################################
            rbit        = self.calc_vbit_dia()/2.0
            r_inlay_top = self.calc_r_inlay_top()
            if (clean_flag != 1 ):
                rmax = rbit
            else:
                clean_w = self.calc_clean_width()
                rmax = max(rbit, clean_w/2.0)
            ###############################################################
            v_stp_crner = float(self.v_stp_crner.get())
            if self.inlay.get():
                v_drv_crner = 360 - v_stp_crner
            else:
                v_drv_crner = float(self.v_drv_crner.get())

            Acc         = float(self.accuracy.get())

            CHK_STRING  = str(self.v_check_all.get())
            not_b_carve = not bool(self.bit_shape.get() == "BALL")

            if self.input_type.get() != "text":
                CHK_STRING  = "all"

            BIT_ANGLE   = float(self.v_bit_angle.get())

            dangle = degrees(dline/rbit)
            if dangle < 2.0:
                dangle = 2.0

            ## Reorder
            if ((self.input_type.get() == "image") and (clean_flag != 1)):
                ##########################
                ###   Create ECOORDS   ###
                ##########################
                ecoords = []
                Lbeg=[]
                Lend=[]
                for i in range(len(self.coords)):
                    [x1,y1,x2,y2,dummy1,dummy2]=self.coords[i]
                    if i == 0:
                        cnt=0
                        ecoords.append([x1,y1])
                        Lbeg.append(cnt)
                        cnt = cnt+1
                        ecoords.append([x2,y2])
                        oldx, oldy = x2, y2
                    else:
                        dist = sqrt((oldx - x1)**2 + (oldy - y1)**2)
                        # check and see if we need to move
                        # to a new discontinuous start point
                        if (dist > Zero):
                            Lend.append(cnt)
                            cnt = cnt+1
                            ecoords.append([x1,y1])
                            Lbeg.append(cnt)
                        cnt = cnt+1
                        ecoords.append([x2,y2])
                        oldx, oldy = x2, y2
                Lend.append(cnt)

                ####################
                if (not self.batch.get()):
                    self.statusMessage.set('Checking Input Image Data')
                    self.master.update()
                ######################################################
                ### Fully Close Closed loops and Remove Open Loops ###
                ######################################################
                i = 0
                LObeg = []
                LOend = []
                while i < len(Lbeg): #for each loop
                    [Xstart, Ystart] = ecoords[Lbeg[i]]
                    [Xend,   Yend  ] = ecoords[Lend[i]]

                    dist = sqrt((Xend-Xstart)**2 +(Yend-Ystart)**2)
                    if  dist <= Zero: #if end is the same as the beginning (changed in V1.55: was Acc)
                        ecoords[Lend[i]] = [Xstart, Ystart]
                        i = i+1
                    else:  #end != to beginning
                        LObeg.append(Lbeg.pop(i))
                        LOend.append(Lend.pop(i))

                LNbeg=[]
                LNend=[]
                LNloop=[]
                #######################################################
                ###  For Each open loop connect to the next closest ###
                ###  loop end until all of the loops are closed     ###
                #######################################################
                Lcnt=0
                while len(LObeg) > 0: #for each Open Loop
                    Start = LObeg.pop(0)
                    End   = LOend.pop(0)
                    Lcnt = Lcnt+1
                    LNloop.append(Lcnt)
                    LNbeg.append(Start)
                    LNend.append(End)
                    [Xstart, Ystart] = ecoords[Start]

                    OPEN = True
                    while OPEN == True and len(LObeg) > 0:
                        [Xend,Yend] = ecoords[End]
                        dist_beg_min = sqrt((Xend-Xstart)**2 +(Yend-Ystart)**2)
                        dist_end_min = dist_beg_min
                        k_min_beg = -1
                        k_min_end = -1
                        for k in range(len(LObeg)):
                            [Xkstart, Ykstart] = ecoords[LObeg[k]]
                            [Xkend  ,   Ykend] = ecoords[LOend[k]]
                            dist_beg = sqrt((Xend-Xkstart)**2 +(Yend-Ykstart)**2)
                            dist_end = sqrt((Xend - Xkend)**2 +(Yend - Ykend)**2)

                            if dist_beg < dist_beg_min:
                                dist_beg_min = dist_beg
                                k_min_beg = k
                            if dist_end < dist_end_min:
                                dist_end_min = dist_end
                                k_min_end = k

                        if k_min_beg == -1 and k_min_end == -1:
                            kbeg = End
                            kend = Start
                            ecoords.append(ecoords[End])
                            ecoords.append(ecoords[Start])
                            LNloop.append(Lcnt)
                            LNbeg.append(len(ecoords)-2)
                            LNend.append(len(ecoords)-1)
                            OPEN = False

                        elif dist_end_min < dist_beg_min:
                            kend = LObeg.pop(k_min_end)
                            kbeg = LOend.pop(k_min_end)

                            ecoords.append(ecoords[End])
                            ecoords.append(ecoords[kbeg])

                            LNloop.append(Lcnt)
                            LNbeg.append(len(ecoords)-2)
                            LNend.append(len(ecoords)-1)
                            LNloop.append(Lcnt)
                            LNbeg.append(kbeg)
                            LNend.append(kend)
                            End  = kend
                        else:
                            kbeg = LObeg.pop(k_min_beg)
                            kend = LOend.pop(k_min_beg)

                            ecoords.append(ecoords[End])
                            ecoords.append(ecoords[kbeg])

                            LNloop.append(Lcnt)
                            LNbeg.append(len(ecoords)-2)
                            LNend.append(len(ecoords)-1)
                            LNloop.append(Lcnt)
                            LNbeg.append(kbeg)
                            LNend.append(kend)
                            End  = kend

                    if OPEN == True and len(LObeg) == 0:
                        ecoords.append(ecoords[End])
                        ecoords.append(ecoords[Start])
                        LNloop.append(Lcnt)
                        LNbeg.append(len(ecoords)-2)
                        LNend.append(len(ecoords)-1)

                ###########################################################
                ### Make new sequential ecoords for each new loop       ###
                ###########################################################
                Loop_last = -1
                for k in range(len(LNbeg)):
                    Start = LNbeg[k]
                    End   = LNend[k]
                    Loop  = LNloop[k]
                    if Loop != Loop_last:
                        Lbeg.append(len(ecoords))

                        if Loop_last != -1:
                            Lend.append(len(ecoords)-1)
                        Loop_last = Loop

                    if Start > End:
                        step = -1
                    else:
                        step = 1
                    for i in range(Start,End+step,step):
                        [x1,y1]   = ecoords[i]
                        ecoords.append([x1,y1])
                if len(Lbeg) > len(Lend):
                    Lend.append(len(ecoords)-1)

                ###########################################
                ###   Determine loop directions CW/CCW  ###
                ###########################################
                if (not self.batch.get()):
                    self.statusMessage.set('Calculating Initial Loop Directions (CW/CCW)')
                    self.master.update()
                Lflip = []
                Lcw   = []

                for k in range(len(Lbeg)):
                    Start = Lbeg[k]
                    End   = Lend[k]
                    step = 1

                    signedArea=0.0

                    [x1,y1]   = ecoords[Start]
                    for i in range(Start+1,End+step,step):
                        [x2,y2]   = ecoords[i]
                        signedArea += (x2-x1)*(y2+y1)
                        x1=x2
                        y1=y2
                    if signedArea > 0.0:
                        Lflip.append(False)
                        Lcw.append(True)
                    else:
                        Lflip.append(True)
                        Lcw.append(False)

                Nloops = len(Lbeg)
                LoopTree=[]
                Lnum=[]
                for iloop in range(Nloops):
                    LoopTree.append([iloop,[],[]])
                    Lnum.append(iloop)

                #####################################################
                # For each loop determine if other loops are inside #
                #####################################################
                for iloop in range(Nloops):
                    CUR_PCT=float(iloop)/Nloops*100.0
                    if (not self.batch.get()):
                        self.statusMessage.set('Determining Which Side of Loop to Cut: %d of %d' %(iloop+1,Nloops))
                        self.master.update()
                    ipoly = ecoords[Lbeg[iloop]:Lend[iloop]]

                    ## Check points in other loops (could just check one) ##
                    if ipoly != []:
                        for jloop in range(Nloops):
                            if jloop != iloop:
                                inside = 0
                                #for jval in range(Lbeg[jloop],Lend[jloop]):
                                #    inside = inside + self.point_inside_polygon(ecoords[jval][0],ecoords[jval][1],ipoly)
                                jval = Lbeg[jloop]
                                inside = inside + self.point_inside_polygon(ecoords[jval][0],ecoords[jval][1],ipoly)
                                if inside > 0:
                                    Lflip[jloop] = not Lflip[jloop]
                                    LoopTree[iloop][1].append(jloop)
                                    LoopTree[jloop][2].append(iloop)

                #####################################################
                # Set Loop clockwise flag to the state of each loop #
                #####################################################
                # could flip cut side here for auto side determination
                for iloop in range(Nloops):
                    if Lflip[iloop]:
                        Lcw[iloop]=not Lcw[iloop]

                CUR_PCT = 0.0
                #################################################
                # Find new order based on distance to next beg  #
                #################################################
                if (not self.batch.get()):
                    self.statusMessage.set('Re-Ordering Loops')
                    self.master.update()
                order_out = []
                if len(Lflip)>0:
                    if Lflip[0]:
                        order_out.append([ Lend[0], Lbeg[0], Lnum[0] ])
                    else:
                        order_out.append([ Lbeg[0], Lend[0], Lnum[0] ])

                inext = 0
                total=len(Lbeg)
                for i in range(total-1):
                    Lbeg.pop(inext)
                    ii = Lend.pop(inext)
                    Lflip.pop(inext)
                    Lnum.pop(inext)

                    Xcur = ecoords[ii][0]
                    Ycur = ecoords[ii][1]

                    dx = Xcur - ecoords[ Lbeg[0] ][0]
                    dy = Ycur - ecoords[ Lbeg[0] ][1]
                    min_dist = dx*dx + dy*dy

                    inext=0
                    for j in range(1,len(Lbeg)):
                        dx = Xcur - ecoords[ Lbeg[j] ][0]
                        dy = Ycur - ecoords[ Lbeg[j] ][1]
                        dist = dx*dx + dy*dy
                        if dist < min_dist:
                            min_dist=dist
                            inext=j

                    if Lflip[inext]:
                        order_out.append([ Lend[inext], Lbeg[inext], Lnum[inext] ])
                    else:
                        order_out.append([ Lbeg[inext], Lend[inext], Lnum[inext] ])

                ###########################################################
                temp_coords=[]
                for k in range(len(order_out)):
                    [Start,End, LN] = order_out[k]
                    if Start > End:
                        step = -1
                    else:
                        step = 1
                    xlast = ""
                    ylast = ""
                    for i in range(Start+step,End+step,step):
                        if xlast != "" and ylast != "":
                            x1 = xlast
                            y1 = ylast
                        else:
                            [x1,y1] = ecoords[i-step]
                        [x2,y2] = ecoords[i]

                        Lseg = sqrt((x2-x1)**2 + (y2-y1)**2)
                        if Lseg >= Acc:
                            temp_coords.append([x1,y1,x2,y2,LN,0])
                            xlast = ""
                            ylast = ""
                        else:
                            last_segment = [x1,y1,x2,y2,LN,0]
                            xlast = x1
                            ylast = y1
                    if  xlast != "" and  ylast != "":
                        temp_coords.append(last_segment)

                self.coords = temp_coords

                for ijunk in range(len(self.coords)):
                    self.coords[ijunk][4]=0
                    self.coords[ijunk][5]=0

            ##########################################################################

            #set variable for first point in loop
            xa = 9999
            ya = 9999
            xb = 9999
            yb = 9999
            #set variable for the point previously calculated in a loop
            x0=9999
            y0=9999
            seg_sin0 = 2
            seg_cos0 = 2
            char_num0 = -1
            theta = 9999.0
            loop_cnt = 0
            if not v_flop:
                v_inc = 1
                v_index = -1
                i_x1 = 0
                i_y1 = 1
                i_x2 = 2
                i_y2 = 3
            else:
                v_inc = -1
                v_index = len(self.coords)
                i_x1 = 2
                i_y1 = 3
                i_x2 = 0
                i_y2 = 1

            coord_radius=[]
            #########################
            # Setup Grid Partitions #
            #########################
            xLength = self.MAXX-self.MINX
            yLength = self.MAXY-self.MINY

            xN=0
            yN=0

            xN_minus_1 = max(int(xLength/((2*rmax+dline)*1.1)),1)
            yN_minus_1 = max(int(yLength/((2*rmax+dline)*1.1)),1)

            xPartitionLength=xLength/xN_minus_1
            yPartitionLength=yLength/yN_minus_1

            xN = xN_minus_1+1
            yN = yN_minus_1+1

            if (xPartitionLength<Zero):
                xPartitionLength=1
            if (yPartitionLength<Zero):
                yPartitionLength=1
            self.xPartitionLength = xPartitionLength
            self.yPartitionLength = yPartitionLength

            self.partitionList = []

            for xCount in range(0,xN):
                self.partitionList.append([])
                for yCount in range(0,yN):
                    self.partitionList[xCount].append([])

            ###############################
            # End Setup Grid Partitions   #
            ###############################

            CUR_CNT=-1
            while (len(self.coords) > CUR_CNT+1):
                CUR_CNT=CUR_CNT+1
                XY_R = self.coords[CUR_CNT][:]
                x1_R = XY_R[0]
                y1_R = XY_R[1]
                x2_R = XY_R[2]
                y2_R = XY_R[3]
                LENGTH = sqrt( (x2_R-x1_R)*(x2_R-x1_R) + (y2_R-y1_R)*(y2_R-y1_R) )
                
                R_R = LENGTH/2 + rmax
                X_R = (x1_R + x2_R)/2
                Y_R = (y1_R + y2_R)/2
                coord_radius.append([X_R, Y_R, R_R])

                #####################################################
                # Determine active partitions for each line segment #
                #####################################################
                coded_index=[]
                ## find the local coordinates of the line segment ends
                x1_G = XY_R[0]-self.MINX
                y1_G = XY_R[1]-self.MINY
                x2_G = XY_R[2]-self.MINX
                y2_G = XY_R[3]-self.MINY

                ## Find the grid box index for each line segment end
                X1i = int( x1_G / xPartitionLength )
                X2i = int( x2_G / xPartitionLength )
                Y1i = int( y1_G / yPartitionLength )
                Y2i = int( y2_G / yPartitionLength )

                ## Find the max/min grid box locations
                Xindex_min = min(X1i,X2i)
                Xindex_max = max(X1i,X2i)
                Yindex_min = min(Y1i,Y2i)
                Yindex_max = max(Y1i,Y2i)

                check_points=[]
                if (Xindex_max > Xindex_min) and (abs(x2_G-x1_G) > Zero):
                    if (Yindex_max > Yindex_min) and (abs(y2_G-y1_G) > Zero):
                        check_points.append([X1i,Y1i])
                        check_points.append([X2i,Y2i])
                        ## Establish line equation variables: y=m*x+b
                        m_G = (y2_G-y1_G)/(x2_G-x1_G)
                        b_G = y1_G - m_G*x1_G
                        ## Add check point in each partition in the range of X values
                        x_ind_check = Xindex_min+1
                        while x_ind_check <= Xindex_max-1:
                            x_val = x_ind_check * xPartitionLength
                            y_val = m_G * x_val + b_G
                            y_ind_check = int(y_val/yPartitionLength)
                            check_points.append([x_ind_check,y_ind_check])
                            x_ind_check = x_ind_check + 1
                        ## Add check point in each partition in the range of Y values
                        y_ind_check = Yindex_min+1
                        while y_ind_check <= Yindex_max-1:
                            y_val =  y_ind_check * yPartitionLength
                            x_val = (y_val-b_G ) / m_G
                            x_ind_check = int(x_val/xPartitionLength)
                            check_points.append([x_ind_check,y_ind_check])
                            y_ind_check = y_ind_check + 1
                    else:
                        x_ind_check = Xindex_min
                        y_ind_check = Yindex_min
                        while x_ind_check <= Xindex_max:
                            check_points.append([x_ind_check,y_ind_check])
                            x_ind_check = x_ind_check + 1
                else:
                    x_ind_check = Xindex_min
                    y_ind_check = Yindex_min
                    while y_ind_check <= Yindex_max:
                        check_points.append([x_ind_check,y_ind_check])
                        y_ind_check = y_ind_check + 1

                ## For each grid box in check_points add the grid box and all adjacent grid boxes
                ## to the list of boxes for this line segment
                for xy_point in check_points:
                    xy_p = xy_point
                    xIndex = xy_p[0]
                    yIndex = xy_p[1]
                    for i in range( max(xIndex-1,0), min(xN,xIndex+2) ):
                        for j in range( max(yIndex-1,0), min(yN,yIndex+2) ):
                            coded_index.append(int(i+j*xN))

                codedIndexSet= set(coded_index)
                
                for thisCode in codedIndexSet:
                    thisIndex = thisCode
                    line_R_appended = XY_R
                    line_R_appended.append(X_R)
                    line_R_appended.append(Y_R)
                    line_R_appended.append(R_R)
                    self.partitionList[int(thisIndex%xN)][int(thisIndex/xN)].append(line_R_appended)
            #########################################################
            # End Determine active partitions for each line segment #
            #########################################################
            ## Loop through again just to determine the total length of segments
            ## For the percent complete calculation
            if (v_index >= len(self.coords)):
                v_index = len(self.coords)
            v_ind = v_index

            CUR_CNT=-1
            TOT_LENGTH = 0.0

            for line in range(len(self.coords)):
                CUR_CNT=CUR_CNT+1
                v_ind = v_ind + v_inc
                x1 = self.coords[v_ind][i_x1]
                y1 = self.coords[v_ind][i_y1]
                x2 = self.coords[v_ind][i_x2]
                y2 = self.coords[v_ind][i_y2]
                LENGTH = sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) )
                if clean_flag == 1:
                    if self.clean_segment[CUR_CNT] != 0:
                        TOT_LENGTH = TOT_LENGTH + LENGTH
                else:
                    TOT_LENGTH = TOT_LENGTH + LENGTH

            CUR_LENGTH = 0.0
            MAX_CNT = len(self.coords)
            CUR_CNT = -1
            START_TIME=time()

            ################################################################################################################
            ################################################################################################################
            ################################################################################################################
            #Update canvas with modified paths
            if (not self.batch.get()):
                self.Plot_Data()

            if TOT_LENGTH > 0.0:
                calc_flag=1
                for line in range(len(self.coords)):
                    CUR_CNT=CUR_CNT+1
                    ####################################################
                    if clean_flag == 0:
                        self.clean_segment.append(0)
                    elif len(self.clean_segment) != len(self.coords):
                        fmessage("Need to Recalculate V-Carve Path")
                        break
                    else:
                        calc_flag = self.clean_segment[CUR_CNT]
                    ####################################################
                    CUR_PCT=float(CUR_LENGTH)/TOT_LENGTH*100.0
                    if CUR_PCT > 0.0:
                        MIN_REMAIN =( time()-START_TIME )/60 * (100-CUR_PCT)/CUR_PCT
                        MIN_TOTAL = 100.0/CUR_PCT * ( time()-START_TIME )/60
                    else:
                        MIN_REMAIN = -1
                        MIN_TOTAL = -1
                    if (not self.batch.get()):
                        self.statusMessage.set('%.1f %% ( %.1f Minutes Remaining | %.1f Minutes Total )' %( CUR_PCT, MIN_REMAIN, MIN_TOTAL ) )
                        self.statusbar.configure( bg = 'yellow' )
                        self.PreviewCanvas.update()

                    if STOP_CALC != 0:
                        STOP_CALC=0

                        if (clean_flag != 1 ):
                            self.vcoords = []
                        else:
                            self.clean_coords = []
                            calc_flag = 0
                        break

                    v_index = v_index + v_inc
                    New_Loop=0
                    x1 = self.coords[v_index][i_x1]
                    y1 = self.coords[v_index][i_y1]
                    x2 = self.coords[v_index][i_x2]
                    y2 = self.coords[v_index][i_y2]
                    char_num = int(self.coords[v_index][5])
                    dx = x2-x1
                    dy = y2-y1
                    Lseg = sqrt(dx*dx + dy*dy)
                    if calc_flag != 0:
                        CUR_LENGTH = CUR_LENGTH + Lseg
                    else:
                        continue

                    if Lseg < Zero: #was Acc
                        continue

                    #calculate the sin and cos of the coord transformation needed for
                    #the distance calculations
                    seg_sin =  dy/Lseg
                    seg_cos = -dx/Lseg
                    phi = Get_Angle(seg_sin,seg_cos)
                    if (fabs(x1-x0) > Zero or fabs(y1-y0) > Zero) or char_num != char_num0:
                        New_Loop=1
                        loop_cnt=loop_cnt+1
                        xa = float(x1)
                        ya = float(y1)
                        xb = float(x2)
                        yb = float(y2)
                        theta = 9999.0
                        seg_sin0 = 2
                        seg_cos0 = 2

                    if seg_cos0 > 1.0:
                        delta = 180
                    else:
                        xtmp1 = (x2-x1) * seg_cos0 - (y2-y1) * seg_sin0
                        ytmp1 = (x2-x1) * seg_sin0 + (y2-y1) * seg_cos0
                        Ltmp=sqrt( xtmp1*xtmp1 + ytmp1*ytmp1 )
                        d_seg_sin =   ytmp1/Ltmp
                        d_seg_cos =   xtmp1/Ltmp
                        delta = Get_Angle(d_seg_sin,d_seg_cos)
                    if delta < float(v_drv_crner) and BIT_ANGLE !=0 and not_b_carve and clean_flag != 1:
                        #drive to corner
                        self.vcoords.append([x1, y1, 0.0, loop_cnt])

                    if delta > float(v_stp_crner):
                       #add sub-steps around corner
                       ###########################
                       phisteps = max(floor((delta-180)/dangle),2)
                       step_phi = (delta-180)/phisteps
                       pcnt = 0
                       while pcnt < phisteps-1:
                           pcnt=pcnt+1
                           sub_phi =  radians( -pcnt*step_phi + theta )
                           sub_seg_cos = cos(sub_phi)
                           sub_seg_sin = sin(sub_phi)

                           rout = self.find_max_circle(x1,y1,rmax,char_num,sub_seg_sin,sub_seg_cos,1,CHK_STRING)
                           xv,yv,rv,clean_seg=self.record_v_carve_data(x1,y1,sub_phi,rout,loop_cnt,clean_flag)
                           self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                           if self.v_pplot.get() == 1 and (not self.batch.get()) and (clean_flag != 1 ):
                               self.Plot_Circ(xv,yv,midx,midy,cszw,cszh,PlotScale,"blue",rv,0)
                       #############################
                    ### end for linec in self.coords
                    theta = phi
                    x0=x2
                    y0=y2
                    seg_sin0=seg_sin
                    seg_cos0=seg_cos
                    char_num0=char_num

                    #Calculate the number of steps then the dx and dy for each step
                    #Don't calculate at the joints.
                    nsteps = max(floor(Lseg/dline),2)
                    dxpt = dx/nsteps
                    dypt = dy/nsteps

                    ### This makes sure the first cut start at the begining of the first segment
                    cnt = 0
                    if New_Loop == 1 and BIT_ANGLE !=0 and not_b_carve:
                        cnt = -1

                    seg_sin =  dy/Lseg
                    seg_cos = -dx/Lseg
                    phi2 = radians(Get_Angle(seg_sin,seg_cos))
                    while cnt < nsteps-1:
                        cnt=cnt+1
                        #determine location of next step along outline (xpt, ypt)
                        xpt = x1 + dxpt * cnt
                        ypt = y1 + dypt * cnt

                        rout = self.find_max_circle(xpt,ypt,rmax,char_num,seg_sin,seg_cos,0,CHK_STRING)
                        # Make the first cut drive down at an angle instead of straight down plunge
                        if cnt==0 and not_b_carve:
                            rout = 0.0
                        xv,yv,rv,clean_seg=self.record_v_carve_data(xpt,ypt,phi2,rout,loop_cnt,clean_flag)

                        self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                        if self.v_pplot.get() == 1 and (not self.batch.get()) and (clean_flag != 1 ):
                            self.master.update_idletasks()
                            self.Plot_Circ(xv,yv,midx,midy,cszw,cszh,PlotScale,"blue",rv,0)

                        if (New_Loop==1 and cnt==1):
                            xpta  = xpt
                            ypta  = ypt
                            phi2a = phi2
                            routa = rout

                    #################################################
                    # Check to see if we need to close an open loop
                    #################################################
                    if (abs(x2-xa) < Acc and abs(y2-ya) < Acc):
                        xtmp1 = (xb-xa) * seg_cos0 - (yb-ya) * seg_sin0
                        ytmp1 = (xb-xa) * seg_sin0 + (yb-ya) * seg_cos0
                        Ltmp=sqrt( xtmp1*xtmp1 + ytmp1*ytmp1 )
                        d_seg_sin =   ytmp1/Ltmp
                        d_seg_cos =   xtmp1/Ltmp
                        delta = Get_Angle(d_seg_sin,d_seg_cos)
                        if delta < v_drv_crner and clean_flag != 1:
                            #drive to corner
                            self.vcoords.append([xa, ya, 0.0, loop_cnt])

                        elif delta > v_stp_crner:
                            #add substeps around corner
                            phisteps = max(floor((delta-180)/dangle),2)
                            step_phi = (delta-180)/phisteps
                            pcnt = 0

                            while pcnt < phisteps-1:
                                pcnt=pcnt+1
                                sub_phi =  radians( -pcnt*step_phi + theta )
                                sub_seg_cos = cos(sub_phi)
                                sub_seg_sin = sin(sub_phi)

                                rout = self.find_max_circle(xa,ya,rmax,char_num,sub_seg_sin,sub_seg_cos,1,CHK_STRING)
                                xv,yv,rv,clean_seg = self.record_v_carve_data(xa,ya,sub_phi,rout,loop_cnt,clean_flag)
                                self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                                if (self.v_pplot.get() == 1) and (not self.batch.get()) and (clean_flag != 1 ):
                                    self.Plot_Circ(xv,yv,midx,midy,cszw,cszh,PlotScale,"blue",rv,0)

                            xv,yv,rv,clean_seg = self.record_v_carve_data(xpta,ypta,phi2a,routa,loop_cnt,clean_flag)
                            self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)
                        else:
                            # Add closing segment
                            xv,yv,rv,clean_seg = self.record_v_carve_data(xpta,ypta,phi2a,routa,loop_cnt,clean_flag)
                            self.clean_segment[CUR_CNT] = bool(self.clean_segment[CUR_CNT]) or bool(clean_seg)

                #end for line in self coords


                #Reset Entry Fields in V-Carve Settings
                if (not self.batch.get()):
                    self.entry_set(self.Entry_Vbitangle,   self.Entry_Vbitangle_Check()   ,1)
                    self.entry_set(self.Entry_Vbitdia,     self.Entry_Vbitdia_Check()     ,1)
                    self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check() ,1)
                    self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check() ,1)
                    self.entry_set(self.Entry_OutsideAngle,self.Entry_OutsideAngle_Check(),1)
                    self.entry_set(self.Entry_StepSize,    self.Entry_StepSize_Check()    ,1)
                    self.entry_set(self.Entry_Allowance,   self.Entry_Allowance_Check()   ,1)
                    self.entry_set(self.Entry_Accuracy,    self.Entry_Accuracy_Check()    ,1)
                    self.entry_set(self.Entry_CLEAN_DIA,   self.Entry_CLEAN_DIA_Check()   ,1)
                    self.entry_set(self.Entry_STEP_OVER,   self.Entry_STEP_OVER_Check()   ,1)
                    self.entry_set(self.Entry_V_CLEAN,     self.Entry_V_CLEAN_Check()     ,1)


            if CUR_CNT==MAX_CNT-1 and (not self.batch.get()):
                self.statusMessage.set('Done -- ' + self.bounding_box.get())
                self.statusbar.configure( bg = 'white' )
            ################################################################################################################
            ################################################################################################################
            ################################################################################################################

        self.master.bind("<Configure>", self.Master_Configure)
        #########################################
        # End V-Carve Stuff
        #########################################


    def Find_Paths(self,check_coords_in,clean_dia,Radjust,clean_step,skip,direction):
        check_coords=[]


        if direction == "Y":
            cnt = -1
            for line in check_coords_in:
                cnt=cnt+1
                XY=line
                check_coords.append([XY[1],XY[0],XY[2]])
        else:
            check_coords=check_coords_in

        minx_c=0
        maxx_c=0
        miny_c=0
        maxy_c=0
        if len(check_coords) > 0:
            minx_c = check_coords[0][0]-check_coords[0][2]
            maxx_c = check_coords[0][0]+check_coords[0][2]
            miny_c = check_coords[0][1]-check_coords[0][2]
            maxy_c = check_coords[0][1]+check_coords[0][2]
        for line in check_coords:
            XY    = line
            minx_c = min(minx_c, XY[0]-XY[2] )
            maxx_c = max(maxx_c, XY[0]+XY[2] )
            miny_c = min(miny_c, XY[1]-XY[2] )
            maxy_c = max(maxy_c, XY[1]+XY[2] )

        DX = clean_dia*clean_step
        DY = DX
        Xclean_coords=[]
        Xclean_coords_short=[]

        if direction != "None":
            #########################################################################
            # Find ends of horizontal lines for carving clean-up
            #########################################################################
            loop_cnt=0
            Y = miny_c
            line_cnt = skip-1
            while Y <= maxy_c:
                line_cnt = line_cnt+1
                X  = minx_c
                x1 = X
                x2 = X
                x1_old = x1
                x2_old = x2

                # Find relevant clean_coord_data
                ################################
                temp_coords=[]
                for line in check_coords:
                    XY=line
                    if Y < XY[1]+XY[2] and Y > XY[1]-XY[2]:
                        temp_coords.append(XY)
                ################################

                while X <= maxx_c:
                    for line in temp_coords:
                        XY=line
                        h = XY[0]
                        k = XY[1]
                        R = XY[2]-Radjust
                        dist=sqrt((X-h)**2 + (Y-k)**2)
                        if dist <= R:
                            Root = sqrt(R**2 - (Y-k)**2)
                            XL = h-Root
                            XR = h+Root
                            if XL < x1:
                                x1 = XL
                            if XR > x2:
                                x2 = XR
                    if x1==x2:
                        X  = X+DX
                        x1 = X
                        x2 = X
                    elif (x1 == x1_old) and (x2 == x2_old):
                        loop_cnt=loop_cnt+1
                        Xclean_coords.append([x1,Y,loop_cnt])
                        Xclean_coords.append([x2,Y,loop_cnt])
                        if line_cnt == skip:
                            Xclean_coords_short.append([x1,Y,loop_cnt])
                            Xclean_coords_short.append([x2,Y,loop_cnt])

                        X  = X+DX
                        x1 = X
                        x2 = X
                    else:
                        X = x2
                    x1_old = x1
                    x2_old = x2
                if line_cnt == skip:
                    line_cnt = 0
                Y=Y+DY
            #########################################################################


        Xclean_coords_out=[]
        Xclean_coords_short_out=[]
        if direction == "Y":

            cnt = -1
            for line in Xclean_coords:
                cnt=cnt+1
                XY=line
                Xclean_coords_out.append([XY[1],XY[0],XY[2]])

            cnt = -1
            for line in Xclean_coords_short:
                cnt=cnt+1
                XY=line
                Xclean_coords_short_out.append([XY[1],XY[0],XY[2]])
        else:
            Xclean_coords_out=Xclean_coords
            Xclean_coords_short_out=Xclean_coords_short

        return Xclean_coords_out,Xclean_coords_short_out


    def Clean_Path_Calc(self,bit_type="straight"):
        #######################################
        #reorganize clean_coords              #
        #######################################
        if bit_type=="straight":
            test_clean = self.clean_P.get()   + self.clean_X.get()   + self.clean_Y.get()
        else:
            test_clean = self.v_clean_P.get() + self.v_clean_Y.get() + self.v_clean_X.get()

        rbit = self.calc_vbit_dia() / 2.0

        clean_w = self.calc_clean_width()
        #clean_w   = float(self.clean_w.get())
        check_coords=[]

        self.statusbar.configure( bg = 'yellow' )
        if bit_type=="straight":
            self.statusMessage.set('Calculating Cleanup Cut Paths')
            self.master.update()
            self.clean_coords_sort   = []

            input_step_over = float(self.clean_step.get()) #percent of cut DIA
            min_step_over = 25 #percent of cut DIA
            skip = ceil(input_step_over/min_step_over)
            step_over = input_step_over/skip

            clean_dia = float(self.clean_dia.get()) #diameter of cleanup bit
            clean_step = step_over/100.0
            Radjust   = clean_dia/2.0 + rbit
            check_coords = self.clean_coords

        elif bit_type == "v-bit":
            skip = 1
            clean_step = 1.0
            self.statusMessage.set('Calculating V-Bit Cleanup Cut Paths')
            self.master.update()
            self.v_clean_coords_sort = []

            clean_dia  = float(self.clean_v.get())*2.0  #effective diameter of clean-up v-bit
            if float(clean_dia) < Zero:
                return
            # We could add something to the readjust line to let the cutter go closer
            # to the limit but avoid contact with the previously v-carved surface.
            Radjust   = clean_dia/2.0 + rbit
            flat_clean_r = float(self.clean_dia.get())/2.0 #diameter of cleanup bit
            for line in self.clean_coords:
                XY    = line
                R = XY[2]-Radjust
                if (R > 0.0) and (R < flat_clean_r):
                    check_coords.append(XY)


        if self.cut_type.get() == "v-carve" and len(self.clean_coords) > 1 and test_clean > 0:
            DX = clean_dia*clean_step
            DY = DX

            if bit_type=="straight":
                MAXD=clean_dia
            else:
                MAXD=sqrt(DX**2+DY**2)*1.1

            Xclean_coords=[]
            Yclean_coords=[]
            clean_coords_out=[]

            if test_clean > 0:
                #########################################################################
                # Find ends of horizontal lines for carving clean-up
                #########################################################################
                Xclean_perimeter,Xclean_coords = self.Find_Paths(check_coords,clean_dia,Radjust,clean_step,skip,"X")

                #########################################################################
                # Find ends of Vertical lines for carving clean-up
                #########################################################################
                Yclean_perimeter,Yclean_coords = self.Find_Paths(check_coords,clean_dia,Radjust,clean_step,skip,"Y")

                loop_cnt = 0
                #######################################################
                # Find new order based on distance                    #
                #######################################################
                if (self.clean_P.get() == 1 and bit_type != "v-bit") or \
                   (self.v_clean_P.get() == 1 and bit_type == "v-bit"):

                    ########################################
                    ecoords=[]
                    for line in Xclean_perimeter:
                        XY=line
                        ecoords.append([XY[0],XY[1]])

                    for line in Yclean_perimeter:
                        XY=line
                        ecoords.append([XY[0],XY[1]])

                    ################
                    ###   ends   ###
                    ################
                    Lbeg=[]
                    for i in range(1,len(ecoords)):
                        Lbeg.append(i)

                    ########################################
                    order_out = []
                    if len(ecoords)>0:
                        order_out.append(Lbeg[0])
                    inext = 0
                    total=len(Lbeg)
                    for i in range(total-1):
                        ii=Lbeg.pop(inext)
                        Xcur = ecoords[ii][0]
                        Ycur = ecoords[ii][1]
                        dx = Xcur - ecoords[ Lbeg[0] ][0]
                        dy = Ycur - ecoords[ Lbeg[0] ][1]
                        min_dist = dx*dx + dy*dy

                        inext=0
                        for j in range(1,len(Lbeg)):
                            dx = Xcur - ecoords[ Lbeg[j] ][0]
                            dy = Ycur - ecoords[ Lbeg[j] ][1]
                            dist = dx*dx + dy*dy
                            if dist < min_dist:
                                min_dist=dist
                                inext=j
                        order_out.append(Lbeg[inext])
                    ###########################################################
                    x_start_loop = -8888
                    y_start_loop = -8888
                    x_old=-999
                    y_old=-999
                    loop_cnt=1
                    for i in order_out:
                        x1   = ecoords[i][0]
                        y1   = ecoords[i][1]
                        dx = x1-x_old
                        dy = y1-y_old
                        dist = sqrt(dx*dx + dy*dy)
                        if dist > MAXD:
                            dx = x_start_loop-x_old
                            dy = y_start_loop-y_old
                            dist = sqrt(dx*dx + dy*dy)
                            if dist < MAXD:
                                clean_coords_out.append([x_start_loop,y_start_loop,clean_dia/2,loop_cnt])
                            loop_cnt=loop_cnt+1
                            x_start_loop=x1
                            y_start_loop=y1
                        clean_coords_out.append([x1,y1,clean_dia/2,loop_cnt])
                        x_old=x1
                        y_old=y1

                ###########################################################
                # Now deal with the horizontal line cuts
                ###########################################################
                if (self.clean_X.get() == 1 and bit_type != "v-bit") or \
                   (self.v_clean_X.get() == 1 and bit_type == "v-bit"):
                    x_old=-999
                    y_old=-999
                    order_out=self.Sort_Paths(Xclean_coords)
                    loop_old=-1
                    for line in order_out:
                        temp=line
                        if temp[0] > temp[1]:
                            step = -1
                        else:
                            step = 1
                        for i in range(temp[0],temp[1]+step,step):
                            x1   = Xclean_coords[i][0]
                            y1   = Xclean_coords[i][1]
                            loop = Xclean_coords[i][2]
                            dx = x1-x_old
                            dy = y1-y_old
                            dist = sqrt(dx*dx + dy*dy)
                            if dist > MAXD and loop != loop_old:
                                loop_cnt=loop_cnt+1
                            clean_coords_out.append([x1,y1,clean_dia/2,loop_cnt])
                            x_old=x1
                            y_old=y1
                            loop_old=loop


                ###########################################################
                # Now deal with the vertical line cuts
                ###########################################################
                if (self.clean_Y.get() == 1 and bit_type != "v-bit") or \
                   (self.v_clean_Y.get() == 1 and bit_type == "v-bit"):
                    x_old=-999
                    y_old=-999
                    order_out=self.Sort_Paths(Yclean_coords)
                    loop_old=-1
                    for line in order_out:
                        temp=line
                        if temp[0] > temp[1]:
                            step = -1
                        else:
                            step = 1
                        for i in range(temp[0],temp[1]+step,step):
                            x1   = Yclean_coords[i][0]
                            y1   = Yclean_coords[i][1]
                            loop = Yclean_coords[i][2]
                            dx = x1-x_old
                            dy = y1-y_old
                            dist = sqrt(dx*dx + dy*dy)
                            if dist > MAXD and loop != loop_old:
                                loop_cnt=loop_cnt+1
                            clean_coords_out.append([x1,y1,clean_dia/2,loop_cnt])
                            x_old=x1
                            y_old=y1
                            loop_old=loop


            self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check()     ,1)
            self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check()     ,1)
            self.entry_set(self.Entry_V_CLEAN,     self.Entry_V_CLEAN_Check()     ,1)

            if bit_type=="v-bit":
                self.v_clean_coords_sort = clean_coords_out
            else:
                self.clean_coords_sort = clean_coords_out
        self.statusMessage.set('Done Calculating Cleanup Cut Paths')
        self.statusbar.configure( bg = 'white' )
        self.master.update_idletasks()
        #######################################
        #End Reorganize                       #
        #######################################


    ################################################################################
    #                         Bitmap Settings Window                              #
    ################################################################################
    #Algorithm options:
    # -z, --turnpolicy policy    - how to resolve ambiguities in path decomposition
    # -t, --turdsize n           - suppress speckles of up to this size (default 2)
    # -a, --alphama n           - corner threshold parameter (default 1)
    # -n, --longcurve            - turn off curve optimization
    # -O, --opttolerance n       - curve optimization tolerance (default 0.2)
    def PBM_Settings_Window(self):
        pbm_settings = Toplevel(width=525, height=250)
        pbm_settings.grab_set() # Use grab_set to prevent user input in the main window during calculations
        pbm_settings.resizable(0,0)
        pbm_settings.title('Bitmap Settings')
        pbm_settings.iconname("Bitmap Settings")

        D_Yloc  = 12
        D_dY = 24
        xd_label_L = 12

        w_label=100
        w_entry=60
        w_units=35
        xd_entry_L=xd_label_L+w_label+10
        xd_units_L=xd_entry_L+w_entry+5

        D_Yloc=D_Yloc+D_dY
        self.Label_BMPturnpol = Label(pbm_settings,text="Turn Policy")
        self.Label_BMPturnpol.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)


        self.BMPturnpol_OptionMenu = OptionMenu(pbm_settings, self.bmp_turnpol,
                                                    "black",
                                                    "white",
                                                    "right",
                                                     "left",
                                                     "minority",
                                                     "majority",
                                                     "random")
        self.BMPturnpol_OptionMenu.place(x=xd_entry_L, y=D_Yloc, width=w_entry+40, height=23)

        D_Yloc=D_Yloc+D_dY
        self.Label_BMPturdsize = Label(pbm_settings,text="Turd Size")
        self.Label_BMPturdsize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPturdsize = Entry(pbm_settings,width="15")
        self.Entry_BMPturdsize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPturdsize.configure(textvariable=self.bmp_turdsize)
        self.bmp_turdsize.trace_variable("w", self.Entry_BMPturdsize_Callback)
        self.Label_BMPturdsize2 = Label(pbm_settings,text="Suppress speckles of up to this pixel size")
        self.Label_BMPturdsize2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(),2)

        D_Yloc=D_Yloc+D_dY+5
        self.Label_BMPalphamax = Label(pbm_settings,text="Alpha Max")
        self.Label_BMPalphamax.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPalphamax = Entry(pbm_settings,width="15")
        self.Entry_BMPalphamax.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPalphamax.configure(textvariable=self.bmp_alphamax)
        self.bmp_alphamax.trace_variable("w", self.Entry_BMPalphamax_Callback)
        self.Label_BMPalphamax2 = Label(pbm_settings,text="0.0 = sharp corners, 1.33 = smoothed corners")
        self.Label_BMPalphamax2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_BMP_longcurve = Label(pbm_settings,text="Long Curve")
        self.Label_BMP_longcurve.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_BMP_longcurve = Checkbutton(pbm_settings,text="", anchor=W)
        self.Checkbutton_BMP_longcurve.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_BMP_longcurve.configure(variable=self.bmp_longcurve)
        self.Label_BMP_longcurve2 = Label(pbm_settings,text="Enable Curve Optimization")
        self.Label_BMP_longcurve2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)

        D_Yloc=D_Yloc+D_dY
        self.Label_BMPoptTolerance = Label(pbm_settings,text="Opt Tolerance")
        self.Label_BMPoptTolerance.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_BMPoptTolerance = Entry(pbm_settings,width="15")
        self.Entry_BMPoptTolerance.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_BMPoptTolerance.configure(textvariable=self.bmp_opttolerance)
        self.bmp_opttolerance.trace_variable("w", self.Entry_BMPoptTolerance_Callback)
        self.Label_BMPoptTolerance2 = Label(pbm_settings,text="Curve Optimization Tolerance")
        self.Label_BMPoptTolerance2.place(x=xd_entry_L+w_entry*1.5, y=D_Yloc, width=300, height=21)
        self.entry_set(self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(),2)


        pbm_settings.update_idletasks()
        Ybut=int(pbm_settings.winfo_height())-30
        Xbut=int(pbm_settings.winfo_width()/2)

        self.PBM_Reload = Button(pbm_settings,text="Re-Load Image")
        self.PBM_Reload.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")
        self.PBM_Reload.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.PBM_Close = Button(pbm_settings,text="Close",command=self.Close_Current_Window_Click)
        self.PBM_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")


        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            pbm_settings.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            pass

################################################################################
#                         General Settings Window                              #
################################################################################
    def GEN_Settings_Window(self):
        gen_settings = Toplevel(width=600, height=480)
        gen_settings.grab_set() # Use grab_set to prevent user input in the main window during calculations
        gen_settings.resizable(0,0)
        gen_settings.title('Settings')
        gen_settings.iconname("Settings")

        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            gen_settings.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            pass

        D_Yloc  = 6
        D_dY = 24
        xd_label_L = 12

        w_label=110+25
        w_entry=60
        w_units=35
        xd_entry_L=xd_label_L+w_label+10
        xd_units_L=xd_entry_L+w_entry+5

        #Radio Button
        D_Yloc=D_Yloc+D_dY
        self.Label_Units = Label(gen_settings,text="Units")
        self.Label_Units.place(x=xd_label_L, y=D_Yloc, width=113, height=21)
        self.Radio_Units_IN = Radiobutton(gen_settings,text="inch", value="in",
                                         width="100", anchor=W)
        self.Radio_Units_IN.place(x=w_label+22, y=D_Yloc, width=75, height=23)
        self.Radio_Units_IN.configure(variable=self.units, command=self.Entry_units_var_Callback )
        self.Radio_Units_MM = Radiobutton(gen_settings,text="mm", value="mm",
                                         width="100", anchor=W)
        self.Radio_Units_MM.place(x=w_label+110, y=D_Yloc, width=75, height=23)
        self.Radio_Units_MM.configure(variable=self.units, command=self.Entry_units_var_Callback )


        D_Yloc=D_Yloc+D_dY
        self.Label_Xoffset = Label(gen_settings,text="X Offset")
        self.Label_Xoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Xoffset_u = Label(gen_settings,textvariable=self.units, anchor=W)
        self.Label_Xoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Xoffset = Entry(gen_settings,width="15")
        self.Entry_Xoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Xoffset.configure(textvariable=self.xorigin)
        self.xorigin.trace_variable("w", self.Entry_Xoffset_Callback)
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_Yoffset = Label(gen_settings,text="Y Offset")
        self.Label_Yoffset.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Yoffset_u = Label(gen_settings,textvariable=self.units, anchor=W)
        self.Label_Yoffset_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Yoffset = Entry(gen_settings,width="15")
        self.Entry_Yoffset.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Yoffset.configure(textvariable=self.yorigin)
        self.yorigin.trace_variable("w", self.Entry_Yoffset_Callback)
        self.entry_set(self.Entry_Yoffset,self.Entry_Yoffset_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_ArcAngle = Label(gen_settings,text="Arc Angle")
        self.Label_ArcAngle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_ArcAngle_u = Label(gen_settings,text="deg", anchor=W)
        self.Label_ArcAngle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_ArcAngle = Entry(gen_settings,width="15")
        self.Entry_ArcAngle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_ArcAngle.configure(textvariable=self.segarc)
        self.segarc.trace_variable("w", self.Entry_ArcAngle_Callback)
        self.entry_set(self.Entry_ArcAngle,self.Entry_ArcAngle_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_Accuracy = Label(gen_settings,text="Accuracy")
        self.Label_Accuracy.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Accuracy_u = Label(gen_settings,textvariable=self.units, anchor=W)
        self.Label_Accuracy_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Accuracy = Entry(gen_settings,width="15")
        self.Entry_Accuracy.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Accuracy.configure(textvariable=self.accuracy)
        self.accuracy.trace_variable("w", self.Entry_Accuracy_Callback)
        self.entry_set(self.Entry_Accuracy,self.Entry_Accuracy_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_ext_char = Label(gen_settings,text="Extended Characters")
        self.Label_ext_char.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_ext_char = Checkbutton(gen_settings,text="", anchor=W)
        self.Checkbutton_ext_char.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_ext_char.configure(variable=self.ext_char)
        self.ext_char.trace_variable("w", self.Settings_ReLoad_Click)

        D_Yloc=D_Yloc+D_dY
        self.Label_arcfit = Label(gen_settings,text="Arc Fitting")
        self.Label_arcfit.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_arcfit_none = Radiobutton(gen_settings,text="None", \
                                            value="none", width="110", anchor=W)
        self.Radio_arcfit_none.place(x=w_label+22, y=D_Yloc, width=90, height=23)
        self.Radio_arcfit_none.configure(variable=self.arc_fit )
        self.Radio_arcfit_radius = Radiobutton(gen_settings,text="Radius Format", \
                                            value="radius", width="110", anchor=W)
        self.Radio_arcfit_radius.place(x=w_label+22+65, y=D_Yloc, width=100, height=23)
        self.Radio_arcfit_radius.configure(variable=self.arc_fit )
        self.Radio_arcfit_center = Radiobutton(gen_settings,text="Center Format", \
                                            value="center", width="110", anchor=W)
        self.Radio_arcfit_center.place(x=w_label+22+65+115, y=D_Yloc, width=100, height=23)
        self.Radio_arcfit_center.configure(variable=self.arc_fit )

        D_Yloc=D_Yloc+D_dY
        self.Label_no_com = Label(gen_settings,text="Suppress Comments")
        self.Label_no_com.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_no_com = Checkbutton(gen_settings,text="", anchor=W)
        self.Checkbutton_no_com.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_no_com.configure(variable=self.no_comments)

        D_Yloc=D_Yloc+D_dY
        self.Label_Gpre = Label(gen_settings,text="G Code Header")
        self.Label_Gpre.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpre = Entry(gen_settings,width="15")
        self.Entry_Gpre.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpre.configure(textvariable=self.gpre)

        D_Yloc=D_Yloc+D_dY
        self.Label_Gpost = Label(gen_settings,text="G Code Postscript")
        self.Label_Gpost.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpost = Entry(gen_settings)
        self.Entry_Gpost.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpost.configure(textvariable=self.gpost)

        D_Yloc=D_Yloc+D_dY
        self.Label_var_dis = Label(gen_settings,text="Disable Variables")
        self.Label_var_dis.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_var_dis = Checkbutton(gen_settings,text="", anchor=W)
        self.Checkbutton_var_dis.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_var_dis.configure(variable=self.var_dis)

        D_Yloc=D_Yloc+D_dY
        self.Label_Fontdir = Label(gen_settings,text="Font Directory")
        self.Label_Fontdir.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Fontdir = Entry(gen_settings,width="15")
        self.Entry_Fontdir.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Fontdir.configure(textvariable=self.fontdir)
        self.Fontdir = Button(gen_settings,text="Select Dir")
        self.Fontdir.place(x=xd_entry_L+310, y=D_Yloc, width=w_label-25, height=23)

        D_Yloc=D_Yloc+D_dY
        self.Label_Hcalc = Label(gen_settings,text="Height Calculation")
        self.Label_Hcalc.place(x=xd_label_L, y=D_Yloc, width=113, height=21)        
        self.Radio_Hcalc_ALL = Radiobutton(gen_settings,text="Max All", \
                                            value="max_all", width="110", anchor=W)
        self.Radio_Hcalc_ALL.place(x=w_label+110, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_ALL.configure(variable=self.H_CALC )
        self.Radio_Hcalc_USE = Radiobutton(gen_settings,text="Max Used", \
                                            value="max_use", width="110", anchor=W)
        self.Radio_Hcalc_USE.place(x=w_label+22, y=D_Yloc, width=90, height=23)
        self.Radio_Hcalc_USE.configure(variable=self.H_CALC )

        if self.input_type.get() != "text":
                self.Entry_Fontdir.configure(state="disabled")
                self.Fontdir.configure(state="disabled")
                self.Radio_Hcalc_ALL.configure(state="disabled")
                self.Radio_Hcalc_USE.configure(state="disabled")
        else:
            self.Fontdir.bind("<ButtonRelease-1>", self.Fontdir_Click)

        D_Yloc=D_Yloc+24
        self.Label_Box = Label(gen_settings,text="Add Box/Circle")
        self.Label_Box.place(x=xd_label_L, y=D_Yloc, width=113, height=21)
        self.Radio_Box_N = Radiobutton(gen_settings,text="No", value="no_box", anchor=W)
        self.Radio_Box_N.place(x=w_label+22, y=D_Yloc, width=55, height=23) #132
        self.Radio_Box_N.configure(variable=self.plotbox )
        self.Radio_Box_Y = Radiobutton(gen_settings,text="Yes", value="box", anchor=W)
        self.Radio_Box_Y.place(x=w_label+75, y=D_Yloc, width=55, height=23) #185
        self.Radio_Box_Y.configure(variable=self.plotbox )

        self.Label_BoxGap = Label(gen_settings,text="Box/Circle Gap:", anchor=E)
        self.Label_BoxGap.place(x=w_label+125, y=D_Yloc, width=w_label, height=21) #252
        self.Entry_BoxGap = Entry(gen_settings)
        self.Entry_BoxGap.place(x=w_label+262, y=D_Yloc, width=w_entry, height=23) #372
        self.Entry_BoxGap.configure(textvariable=self.boxgap)
        self.boxgap.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(gen_settings,textvariable=self.units, anchor=W)

        self.Label_BoxGap_u.place(x=w_label+325, y=D_Yloc, width=100, height=21) #435
        self.entry_set(self.Entry_BoxGap,self.Entry_BoxGap_Check(),2)

        D_Yloc=D_Yloc+D_dY+10
        self.Label_SaveConfig = Label(gen_settings,text="Configuration File")
        self.Label_SaveConfig.place(x=xd_label_L, y=D_Yloc, width=113, height=21)
        self.GEN_SaveConfig = Button(gen_settings,text="Save")
        self.GEN_SaveConfig.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=21, anchor="nw")
        self.GEN_SaveConfig.bind("<ButtonRelease-1>", self.Write_Config_File)


        ## Buttons ##
        gen_settings.update_idletasks()
        Ybut=int(gen_settings.winfo_height())-30
        Xbut=int(gen_settings.winfo_width()/2)

        self.GEN_Reload = Button(gen_settings,text="Recalculate")
        self.GEN_Reload.place(x=Xbut-65, y=Ybut, width=130, height=30, anchor="e")
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        self.GEN_Recalculate = Button(gen_settings,text="Re-Load Image")
        self.GEN_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="c")
        self.GEN_Recalculate.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.GEN_Close = Button(gen_settings,text="Close",command=self.Close_Current_Window_Click)
        self.GEN_Close.place(x=Xbut+65, y=Ybut, width=130, height=30, anchor="w")

    ################################################################################
    #                         V-Carve Settings window                              #
    ################################################################################
    def VCARVE_Settings_Window(self):
        vcarve_settings = Toplevel(width=580, height=620+25) #+100
        vcarve_settings.grab_set() # Use grab_set to prevent user input in the main window during calculations
        vcarve_settings.resizable(0,0)
        vcarve_settings.title('V-Carve Settings')
        vcarve_settings.iconname("V-Carve Settings")

        try: #Attempt to create temporary icon bitmap file
            f = open("f_engrave_icon",'w')
            f.write("#define f_engrave_icon_width 16\n")
            f.write("#define f_engrave_icon_height 16\n")
            f.write("static unsigned char f_engrave_icon_bits[] = {\n")
            f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
            f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
            f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
            f.close()
            vcarve_settings.iconbitmap("@f_engrave_icon")
            os.remove("f_engrave_icon")
        except:
            pass

        D_Yloc  = 12
        D_dY = 24
        xd_label_L = 12

        w_label=250
        w_entry=60
        w_units=35
        xd_entry_L=xd_label_L+w_label+10
        xd_units_L=xd_entry_L+w_entry+5

        #----------------------
        self.Label_cutter_type = Label(vcarve_settings,text="Cutter Type")
        self.Label_cutter_type.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Radio_Type_VBIT = Radiobutton(vcarve_settings,text="V-Bit", value="VBIT",
                                         width="100", anchor=W)
        self.Radio_Type_VBIT.place(x=xd_entry_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_Type_VBIT.configure(variable=self.bit_shape)

        D_Yloc=D_Yloc+24
        self.Radio_Type_BALL = Radiobutton(vcarve_settings,text="Ball Nose", value="BALL",
                                         width="100", anchor=W)
        self.Radio_Type_BALL.place(x=xd_entry_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_Type_BALL.configure(variable=self.bit_shape)

        D_Yloc=D_Yloc+24
        self.Radio_Type_STRAIGHT = Radiobutton(vcarve_settings,text="Straight", value="FLAT",
                                         width="100", anchor=W)
        self.Radio_Type_STRAIGHT.place(x=xd_entry_L, y=D_Yloc, width=w_label, height=21)
        self.Radio_Type_STRAIGHT.configure(variable=self.bit_shape)

        self.bit_shape.trace_variable("w", self.Entry_Bit_Shape_var_Callback)
        #----------------------

        D_Yloc=D_Yloc+D_dY
        self.Label_Vbitangle = Label(vcarve_settings,text="V-Bit Angle")
        self.Label_Vbitangle.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Vbitangle_u = Label(vcarve_settings,text="deg", anchor=W)
        self.Label_Vbitangle_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Vbitangle = Entry(vcarve_settings,width="15")
        self.Entry_Vbitangle.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Vbitangle.configure(textvariable=self.v_bit_angle)
        self.v_bit_angle.trace_variable("w", self.Entry_Vbitangle_Callback)
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_Vbitdia = Label(vcarve_settings,text="V-Bit Diameter")
        self.Label_Vbitdia.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Vbitdia_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_Vbitdia_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Vbitdia = Entry(vcarve_settings,width="15")
        self.Entry_Vbitdia.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Vbitdia.configure(textvariable=self.v_bit_dia)
        self.v_bit_dia.trace_variable("w", self.Entry_Vbitdia_Callback)
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_VDepthLimit = Label(vcarve_settings,text="Cut Depth Limit")
        self.Label_VDepthLimit.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_VDepthLimit_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_VDepthLimit_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_VDepthLimit = Entry(vcarve_settings,width="15")
        self.Entry_VDepthLimit.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_VDepthLimit.configure(textvariable=self.v_depth_lim)
        self.v_depth_lim.trace_variable("w", self.Entry_VDepthLimit_Callback)
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_maxcut = Label(vcarve_settings,text="Max Cut Depth")
        self.Label_maxcut.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_maxcut_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_maxcut_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Label_maxcut_i = Label(vcarve_settings,textvariable=self.maxcut, anchor=W)
        self.Label_maxcut_i.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=21)

        D_Yloc=D_Yloc+D_dY+5
        self.Label_StepSize = Label(vcarve_settings,text="Sub-Step Length")
        self.Label_StepSize.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_StepSize_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_StepSize_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_StepSize = Entry(vcarve_settings,width="15")
        self.Entry_StepSize.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_StepSize.configure(textvariable=self.v_step_len)
        self.v_step_len.trace_variable("w", self.Entry_StepSize_Callback)
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_v_flop = Label(vcarve_settings,text="Flip Normals (V-Carve Side)")
        self.Label_v_flop.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_flop = Checkbutton(vcarve_settings,text="", anchor=W)
        self.Checkbutton_v_flop.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_flop.configure(variable=self.v_flop)
        self.v_flop.trace_variable("w", self.Entry_recalc_var_Callback)

        D_Yloc=D_Yloc+D_dY
        self.Label_inlay = Label(vcarve_settings,text="Prismatic (Inlay)")
        self.Label_inlay.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_inlay = Checkbutton(vcarve_settings,text="", anchor=W)
        self.Checkbutton_inlay.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_inlay.configure(variable=self.inlay)
        self.inlay.trace_variable("w", self.Entry_Prismatic_Callback)

        D_Yloc=D_Yloc+D_dY
        self.Label_Allowance = Label(vcarve_settings,text="Prismatic Overcut")
        self.Label_Allowance.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_Allowance_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_Allowance_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_Allowance = Entry(vcarve_settings,width="15")
        self.Entry_Allowance.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_Allowance.configure(textvariable=self.allowance)
        self.allowance.trace_variable("w", self.Entry_Allowance_Callback)
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_v_pplot = Label(vcarve_settings,text="Plot During V-Carve Calculation")
        self.Label_v_pplot.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Checkbutton_v_pplot = Checkbutton(vcarve_settings,text="", anchor=W)
        self.Checkbutton_v_pplot.place(x=xd_entry_L, y=D_Yloc, width=75, height=23)
        self.Checkbutton_v_pplot.configure(variable=self.v_pplot)

        ### Update Idle tasks before requesting anything from winfo
        vcarve_settings.update_idletasks()
        center_loc=int(float(vcarve_settings.winfo_width())/2)

        ## Multipass Settings ##
        D_Yloc=D_Yloc+D_dY+12
        self.vcarve_separator1 = Frame(vcarve_settings,height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.place(x=0, y=D_Yloc,width=580, height=2)

        D_Yloc=D_Yloc+D_dY-12
        self.Label_multipass = Label(vcarve_settings,text="Multipass Cutting")
        self.Label_multipass.place(x=center_loc, y=D_Yloc, width=w_label, height=21,anchor=CENTER)

        D_Yloc=D_Yloc+D_dY
        self.Label_v_rough_stk = Label(vcarve_settings,text="V-Carve Finish Pass Stock")
        self.Label_v_rough_stk.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_v_rough_stk_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_v_rough_stk_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)

        self.Label_right_v_rough_stk= Label(vcarve_settings,text="(Zero disables multipass cutting)", anchor=W)
        self.Label_right_v_rough_stk.place(x=xd_units_L+20, y=D_Yloc, width=w_label, height=21)

        self.Entry_v_rough_stk = Entry(vcarve_settings,width="15")
        self.Entry_v_rough_stk.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_v_rough_stk.configure(textvariable=self.v_rough_stk)
        self.v_rough_stk.trace_variable("w", self.Entry_v_rough_stk_Callback)
        self.entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_v_max_cut = Label(vcarve_settings,text="V-Carve Max Depth per Pass")
        self.Label_v_max_cut.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_v_max_cut_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_v_max_cut_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_v_max_cut = Entry(vcarve_settings,width="15")
        self.Entry_v_max_cut.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_v_max_cut.configure(textvariable=self.v_max_cut)
        self.v_max_cut.trace_variable("w", self.Entry_v_max_cut_Callback)
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(),2)

        if float(self.v_rough_stk.get()) == 0.0:
            self.Label_v_max_cut.configure(state="disabled")
            self.Label_v_max_cut_u.configure(state="disabled")
            self.Entry_v_max_cut.configure(state="disabled")
        else:
            self.Label_v_max_cut.configure(state="normal")
            self.Label_v_max_cut_u.configure(state="normal")
            self.Entry_v_max_cut.configure(state="normal")


        if not bool(self.inlay.get()):
            self.Label_Allowance.configure(state="disabled")
            self.Entry_Allowance.configure(state="disabled")
            self.Label_Allowance_u.configure(state="disabled")
        else:
            self.Label_Allowance.configure(state="normal")
            self.Entry_Allowance.configure(state="normal")
            self.Label_Allowance_u.configure(state="normal")
                
        ## Cleanup Settings ##
        D_Yloc=D_Yloc+D_dY+12
        self.vcarve_separator1 = Frame(vcarve_settings,height=2, bd=1, relief=SUNKEN)
        self.vcarve_separator1.place(x=0, y=D_Yloc,width=580, height=2)

        right_but_loc=int(vcarve_settings.winfo_width())-10
        width_cb = 100
        height_cb = 35

        D_Yloc=D_Yloc+D_dY-12
        self.Label_clean = Label(vcarve_settings,text="Cleanup Operations")
        self.Label_clean.place(x=center_loc, y=D_Yloc, width=w_label, height=21,anchor=CENTER)

        self.CLEAN_Recalculate = Button(vcarve_settings,text="Calculate\nCleanup", command=self.CLEAN_Recalculate_Click)
        self.CLEAN_Recalculate.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb*1.5, anchor="ne")

        D_Yloc=D_Yloc+D_dY
        self.Label_CLEAN_DIA = Label(vcarve_settings,text="Cleanup Cut Diameter")
        self.Label_CLEAN_DIA.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_CLEAN_DIA_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_CLEAN_DIA_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_CLEAN_DIA = Entry(vcarve_settings,width="15")
        self.Entry_CLEAN_DIA.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_CLEAN_DIA.configure(textvariable=self.clean_dia)
        self.clean_dia.trace_variable("w", self.Entry_CLEAN_DIA_Callback)
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(),2)

        D_Yloc=D_Yloc+D_dY
        self.Label_STEP_OVER = Label(vcarve_settings,text="Cleanup Cut Step Over")
        self.Label_STEP_OVER.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_STEP_OVER_u = Label(vcarve_settings,text="%", anchor=W)
        self.Label_STEP_OVER_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_STEP_OVER = Entry(vcarve_settings,width="15")
        self.Entry_STEP_OVER.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_STEP_OVER.configure(textvariable=self.clean_step)
        self.clean_step.trace_variable("w", self.Entry_STEP_OVER_Callback)
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(),2)

        D_Yloc=D_Yloc+24
        check_delta=40
        self.Label_clean_P = Label(vcarve_settings,text="Cleanup Cut Directions")
        self.Label_clean_P.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Write_Clean = Button(vcarve_settings,text="Save Cleanup\nG-Code", command=self.Write_Clean_Click)
        self.Write_Clean.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb, anchor="e")

        self.Checkbutton_clean_P = Checkbutton(vcarve_settings,text="P", anchor=W)
        self.Checkbutton_clean_P.configure(variable=self.clean_P)
        self.Checkbutton_clean_P.place(x=xd_entry_L, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_clean_X = Checkbutton(vcarve_settings,text="X", anchor=W)
        self.Checkbutton_clean_X.configure(variable=self.clean_X)
        self.Checkbutton_clean_X.place(x=xd_entry_L+check_delta, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_clean_Y = Checkbutton(vcarve_settings,text="Y", anchor=W)
        self.Checkbutton_clean_Y.configure(variable=self.clean_Y)
        self.Checkbutton_clean_Y.place(x=xd_entry_L+check_delta*2, y=D_Yloc, width=w_entry+40, height=23)

        D_Yloc=D_Yloc+12

        D_Yloc=D_Yloc+D_dY
        self.Label_V_CLEAN = Label(vcarve_settings,text="V-Bit Cleanup Step")
        self.Label_V_CLEAN.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Label_V_CLEAN_u = Label(vcarve_settings,textvariable=self.units, anchor=W)
        self.Label_V_CLEAN_u.place(x=xd_units_L, y=D_Yloc, width=w_units, height=21)
        self.Entry_V_CLEAN = Entry(vcarve_settings,width="15")
        self.Entry_V_CLEAN.place(x=xd_entry_L, y=D_Yloc, width=w_entry, height=23)
        self.Entry_V_CLEAN.configure(textvariable=self.clean_v)
        self.clean_v.trace_variable("w", self.Entry_V_CLEAN_Callback)
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(),2)

        D_Yloc=D_Yloc+24
        self.Label_v_clean_P = Label(vcarve_settings,text="V-Bit Cut Directions")
        self.Label_v_clean_P.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Write_V_Clean = Button(vcarve_settings,text="Save V Cleanup\nG-Code", command=self.Write_V_Clean_Click)
        self.Write_V_Clean.place(x=right_but_loc, y=D_Yloc, width=width_cb, height=height_cb, anchor="e")

        self.Checkbutton_v_clean_P = Checkbutton(vcarve_settings,text="P", anchor=W)
        self.Checkbutton_v_clean_P.configure(variable=self.v_clean_P)
        self.Checkbutton_v_clean_P.place(x=xd_entry_L, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_v_clean_X = Checkbutton(vcarve_settings,text="X", anchor=W)
        self.Checkbutton_v_clean_X.configure(variable=self.v_clean_X)
        self.Checkbutton_v_clean_X.place(x=xd_entry_L+check_delta, y=D_Yloc, width=w_entry+40, height=23)
        self.Checkbutton_v_clean_Y = Checkbutton(vcarve_settings,text="Y", anchor=W)
        self.Checkbutton_v_clean_Y.configure(variable=self.v_clean_Y)
        self.Checkbutton_v_clean_Y.place(x=xd_entry_L+check_delta*2, y=D_Yloc, width=w_entry+40, height=23)

        ## V-Bit Picture ##
        self.PHOTO = PhotoImage(format='gif',data=
             'R0lGODlhoABQAIABAAAAAP///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEK'
            +'AAEALAAAAACgAFAAAAL+jI+pBu2/opy02ouzvg+G7m3iSJam1XHpybbuezhk'
            +'CFNyjZ9AS+ff6gtqdq5eMUQUKlG4GwsYW0ptPiMGmkhOtwhtzioBd7nkqBTk'
            +'BV3LZe8Z7Vyzue75zL6t4zf6fa3vxxGoBDhIZViFKFKoeNeYwfjIJylHyWPJ'
            +'hPmkechZEmkJ6hk2GiFaqnD6qIpq1ur6WhnL+kqLaIuKO6g7yuvnywmMJ4xJ'
            +'PGdMidxmkpaFxDClTMar1ZA1hr0kTcecDUu0Exe0nacDy/D8ER17vgidugK+'
            +'zq7OHB5jXf1Onkpf311HXz1+1+gBs7ZAzcB57Aj+IPUFoUNC6CbCgKMGYa3+'
            +'cBjhBOtisUkzf2FCXjT5C+UTlSl7sQykMRQxhf8+RSxmrFrOKi9VXCwI7gbH'
            +'h/iCGgX56SAae3+AEg36FN0+qQt10BIHj1XMIk6xJZH3D+zXd1Yhab2ybaRR'
            +'sFXjVZR4JJOjCVtf6IQ2NuzUrt7KlrwUkB/NoXD35hM7tOZKvjy21v0D6NRI'
            +'xZBBKovzmCTPojeJao6WeFzmz6InjiYtmtBp1Jtb9/y8eoZA1nmkxaYt5LbZ'
            +'frhrx+29R7eNPq9JCzcVGTgdXLGLG7/qXHlCVcel+/Y5vGBRjWyR7n6OAtTs'
            +'b9otfwdPV9R4sgux3sN7NzHWjX8htQPSfW/UgYRL888KPAllP3jgX14GRpFP'
            +'O/85405YCZpRIIEQIsjRfAtStYgeAuUX34TwCajZYUkhJ6FizRgIgYggNlTd'
            +'EMR1Ux5q0Q2BoXUbTVQAADs=')

        self.Label_photo = Label(vcarve_settings,image=self.PHOTO)
        self.Label_photo.place(x=w_label+150, y=40)
        self.Entry_Bit_Shape_Check()

        ## Buttons ##

        Ybut=int(vcarve_settings.winfo_height())-30
        Xbut=int(vcarve_settings.winfo_width()/2)

        self.VCARVE_Recalculate = Button(vcarve_settings,text="Calculate V-Carve", command=self.VCARVE_Recalculate_Click)
        self.VCARVE_Recalculate.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")


        if self.cut_type.get() == "v-carve":
            self.VCARVE_Recalculate.configure(state="normal", command=None)
        else:
            self.VCARVE_Recalculate.configure(state="disabled", command=None)

        self.VCARVE_Close = Button(vcarve_settings,text="Close",command=vcarve_settings.destroy)
        self.VCARVE_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")

####################################
# Gcode class for creating G-Code
####################################
class Gcode:
    def __init__(self,
                 safetyheight = 0.04,
                 tolerance=0.001,
                 target=lambda s: sys.stdout.write(s + "\n"),
                 arc_fit = "none"
                 ):
        
        self.lastx = self.lasty = self.lastz = self.lastf = None
        self.feed = None
        self.lastgcode = self.lastfeed = None
        self.plane = None
        self.cuts = []
        self.dp = 4
        self.dpfeed = 2
        
        self.safetyheight = self.lastz = safetyheight
        self.tolerance = tolerance
        self.write = target
        self.arc_fit = arc_fit

    def set_plane(self, p):
        if (self.arc_fit!="none"):
            assert p in (17,18,19)
            if p != self.plane:
                self.plane = p
                self.write("G%d" % p)
        
        
    # If any 'cut' moves are stored up, send them to the simplification algorithm
    # and actually output them.
    #
    # This function is usually used internally (e.g., when changing from a cut
    # to a rapid) but can be called manually as well.  For instance, when
    # a contouring program reaches the end of a row, it may be desirable to enforce
    # that the last 'cut' coordinate is actually in the output file, and it may
    # give better performance because this means that the simplification algorithm
    # will examine fewer points per run.
    def flush(self):
        if not self.cuts: return
        for move, (x, y, z), cent in douglas(self.cuts, self.tolerance, self.plane):
            if cent:
                self.move_common(x, y, z, I=cent[0], J=cent[1], gcode=move)
            else:
                self.move_common(x, y, z, gcode="G1")
        self.cuts = []

    def end(self):
        self.flush()
        self.safety()

    def rapid(self, x=None, y=None, z=None):
        #"Perform a rapid move to the specified coordinates"
        self.flush()
        self.move_common(x, y, z, gcode="G0")

    def move_common(self, x=None, y=None, z=None, I=None, J=None, gcode="G0"):
        #"An internal function used for G0 and G1 moves"
        gcodestring = xstring = ystring = zstring = Istring = Jstring = Rstring = fstring = ""
        if x == None: x = self.lastx
        if y == None: y = self.lasty
        if z == None: z = self.lastz

        if (self.feed != self.lastf):
            fstring = self.feed
            self.lastf = self.feed
        FORMAT  =  "%%.%df" % (self.dp)

        if (gcode == "G2" or gcode == "G3"):
            XC = self.lastx+I
            YC = self.lasty+J
            R_check_1 = sqrt( (XC-self.lastx)**2+(YC-self.lasty)**2 )
            R_check_2 = sqrt( (XC-x         )**2+(YC-y         )**2 )
            
            Rstring = " R"+FORMAT % ((R_check_1+R_check_2)/2.0)
            if  abs(R_check_1-R_check_2) > Zero:
                fmessage("-- G-Code Curve Fitting Anomaly - Check Output --")
                fmessage("R_start: %f R_end %f" %(R_check_1,R_check_2))
                fmessage("Begining and end radii do not match: delta = %f" %(abs(R_check_1-R_check_2)))
                

        if x != self.lastx:
                xstring = " X"+FORMAT % (x)
                self.lastx = x
        if y != self.lasty:
                ystring = " Y"+FORMAT % (y)
                self.lasty = y
        if z != self.lastz:
                zstring = " Z"+FORMAT % (z)
                self.lastz = z
        if I != None:
                Istring = " I"+FORMAT % (I)
        if J != None:
                Jstring = " J"+FORMAT % (J)
        if xstring == ystring == zstring == fstring == "":
            return
        
        gcodestring = gcode
        if (self.arc_fit == "radius"):
            cmd = "".join([gcodestring, xstring, ystring, zstring, Rstring, fstring])
        else:
            cmd = "".join([gcodestring, xstring, ystring, zstring, Istring, Jstring, fstring])
       
        if cmd:
            self.write(cmd)
            

    def set_feed(self, feed):
        #"Set the feed rate to the given value"
        self.flush()
        #self.write("F%.4f" % feed)
        self.feed = "F%s" % feed
        self.lastf = None
        
        

    def cut(self, x=None, y=None, z=None):
        #"Perform a cutting move at the specified feed rate to the specified coordinates"
        if self.cuts:
            lastx, lasty, lastz = self.cuts[-1]
        else:
            lastx, lasty, lastz = self.lastx, self.lasty, self.lastz
        if x is None: x = lastx
        if y is None: y = lasty
        if z is None: z = lastz
        self.cuts.append([x,y,z])

    def safety(self):
        #"Go to the 'safety' height at rapid speed"
        self.flush()
        self.rapid(z=self.safetyheight)

# Perform Douglas-Peucker simplification on the path 'st' with the specified
# tolerance.  The '_first' argument is for internal use only.
#
# The Douglas-Peucker simplification algorithm finds a subset of the input points
# whose path is never more than 'tolerance' away from the original input path.
#
# If 'plane' is specified as 17, 18, or 19, it may find helical arcs in the given
# plane in addition to lines.
#
# -- I modified the code so the note below does not apply when using plane 17 --
# Note that if there is movement in the plane
# perpendicular to the arc, it will be distorted, so 'plane' should usually
# be specified only when there is only movement on 2 axes
#
def douglas(st, tolerance=.001, plane=None, _first=True):
    if len(st) == 1:
        yield "G1", st[0], None
        return
    
    L1 = st[0]
    L2 = st[-1]
    
    last_point = None
    while (abs(L1[0]-L2[0]) < Zero) and (abs(L1[1]-L2[1]) < Zero) and (abs(L1[2]-L2[2]) < Zero):
        last_point=st.pop()
        L2 = st[-1]

    worst_dist = 0
    worst_distz = 0 #added to fix out of plane inacuracy problem
    worst = 0
    min_rad = MAXINT
    max_arc = -1

    ps = st[0]
    pe = st[-1]

    for i, p in enumerate(st):
        if p is L1 or p is L2: continue
        dist  = dist_lseg(L1, L2, p)
        distz = dist_lseg(L1, L2, p, z_only=True) #added to fix out of plane inacuracy problem
        if dist > worst_dist:
            worst = i
            worst_dist = dist
            rad = arc_rad(plane, ps, p, pe)
            if rad < min_rad:
                max_arc = i
                min_rad = rad
        if distz > worst_distz: #added to fix out of plane inacuracy problem
            worst_distz = distz #added to fix out of plane inacuracy problem

    worst_arc_dist = 0
    if min_rad != MAXINT:
        c1, c2 = arc_center(plane, ps, st[max_arc], pe)
        Lx, Ly, Lz = st[0]
        if one_quadrant(plane, (c1, c2), ps, st[max_arc], pe):
            for i, (x,y,z) in enumerate(st):
                if plane == 17:
                    dist1 = abs(hypot(c1-x, c2-y) - min_rad)
                    dist = sqrt(worst_distz**2 + dist1**2) #added to fix out of plane inacuracy problem
                elif plane == 18:
                    dist = abs(hypot(c1-x, c2-z) - min_rad)
                elif plane == 19:
                    dist = abs(hypot(c1-y, c2-z) - min_rad)
                else: dist = MAXINT
                
                if dist > worst_arc_dist: worst_arc_dist = dist

                mx = (x+Lx)/2
                my = (y+Ly)/2
                mz = (z+Lz)/2
                if plane == 17: dist = abs(hypot(c1-mx, c2-my) - min_rad)
                elif plane == 18: dist = abs(hypot(c1-mx, c2-mz) - min_rad)
                elif plane == 19: dist = abs(hypot(c1-my, c2-mz) - min_rad)
                else: dist = MAXINT
                Lx, Ly, Lz = x, y, z
        else:
            worst_arc_dist = MAXINT
    else:
        worst_arc_dist = MAXINT

    if worst_arc_dist < tolerance and worst_arc_dist < worst_dist:
        ccw = arc_dir(plane, (c1, c2), ps, st[max_arc], pe)
        if plane == 18: ccw = not ccw
        yield "G1", ps, None
        if ccw:
            yield "G3", st[-1], arc_fmt(plane, c1, c2, ps)
        else:
            yield "G2", st[-1], arc_fmt(plane, c1, c2, ps)
    elif worst_dist > tolerance:
        if _first: yield "G1", st[0], None
        for i in douglas(st[:worst+1], tolerance, plane, False):
            yield i
        yield "G1", st[worst], None
        for i in douglas(st[worst:], tolerance, plane, False):
            yield i
        if _first: yield "G1", st[-1], None
    else:
        if _first: yield "G1", st[0], None
        if _first: yield "G1", st[-1], None

    if last_point != None:      #added to fix closed loop problem
        yield "G1", st[0], None #added to fix closed loop problem


################################################################################
#             Author.py                                                        #
#             A component of emc2                                              #
################################################################################

# Compute the 3D distance from the line segment l1..l2 to the point p.
# (Those are lower case L1 and L2)
def dist_lseg(l1, l2, p, z_only=False):
    x0, y0, z0 = l1
    xa, ya, za = l2
    xi, yi, zi = p
    
    dx = xa-x0
    dy = ya-y0
    dz = za-z0
    d2 = dx*dx + dy*dy + dz*dz

    if d2 == 0: return 0

    t = (dx * (xi-x0) + dy * (yi-y0) + dz * (zi-z0)) / d2
    if t < 0: t = 0
    if t > 1: t = 1
    
    if (z_only==True):
        dist2 = (zi - z0 - t*dz)**2
    else:
        dist2 = (xi - x0 - t*dx)**2 + (yi - y0 - t*dy)**2 + (zi - z0 - t*dz)**2

    return dist2 ** .5

def rad1(x1,y1,x2,y2,x3,y3):
    x12 = x1-x2
    y12 = y1-y2
    x23 = x2-x3
    y23 = y2-y3
    x31 = x3-x1
    y31 = y3-y1

    den = abs(x12 * y23 - x23 * y12)
    if abs(den) < 1e-5: return MAXINT
    return hypot(float(x12), float(y12)) * hypot(float(x23), float(y23)) * hypot(float(x31), float(y31)) / 2 / den

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self): return "<%f,%f>" % (self.x, self.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __mul__(self, other):
        return Point(self.x * other, self.y * other)
    __rmul__ = __mul__
    def cross(self, other):
        return self.x * other.y - self.y * other.x
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def mag(self):
        return hypot(self.x, self.y)
    def mag2(self):
        return self.x**2 + self.y**2

def cent1(x1,y1,x2,y2,x3,y3):
    P1 = Point(x1,y1)
    P2 = Point(x2,y2)
    P3 = Point(x3,y3)

    den = abs((P1-P2).cross(P2-P3))
    if abs(den) < 1e-5: return MAXINT, MAXINT

    alpha = (P2-P3).mag2() * (P1-P2).dot(P1-P3) / 2 / den / den
    beta  = (P1-P3).mag2() * (P2-P1).dot(P2-P3) / 2 / den / den
    gamma = (P1-P2).mag2() * (P3-P1).dot(P3-P2) / 2 / den / den

    Pc = alpha * P1 + beta * P2 + gamma * P3
    return Pc.x, Pc.y

def arc_center(plane, p1, p2, p3):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    if plane == 17: return cent1(x1,y1,x2,y2,x3,y3)
    if plane == 18: return cent1(x1,z1,x2,z2,x3,z3)
    if plane == 19: return cent1(y1,z1,y2,z2,y3,z3)

def arc_rad(plane, P1, P2, P3):
    if plane is None: return MAXINT

    x1, y1, z1 = P1
    x2, y2, z2 = P2
    x3, y3, z3 = P3

    if plane == 17: return rad1(x1,y1,x2,y2,x3,y3)
    if plane == 18: return rad1(x1,z1,x2,z2,x3,z3)
    if plane == 19: return rad1(y1,z1,y2,z2,y3,z3)
    return None, 0

def get_pts(plane, x,y,z):
    if plane == 17: return x,y
    if plane == 18: return x,z
    if plane == 19: return y,z

def one_quadrant(plane, c, p1, p2, p3):
    xc, yc = c
    x1, y1 = get_pts(plane, p1[0],p1[1],p1[2])
    x2, y2 = get_pts(plane, p2[0],p2[1],p2[2])
    x3, y3 = get_pts(plane, p3[0],p3[1],p3[2])

    def sign(x):
        if abs(x) < 1e-5: return 0
        if x < 0: return -1
        return 1

    signs = set((
        (sign(x1-xc),sign(y1-yc)),
        (sign(x2-xc),sign(y2-yc)),
        (sign(x3-xc),sign(y3-yc))
    ))

    if len(signs) == 1: return True

    if (1,1) in signs:
        signs.discard((1,0))
        signs.discard((0,1))
    if (1,-1) in signs:
        signs.discard((1,0))
        signs.discard((0,-1))
    if (-1,1) in signs:
        signs.discard((-1,0))
        signs.discard((0,1))
    if (-1,-1) in signs:
        signs.discard((-1,0))
        signs.discard((0,-1))

    if len(signs) == 1: return True

def arc_dir(plane, c, p1, p2, p3):
    xc, yc = c
    x1, y1 = get_pts(plane, p1[0],p1[1],p1[2])
    x2, y2 = get_pts(plane, p2[0],p2[1],p2[2])
    x3, y3 = get_pts(plane, p3[0],p3[1],p3[2])

    theta_start = atan2(y1-yc, x1-xc)
    theta_mid = atan2(y2-yc, x2-xc)
    theta_end = atan2(y3-yc, x3-xc)

    if theta_mid < theta_start:
        theta_mid = theta_mid + 2 * pi
    while theta_end < theta_mid:
        theta_end = theta_end + 2 * pi

    return theta_end < 2 * pi

def arc_fmt(plane, c1, c2, p1):
    x, y, z = p1
    if plane == 17:
        #return "I%.4f J%.4f" % (c1-x, c2-y)
        return [c1-x, c2-y]
    if plane == 18:
        #return "I%.4f K%.4f" % (c1-x, c2-z)
        return [c1-x, c2-z]
    if plane == 19:
        #return "J%.4f K%.4f" % (c1-y, c2-z)
        return [c1-y, c2-z]

################################################################################
#                          Start-up Application                                #
################################################################################
root = Tk()
app = Application(root)
app.master.title("F-Engrave V"+version)
app.master.iconname("F-Engrave")
app.master.minsize(780,540)
app.f_engrave_init()


try: #Attempt to create temporary icon bitmap file
    f = open("f_engrave_icon",'w')
    f.write("#define f_engrave_icon_width 16\n")
    f.write("#define f_engrave_icon_height 16\n")
    f.write("static unsigned char f_engrave_icon_bits[] = {\n")
    f.write("   0x3f, 0xfc, 0x1f, 0xf8, 0xcf, 0xf3, 0x6f, 0xe4, 0x6f, 0xed, 0xcf, 0xe5,\n")
    f.write("   0x1f, 0xf4, 0xfb, 0xf3, 0x73, 0x98, 0x47, 0xce, 0x0f, 0xe0, 0x3f, 0xf8,\n")
    f.write("   0x7f, 0xfe, 0x3f, 0xfc, 0x9f, 0xf9, 0xcf, 0xf3 };\n")
    f.close()
    app.master.iconbitmap("@f_engrave_icon")
    os.remove("f_engrave_icon")
except:
    fmessage("Unable to create temporary icon file.")

root.mainloop()

