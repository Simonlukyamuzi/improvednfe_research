

import csv
import pdb

#Variable Intialization

filename = "/path/Data.csv"

#If this script and csv is in same foder then path can be given below

#filename = "Data.csv"

#ITEMS will be used as header or list of attributes
ITEMS = set()

#LABELES will have different class/type 
LABELS = set()

#with same primary file a .arff file will be created and will be saved in same folder

arffFilename = filename.split(".")[0] + ".arff"

#opening the csv file. each row of file will be in the format [A1,A2..... An-1,classtype]
#CSV file must not have the header 

myfile = csv.reader(open(filename,'rb'))


#Get List of all the unique items from the Input
for line in myfile:
        [ITEMS.add(item.strip()) for item in line[:-1]]
	#Get List of all the unqiue classes
        LABELS.add(line[-1].strip())

#Open created arff file to write the data
myARFF = open(arffFilename,'w+')

myARFF.write('@relation Weka\n\n\n')

#So that items will iterate in order
ITEMS = list(ITEMS) 
ITEMS.append("class")

LABELS = list(LABELS)

#writing different attributes. this script treat each attribute as nominal and of binary type {true,false}

for item in ITEMS[:-1]: myARFF.write(str("@attribute "+item+" {false,true}\n"))

#writing last attribute as class

myARFF.write("@attribute "+ ITEMS[-1]+ "{" + ",".join(LABELS) + "}" + "\n")

#writing data part

myARFF.write('\n\n@data\n\n')

#Iterate over the data file
myfile = csv.reader(open(filename,'rb'))

for line in myfile:
    tmp = []
    newLine = "{ "
    for word in line[:-1]:
        tmp.append(ITEMS.index(word.strip()))
    for i in sorted(list(set(tmp))):
        newLine += str(i) +" "+"true"+","

    #Adding the class of the sample
    newLine += str(len(ITEMS)-1) + " " + line[-1]   
 
    writeLine = newLine
    writeLine += "}\n"
    print writeLine
    myARFF.write(writeLine)

#closing file
myARFF.close()


