import sys
import os
import argparse
import fileinput
from subprocess import Popen, PIPE, STDOUT
import humanize

try:
    from subprocess import DEVNULL
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'r+b')

argParser = argparse.ArgumentParser(description="Python script for creating a partition diagram as a latex vector graphic from the output for sleuthkit's mmls")
argParser.add_argument('-i', '--input', help='output of mmls. default: read from stdin (pipe mmls to this script)')
argParser.add_argument('-o', '--output', default='partitionDiagram.tex', help='latex output file. default: partitionDiagram.tex')
args = argParser.parse_args()

args.output = os.path.abspath(args.output)
if args.input is None:
    inputData = sys.stdin.readlines()
else:
    with open(args.input, 'r') as inputFile:
        inputData = inputFile.readlines()

bytes = 1
partitions = []
for line in inputData:
    line = line.split()
    if not len(line):
        continue
    if line[0].startswith('Unit'):
        for word in line:
            if 'byte' in word:
                bytes = int(word.replace('-byte', ''))
    elif ':' in line[0]:
        partNum = line[0].replace(':','')
        partNum = int(partNum) if len(partNum) else 0
        if partNum < 1:
            continue
        name = ''
        if len(line) > 5:
            for i in range(5, len(line)):
                name += (line[i]) + ' '
        if 'xtended' in name:
            continue
        name = name.replace('#', '\#').strip()
        length = humanize.naturalsize(int(line[4])*bytes)
        if not length[-1] == 'B':
            length += 'B'
        partitions.append({'start': int(line[2]), 'end': int(line[3]), 'size': length, 'name': name, 'length': 0, 'color1': '', 'color2': ''})
        
if not len(partitions):
    print('Did not find any partitions')
    sys.exit(0)

colors = [['myBlue','myLightBlue'],['myOrange','myLightOrange'],['myRed','myLightRed'],['myGreen','myLightGreen'],['myBlueB','myLightBlueB']]
colorIdx = 0
for partition in partitions:
    length = 10.0 * float(partition['end']-partition['start']) / float(partitions[-1]['end'])
    if length < 0.1:
        length = 0.1
        partition['color1'] = 'grey'
        partition['color2'] = 'lightGrey'
    else:
        length = round(length, 2)
        partition['color1'] = colors[colorIdx][0]
        partition['color2'] = colors[colorIdx][1]
        colorIdx = colorIdx+1 if colorIdx < len(colors)-1 else 0
    partition['length'] = length
    
