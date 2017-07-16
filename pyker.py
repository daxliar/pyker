#
# Create a C include file with the content from files from a source directory.
#
# Usage: pyker.py <source-directory> <destination-header-file>
#
# https://github.com/daxliar/pyker
#

import os
import sys
import re
import struct

if len(sys.argv) != 3:
    print "usage: " + sys.argv[0] + " <source-directory> <destination-header-file>"
else:
    srcDir = sys.argv[1]
    dstHdr = sys.argv[2]
    if not os.path.isdir(srcDir):
        print srcDir + " isn't a directory!"
        sys.exit(1)

    # list resources
    resources = []
    for root, dirnames, filenames in os.walk(srcDir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                resources.append(filepath)

    # open header file
    hdrFile = open(dstHdr, 'w')
    try:
        # write header part
        define =  re.sub(' +', '_', re.sub('(\ |\.)+',' ', os.path.basename(dstHdr).upper())) + "_INCLUDED"
        hdrFile.write( '#ifndef ' + define + '\n')
        hdrFile.write( '#define ' + define + '\n\n')

        # write const number of resources
        count = len(resources)
        hdrFile.write( 'const unsigned int fileCount = ' + str(count)  + ';\n\n')

        # write resources filenames
        hdrFile.write( 'const char* fileNames[] = {\n')
        for resource in resources:
            hdrFile.write( '\t\"' + os.path.relpath(resource, srcDir).encode('string-escape') + '\",\n' )
        hdrFile.write( '0 };\n\n')

        # write files content
        hdrFile.write( 'const char * fileData[][' + str(count)  + '] = {')
        for resource in resources:
            file = open(resource,"rb")
            hexline = ""
            byteread = 0
            try:
                finalFilePath = re.sub('\\\\','/', os.path.relpath(resource, srcDir))
                print "Processing " + finalFilePath
                hdrFile.write( '\n// ' + finalFilePath + '\n{\n' )
                byte = file.read(1)
                while byte != "":
                    byteread = byteread + 1
                    value = struct.unpack('B', byte[0])[0]
                    hexline = hexline + '\\x' + format( value, '02x')
                    if byteread == 16:
                        hdrFile.write( '\t\"' + hexline + '\"\n')
                        hexline = ""
                        byteread = 0
                    byte = file.read(1)
                if byteread > 0:
                    hdrFile.write( '\t\"' + hexline + '\"\n},')
                else:
                    hdrFile.write( '},' )
            finally:
                file.close()
        hdrFile.write( '\n};\n\n')
        hdrFile.write( '#endif // ' + define + '\n')
    finally:
        hdrFile.close()