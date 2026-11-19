"""Word-level comparison of two PDFs' text, ignoring layout, hyphenation and page numbers.

Usage: python3 build/verify.py previous.pdf new.pdf
"""
import re,difflib,subprocess,sys
def toks(pdf):
    t=subprocess.run(['pdftotext',pdf,'-'],capture_output=True,text=True).stdout
    t=re.sub(r'AQEF MEASUREMENT GUIDE 1\.\d\s*\n*\s*\d*','',t).replace('­','')
    return [re.sub(r'[\-‐]','',w).replace('’',"'") for w in re.findall(r'\S+',t)]
P=toks(sys.argv[1]); N=toks(sys.argv[2])
sm=difflib.SequenceMatcher(None,P,N,autojunk=False)
real=[]
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op=='equal': continue
    a=''.join(P[i1:i2]); b=''.join(N[j1:j2])
    if a==b or (re.fullmatch(r'\d*',a) and re.fullmatch(r'\d*',b)): continue
    real.append((op,i1,' '.join(P[i1:i2]),' '.join(N[j1:j2]),' '.join(P[max(0,i1-6):i1])))
print('words',len(P),len(N),'hunks',len(real))
for r in real: print(r[0],r[1],'| ctx:',r[4][-60:],'|',r[2][:150],'|',r[3][:150])