latex = '\documentclass[margin=5mm]{standalone}\n' \
    + '\usepackage{tikz, calc, xcolor, tikz-3dplot}\n' \
    + '\usetikzlibrary{decorations.pathreplacing, arrows}\n' \
    + '\\begin{document}' + '%\n' \
    + '\\newcommand{\partition}[5]{% no name\n' \
    + '\draw[draw=black,fill=#3,opacity=#5] (#1,0,0) -- ++(#2,0,0) -- ++(0,1,0) -- ++(-#2,0,0) -- cycle;% front\n' \
    + '\draw[draw=black,fill=#3,opacity=#5] (#1+#2,0,0) -- ++(0,0,-0.33) -- ++(0,1,0) -- ++(0,0,0.33) -- cycle;% right\n' \
    + '\draw[draw=black,fill=#4,opacity=#5] (#1,1,0) -- ++(#2,0,0) -- ++(0,0,-0.33) -- ++(-#2,0,0) -- cycle;% top\n' + '}%\n'+ '%\n' \
    + '\\newcommand{\partitionBraceAbove}[6]{% with brace above\n' \
    + '\partition{#1}{#2}{#3}{#4}{#5}%\n' \
    + '\draw[decorate,decoration={brace,amplitude=8},align=center] (#1,1,-0.33) -- ++ (#2,0,0) node [midway,above,yshift=5] {#6};% Brace with Text above\n' + '}%\n%\n' \
    + '\\newcommand{\partitionBraceBelow}[6]{% with brace below\n' \
    + '\partition{#1}{#2}{#3}{#4}{#5}%\n' \
    + '\draw[decorate,decoration={brace,amplitude=8,mirror},align=center] (#1,0,0) -- ++ (#2,0,0) node [midway,below,yshift=-8] {#6};% Brace with Text below\n}%\n%\n' \
    + '\\newcommand{\partitionArrowAbove}[7]{% with arrow above\n' \
    + '\partition{#1}{#2}{#3}{#4}{#5}%\n' \
    + '\\node[inner sep=2.5,align=center,xshift=#7] (Name) at (#1+0.5*#2,1.75,-0.33) {#6};% description\n' \
    + '\draw[->, line width=0.75pt] (Name) -- (#1+0.5*#2,1.05,-0.33);% arrow\n}%\n%\n' \
    + '\\newcommand{\partitionArrowBelow}[7]{% with arrow below\n' \
    + '\partition{#1}{#2}{#3}{#4}{#5}%\n' \
    + '\\node[inner sep=2.5,align=center,xshift=#7] (Name) at (#1+0.5*#2,-0.75,0) {#6};% description\n' \
    + '\draw[->, line width=0.75pt] (Name) -- (#1+0.5*#2,-0.05,0);% arrow\n}%\n%\n' \
    + '\\newcommand{\partitionTextFront}[6]{% text on front side\n' \
    + '\partition{#1}{#2}{#3}{#4}{#5}%\n' \
    + '\\node[align=center] at (#1+0.5*#2,0.5,0) {#6};%\n}%\n%\n' \
    + '\colorlet{grey}{black!50}%\n' \
    + '\colorlet{lightGrey}{black!30}%\n' \
    + '\colorlet{myBlue}{blue!60!green!80}%\n' \
    + '\colorlet{myLightBlue}{blue!60!green!60}%\n' \
    + '\colorlet{myOrange}{orange!60!red!80}%\n' \
    + '\colorlet{myLightOrange}{orange!60!red!60}%\n' \
    + '\colorlet{myRed}{black!40!red!80}%\n' \
    + '\colorlet{myLightRed}{black!40!red!60}%\n' \
    + '\colorlet{myGreen}{black!60!green!70}%\n' \
    + '\colorlet{myLightGreen}{black!60!green!50}%\n' \
    + '\colorlet{myBlueB}{black!50!blue!80}%\n' \
    + '\colorlet{myLightBlueB}{black!50!blue!60}%\n' \
    + '%\\tdplotsetmaincoords{0}{0}% 2D\n' \
    + '\\begin{tikzpicture}[x=1cm, y=1cm, z=-1cm]%, tdplot_main_coords]\n'
    
for i in range(len(partitions)):
    latex += '\\newcommand{\length' + chr(65+i) + '}{' + str(partitions[i]['length']) + '}\n'
latex += '%\partition<type>{xStart}{length}{colorFront}{colorTop}{opacity}{name}{xShiftArrowText}\n\n'

xPos = '0'
for i in range(len(partitions)):
    arrow = True
    if 'nallocated' in partitions[i]['name']:
        latex += '\partitionArrowBelow{'
    elif partitions[i]['length'] < 1:
        latex += '\partitionArrowAbove{'
    else:
        latex += '\partitionBraceAbove{'
        arrow = False
    
    latex += xPos + '}{' \
        + '\length' + chr(65+i) + '}{' \
        + partitions[i]['color1'] + '}{' \
        + partitions[i]['color2'] + '}{' \
        + str(1) + '}{' \
        + partitions[i]['name'] + ' \\\\ (' + partitions[i]['size'] + ')}'
    
    if arrow:
        latex += '{' + str(0) + '}'
    latex += '\n\n'
    xPos += '+' + '\length' + chr(65+i)

latex += '\end{tikzpicture}\n\end{document}\n'
latex = latex.encode("utf-8")
with open(args.output, 'w') as tex_file:
    tex_file.write(latex)
print('Output file written to ' + args.output)

try:
    proc = Popen(['pdflatex ', args.output], stdin = PIPE, stdout = DEVNULL, stderr = STDOUT)
    proc.communicate()
except:
    print('Could not compile TEX-file')
    sys.exit(1)
    
try:
    filename = args.output.replace(os.path.splitext(args.output)[-1], '') + '.pdf'
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.call([opener, filename])
except:
    pass
