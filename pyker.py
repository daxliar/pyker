import os
import sys
import re
import struct

if len(sys.argv) != 3:
    print "usage: " + sys.argv[0] + " <source-directory> <destination-header>"
else:
    srcDir = sys.argv[1]
    dstHdr = sys.argv[2]
    if not os.path.isdir(srcDir):
        print srcDir + " isn't a directory!"
        sys.exit(1)

    # Get resources
    resources = []
    for root, dirnames, filenames in os.walk(srcDir):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                resources.append(filepath)

    # open header file
    hdrFile = open(dstHdr, 'w')
    try:
        # Header part
        define =  re.sub(' +', '_', re.sub('(\ |\.)+',' ', os.path.basename(dstHdr).upper())) + "_INCLUDED"
        hdrFile.write( '#ifndef ' + define + '\n')
        hdrFile.write( '#define ' + define + '\n\n')

        # generate resources list
        hdrFile.write( 'const char* resourceFiles[] = {\n')
        for resource in resources:
            hdrFile.write( '\t\"' + re.sub('\\\\','/', os.path.relpath(resource, srcDir)) + '\",\n' )
        hdrFile.write( '0 };\n\n')

        # process file content
        count = len(resources) + 1
        hdrFile.write( 'unsigned char filesData[] = {\n')
        hexline = ""
        byteread = 0
        for resource in resources:
            file = open(resource,"rb")
            try:
                finalFilePath = re.sub('\\\\','/', os.path.relpath(resource, srcDir))
                print "Processing " + finalFilePath
                byte = file.read(1)
                while byte != "":
                    byteread = byteread + 1
                    value = struct.unpack('B', byte[0])[0]
                    hexline = hexline + '0x' + format( value, '02x') + ','
                    if byteread == 32:
                        hdrFile.write( '\t' + hexline + '\n')
                        hexline = ""
                        byteread = 0
                    byte = file.read(1)
            finally:
                file.close()
        if byteread > 0:
            hdrFile.write( '\t' + hexline + '\n')
        hdrFile.write( '};\n\n')
        hdrFile.write( '#endif // ' + define + '\n')

    finally:
        hdrFile.close()