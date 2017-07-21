# Sleuthkit mmls to Partition Diagram
Python script for creating a partition diagram as a latex vector graphic from the output for sleuthkit's mmls 

## Usage
```
mmls partition.dd | python partitionTableDiagram.py
```
```
usage: partitionTableDiagram.py [-h] [-i INPUT] [-o OUTPUT]

Python script for creating a partition diagram as a latex vector graphic from
the output for sleuthkit's mmls

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        output of mmls. default: read from stdin (pipe mmls to
                        this script)
  -o OUTPUT, --output OUTPUT
                        latex output file. default: partitionDiagram.tex
```

## Example
Input:
```
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0016777215   0016775168   Linux (0x83)
003:  -------   0016777216   0016779263   0000002048   Unallocated
004:  Meta      0016779262   0018872319   0002093058   DOS Extended (0x05)
005:  Meta      0016779262   0016779262   0000000001   Extended Table (#1)
006:  001:000   0016779264   0018872319   0002093056   Linux Swap / Solaris x86 (0x82)
007:  -------   0018872320   0018874367   0000002048   Unallocated
```
Output:
