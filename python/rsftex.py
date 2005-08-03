##   Copyright (C) 2004 University of Texas at Austin
##  
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2 of the License, or
##   (at your option) any later version.
##  
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.
##  
##   You should have received a copy of the GNU General Public License
##   along with this program; if not, write to the Free Software
##   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os, re, glob, string, commands, types
import cStringIO, token, tokenize, cgi, sys, keyword
import rsfconf, rsfdoc, rsfprog

import SCons

# The following adds all SCons SConscript API to the globals of this module.
if SCons.__version__ == '0.96.90':
    from SCons.Script import *
else:
    import SCons.Script.SConscript
    globals().update(SCons.Script.SConscript.BuildDefaultGlobals())


#############################################################################
# CONFIGURATION VARIABLES
#############################################################################

latex       = WhereIs('pdflatex')
bibtex      = WhereIs('bibtex')
acroread    = WhereIs('acroread') or WhereIs('xpdf') or WhereIs('gv')
epstopdf    = WhereIs('epstopdf')
fig2dev     = WhereIs('fig2dev')
latex2html  = WhereIs('latex2html')
pdf2ps      = WhereIs('pdf2ps')
pstoimg     = WhereIs('pstoimg')
mathematica = WhereIs('mathematica')
if mathematica:
    mathematica = WhereIs('math')

ressuffix = '.pdf'
vpsuffix  = '.vpl'
pssuffix  = '.eps'

rerun = re.compile(r'\bRerun')

# directory tree for executable files
top = os.environ.get('RSFROOT')
bindir = os.path.join(top,'bin')
libdir = os.path.join(top,'lib')
incdir = os.path.join(top,'include')
figdir = os.environ.get('RSFFIGS',os.path.join(top,'figs'))

# temporary (I hope)
sep = os.path.join(os.environ.get('SEP'),'bin/')

#############################################################################
# CUSTOM BUILDERS
#############################################################################

def latify(target=None,source=None,env=None):
    "Add header and footer to make a valid LaTeX file"
    tex = open(str(source[0]),'r')
    ltx = open(str(target[0]),'w')
    lclass = env.get('lclass','geophysics')
    options = env.get('options','12pt')
    if not options:
        options = '12pt'
    ltx.write('%% This file is automatically generated. Do not edit!\n')
    ltx.write('\\documentclass[%s]{%s}\n\n' % (options,lclass))
    use = env.get('use')
    resdir = env.get('resdir','Fig')
    include = env.get('include')
    if include:
         ltx.write(include+'\n\n')
    if use:
         if type(use) is not types.ListType:
              use = [use]
         for package in use:
              options = re.match(r'(\[[^\]]*\])\s*(\S+)',package)
              if options:
                   ltx.write('\\usepackage%s{%s}\n' % options.groups())
              else:
                   ltx.write('\\usepackage{%s}\n' % package)
         ltx.write('\n')
    if lclass == 'geophysics' or lclass == 'segabs':
        ltx.write('\\renewcommand{\\figdir}{%s}\n\n' % resdir)
    ltx.write('\\begin{document}\n')
    for line in tex.readlines():
        ltx.write(line)
    ltx.write('\\end{document}\n')
    ltx.close()
    return 0

def latex_emit(target=None, source=None, env=None):
    tex = str(source[0])    
    stem = re.sub('\.[^\.]+$','',tex)
    target.append(stem+'.aux')
    target.append(stem+'.log')
    target.append(stem+'.bbl')
    target.append(stem+'.blg')
    return target, source

def latex2dvi(target=None,source=None,env=None):
    "Convert LaTeX to DVI/PDF"
    tex = str(source[0])
    dvi = str(target[0])
    stem = re.sub('\.[^\.]+$','',dvi)    
    run = string.join([latex,tex],' ')
    # First latex run
    if os.system(run):
        return 1
    # Check if bibtex is needed
    aux = open(stem + '.aux',"r")    
    for line in aux.readlines():
        if re.search("bibdata",line):
            os.system(string.join([bibtex,stem],' '))
            os.system(run)
            os.system(run)
            break        
    aux.close()
    # (Add makeindex later)
    # Check if rerun is needed
    for i in range(3): # repeat 3 times at most
        done = 1
        log = open(stem + '.log',"r")
        for line in log.readlines():
            if rerun.search(line):
                done = 0
                break
        log.close()
        if done:
            break
        os.system(run)
    return 0

