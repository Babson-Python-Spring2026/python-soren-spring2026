'''
When you run a Python file, you can import: 

other .py files in the same folder as the file you are running  
.py files inside subfolders of that same folder 
'''

import sys
for p in sys.path:
    print(p)

'''
CASE 1

functions.py is inside utilities/  which is inside 02-17 TUESDAY/

02-17 TUESDAY/
    my_program.py
    utilities/
        functions.py
'''


dic = {'apple':'red','banana':'yellow'}   
#Valid Calls
import utilities.functions                                              #1                                         
utilities.functions.print_dict(dic)                                     #1
utilities.functions.print_header("hello")                               #1

#Valid Calls
import utilities.functions as gu                                        #2
from utilities import functions as gu                                   #3

gu.print_dict(dic)                                                      #2,3
gu.print_header("hello")                                                #2,3

#valid calls
from utilities.functions import print_header, clear_screen              #4
from utilities.functions import *                                       #6

print_dict(dic)                                                         #4,6
print_header("hello")                                                   #4,6

#valid calls
from utilities.functions import print_header as ph, print_dict as pd    #5

ph("hello")                                                             #5
pd(dic)                                                                 #5


'''

CASE 2

functions2.py is directly in 02-17 TUESDAY/

02-17 TUESDAY/
    my_program.py
    functions2.py
'''

#Valid Calls
import functions2                                                       #7
functions2.print_dict(dic)                                              #7
functions2.print_header("hello")                                        #7

#valid calls
import functions2 as g2                                                 #8
g2.print_dict(dic)                                                      #8
g2.print_header("hello")                                                #8

#valid calls

from functions2 import print_header, print_dict                         #9
from functions2 import *                                                #11

print_dict(dic)                                                         #9,11
print_header("hello")                                                   #9,11

#valid calls
from functions2 import print_header as ph, print_dict as pd             #10

pd(dic)                                                                 #10
ph("hello")                                                             #10


'''
the problem with this approach is we need to copy our functions.py
file into every class date folder.

How can we address that?

We can add PYTHONPATH as an evironment variable and add
C:\PythonClass\student_repo

be sure to restart vs code.

'''

'''
from myImports import functions as mif

import sys
for p in sys.path:
    print(p)

from myImports import functions as mif
mif.print_header('hello')  
'''

