from jinja2 import Environment, FileSystemLoader, Template, StrictUndefined
import subprocess
import re
import random
import importlib
import base64
from pathlib import Path
import sys 
import graphviz as gv

import os
os.environ["PATH"] += os.pathsep + 'C:/tools/Anaconda3/Library/bin/graphviz'

#PythonInterpreter="\"C:\Applications and Installers\PortableApps\Portable Python 3.2.1.1\App\python.exe\""
#PythonInterpreter="python.exe"
#PythonInterpreter= str( Path('C:/ProgramData/Anaconda3/python.exe').resolve() )
PythonInterpreter=sys.executable

# The various templates for rendering the parts of the exam

SECTION_HEADER_TEMPLATE="""
<h2 class="sectionheader"> {% print snum %} {% print title %} </h2>

<p> {% print preamble %} </p>

<ol start=\"{% print qnum %}\" >
"""

SECTION_TRAILER_TEMPLATE="""
</ol>
<hr style="width: 100%; height: 2px;">
"""

QUESTION_HEADER_TEMPLATE="""
<li>
"""

QUESTION_TRAILER_TEMPLATE="""
</li>
"""

QUESTION_BODY_TEMPLATE="""
<div class="questionbody">
{% print body %}
</div>
"""

QUESTION_ANSWER_TEMPLATE="""
<div class="questionanswer">
Solution:<br>
{% print answer %}
</div>
"""

QUESTIONBOX_HEADER="""
<table style="width: 600px; height: 100px; text-align: left; margin-left: auto; margin-right: auto;" border="1" cellpadding="2" cellspacing="2">
<tbody>
"""

QUESTIONBOX_TRAILER="""
</tbody>
</table>
"""

QUESTIONBOX_LINE_1 = """
<td class="qbox_cell" {% print background %}>
{% print sectionid %}<br>
{% print marks %}<br>
</td>
"""

QUESTIONBOX_LINE_2 = """
<td class="qbox_cell" {% print background %}>
</td>
"""


def RenderRecursive(template, values):
    p = template
    #print(">>>>",p,values,"<<<<")
    t = Template(template)
    s = t.render(**values )
    while ( p != s):
        p = s
        t = Template(s)
        s = t.render(**values )
    #print("***** Result *****", s)
    return s

def MergeDictionaries( d1, d2):
    nd = {}
    for k in d1.keys():
        nd[k] = d1[k]
    for k in d2.keys():
        nd[k] = d2[k]
    return nd

class Exam:
    def __init__(self, values = None):
        self.sections = []
        self.values = values
        self.currentSection = None

    def _AddSection(self, section ):
        self.sections = self.sections + [section]
        self.currentSection = section

    def Render(self):
        s = ""
        snum = 1
        qnum = 1

        for i in range(len(self.sections)):
            s = s + self.sections[i].Render(snum, qnum)
            snum = snum + 1
            qnum = qnum + len(self.sections[i].questions)
        qb = self.RenderQuestionBox()
        RenderRecursive(s, MergeDictionaries( self.values, { 'questionbox' : qb} ) )
        return s

    def RenderQuestionBox(self):
        nSec = len(self.sections)
        s = RenderRecursive(QUESTIONBOX_HEADER, self.values )
        s = s + "<tr>"
        for i in range(nSec):
            ldict = { 'sectionid' : chr(ord('A') + i ), 'background' : "", 'marks' : str(self.sections[i].TotalMarks()) }
            s = s + RenderRecursive(QUESTIONBOX_LINE_1,  MergeDictionaries( self.values, ldict ) )
        ldict = { 'sectionid' : "Total", 'marks' : str(self.TotalMarks()), 'background' : "style=\"background-color: rgb(204, 204, 204);\"" }
        s = s + RenderRecursive(QUESTIONBOX_LINE_1, MergeDictionaries(self.values, ldict ) )
        s = s + "</tr>"

        s = s + "<tr>"
        for i in range(nSec):
            ldict = { 'sectionmarks' : str(self.sections[i].TotalMarks() ), 'background' : "" }
            s = s + RenderRecursive(QUESTIONBOX_LINE_2, MergeDictionaries(self.values, ldict) )
        ldict = { 'sectionid' : "Total", 'marks' : str(self.TotalMarks()), 'background' : "style=\"background-color: rgb(204, 204, 204);\"" }
        s = s + RenderRecursive(QUESTIONBOX_LINE_2, MergeDictionaries(self.values, ldict) )
        s = s + "</tr>"

        s = s + RenderRecursive(QUESTIONBOX_TRAILER, self.values )
        return s

    def TotalMarks(self):
        ssum = 0
        for s in self.sections:
            ssum = ssum + s.TotalMarks()
        return ssum

    def AddSection(self, title, preamble ):
        s = Section( title, preamble )
        self._AddSection( s )

    def AddQuestion(self, marks, body, answer, values):
        q = Question( marks, body, answer, values )
        self.currentSection._AddQuestion(q)

    def AddQuestionFromFile(self, fname, marks, vars ):
        self.currentSection.AddQuestionFromFile( fname, marks, vars )
        
