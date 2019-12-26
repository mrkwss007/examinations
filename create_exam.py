__author__ = 'Jacky Baltes'

import sys
import argparse
import importlib
import codecs
import builtins
from pathlib import Path

args = None

DEFAULT_TEMPLATE_DIR = 'C:/Users/yuihjk003/SkyDrive/Documents/Teaching/Templates'

def main( argv = None ):
    if argv == None:
        argv = sys.argv[1:]
    global args
    parser = argparse.ArgumentParser(description='Create an exam or midterm')
    parser.add_argument('exam', default='exam.py', nargs='?', help='Examination file (a python script that will be imported into the current python context')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase verbosity level')
    parser.add_argument('-r', '--resource_dir', metavar='R', nargs='+', action = 'append', help='Additional directories to search for questions')
    parser.add_argument('-t', '--template_dir', metavar='T', default=DEFAULT_TEMPLATE_DIR, help='Additional directories for moody templates')
    parser.add_argument('-s', '--styles', metavar='S', default=DEFAULT_TEMPLATE_DIR + '/' + 'exam_template.css', help='CSS styles')
    args = parser.parse_args(argv)

    homeDir = Path( args.exam ).parent.resolve()
    print('*** HOME ***', str(homeDir), '*** exam ***', args.exam )
    dirs = [ homeDir ]

    print('R', args.resource_dir)
    if args.resource_dir is not None:
        dirs = dirs + [ ddir for llist in args.resource_dir for ddir in llist  ]

    if args.template_dir is not None:
        dirs.append(args.template_dir)

    for d in ['Code', 'Resources', 'Questions']:
        dn = homeDir / d
        if dn not in dirs:
            dirs.append(dn)

    #print('Appending dirs', dirs)
    for d in dirs:
        sys.path.append( str(d) )

    # Export my global variables
    builtins.args = args

    import exam_template_routines as ex
    ex.init()
    builtins.exam = ex.exam

    if args.verbose > 0:
        print('Module path {0}'.format(sys.path))
        print('Loading exam {0}'.format(args.exam))

    #print(args.exam)
    #print(sys.path)
    exp = Path( args.exam )
    if (exp.suffix == '.py'):
        pass
        
    exam = importlib.import_module( exp.name[0:-3] )

    ### Epilog to create the exam. Do not change.

    c = ex.CreateExam( ex.exam, args.template_dir, 'exam_template.html', args.styles )
    base = Path( args.exam ).name[0:-3]
    saveFileName = Path(base + '_out.html')
    with codecs.open(saveFileName,"w","utf-8") as f:
        f.write( c ) 

if __name__ == '__main__':
    main()
