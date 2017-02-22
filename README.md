# texturetool
A command line tool to convert TexturePacker file format.
my code is only suitable for our project for now, you may feel confused how to use.
the project is works on list based resource management auto generate set of pvr resource for ios.

### install

`pip install textool`

### update

`pip install -U textool`

### usage
```
$ textool -h
usage:
textool build project/tag/v2.0 -i project/tag/v1.0 -r
textool build project/tag/v2.0 -i project/tag/v1.0 -r -if ui/item0 ui/item1

positional arguments:
  command            command to use 
			[build] auto compair flist and convert to pvr.ccz 
  path		     tag directory

optional arguments:
  -h, --help            show this help message and exit

For file:
  -i input, --input		input directory to compair
  -if image_folder, --image_folder		specified image folder to convert

For directory:
  -r, --recursive

For option
  -opt --image_option			RGBA8888 PVRTC4 default is RGBA8888
  -l, --log

