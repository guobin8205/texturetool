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
textool build D:/project/tag/v2.0 -i D:/project/tag/v1.0 -l
textool build D:/project/tag/v2.0 -i D:/project/tag/v1.0 -l -if ui/item0 ui/item1
textool unpack D:/project/tag/v2.0/ui/button.plist -o D:/prj/test
textool pack D:/project/tag/v2.0/ui -o D:/prj/test -r
textool convert D:/project/tag/v2.0/ui/button.plist -o D:/prj/test
textool convert D:/project/tag/v2.0 -o D:/prj/test -r -if *

positional arguments:
  command            command to use 
			[build] auto compair flist and convert to pvr.ccz 
			[unpack] unpack plist file to pngs
      [pack] pack a folder to plist
			[convert] convert png pvr.ccz to pvr.ccz
  path		     tag directory

optional arguments:
  -h, --help            show this help message and exit

For file:
  -i input, --input		input directory to compair when use command build
  -o output, --output		output directory when use command unpack or convert
  -if image_folder, --image_folder	specified image folder to convert,use * to convert all png or pvr.ccz

For directory:
  -r, --recursive        

For option
  -tf  --texture_format   value is png or pvr2ccz default is png
  -opt --image_option			RGBA8888 PVRTC4 default is RGBA8888
  -mpk --multipack        texturepacker multipack
  -l, --log
  -nti --no_trim_image    a.plist for some specified not suit trim
  -igl --ignore_list      ignore folder when pack a directory
  -oo  --other_option     other texturePacker option. not support space and -, need replace by + and _

the command unpack texturepacker plist files base on https://github.com/justbilt/untp