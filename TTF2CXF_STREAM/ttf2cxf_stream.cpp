/*
##############################################################################
    ttf2cxf_stream converts True Type files to CXF Font file format

    This program is based on ttf2cxf previously released by RibbonSoft
    -- info@ribbonsoft.com; http://www.ribbonsoft.com
    ** $Id: rs_information.cpp,v 1.16 2003/10/18 14:26:26 andrew Exp $
	** Copyright (C) 2001-2003 RibbonSoft. All rights reserved.
	
    This modified version includes new features to allow streaming
    the CXF file data to another program through STDOUT

    ttf2cxf_stream
    Version 0.4
	
    V0.4
	- Changed fixed number of segments per arc to fixed arc angle limit
    - Removed '-n' command line option to set the number of points in an arc approximation
	- Added '-s' command line option to set the seg_arc_limit (maximum angle of arc approximations)
	
    V0.3
    - Added '-e' option to include extended characters greater than decimal 256
    - Added mapping of '-' as the output file name to stdout 

    V0.2
    - Added cast to (unsigned int) to charcode to avoid warning message during build

    V0.1
    - First release modified to allow streaming the CXF file data to other
      programs via STDOUT

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; version 2.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, see <http://www.gnu.org/licenses/>
	Or write to the Free Software Foundation, Inc.,
	51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
	
##############################################################################
*/

#include <iostream>
#include <math.h>
#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_OUTLINE_H
#include FT_GLYPH_H

FT_Library library;
FT_Face face;
double prevx;
double prevy;
double seg_arc_limit;
double factor;
int yMax;
FILE* fpCxf;

std::string name;
double letterSpacing;
double wordSpacing;
double lineSpacingFactor;
int extended_chars;
std::string author;

int STDOUT = 0; 

int moveTo(FT_Vector* to, void* fp);
int lineTo(FT_Vector* to, void* fp);
int conicTo(FT_Vector* control, FT_Vector* to, void* fp);
int cubicTo(FT_Vector* control1, FT_Vector* control2, FT_Vector* to, void* fp);


static const FT_Outline_Funcs funcs
= {
      (FT_Outline_MoveTo_Func) moveTo,
      (FT_Outline_LineTo_Func) lineTo,
      (FT_Outline_ConicTo_Func)conicTo,
      (FT_Outline_CubicTo_Func)cubicTo,
      0, 0
  };

  
int moveTo(FT_Vector* to, void* fp) {
    prevx = to->x;
    prevy = to->y;
    return 0;
}


int lineTo(FT_Vector* to, void* fp) {
    if (fp!=NULL) {
        fprintf((FILE*)fp, "L %f,%f,%f,%f \n", prevx*factor, prevy*factor,
                (double)to->x*factor, (double)to->y*factor);
    }
    prevx = to->x;
    prevy = to->y;

    if (to->y>yMax) {
        yMax = to->y;
    }
    return 0;
}


int conicTo(FT_Vector* control, FT_Vector* to, void* fp)
{
    double px, py;
    double ox = prevx;
    double oy = prevy;
	
	double x2,y2,xtest,ytest,DX,DY,cord,DXtest,DYtest;
	double t,R, angle,dx1,dx2,dy1,dy2,L1squared,L2squared;
	
    if (fp!=NULL)
	{
		double t1,t2;
		double test;
		double step;
		double Zero = 0.000001;
		double angle;
		double tol = seg_arc_limit *3.14/180;

		t1  = 0.0;
		step = 1.0/4.0;
		double x1 = pow(1.0-t1, 2)*prevx + 2*t1*(1.0-t1)*control->x + t1*t1*to->x;
		double y1 = pow(1.0-t1, 2)*prevy + 2*t1*(1.0-t1)*control->y + t1*t1*to->y;
		
		while (t1<1)
		{
			t2 = t1 + step;
			if (t2 >= 1.0) t2 = 1.0;
			x2 = pow(1.0-t2, 2)*prevx + 2*t2*(1.0-t2)*control->x + t2*t2*to->x;
			y2 = pow(1.0-t2, 2)*prevy + 2*t2*(1.0-t2)*control->y + t2*t2*to->y;

			test = (t1+t2)/2;
			xtest = pow(1.0-test, 2)*prevx + 2*test*(1.0-test)*control->x + test*test*to->x;
			ytest = pow(1.0-test, 2)*prevy + 2*test*(1.0-test)*control->y + test*test*to->y;

			DX = x2-x1;
			DY = y2-y1;
			cord = sqrt(DX*DX + DY*DY);
			DXtest = xtest-(x1+x2)/2;
			DYtest = ytest-(y1+y2)/2;
			t = sqrt(DXtest*DXtest + DYtest*DYtest);
			R = (cord*cord/4 + t*t)/(2*t);
			angle = 2 * asin((cord/2)/R); 
			
			dx1 = (xtest - x1);
			dy1 = (ytest - y1);
			L1squared = dx1*dx1 + dy1*dy1;
			
			dx2 = (x2 - xtest);
			dy2 = (y2 - ytest);
			L2squared = dx2*dx2 + dy2*dy2;
			
			if ((L1squared < Zero) or (L2squared < Zero)) angle=0.0;
						
            if (angle > tol)
			{
				step = step/2.0;
				//printf("L1 = %f L2 = %f cos_angle = %f angle = %f\n",L1,L2,cos_angle,acos(cos_angle)*180/3.14);
			}
            else
			{
				fprintf((FILE*)fp, "L %f,%f,%f,%f \n", x1*factor, y1*factor, (double)x2*factor, (double)y2*factor);
				step = step*2;
				t1 = t2;
				x1 = x2;
				y1 = y2;	
			}
		}
	}

    prevx = to->x;
    prevy = to->y;
    if (to->y>yMax)
	{
        yMax = to->y;
    }
    return 0;
}