ppi = 72 # points per inch resolution
def pstexpen(target=None,source=None,env=None):
    "Convert vplot to EPS"
    vplot = str(source[0])
    eps = str(target[0])
    space = os.environ.get('PSBORDER')
    if not space:
        space=0.
    else:
        space=float(space)
    opts = os.environ.get(os.path.splitext(os.path.basename(eps))[0]+'.pspen')
    if not opts:
        opts = os.environ.get('PSTEXPENOPTS',
                              'color=n fat=1 fatmult=1.5 invras=y')
    print opts
    # bounding box
    head = string.split(
        commands.getoutput(sep +
                           "vppen big=n stat=l %s < %s | %s -1" %
                           (opts,vplot,WhereIs('head'))))
    bb = []
    for x in (7, 12, 9, 14):
        bb.append(int((float(head[x])-space)*ppi))
    try:
        file = open(eps,"w")
        file.write("%\!PS-Adobe-2.0 EPSF-2.0\n")
        file.write("%%%%BoundingBox: %d %d %d %d\n" % tuple(bb))
        file.write(commands.getoutput(sep + "pspen size=a tex=y %s < %s" %
                                      (opts,vplot)))
        file.write("\n")
        file.close()
    except:
        return 1
    return 0

_KEYWORD = token.NT_OFFSET + 1
_TEXT    = token.NT_OFFSET + 2

_colors = {
     token.NUMBER:       '#0080C0',
     token.OP:           '#0000C0',
     token.STRING:       '#004080',
     tokenize.COMMENT:   '#008000',
     token.NAME:         '#000000',
     token.ERRORTOKEN:   '#FF8080',
     _KEYWORD:           '#C00000',
     _TEXT:              '#000000',
     'Fetch':            '#0000C0',
     'Flow':             '#0000C0',
     'Plot':             '#0000C0',
     'Result':           '#C00000'
     }

_styles = {
     token.NUMBER:       'number',
     token.OP:           'op',
     token.STRING:       'string',
     tokenize.COMMENT:   'comment',
     token.NAME:         'name',
     token.ERRORTOKEN:   'error',
     _KEYWORD:           'keyword',
     _TEXT:              'text',
     'Fetch':            'fetch',
     'Flow':             'flow',
     'Plot':             'plot',
     'Result':           'result'
     }

_pos = 0

def _link(name):
     link = '<a href="/RSF/%s.html">%s</a>' % (rsfdoc.progs[name].name, name)
     return link
 
