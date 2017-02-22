A command line tool to convert TexturePacker file format.

### install

`pip install textool`

### update

`pip install -U textool`

### usage
```
$ textool -h
usage:
textool ../btn.plist
textool ../btn.plist -i ../btn.png
textool ../data
textool ../data -r

positional arguments:
  path                  plist file name or directory

optional arguments:
  -h, --help            show this help message and exit

For file:
  -i image_file, --image_file image_file
                        specified image file for plist

For directory:
  -r, --recursive
```



