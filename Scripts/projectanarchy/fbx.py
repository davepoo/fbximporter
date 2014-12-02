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
Handles calling the FBX Importer executable and then processing the result
of that with Havok Content Tools filter manager. Given an FBX file it will:
    - Convert animated FBX files to rig and animation files
    - Convert static FBX files to Vision static mesh files (.vmesh)
"""

import sys
import os
import traceback

import utilities
from hct import HCT


class HavokScene():
    """
    Simple class that contains all the data needed to re-export
    a scene file that could describe an animation or mesh
    """
    def __init__(self, sceneFile, filter_set_file, asset_path,
                 output_path, scene_length, is_root, target_file):
        self.sceneFile = sceneFile
        self.filter_set_file = filter_set_file
        self.asset_path = asset_path
        self.output_path = output_path
        self.scene_length = scene_length
        self.is_root = is_root
        self.target_file = target_file

        return

def convert(fbx_file, options):
    """
    Takes as input an FBX file and converts it to files that can be
    used by either Vision or Animation Studio.
    """

    success = False

    # These are the labels that are spit out by the FBX Importer that
    # we use to parse out the relevant information about the export
    labelAnimationStacks = "Animation stacks:"
    labelTagFile = "Saved tag file:"
    labelSceneLength = "Scene length:"
    labelBones = "Bones:"

    def log(message):
        """ Only print a message if we're in options.verbose mode """
        if options.verbose:
            print(message)

    try:
        inputFile = os.path.abspath(fbx_file)
        if not os.path.isfile(inputFile):
            log("Input file does not exists! [%s]" % fbx_file)
            return False
        else:
            log("Input FBX file: %s" % inputFile)

        currentDirectory = os.path.dirname(os.path.realpath(__file__))

        # If this is a compiled script, then this is going to be 'Tools\FBXImporter.exe\projectanarchy' so
        # it needs some special processing to make it a valid folder
        if '.exe' in currentDirectory:
            extensionIndex = currentDirectory.find('.exe')
            endSlashIndex = currentDirectory.rfind('\\', 0, extensionIndex)
            currentDirectory = currentDirectory[0:endSlashIndex]

        root = os.path.join(currentDirectory, "../../Tools/FBXImporter")
        fbxImporter = os.path.join(root, "Bin/FBXImporter.exe")
        if not os.path.isfile(fbxImporter):
            root = os.path.join(currentDirectory, "../../")
            fbxImporter = os.path.join(root, "Bin/FBXImporter.exe")

        fbxImporter = os.path.abspath(fbxImporter)
        if not os.path.exists(fbxImporter):
            log("Failed to find FBX importer!")
            return False

        # Save
        configPath = os.path.abspath(os.path.join(root, "Scripts/configurations"))

        inputDirectory = os.path.dirname(inputFile)

        log("Converting FBX to Havok Scene Format...")
        fbxImporterOutput = utilities.run([fbxImporter, inputFile], options.verbose)

        parseIndex = fbxImporterOutput.find(labelTagFile)
        if parseIndex == -1:
            log("Conversion to FBX failed!")
            log(utilities.line())
            print(fbxImporterOutput)
            return False

        animationStacks = int(utilities.parse_text(
            fbxImporterOutput,
            labelAnimationStacks))
        
        numBones = int(utilities.parse_text(
            fbxImporterOutput,
            labelBones))

        havokScenes = []
        isRootNode = True
        isAnimationExport = (animationStacks > 0) and (numBones > 0)
        intermediate_files = []

        # Parse the output of the FBXImporter
        while parseIndex >= 0:
            sceneFile = utilities.parse_text(fbxImporterOutput, labelTagFile, parseIndex)
            sceneFile = os.path.join(inputDirectory, sceneFile)
            intermediate_files.append(sceneFile)

            (input_file_path, _) = os.path.splitext(sceneFile)
            target_filename = os.path.basename(input_file_path)

            if isRootNode:
                rootName = target_filename
            else:
                animName = target_filename[len(rootName) + 1:]

            sceneLength = float(utilities.parse_text(
                fbxImporterOutput,
                labelSceneLength,
                parseIndex))

            def _createScene(configFile, outputConfigFile, targetFilename):
                configFile = os.path.abspath(os.path.join(
                    currentDirectory,
                    configFile))
                outputConfigFile = os.path.abspath(outputConfigFile + ".hko")
                
                updateConfigFile = False

                try:
                    with open(outputConfigFile):
                        updateConfigFile = options.overwrite
                except IOError:
                    updateConfigFile = True

                if updateConfigFile:
                    with open(outputConfigFile, 'wt') as out:
                        for line in open(configFile):
                            out.write(line.replace('$(output)', targetFilename))

                havokScene = HavokScene(sceneFile=sceneFile,
                                        filter_set_file=outputConfigFile,
                                        asset_path=inputDirectory,
                                        output_path=inputDirectory,
                                        scene_length=sceneLength,
                                        is_root=isRootNode,
                                        target_file=targetFilename)
                
                
                # Keep config file if command line told us not to delete it or if it didn't exist already, 
                # otherwise it is consindered intermediate and gets removed
                if updateConfigFile and options.keepconfig == False:
                    intermediate_files.append(outputConfigFile)

                return havokScene

            if isRootNode and (not options.anim):
                # always output the Vision model file
                configFile = os.path.join(configPath, "VisionModel.hko")
                target_filename = "%s.model" % (rootName)
                havokScenes.append(_createScene(configFile, input_file_path + '_vision', target_filename))
                intermediate_files.append(input_file_path + '.anim')
                
                # output static mesh
                if not isAnimationExport:
                    configFile = os.path.join(configPath, "VisionStaticMesh.hko")
                    target_filename = "%s.vmesh" % (rootName)
                    havokScenes.append(_createScene(configFile, input_file_path, target_filename))

                # output the rig file for Animation Studio
                if isAnimationExport:
                    configFile = os.path.join(configPath, "AnimationRig.hko")
                    target_filename = "%s__out_rig.hkx" % (rootName)
                    havokScenes.append(_createScene(configFile, input_file_path + '_hat', target_filename))                
            elif (not isRootNode) and isAnimationExport:
                if options.anim:
                    configFile = os.path.join(configPath, "VisionModel.hko")
                    target_filename = "%s__out_anim_%s.model" % (rootName, animName)
                    havokScenes.append(_createScene(configFile, input_file_path, target_filename))
                else:
                    configFile = os.path.join(configPath, "Animation.hko")
                    target_filename = "%s__out_anim_%s.hkx" % (rootName, animName)
                    havokScenes.append(_createScene(configFile, input_file_path, target_filename))

            # We can break out of the loop early if this is just
            # a static mesh export
            if isRootNode and (not isAnimationExport):
                break
           
            isRootNode = False

            # Get the next file that was exported
            parseIndex = fbxImporterOutput.find(labelTagFile,
                                                   parseIndex + 1)

        log(utilities.line())
        log("Generating Vision / Animation Studio files")
        log(utilities.line())

        # Instantiate the Havok Content Tools class so that we can start
        # using it to convert over the scene files we've just exported
        havokContentTools = HCT()

        # Now go through each scene and run the standalone filter manager on each one
        for havokScene in havokScenes:
            log("Tag file: %s" % os.path.basename(havokScene.sceneFile))
            log("Filter set: %s" % os.path.basename(havokScene.filter_set_file))
            log("Output: %s" % os.path.basename(havokScene.target_file))
            log(utilities.line(True))

            interactive = False
            if options.anim:
                interactive = (".model" in havokScene.target_file) and (not havokScene.is_root)
            else:
                interactive = options.interactive

            havokContentTools.run(havokScene.sceneFile,
                                    havokScene.filter_set_file,
                                    havokScene.asset_path,
                                    havokScene.output_path,
                                    interactive)
        
        # Remove intermediate files if we didn't set the flag to keep them
        if not options.keep:
            for file in intermediate_files:
                if os.path.exists(file):
                    os.remove(file)

        success = True
    except IOError as error:
        print("I/O error({0}): {1}".format(error[0], error[1]))
        traceback.print_exc(file=sys.stdout)
        utilities.wait()
    except:
        print("Unexpected error: %s" % sys.exc_info()[0])
        traceback.print_exc(file=sys.stdout)
        utilities.wait()

    return success