def colorize(target=None,source=None,env=None):
     "Colorize python source"
     py = str(source[0])
     html = str(target[0])
     tgz = re.sub('\.html$','.tgz',html)

     src = open(py,'r').read()
     raw = string.strip(string.expandtabs(src))

     out = open(html,'w')
     out.write('''
     <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
     <html>
     <head>
     <title>%s</title>
     <style type="text/css">
     div.progs {
     background-color: #DCE3C4;
     border: thin solid black;
     padding: 1em;
     margin-left: 2em;
     margin-right: 2em; }
     div.scons {
     background-color: #FFF8ED;
     border: thin solid black;
     padding: 1em;
     margin-left: 2em;
     margin-right: 2em; }
     ''' % py)
     for style in _styles.keys():
          out.write('.%s { color: %s; }\n' % (_styles[style],_colors[style])) 
     out.write('''</style>
     </head>
     <body>
     <div>
     <a href="paper_html/paper.html"><img width="32" height="32"
     align="bottom" border="0" alt="up" src="paper_html/icons/up.png"></a>
     <a href="paper.pdf"><img src="paper_html/icons/pdf.png" alt="[pdf]"
     width="32" height="32" border="0"></a>
     <a href="%s"><img src="paper_html/icons/tgz.png" alt="[tgz]"
     width="32" height="32" border="0"></a>
     </div>
     <div class="scons">
     <table><tr><td>
     ''' % tgz)

     # store line offsets in self.lines
     lines = [0, 0]
     _pos = 0
     while 1:
          _pos = string.find(raw, '\n', _pos) + 1
          if not _pos: break
          lines.append(_pos)
     lines.append(len(raw))


     # parse the source and write it
     _pos = 0
     text = cStringIO.StringIO(raw)
     out.write('<pre><font face="Lucida,Courier New">')

     def call(toktype, toktext, (srow,scol), (erow,ecol), line):
          global _pos
          
          # calculate new positions
          oldpos = _pos
          newpos = lines[srow] + scol
          _pos = newpos + len(toktext)
    
          # handle newlines
          if toktype in [token.NEWLINE, tokenize.NL]:
               out.write("\n")
               return

          # send the original whitespace, if needed
          if newpos > oldpos:
               out.write(raw[oldpos:newpos])

          # skip indenting tokens
          if toktype in [token.INDENT, token.DEDENT]:
               _pos = newpos
               return

          # map token type to a color group
          if token.LPAR <= toktype and toktype <= token.OP:
               toktype = token.OP
          elif toktype == token.NAME and keyword.iskeyword(toktext):
               toktype = _KEYWORD
          elif toktype == token.NAME and toktext in _colors.keys():
               toktype = toktext
               
          style = _styles.get(toktype, _styles[_TEXT])
 
          # send text
          out.write('<span class="%s">' % style)
          out.write(cgi.escape(toktext))
          out.write('</span>')

     try:
          tokenize.tokenize(text.readline, call)
     except tokenize.TokenError, ex:
          msg = ex[0]
          line = ex[1][0]
          out.write("<h3>ERROR: %s</h3>%s\n" % (msg, raw[lines[line]:]))
          return 1

     out.write('</font></pre></table>')

     cwd = os.getcwd()
     os.chdir(os.path.dirname(py))
     (status,progs) = commands.getstatusoutput('scons -s .sf_uses')
     os.chdir(cwd)
    
     if not status:
          out.write('</div><p><div class="progs">')
          out.write(rsfdoc.multicolumn(string.split(progs),_link))
     
     out.write('''
     </div>
     </body>
     </html>
     ''')
     return 0


plotoption = {}

def eps2png(target=None,source=None,env=None):
     png = str(target[0])
     eps = str(source[0])
     option = plotoption.get(os.path.basename(eps),'')
     command =  'PAPERSIZE=ledger %s %s -out %s' \
               + ' -type png -interlaced -antialias -crop a %s'
     command = command % (pstoimg,eps,png,option)
     print command
     os.system(command)
     return 0

def dummy(target=None,source=None,env=None):
     tex = open(str(target[0]),'w')
     tex.write('%% This file is automatically generated. Do not edit!\n')
     user = commands.getoutput('whoami')
     name = string.split(commands.getoutput('finger -m ' + user),'\n').pop(0)
     real = re.match(r'^.*:\s*(.*)$',name)
     if real:
         name = real.group(1)
     else:
         name = 'Anonymous'
     tex.write('\\author{%s}\n' % name)
     tex.write('\\title{Dummy paper}\n\n\maketitle\n')
     dirold = ''
     for src in source:
         fig = str(src)
         plt = os.path.splitext(os.path.basename(fig))[0]
         plt2 = string.replace(plt,'_','\_')
         dir = os.path.split(os.path.split(fig)[0])[0]
         if dir != dirold:
             tex.write('\n\\section{%s}\n' % dir)
             tex.write('\\inputdir{%s}\n\n' % dir)
             dirold = dir
         tex.write('\\plot{%s}{width=\\textwidth}{%s/%s} ' % (plt,dir,plt2))
         tex.write('\\clearpage\n')
     tex.close()    
     return 0

Latify = Builder(action = Action(latify,
                                 varlist=['lclass','options','use',
                                          'include','resdir']),
                 src_suffix='.tex',suffix='.ltx')
Pdf = Builder(action=Action(latex2dvi,varlist=['latex']),
              src_suffix='.ltx',suffix='.pdf',emitter=latex_emit)

