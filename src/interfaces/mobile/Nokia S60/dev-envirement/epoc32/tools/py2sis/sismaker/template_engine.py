# Copyright (c) 2005 Nokia Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from StringIO import StringIO
import re
import os.path
import traceback
import sys

TEMPLATEFILE_SUFFIX='.template'

def is_templatefile(filename):
    return filename.endswith(TEMPLATEFILE_SUFFIX)

def outfilename_from_infilename(infilename):
    if not is_templatefile(infilename):
        raise ValueError, "expected file name with suffix "+TEMPLATEFILE_SUFFIX+", got "+infilename
    return infilename[:-len(TEMPLATEFILE_SUFFIX)]

class MacroEvaluationError(Exception): pass

macro_delimiter_re=re.compile(r'(\${{|}})')
macro_eval_re=re.compile('\${{(.*?)}}$',re.S)
macro_exec_re=re.compile('\${{!(\s*\n)?(.*?)\s*}}$',re.S)
macro_if_re  =re.compile('\${{if (.*)}}$',re.S)

def process_macros(instr, namespace=None):
    """Return result of doing macro processing on instr, in namespace namespace. 
    
    Basic substitution and evaluation:
    >>> process_macros('${{foo}}',{'foo':1})
    '1'
    >>> process_macros('${{2+2}}')
    '4'
    >>> process_macros('${{foo+bar}}',{'foo': 1, 'bar': 2})
    '3'
    
    Error cases:
    >>> process_macros('}}')
    Traceback (most recent call last):
      ...
    MacroEvaluationError: Mismatched parens in macro }}
    >>> process_macros('${{')
    Traceback (most recent call last):
      ...
    MacroEvaluationError: Mismatched parens in macro ${{

    Corner cases:
    >>> process_macros('')
    ''
    >>> process_macros(u'')
    u''

    Code execution:
    >>> process_macros("${{!print 'foo'}}")
    foo
    ''
    >>> process_macros("${{!  \\nfor k in range(4):\\n    write(str(k))}}")
    '0123'
    
    >>> process_macros('${{if 1\\nfoo\\n$else\\nbar}}')
    'foo'
    >>> process_macros('xxx${{if 1\\n${{foo}}\\n$else\\nbar}}yyy',{'foo':42})
    'xxx42yyy'
    >>> process_macros('${{!#}}')
    ''
    >>> process_macros('${{"${{foo}}"}}',{'foo':42})
    '42'
    >>> process_macros('${{"${{bar}}"}}',{'foo':42})
    Traceback (most recent call last):
      ...
    MacroEvaluationError: Error evaluating expression "${{bar}}": NameError: name 'bar' is not defined
    <BLANKLINE>
    """
    if namespace is None:
        namespace={}
    
    def process_text(text):
        #print "Processing text: "+repr(text)
        pos=0 # position of the first character of text that is not yet processed
        outbuf=[]
        macrobuf=[]
        while 1:
            m=macro_delimiter_re.search(text, pos)
            if m:
                ##print "found delimiter: "+text[m.start():]
                outbuf.append(text[pos:m.start()])
                pos=m.start()
                paren_level=0
                for m in macro_delimiter_re.finditer(text,pos): # find a single whole macro expression
                    delim=m.group(1)
                    if delim=='${{':
                        paren_level+=1
                    elif delim=='}}':
                        paren_level-=1
                    else:
                        assert 0
                    if paren_level<0:
                        raise MacroEvaluationError("Mismatched parens in macro %s"%text[pos:m.end()])
                    if paren_level == 0: # macro expression finishes here, evaluate it.
                        outbuf.append(process_text(process_macro(text[pos:m.end()])))
                        pos=m.end()
                        break
                if paren_level!=0:
                    raise MacroEvaluationError("Mismatched parens in macro %s"%text[pos:m.end()])                
            else: # no more macros, just output the rest of the plain text
                outbuf.append(text[pos:])
                break
        result=''.join(outbuf)
        #print "Text after processing: "+repr(result)
        return result
    def process_macro(macro_expression):
        #print 'Processing macro: '+repr(macro_expression)
        try: 
            outstr=StringIO()
            namespace['write']=outstr.write
            m=macro_exec_re.match(macro_expression) # ${{!code}} -- exec the code
            if m:
                exec m.group(2) in namespace
            else:
                m=macro_if_re.match(macro_expression) # ${{if -- if expression
                if m:
                    outstr.write(handle_if(process_text(m.group(1)),namespace))
                else:
                    m=macro_eval_re.match(macro_expression)
                    if m: # ${{code}}  -- eval the code
                        outstr.write(str(eval(m.group(1),namespace)))
                    else:                        
                        raise MacroEvaluationError, 'Invalid macro'
            #print 'Macro result: '+repr(outstr.getvalue())
            return outstr.getvalue()
        except:
            raise MacroEvaluationError, 'Error evaluating expression "%s": %s'%(
                macro_expression,
                '\n'.join(traceback.format_exception_only(sys.exc_info()[0],sys.exc_info()[1])))
    def if_tokenized(code):
        #print "code: "+repr(code)
        lines=code.split('\n')
        yield ('if',lines[0])
        #print 'lines: '+repr(lines)
        for line in lines[1:]:
            m=re.match('\$(elif|else)(.*)',line)
            if m:
                yield (m.group(1),m.group(2))
            else:
                #print "data line "+repr(line)
                yield ('data',line)
        raise StopIteration
    def handle_if(code,namespace):
        outbuf=[]
        true_condition_found=0
        for token,content in if_tokenized(code):
            if token=='data' and true_condition_found:
                outbuf.append(content)
            else:
                if true_condition_found: # end of true block reached
                    break
                if token=='if' or token=='elif':
                    true_condition_found=eval(content,namespace)
                elif token=='else':
                    true_condition_found=1
        return '\n'.join(outbuf)
    return process_text(instr)
    
def process_file(infilename,namespace):
    outfilename=outfilename_from_infilename(infilename)
    infile=open(infilename,'rt')
    outfile=open(outfilename,'wt')
    outfile.write(process_macros(infile.read(),namespace))
    outfile.close()
    infile.close()

def templatefiles_in_tree(rootdir):
    files=[]
    for dirpath, dirnames, filenames in os.walk(rootdir):
        files+=[os.path.join(dirpath,x) for x in filenames if is_templatefile(x)]
    return files

def misctest():
    files=templatefiles_in_tree('.')
    print "Templates in tree: "+str(files)

    for k in files:
        print "Processing file: "+k
        process_file(k,namespace)
    # import code
    # code.interact(None,None,locals())

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
    
    
