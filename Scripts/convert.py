#! /usr/bin/python
#
# Confidential Information of Telekinesys Research Limited (t/a Havok). Not for
# disclosure or distribution without Havok's prior written consent. This
# software contains code, techniques and know-how which is confidential and
# proprietary to Havok. Product and Trade Secret source code contains trade
# secrets of Havok. Havok Software (C) Copyright 1999-2013 Telekinesys Research
# Limited t/a Havok. All Rights Reserved. Use of this software is subject to
# the terms of an end user license agreement.
#

"""
convert.py - The main script of Havok FBX conversion suite.
"""

import sys
import re

from optparse import OptionParser

import projectanarchy.fbx
import projectanarchy.utilities

COMMAND_LINE_OPTIONS = (
    (('-f', '--filename',),
     {'action': 'store',
      'dest': 'filename',
      'help': "FBX file to convert/import"}),
    (('-i', '--interactive',),
     {'action': 'store_true',
      'dest': 'interactive',
      'default': False,
      'help': "Use interactive mode which will bring up the standalone filter manager"}),
    (('-s', '--semi-interactive',),
     {'action': 'store',
      'dest': 'semiinteractive',
      'default': '.',
      'help': "Bring up the standalone filter manager only when the output filename matches a regular expression"}),      
    (('-q', '--quiet',),
     {'action': 'store_false',
      'dest': 'verbose',
      'default': True,
      'help': "Don't print out status updates"}),
    (('-a', '--anim',),
     {'action': 'store_true',
      'dest': 'anim',
      'default': False,
      'help': "Bring up interactive mode for the animated files"}),
    (('-o', '--overwrite',),
     {'action': 'store_true',
      'dest': 'overwrite',
      'default': False,
      'help': "Overwrite any existing output files"}),
    (('-k', '--keep',),
     {'action': 'store_true',
      'dest': 'keep',
      'default': False,
      'help': "Keeps all intermediate files around instead of deleting them"}),
    (('-c', '--keepfilterset',),
     {'action': 'store_true',
      'dest': 'keepconfig',
      'default': False,
      'help': "Keeps intermediate configuration filter set files around instead of deleting them"}))


def main():
    """
    Exports/converts the FBX file passed in as an argument.
    """

    parser = OptionParser('')
    for options in COMMAND_LINE_OPTIONS:
        parser.add_option(*options[0], **options[1])
    (options, _) = parser.parse_args()

    # Print the header
    if options.verbose:
        projectanarchy.utilities.print_line()
        print("Havok FBX Importer")
        projectanarchy.utilities.print_line()
        
    # fail fast, check the --semi-interactive regex is valid
    if options.semiinteractive != '.':
      try:
        re.compile( options.semiinteractive )
      except:
        raise ValueError("Error: The semi-interactive regular expression '" + options.semiinteractive + "' is not valid")

    fbx_file = options.filename
    if not fbx_file and len(sys.argv) > 1:
        fbx_file = sys.argv[len(sys.argv) - 1]

    success = False

    if not fbx_file:
        print("Missing FBX input filename!")
    else:
        success = projectanarchy.fbx.convert(fbx_file, options)

    return success

if __name__ == "__main__":
    SUCCESS = main()