if acroread:
    Read = Builder(action = acroread + " $SOURCES",
                   src_suffix='.pdf',suffix='.read')
    Print = Builder(action =
                    'cat $SOURCES | %s -toPostScript | lpr' % acroread,
                    src_suffix='.pdf',suffix='.print')

Build = Builder(action = Action(pstexpen),
                src_suffix=vpsuffix,suffix=pssuffix)

if epstopdf:
    PDFBuild = Builder(action = epstopdf + " $SOURCES",
		       src_suffix=pssuffix,suffix='.pdf')

if fig2dev:
    XFig = Builder(action = fig2dev + ' -L pdf -p dummy $SOURCES $TARGETS',
                   suffix='.pdf',src_suffix='.fig')


if pstoimg:
     PNGBuild = Builder(action = Action(eps2png),
                        suffix='.png',src_suffix=pssuffix)

if pdf2ps:
    PSBuild = Builder(action = pdf2ps + ' $SOURCE $TARGET',
                      suffix=pssuffix,src_suffix='.pdf')

if latex2html:
    l2hdir = os.environ.get('LATEX2HTML','')
    inputs = os.environ.get('TEXINPUTS','')
    if l2hdir:
        init = '-init_file ' + os.path.join(l2hdir,'.latex2html-init')
        css0 = os.path.join(l2hdir,'style.css')
        icons0 = os.path.join(l2hdir,'icons')
    else:
        init = ''

    HTML = Builder(action = 'TEXINPUTS=%s LATEX2HTMLSTYLES=%s/perl %s '
                   '-debug $SOURCE -dir $TARGET.dir %s' %
                   (inputs,l2hdir,latex2html,init),src_suffix='.ltx')

if mathematica and epstopdf:
     Math = Builder(action = 'DISPLAY=" " nohup %s -batchoutput '
                    '< $SOURCE >& /dev/null > /dev/null && '
                    '%s junk_ma.eps -o=$TARGET && rm junk_ma.eps' %
                    (mathematica,epstopdf),
                    suffix='.pdf',src_suffix='.ma')
     
Color = Builder(action = Action(colorize),suffix='.html')
                   
#############################################################################
# CUSTOM SCANNERS
#############################################################################

isplot = re.compile(r'^[^%]*\\(?:side|full)?plot\*?\s*(?:\[[htbp]+\])?\{([^\}]+)')
ismplot = re.compile(r'^[^%]*\\multiplot\*?\{[^\}]+\}\s*\{([^\}]+)')
isfig  = re.compile(r'^[^%]*\\includegraphics\s*(\[[^\]]*\])?\{([^\}]+)')
isbib = re.compile(r'\\bibliography\s*\{([^\}]+)')
input = re.compile(r'[^%]\\input\s*\{([^\}]+)')
# listing = re.compile(r'\\lstinputlisting(?:\[[^\]]+\])?\{([^\}]+)')
chdir = re.compile(r'\\inputdir\s*\{([^\}]+)')
subdir = re.compile(r'\\renewcommand\s*\{\\figdir}{([^\}]+)')

def latexscan(node,env,path):
    top = str(node)
    if top[-4:] != '.tex':
        return []
    contents = node.get_contents()
    inputs = map(lambda x: x+'.tex',input.findall(contents))
    inputs.append(str(node))
    resdir = env.get('resdir','Fig')
    inputdir = env.get('inputdir','.')
    plots = []
    for file in inputs:
        inp = open(file,'r')
        for line in inp.readlines():            
            dir  = chdir.search(line)
            if dir:
                inputdir = dir.group(1)
            dir = subdir.search(line)
            if dir:
                resdir = dir.group(1)
            resdir2 = os.path.join(inputdir,resdir)
            
            check = isplot.search(line)
            if check:
                 plot = check.group(1)
                 plot = string.replace(plot,'\_','_')
                 plots.append(os.path.join(resdir2,plot + ressuffix))
                 if re.search('angle=90',line):
                      plotoption[plot+pssuffix] = '-flip r90'

            
            check = ismplot.search(line)
            if check:
                 mplot = check.group(1)
                 mplot = string.replace(mplot,'\_','_')
                 for plot in string.split(mplot,','):
                     plots.append(os.path.join(resdir2,plot + ressuffix))
                     if re.search('angle=90',line):
                         plotoption[plot+pssuffix] = '-flip r90'

            check = isfig.search(line)
            if check:
                 plot = check.group(2)
                 if plot[-len(ressuffix):] != ressuffix:
                     plot = plot + ressuffix
                 plots.append(plot)
  
        inp.close()
    bibs = []
    for bib in isbib.findall(contents):
        for file in string.split(bib,','):
            file = file+'.bib'
            if os.path.isfile(file):
                bibs.append(file)
    return plots + inputs + bibs

