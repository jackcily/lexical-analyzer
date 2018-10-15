# -*-coding:utf-8 -*-
from auto import *
import sys

#inp = "1(0|1)*101"   #待转换的正规式
#inp = "(ab)*(a*|b*)(ba)*"
#inp = "(1|2)*121"
inp ="(a|b)*.(a.a|b.b).(a|b)*"


nfas = RegextoNFA(inp)  #正规式转成NFA
nfa = nfas.getNFA()
nfas.displayNFA()
#drawGraph(nfa,"mynfa") 绘图函数 需要时使用


dfas = NFAtoDFA(nfa)  #NFA 转成 DFA
dfas.dispalyDFA()
dfa = dfas.getDFA()
#drawGraph(dfa,"myDFA")   绘图函数  需要时使用


mfas = DFAtoMFA(dfa)    #DFA转成MFA
mfas.dispalyMFA()
mfa = mfas.getMFA()
#drawGraph(mfa,"myMFA")  绘图函数 需要时用