int cubicTo(FT_Vector* control1, FT_Vector* control2, FT_Vector* to, void* fp) {
    if (fp!=NULL) {
		//printf("\n\n ---------          Cubic Bezier Curve Found!  --------------\n\n\n");
        fprintf((FILE*)fp, "L %f,%f,%f,%f \n", prevx*factor, prevy*factor,
                (double)to->x*factor, (double)to->y*factor);
    }
    prevx = to->x;
    prevy = to->y;

    if (to->y>yMax) {
        yMax = to->y;
    }
    return 0;
}

/**
 * Converts one single glyph (character, sign) into CXF.
 */
FT_Error convertGlyph(FT_ULong charcode) {
    FT_Error error;
    FT_Glyph glyph;

	// load glyph
    error = FT_Load_Glyph(face,
                          FT_Get_Char_Index(face, charcode),
                          FT_LOAD_NO_BITMAP | FT_LOAD_NO_SCALE);
    if (error) {
        std::cout << "FT_Load_Glyph: error\n";
    }

    FT_Get_Glyph(face->glyph, &glyph);
    FT_OutlineGlyph og = (FT_OutlineGlyph)glyph;
    if (face->glyph->format != ft_glyph_format_outline) {
        std::cout << "not an outline font\n";
    }

	// write glyph header
    if (fpCxf!=NULL) {
        fprintf(fpCxf, "\n[#%04X]\n", (unsigned int)charcode);
    }

	// trace outline of the glyph
    error = FT_Outline_Decompose(&(og->outline),&funcs, fpCxf);

    if (error==FT_Err_Invalid_Outline) {
        std::cout << "FT_Outline_Decompose: FT_Err_Invalid_Outline\n";
    } else if (error==FT_Err_Invalid_Argument) {
        std::cout << "FT_Outline_Decompose: FT_Err_Invalid_Argument\n";
    } else if (error) {
        std::cout << "FT_Outline_Decompose: error: " << error << "\n";
    }

    return error;
}

/**
 * Main.
 */
