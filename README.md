FBX Importer
============

The FBX file format is used by a lot of applications today including Blender, Modo, and many more. Since Project Anarchy doesn't directly support FBX format, this tool will take a FBX file and automatically convert it to a format that can be used with Project Anarchy. It will:

- Convert FBX files with animated objects to rig and animation files that can be used with Animation Studio
- Convert FBX files with static objects to Vision static mesh files (.vmesh)

For the most recent packaged version, go to the main Project Anarchy download page: [http://www.projectanarchy.com/download][3]

Here are the tools included in the package:

1. **Bin\\Tools\\FBXConverter.exe** - This takes an FBX file as input, calls **FBXImporter.exe** to generate the HKX files, and then it takes the outputted files and generates corresponding Vision or Animation Studio compatible files by calling the Havok Content Tools standalone filter manager (hctStandAloneFilterManager.exe). If you just have source, then this won't exist until you run the packaging step (see Packaging section below), which converts the **Tools\\FBXImporter\\Bin\\Scripts\\convert.py** script into an executable.
2. **Bin\\Tools\\PreviewTool.exe** - Drag/drop outputted hkx/hkt files onto this executable and it will attempt to find the Havok Content Tools preview tool (ToolStandAlone.exe) and use that to preview the asset. You can just as easily 
3. **Tools\\FBXImporter\\Bin\\FBXImporter.exe** - Takes an FBX file as input and converts it to a Havok scene file (e.g. a tag file with extension .hkx or .hkt). Usually won't need to call this manually as **FBXConverter.exe** will call it.

Usage
-----

Extract the package (e.g. **ProjectAnarchy_FBXImporter_20130730.zip**) to the root of your Anarchy SDK folder (e.g. **C:\\Projects\\Havok\\AnarchySDK**). To convert an FBX, just drag/drop your FBX file onto the executable. There are also some command line options available, which you can read more about below. The process that **FBXConverter.exe** (i.e. the executable version of **Tools\\FBXImporter\\Bin\\Scripts\\convert.py**) does behind the scenes is:

1. Call **Tools\\FBXImporter\\Bin\\FBXImporter.exe** on the FBX which will generate an HKT (i.e. Havok Scene File) for each take / animation-stack in the FBX.
2. Generates an HKO / filter-set for each HKT using one of the templates in **Tools\\FBXImporter\\Scripts\\configurations**.
3. Call **hctStandAloneFilterManager.exe** on each HKT and pass in the corresponding generated HKO file. For example, it might call it like this: ```hctStandAloneFilterManager.exe -s StaticBox.hko StaticBox.hkt```

### Command Line Options

- **Bin\\Tools\\FBXConverter.exe** [Options] model.fbx

Options:

- **-h, --help**: Show help message and exit
- **-i, --interactive**: Use interactive mode which will bring up the standalone filter manager for all output files
- **-s, --semi-interactive**: Bring up the standalone filter manager only when the output filename matches a regular expression (see example below).
- **-a, --anim**: Export model files along with animation files used just for Vision and not for Havok Animation Studio. One model will be exported for each take.
- **-o, --overwrite**: Overwrite any configuration files or output files that may already exist on disk.
- **-q, --quiet**: Don't print out status updates
- **-k, --keep**: Keeps all intermediate files around instead of deleting them
- **-c, --keepfilterset**: Keeps intermediate configuration filter set files around instead of deleting them
 
#### Example: -s, --semi-interactive

**Example 1:** Bring up the standalone filter manager only when the "walk" animation file is being processed:

`Bin\Tools\FBXConverter.exe** -s walk model.fbx`

This will bring up the filter manager when the `model__out_anim_walk.hkx` output file is being processed.

**Example 2:** Bring up the standalone filter manager only when any animation file is being processed:

`Bin\Tools\FBXConverter.exe** -s anim model.fbx`

This will bring up the filter manager when the `model__out_anim_walk.hkx` and `model__out_anim_idle.hkx` output file is being processed.

Note: You can use any valid [Python regular expression](https://docs.python.org/2/library/re.html "Python regular expression") to match against the filenames of the output files being processed.

### Static Mesh (Vision)

If you have an FBX file named **StaticBox.fbx** that has no animations, passing it to **convert.py** will generate the following files:

- ```StaticBox.vmesh```

Intermediate files (must specifiy --keep command line option if you want them):

- ```StaticBox.hkt``` (must specifiy --keep command line option)
- ```StaticBox.hko``` - The configuration (filter set) that's passed to the filter tools. (must specifiy --keep command line option)

Some packages, like Blender, will always export an animation stack which will make the converter think that it's an animation.

### Animation Studio

If you have an FBX file named **AnimatedBox.fbx** that has one animation named *Bounce*, passing this to **convert.py** will generate the following files:

- ```AnimatedBox.model``` - Model file with bones so that it can be used in Vision
- ```AnimatedBox__out_rig.hkx``` - Rig file used for Animation Studio. Put this in the **CharacterAssets** folder.
- ```AnimatedBox__out_anim_Bounce.hkx``` - Contains animation data that is compressed and includes extracted motion. Put this in the **Animations** folder.

Intermediate files (.hkt/.hko -specifiy **--keep** command line option if you want them):

- ```AnimatedBox.hkt```
- ```AnimatedBox.hko``` - Filter set used to generate ```AnimatedBox__out_rig.hkx```.
- ```AnimatedBox_Bounce.hkt```
- ```AnimatedBox_Bounce.hko``` - Filter set used to generate ```AnimatedBox__out_anim_Bounce.hkx```.

Intermediate filter set files (.hko -specifiy **--keepfilterset** command line option if you want them):

- ```AnimatedBox.hko``` - Filter set used to generate ```AnimatedBox__out_rig.hkx```.

If a filter set file does not exist when you run the tool then one will be created from one of the templates included.
If you want to keep these filter sets for later tuning of the output then specify **--keepfilterset** on the command line.
If you do not specify the  **--keepfilterset** parameter then the tool will still only clean up .hko files if they were created during the current run, Any previously existing .hko files will be left alone.

These files are to be used with Animation Studio.

### Model (Vision)

If you have an FBX file named **StaticBox.fbx**, passing it to **convert.py** will generate the following files:

- ```StaticBox.model```

Intermediate files (must specifiy --keep command line option if you want them):

- ```StaticBox.hkt```
- ```StaticBox.hko``` - The configuration (filter set) that's passed to the filter tools.

Dependencies
------------

* [Visual C++ 2010][1]
* [Python 2.7.X][2]
* [FBX SDK 2014.1 VS 2010][4]
* [Python Tools for Visual Studio][5] - Useful for debugging your projects and we include a .pyproj/.sln so you'll need to have it installed to successfully open the solution.
* [py2exe][6] - Needed if you're going to create a package

Compiling
---------

1. Install the Project Anarchy SDK from the [homepage][3]
    * Make sure the **Havok Content Tools** (32bit or 64bit) and **Havok Anarchy SDK** are downloaded and installed
2. Install [FBX SDK 2014.1 VS 2010][4]
2. Git clone the repository into **$(AnarchySDK)\\Tools\\FBXImporter**. From **$(AnarchySDK)\\Tools** on the command line execute the following:
    * ```git clone https://github.com/projectanarchy/fbximporter.git FBXImporter```
3. Open **$(AnarchySDK)\\Tools\\FBXImporter\\Workspace\\FBXImporter_C++.sln**
    * Build the project using **Dev DLL** Configuration. This will output an executable to: **$(AnarchySDK)\\Tools\\FBXImporter\\Bin\\FBXImporter.exe**

Packaging
---------

Although the steps for generating packages is simple, there are a lot of caveats with generating binaries with [py2exe][6] and sometimes executables generated from different versions of Windows behave differently.
 
1. Install [py2exe][6]
2. Run **$(AnarchySDK)\\Tools\\FBXImporter\\Package\\package.bat**
3. If all went well, you should have a package in the **$(AnarchySDK)\\Tools\\FBXImporter\\Package\\Output** folder

License
-------

Confidential Information of Havok.  (C) Copyright 1999-2013 Telekinesys Research Limited t/a Havok. All Rights Reserved. The Havok Logo, and the Havok buzzsaw logo are trademarks of Havok.  Title, ownership rights, and intellectual property rights in the Havok software remain in Havok and/or its suppliers.

Use of this software for evaluation purposes is subject to and indicates acceptance of the End User licence Agreement for this product. A copy of the license is included with this software and is also available from salesteam@havok.com.

[1]: http://www.microsoft.com/visualstudio/eng/downloads#d-2010-express
[2]: http://www.python.org/download/releases/2.7.5/
[3]: http://www.projectanarchy.com/download
[4]: http://usa.autodesk.com/adsk/servlet/pc/item?siteID=123112&id=10775847
[5]: http://pytools.codeplex.com/
[6]: http://www.py2exe.org/