import sys
import os
from pathlib import Path
import platform

# set HOME=%HOMEDRIVE%\%HOMEPATH%
# set COURSE=NTNU Simultaneous Localization and Mapping
# set EXAMTITLE=%COURSE% Final Exam 2016
# set ROOTDIR=%HOME%\OneDrive\Documents\%COURSE%\%EXAMTITLE%
# set EXAMDIR=%HOME%\OneDrive\Documents\Examinations
# set TEMPLATE=%EXAMDIR%\Templates
# set CODEDIR=%ROOTDIR%\Code

COURSE = 'Machine Learning'
YEAR = 2019
EXAMTYPE = 'Final Exam'
UNIVERSITY = 'NTNU'

EXAMTITLE = COURSE + ' - ' + EXAMTYPE  + ' - ' + UNIVERSITY + ' - ' + str(YEAR)

vars = {
    'NTNU-ERC' : { 'ROOTDIR': 'D:/OneDrive - dkclauson003/OneDrive/Machine Learning/' + EXAMTITLE,
                   'EXAMDIR': 'D:/OneDrive - dkclauson003/OneDrive/Examinations',
               }, 
    'I157000': { 'ROOTDIR': 'C:/Users/mrkwss007/OneDrive/SharedWithAliases/Documents/Teaching/Courses/Machine Learning/' + EXAMTITLE,
                 'EXAMDIR': 'C:/Users/mrkwss007/OneDrive/SharedWithAliases/Documents/Teaching/Examinations',
               },
    'DESKTOP-1N7BG4A' : {
                'ROOTDIR': 'D:/OneDrive - negrin006/OneDrive/Machine Learning/' + EXAMTITLE,
                'EXAMDIR': 'D:/OneDrive - negrin006/OneDrive/Examinations',
    }
}

host = os.getenv('HOSTNAME', os.getenv('COMPUTERNAME', platform.node())).split('.')[0]

paths = vars[host]

ROOTDIR = Path( paths['ROOTDIR'] )
EXAMDIR = Path( paths['EXAMDIR'] )

if ( ROOTDIR is None ) or ( EXAMDIR is None ):
    print("ERROR: Unable to find ROOTDIR", ROOTDIR, "or EXAMDIR", EXAMDIR)
    sys.exit(2)

TEMPLATEDIR = EXAMDIR  / 'Templates' 
CODEDIR = ROOTDIR / 'Code'
STYLES = TEMPLATEDIR / 'exam_template.css'

codePaths = [ Path('.' + '/' + 'Code' ).resolve(),
              CODEDIR,
              CODEDIR / '..' / '..' /  'Code' ]

questionPaths = [ Path('.' + '/' + 'Questions' ).resolve(),
                  ROOTDIR / 'Questions',
                  ROOTDIR  / '..' / 'Questions' ]

#for k in os.environ:
#    print('k', k, '=', os.environ[k] )

PYTHON_EXECUTABLE = sys.executable
VERBOSE = '-v -v'

examPath = Path('.' + '/' + EXAMTITLE + ".py").resolve()
print('+++ examPath', examPath )

commandLine = PYTHON_EXECUTABLE \
                + ' ' '"' + str( EXAMDIR / 'create_exam.py' ) + '"' \
                + ' ' + VERBOSE + ' ' \
                + ' ' + '"' + str( examPath ) + '"' \
                + ' -t ' + '"' + str(TEMPLATEDIR) + '"' \
                + ' -s ' + '"' + str(STYLES) + '"'

for q in questionPaths:
    print('q',q)
    commandLine = commandLine + ' -r ' + '"' + str(q) + '"' + ' '

for c in codePaths:
    commandLine = commandLine + ' -r ' + '"' + str(c) + '"' + ' '

print('Command line', commandLine )
os.system( commandLine )