class Section:
    def __init__(self, title, preamble ):
        self.questions = []
        self.values = {}

        self.values['title'] = title
        self.values['preamble'] = preamble

    def _AddQuestion(self, question ):
        if question is not None:
            self.questions = self.questions + [ question ]

    def Render(self, snum, qnum):
        self.values['snum'] = snum
        self.values['qnum'] = qnum

        s = ""
        s = s + RenderRecursive(SECTION_HEADER_TEMPLATE, self.values)
        for i in range(len(self.questions)):
            s = s + self.questions[i].Render(snum, qnum )
        s = s + RenderRecursive(SECTION_TRAILER_TEMPLATE, self.values)
        return s

    def TotalMarks(self):
        ssum = 0
        for q in self.questions:
            ssum = ssum + int(round(float(q.values['marks'])))
        return ssum

    def AddQuestion(self, marks, body, answer, values):
        q = Question( marks, body, answer, values )
        self._AddQuestion(q)

    def AddQuestionFromFile(self, fname, marks, vars ):
        if fname[-3:] == '.py':
            fname = fname[:-3]
        q = importlib.import_module(fname)
        q.run(self, marks, vars)

class Question:
    def __init__(self, marks, body, answer, values ):
        self.exam = exam
        self.values = {}

        for k in values.keys():
            self.values[k] = values[k]

        if ( "marks" in self.values ) and (marks != self.values['marks']):
            raise Exception("Marks mismatch in question")
        else:
            self.values['marks'] = str(marks)

        if ( "body" in self.values ) and ( body != self.values['body']):
            raise Exception("Body mismatch in question")
        else:
            self.values['body'] = body

        if ( "answer" in self.values ) and (answer != self.values['answer']):
            raise Exception("Answer mismatch in question")
        else:
            self.values['answer'] = answer

    def Render(self, snum, qnum):
        s = ""
        s = s + RenderRecursive(QUESTION_HEADER_TEMPLATE, self.values )
        s = s + self.RenderQuestion()
        s = s + self.RenderAnswer()
        s = s + RenderRecursive(QUESTION_TRAILER_TEMPLATE, self.values )
        return s

    def RenderQuestion(self):
        s = ""
        s = s + RenderRecursive(QUESTION_BODY_TEMPLATE, self.values)
        qbox = re.search('<div +class="questionanswerbox"', s)
        if qbox is not None:
            s = s[:qbox.start()] + '<div style="text-align: right">Marks: ' + self.values['marks'] + '</div>' + s[qbox.start():]
        else:
            raise Exception("Missing answerbox in question")
        return s

    def RenderAnswer(self):
        s = ""
        s = s + RenderRecursive(QUESTION_ANSWER_TEMPLATE, self.values)
        return s

def RunCode( code ):
    f = open("tmp.py","w")
    f.write(code)
    f.close()

#    result = "<div class=\"codeoutput\"><code><pre>" + subprocess.check_output( PythonInterpreter + " " + "tmp.py", stderr=subprocess.STDOUT, universal_newlines=True, shell = True ) + "</pre></code></div>"
    result = subprocess.check_output( PythonInterpreter + " " + "tmp.py", stderr=subprocess.STDOUT, universal_newlines=True, shell = True )
    subprocess.call(["del", "tmp.py"], shell=True)
    return result

def ScrambleCode( code ):
    lines = code.splitlines()
    i = 0
    while(i < len(lines) ):
        if ( len(lines[i]) <= 0 ):
            del lines[i]
        else:
            i = i + 1
    for i in range(len(lines)):
        lines[i] = re.sub("^[ \t]+","",lines[i])
    random.shuffle(lines)
    return "\n".join(lines)

