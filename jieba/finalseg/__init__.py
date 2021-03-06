import re
import os
from math import log

MIN_FLOAT=-3.14e100

def load_model(f_name):
	_curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) )  )
	prob_p_path = os.path.join(_curpath,f_name)
	tab = eval(open(prob_p_path,"rb").read())
	return tab

prob_start = load_model("prob_start.py")
prob_trans = load_model("prob_trans.py")
prob_emit = load_model("prob_emit.py")



def viterbi(obs, states, start_p, trans_p, emit_p):
	V = [{}] #tabular
	path = {}
	for y in states: #init
		V[0][y] = start_p[y] + emit_p[y].get(obs[0],MIN_FLOAT)
		path[y] = [y]
	for t in range(1,len(obs)):
		V.append({})
		newpath = {}
		for y in states:
			(prob,state ) = max([(V[t-1][y0] + trans_p[y0].get(y,MIN_FLOAT) + emit_p[y].get(obs[t],MIN_FLOAT) ,y0) for y0 in states ])
			V[t][y] =prob
			newpath[y] = path[state] + [y]
		path = newpath
	
	(prob, state) = max([(V[len(obs) - 1][y], y) for y in ('E','S')])
	
	return (prob, path[state])


def __cut(sentence):
	prob, pos_list =  viterbi(sentence,('B','M','E','S'), prob_start, prob_trans, prob_emit)
	begin, next = 0,0
	#print pos_list, sentence
	for i,char in enumerate(sentence):
		pos = pos_list[i]
		if pos=='B':
			begin = i
		elif pos=='E':
			yield sentence[begin:i+1]
			next = i+1
		elif pos=='S':
			yield char
			next = i+1
	if next<len(sentence):
		yield sentence[next:]

def cut(sentence):
	if not ( type(sentence) is unicode):
		try:
			sentence = sentence.decode('utf-8')
		except:
			sentence = sentence.decode('gbk','ignore')
	re_han, re_skip = re.compile(ur"([\u4E00-\u9FA5]+)"), re.compile(ur"([\.0-9]+|[a-zA-Z0-9]+)")
	blocks = re_han.split(sentence)
	for blk in blocks:
		if re_han.match(blk):
			for word in __cut(blk):
				yield word
		else:
			tmp = re_skip.split(blk)
			for x in tmp:
				if x!="":
					yield x