int main(int argc, char* argv[]) {
    FT_Error error;
    std::string fTtf;
    std::string fCxf;

    // init:
    fpCxf = NULL;
	seg_arc_limit = 50; //degrees
    name = "Unknown";
    letterSpacing = 3.0;
    wordSpacing = 6.75;
    lineSpacingFactor = 1.0;
    author = "Unknown";
    extended_chars = 0;

    // handle arguments:
    if (argc<2) {
        std::cout << "Usage: ttf2cxf <options> <ttf file> <cxf file>\n";
        std::cout << "  ttf file: An existing True Type Font file\n";
        std::cout << "  cxf file: The CXF font file to create\n";
		std::cout << "options are:\n";
        std::cout << "  -s seg_arc_limit               Arc angle approximation limit (double)\n";
        std::cout << "  -a author                      Author of the font. Preferably full name and e-mail address\n";
        std::cout << "  -l letter spacing              Letter spacing (float)\n";
        std::cout << "  -w word spacing                Word spacing (float)\n";
        std::cout << "  -f line spacing factor         Default is 1.0 (float)\n";
        std::cout << "  -e enable extended characters\n";
        exit(1);
    }

	for (int i=1; i<argc; ++i) {
		if (!strcmp(argv[i], "-s")) {
			++i;
			seg_arc_limit = atof(argv[i]);
			if (seg_arc_limit==0) seg_arc_limit = 45;
		}
		else if (!strcmp(argv[i], "-a")) {
			++i;
			author = argv[i];
		}
		else if (!strcmp(argv[i], "-l")) {
			++i;
			letterSpacing = atof(argv[i]);
		}
		else if (!strcmp(argv[i], "-w")) {
			++i;
			wordSpacing = atof(argv[i]);
		}
		else if (!strcmp(argv[i], "-f")) {
			++i;
			lineSpacingFactor = atof(argv[i]);
		}
		else if (!strcmp(argv[i], "-e")) {
                        extended_chars = 1;
		}

	}

    fTtf = argv[argc-2];
    fCxf = argv[argc-1];


    if (fTtf == "TEST")
	{
		std::cout << "TTF2CXF TEST MESSAGE";
		exit(0);
	}

    if (STDOUT != 1) std::cout << "TTF file: " << fTtf.c_str() << "\n";
    if (STDOUT != 1) std::cout << "CXF file: " << fCxf.c_str() << "\n";

    // init freetype
    error = FT_Init_FreeType(&library);
    if (error) {
        std::cerr << "Error: FT_Init_FreeType\n";
    }

    // load ttf font
    error = FT_New_Face(library,
                        fTtf.c_str(),
                        0,
                        &face);
    if (error==FT_Err_Unknown_File_Format) {
        std::cerr << "FT_New_Face: Unknown format\n";
    } else if (error) {
        std::cerr << "FT_New_Face: Unknown error\n";
    }

    if (STDOUT != 1) std::cout << "family: " << face->family_name << "\n";
	name = face->family_name;
    if (STDOUT != 1) std::cout << "height: " << face->height << "\n";
    if (STDOUT != 1) std::cout << "ascender: " << face->ascender << "\n";
    if (STDOUT != 1) std::cout << "descender: " << face->descender << "\n";

    // find out height by tracing 'A'
    yMax = -1000;
    convertGlyph(65);
    factor = 1.0/(1.0/9.0*yMax);

    if (STDOUT != 1) std::cout << "factor: " << factor << "\n";

    // write font file:    
    if (fCxf=="STDOUT" || fCxf=="-")
      {
	STDOUT = 1;
	fpCxf = stdout;
      }
    else
      {
	fpCxf = fopen(fCxf.c_str(), "wt");
      }

    if (fpCxf==NULL) {
      std::cerr << "Cannot open file " << fCxf.c_str() << " for writing.\n";
      exit(2);
    }

    // write font header
    fprintf(fpCxf, "# Format:            QCad 2 Font\n");
    fprintf(fpCxf, "# Creator:           ttf2cxf\n");
    fprintf(fpCxf, "# Version:           1\n");
    fprintf(fpCxf, "# Name:              %s\n", name.c_str());
    fprintf(fpCxf, "# LetterSpacing:     %f\n", letterSpacing);
    fprintf(fpCxf, "# WordSpacing:       %f\n", wordSpacing);
    fprintf(fpCxf, "# LineSpacingFactor: %f\n", lineSpacingFactor);
    fprintf(fpCxf, "# Author:            %s\n", author.c_str());
    fprintf(fpCxf, "\n");

    //uint 
    FT_UInt first;
    FT_Get_First_Char(face, &first);

    FT_ULong  charcode;
    FT_UInt   gindex;

	// iterate through glyphs
    charcode = FT_Get_First_Char( face, &gindex);
    int skip_cnt=0;
    while (gindex != 0) {
      // Skipping codes greater than 255 unless specifically requested by "-e" command line option
      if (charcode > 255  && extended_chars == 0)
	{
	  skip_cnt = skip_cnt+1;
	}
     else
	{
	  convertGlyph(charcode);
	}

      charcode = FT_Get_Next_Char(face, charcode, &gindex);
    }
    if (skip_cnt > 0) printf("Skipped %d characters...\n",skip_cnt);

	return 0;
}