LaTeX = Scanner(name='LaTeX',function=latexscan,skeys=['.tex','.ltx'])

#############################################################################

class TeXPaper(Environment):
    def __init__(self,**kw):
        apply(Environment.__init__,(self,),kw)
        opts = Options(os.path.join(libdir,'rsfconfig.py'))
        rsfconf.options(opts)
        opts.Update(self)
        self.Append(ENV={'XAUTHORITY':
                         os.path.join(os.environ.get('HOME'),'.Xauthority'),
                         'DISPLAY': os.environ.get('DISPLAY'),
                         'HOME': os.environ.get('HOME')},
                    SCANNERS=[LaTeX],
                    BUILDERS={'Latify':Latify,
                              'Pdf':Pdf,
                              'Build':Build,
                              'Color':Color},
                    TARFLAGS = '-cvz',
                    TARSUFFIX = '.tgz')
        dir = os.getcwd()
        self.docdir = string.replace(dir,'book','doc/book',1)
        if self.docdir == dir:
            self.docdir = os.path.join(dir,'doc')
        if acroread:
            self.Append(BUILDERS={'Read':Read,'Print':Print})
        if epstopdf:
            self.Append(BUILDERS={'PDFBuild':PDFBuild})
        if fig2dev:
            self.Append(BUILDERS={'XFig':XFig})
        if latex2html:
            self.Append(BUILDERS={'HTML':HTML})
            if pstoimg:
                self.Append(BUILDERS={'PNGBuild':PNGBuild})
                self.imgs = []
        if pdf2ps:
            self.Append(BUILDERS={'PSBuild':PSBuild})
        if mathematica and epstopdf:
            self.Append(BUILDERS={'Math':Math})
        self.scons = []
        self.figs = []
        self.Dir()
    def Dir(self,topdir='.',resdir='Fig'):
        for scons in glob.glob('%s/[a-z]*/SConstruct' % topdir):
             dir = os.path.dirname(scons)
             html = dir+'.html'
             self.Color(html,scons)
             self.scons.append(html)
             tgz = dir+'.tgz'
             self.Tar(tgz,dir)
             self.scons.append(tgz)
        if self.scons:
             self.Install(self.docdir,self.scons)
        self.Alias('install',self.docdir)        
        # reproducible figures
        erfigs = []
        vpldir = re.sub(r'.*\/((?:[^\/]+)\/(?:[^\/]+))$',
                        figdir+'/\\1',os.path.abspath(topdir)) 
        for fig in glob.glob('%s/[a-z]*/*%s' % (vpldir,vpsuffix)):
             eps = re.sub(r'.*\/([^\/]+)\/([^\/]+)'+vpsuffix+'$',
                          r'%s/\1/%s/\2%s' % (topdir,resdir,pssuffix),fig)
             resdir2 = os.path.join(self.docdir,os.path.dirname(eps))
             self.Build(eps,fig)
             if epstopdf:
                  pdf = re.sub(pssuffix+'$','.pdf',eps)
                  self.PDFBuild(pdf,eps)
                  erfigs.append(pdf)
             if latex2html and pstoimg:
                  png = re.sub(pssuffix+'$','.png',eps)
                  self.PNGBuild(png,eps)
                  self.imgs.append(png)
                  self.Install(resdir2,[png,pdf])
                  self.Alias('install',resdir2)
        self.figs.extend(erfigs)
        # conditionally reproducible figures
        crfigs = []
        # mathematica figures:
        mths = glob.glob('%s/Math/*.ma' % topdir)
        if mths:
            for mth in mths:
                pdf = re.sub(r'([^/]+)\.ma$',
                             os.path.join(resdir,'\g<1>.pdf'),mth)
                if mathematica:
                    self.Math(pdf,mth)
                crfigs.append(pdf)
            mathdir = os.path.join(self.docdir,'Math')
            self.Install(mathdir,mths)
            self.Alias('install',mathdir)
        # xfig figures:
        figs =  glob.glob('%s/XFig/*.fig' % topdir)
        if figs:
            for fig in figs:
                pdf = re.sub(r'([^/]+)\.fig$',
                             os.path.join(resdir,'\g<1>.pdf'),fig)
                if fig2dev:
                    self.XFig(pdf,fig)
                crfigs.append(pdf)
            resdir2 = os.path.join(self.docdir,'XFig')
            self.Install(resdir2,figs)
            self.Alias('install',resdir2)
        # non-reproducible figures
        nrfigs = crfigs + glob.glob(
            os.path.join(topdir,os.path.join(resdir,'*.pdf'))) 
        for pdf in nrfigs:
             if pdf2ps:
                eps = re.sub('.pdf$',pssuffix,pdf)
                self.PSBuild(eps,pdf)
                if latex2html and pstoimg:
                    png = re.sub(pssuffix+'$','.png',eps)
                    self.PNGBuild(png,eps)
                    self.imgs.append(png)
                    resdir2 = os.path.join(self.docdir,os.path.dirname(png))
                    self.Install(resdir2,[png,pdf])
                    self.Alias('install',resdir2)
        self.figs.extend(nrfigs)
    def Paper(self,paper,lclass='geophysics',
              use=None,include=None,options=None):
        self.Latify(target=paper+'.ltx',source=paper+'.tex',
                    use=use,lclass=lclass,options=options,include=include)
        pdf = self.Pdf(target=paper,source=paper+'.ltx')
        pdf[0].target_scanner = LaTeX
        pdfinstall = self.Install(self.docdir,paper+'.pdf')
        self.Alias(paper+'.install',pdfinstall)
        if acroread:
            self.Alias(paper+'.read',self.Read(paper))
            self.Alias(paper+'.print',self.Print(paper))
        if latex2html and l2hdir:
            dir = paper+'_html'
            css  = os.path.join(dir,paper+'.css')
            html = os.path.join(dir,'index.html')
            icons = os.path.join(dir,'icons')
            self.InstallAs(css,css0)
            self.Install(icons,glob.glob('%s/*.png' % icons0))
            self.HTML(html,paper+'.ltx')
            self.Depends(self.imgs,pdf)
            self.Depends(html,self.imgs)
            self.Depends(html,self.scons)
            self.Depends(html,pdf)
            self.Depends(html,css)
            self.Depends(html,icons)
            self.Alias(paper+'.html',html)
            docdir = os.path.join(self.docdir,dir)
            dochtml = os.path.join(docdir,'index.html')
            self.Command(dochtml,html,
                         'cd $SOURCE.dir && cp -r * $TARGET.dir && cd ..')
            self.Alias(paper+'.install',dochtml)
    def End(self,paper='paper',**kw):
         if os.path.isfile(paper+'.tex'):
            apply(self.Paper,(paper,),kw)
            self.Alias('pdf',paper+'.pdf')
            self.Alias('read',paper+'.read')
            self.Alias('print',paper+'.print')
            self.Alias('html',paper+'.html')
            self.Alias('install',paper+'.install')
            self.Default('pdf')
         self.Command('dummy.tex',self.figs,Action(dummy))
#         apply(self.Paper,('dummy','dummy.tex'),kw)

default = TeXPaper()
def Dir(**kw):
     return apply(default.Dir,[],kw)
def Paper(paper,**kw):
    return apply(default.Paper,(paper,),kw)
def Command2(target,source,command):
    return default.Command(target,source,command)
def End(paper='paper',**kw):
    return apply(default.End,(paper,),kw)
def Depends2(target,source):
    return default.Depends(target,source)

if __name__ == "__main__":
     import pydoc
     pydoc.help(TeXPaper)

# 	$Id$
