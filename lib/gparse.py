
class g_command:
    def __init__(self):
        self.command_type=""
        self.command_value=""
        self.x="nan"
        self.y="nan"
        self.z="nan"
        self.i="nan"
        self.j="nan"
        self.k="nan"
        self.f="nan"
        self.units=""
        self.coordinates=""
        self.description=""
        self.interpretation=""
        #self.comment=""

import re

def gparse(line):
    #non greedily strip comments with great haste
    line = re.sub(r'\([^)]*\)', '', line)
    #ignor parenthesise
    command_found=False
    parsed_g_command = g_command()
    g_found=False

    #Correct for the non witespace gcode formats you may encouter
    previous_letter = ""
    new_line = ""
    for letter in line:
        if (letter in 'GgXxYyZzIiJjKkFfMm') and (previous_letter != ' '):
            new_line = new_line + ' '
        new_line = new_line + letter
        #print letter
        old_letter = letter
    line = new_line.strip()
    print line
    if "g" in line or "G" in line:

        parsed_g_command.command_type="G"
        lineofwords=line.split()

        for word in lineofwords:
            if "g" in word or "G" in word:
                g_value = re.sub("g|G","",word)
                #print "G value = " + (g_value)
                parsed_g_command.command_value=float(g_value)
                #print line
                if g_found == True:
                    print "to manny G's in this line"
                else:
                    g_found=True
                    command_found=True

        if g_found==True and (int(g_value)==0 or int(g_value)==1):
            if int(g_value)==0:
                parsed_g_command.description="Rapid Move"
            elif int(g_value)==1:
                parsed_g_command.description="Linear Move"
            elif int(g_value)==2:
                parsed_g_command.description="Arc Move"
            else:
                  print "how did i get here"

            #G2 X1.0000 Y1.1600 Z0.4500 I0.0000 J-0.1600
            for word in lineofwords:
                if "x" in word or "X" in word:
                    x_value = re.sub("x|X","",word)
                    #print "X = " + (x_value)
                    parsed_g_command.x=float(x_value)
                elif "y" in word or "Y" in word:
                    y_value = re.sub("y|Y","",word)
                    #print "Y = " + (y_value)
                    parsed_g_command.y=float(y_value)
                elif "z" in word or "Z" in word:
                    z_value = re.sub("z|Z","",word)
                    #print "Z = " + (z_value)
                    parsed_g_command.z=float(z_value)
                elif "i" in word or "I" in word:
                    i_value = re.sub("i|I","",word)
                    #print "Z = " + (z_value)
                    parsed_g_command.i=float(i_value)
                elif "j" in word or "J" in word:
                    j_value = re.sub("j|J","",word)
                    #print "Z = " + (z_value)
                    parsed_g_command.j=float(j_value)
                elif "k" in word or "K" in word:
                    k_value = re.sub("k|K","",word)
                    #print "Z = " + (z_value)
                    parsed_g_command.k=float(k_value)
                elif "f" in word or "F" in word:
                    f_value = re.sub("f|F","",word)
                    #print "Z = " + (z_value)
                    parsed_g_command.f=float(f_value)
        elif g_found==True and (int(g_value)==20):
            parsed_g_command.units = "in"
            parsed_g_command.description="Units set to:    inches"
        elif g_found==True and (int(g_value)==21):
            parsed_g_command.units = "mm"
            parsed_g_command.description="Units set to:    mm"
        elif g_found==True and (int(g_value)==90):
            parsed_g_command.coordinates = "absolute"
            parsed_g_command.description="Coords set to:    absolute"
        elif g_found==True and (int(g_value)==91):
            parsed_g_command.coordinates = "relative"
            parsed_g_command.description="Coords set to:    relative"




    if command_found==True:
        return parsed_g_command
    else:
        return False
        print "no command found on this line"




def gcode_interpret(code):
#variables
#internal
    interpeted_gcommands=[]
    AbsX="nan"
    AbsY="nan"
    AbsZ="nan"
#external
    #DefaultMoveSpeed=
#constant
    ConversionToIN=1

    LastCommand = g_command()

    for command in code:
        interpreted_gcommand = command
        if command.command_type == "g":
            if command.command_value==20:
                ConversionToIN=1
            elif command.command_value==21:
                ConversionToIN=1/25.4
                interpreted_gcommand.value = 20
            elif command.command_value==90:
                coordinates=absolute
            elif command.command_value==91:
                coordinates=relative
                interpreted_gcommand.value = 90
            elif command.command_value==0 or command.command_value==1:
                if coordinates==absolute:
                    AbsX=ConversionToIN*command.x
                    AbsY=ConversionToIN*command.y
                    AbsZ=ConversionToIN*command.z
                elif coordinates==relative:
                    AbsX=AbsX+ConversionToIN*command.x
                    AbsY=AbsY+ConversionToIN*command.y
                    AbsZ=AbsZ+ConversionToIN*command.z
                interpreted_gcommand.x=AbsX
                interpreted_gcommand.y=AbsY
                interpreted_gcommand.z=AbsZ

        #interpret move type
        if LastCommand.x == interpreted_gcommand.x and LastCommand.y == interpreted_gcommand.y :
            if LastCommand.z == interpreted_gcommand.z :
                interpreted_gcommand.interpretation = "Stationary"
            elif LastCommand.z > interpreted_gcommand.z:
                interpreted_gcommand.interpretation = "Plunge"
            elif LastCommand.z < interpreted_gcommand.z:
                interpreted_gcommand.interpretation = "Lift"
                #if or elif for this next line not sure
            elif LastCommand.z>0 and interpreted_gcommand.z>0:
                interpreted_gcommand.interpretation = "Move"
        elif LastCommand.z>0 and interpreted_gcommand.z>0:
            interpreted_gcommand.interpretation = "Move"
        elif LastCommand.z<=0 and interpreted_gcommand.z<=0:
            interpreted_gcommand.interpretation = "Mill"
        elif LastCommand.z > interpreted_gcommand.z and LastCommand.z>0:
            interpreted_gcommand.interpretation = "Decending Mill"
        elif LastCommand.z < interpreted_gcommand.z and interpreted_gcommand.z>0:
            interpreted_gcommand.interpretation = "Ascending Mill"
        else:
            print "I don't know what to call this move!"

        interpeted_gcommands.append(interpreted_gcommand)
        LastCommand = interpreted_gcommand
    return interpeted_gcommands

#this blck commented out for learning python purposes
'''
from sys import argv
print "number of input args is:" + str(len(argv)-1)
numberofinputs=len(argv)-1

#default filename
filename="findhieght.nc"

#default verbosity
verbose = False

#import arguments

#warning
if numberofinputs==0:
    print "please input filename as arg"
#load filename
elif numberofinputs==1:
    script, filename= argv

txt = open(filename)
mydata= txt.readlines()

gcommands=[]

for line in mydata:
    if gparse(line):
        gcommands.append(gparse(line))

inted_gcommands = gcode_interpret(gcommands)

if verbose:

    for eachcommand in inted_gcommands:

        print eachcommand.x
        print eachcommand.y
        print eachcommand.z
        print eachcommand.description
        print eachcommand.interpretation
'''