def mergeDictionaries(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def CreateExam( exam, templateDir, templateFilename, styleFile ):
    template_args = exam.values
    if "note" not in template_args:
        template_args['note'] = """
Attempt all questions.<br>
This is an <em>open</em> book examination.<br>
Use of laptops and computers <b>with Internet connectivity</b> is <em>permitted</em>,
but <b>no chat application</b> is allowed.<br>
Use of any other electronic equipment is strictly <em>forbidden</em>.<br>
Show your work to receive full marks.<br>
Some of the questions may not be solvable, that is it may be impossible
to calculate the requested information. In this case, say so in your answer
and explain why.<br>
"""
    if 'templateDir' not in template_args:
        template_args['templateDir'] = templateDir
    if 'questionbox' not in template_args:
        template_args['questionbox'] = exam.RenderQuestionBox()

    with open( styleFile ) as file:
        styles = file.read()

    template_args['styles'] = styles
    template_args['content'] = exam.Render()

    loader = FileSystemLoader(templateDir)
    # print("***Loader***", loader, "file", templateFilename, 'dir', templateDir)
    env = Environment(loader=loader, undefined = StrictUndefined )
    template = env.get_template( templateFilename )
    x = template.render( mode = "Print",  **template_args)

    x = template.render( **template_args )
    return x

exam = None

def init( template_args = None ):
    global exam
    if args.verbose:
        print('Creating exam with arguments ' )
    exam = Exam( template_args )

def main():
    pass


def createTable( data, header, cls ):
    cls_s = ""
    cls_hc = ""
    cls_c = ""

    if cls is not None:
        cls_s = ' class="'+cls+'" '
        cls_hc = ' class="' + 'h' + cls + 'cell' + '"'
        cls_c = ' class="' + cls + 'cell' + '"'

    s = '<table border=1' + cls_s + 'style="margin-left: auto; margin-right: auto;">' + '\n'
    s += '   <thead>'  + '\n'
    if ( header is not None):
        s += '      <tr>' + '\n'
        for h in header:
            s += '         ' + '<td ' + cls_hc + '" style="padding:5px;">' + h + '</td>' + '\n'
        s += '      </tr>' + '\n'
    s += '   </thead>'  + '\n'
    s += '   <tbody>'  + '\n'
    for r in data:
        s += '      <tr>' + '\n'
        for c in r:
            s += '         ' + '<td ' + cls_c + '" style="padding:5px;">' + str(c) + '</td>' + '\n'
        s += '      </tr>' + '\n'
    s += '   </tbody>'  + '\n'
    s += '</table>' + '\n'
    return s

def createRowTable( data, header, cls ):
    cls_s = ""
    cls_hc = ""
    cls_c = ""

    if cls is not None:
        cls_s = ' class="'+cls+'" '
        cls_hc = ' class="' + 'h' + cls + 'cell' + '"'
        cls_c = ' class="' + cls + 'cell' + '"'

    s = '<table border=1' + cls_s + 'style="margin-left: auto; margin-right: auto;">' + '\n'
    s += '   <thead>'  + '\n'
    s += '   </thead>'  + '\n'
    s += '   <tbody>'  + '\n'
    for i in range(len(data[0])):
        s += '      <tr>'  + '\n'
        if ( header is not None):
            s += '         ' + '<td ' + cls_hc + '" style="padding:5px;">' + header[i] + '</td>' + '\n'
        for ci in range(len(data)):
            s += '         ' + '<td ' + cls_c + '" style="padding:5px;">' + str(data[ci][i]) + '</td>' + '\n'
        s += '      </tr>' + '\n'
    s += '   </tbody>'  + '\n'
    s += '</table>' + '\n'
    return s

def array2DToString( arr, fmt = '{0}' ):
    s = '[ '
    for i in range(len(arr)):
        if ( i > 0 ):
            s = s + ','
        s = s + '[ '
        for j in range(len(arr[i])):
            if ( j > 0 ):
                s = s + ','
            s = s + fmt.format(arr[i][j])
        s = s + ' ]'
    s = s + ' ]'
    return s

def createSVGFromGraphviz( graph, format='svg' ):
    graph.format = 'svg'
    s = graph.pipe().decode('utf-8')
    #graph.save('bbn1_out.svg')
    return s

def createBase64ImageFromFigure( fig ):
    from io import BytesIO
    import base64 
    
    figfile = BytesIO()
    fig.savefig(figfile, dpi=300, bbox_inches='tight', format="png")
    figfile.seek(0)  # rewind to beginning of file
    # figdata_png = base64.b64encode(figfile.read())
    image = base64.b64encode(figfile.getvalue()).decode('utf-8')
    return image

def createSVGImageFromFigure( fig ):
    from io import BytesIO
    figfile = BytesIO()
    fig.savefig(figfile, dpi=300, bbox_inches='tight', format="svg" )
    figfile.seek(0)  # rewind to beginning of file
    image = figfile.getvalue().decode('utf-8')
    return image

def svgAdjust( svg, width, height, rotate = False ):
    #print("svgAdjust", svg[0:300], width, height )
    sizeRE = r'width=\w*"([^"]+)" height="([^"]+)"' # ([^"]*)"\w+height="(.*)"' #\w+height="(?P<height>[^"]+)"'
    svg = re.sub( sizeRE, f'width="{width}%" height="{height}"', svg )

    if rotate:
        rotRE = r''

    print(svg[0:400])
    return svg

if __name__ == '__main__':
    main()
