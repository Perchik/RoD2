import sys
import os
from PIL import Image
import numpy as np
import pywt
import math
from buzhug import Base
from sklearn.externals import joblib



def f1(): #pixel intensity
	global X,Y
	global V
	sum_ = 0
	for i in range(Y):
	    for j in range(X):
	        sum_ += V[i][j]
	return float(sum_)/float((X*Y))

def f3(): #pixel intensity
	global X,Y
	global S
	sum_ = 0
	for i in range(Y):
		for j in range(X):
			sum_ += S[i][j]
	return float(sum_)/float((X*Y))

def f4(): #pixel intensity
	global X,Y
	global H
	sum_ = 0
	for i in range(Y):
		for j in range(X):
			sum_ += H[i][j]
	return float(sum_)/float((X*Y))

def f5(): #rule of thirds
	global X,Y
	global H
	sum_=0
	for i in range(Y/3, (2*Y)/3):
		for j in range(X/3, (2*X)/3):
			sum_ += H[i][j]
	return float(sum_*9)/float((X*Y))

def f6(): #rule of thirds
	global X,Y
	global S
	sum_=0
	for i in range(Y/3, (2*Y)/3):
		for j in range(X/3, (2*X)/3):
			sum_ += S[i][j]
	return float(sum_*9)/float((X*Y))

def f7(): #rule of thirds
	global X,Y
	global V
	sum_=0
	for i in range(Y/3, (2*Y)/3):
		for j in range(X/3, (2*X)/3):
			sum_ += V[i][j]
	return float(sum_*9)/float((X*Y))

def f10_12(): #texture of H
    global H
    LL, (LH1, HL1, HH1), (LH2, HL2, HH2), (LH3, HL3, HH3) = pywt.wavedec2(H ,'db4', level=3)
    y1 = len(HL1)
    x1 = len(HL1[0])
    S1 = x1*y1

    sum1=0
    for i in range(y1):
		for j in range(x1):
			sum1 += LH1[i][j]
			sum1 += HL1[i][j]
			sum1 += HH1[i][j]

    f10 = float(sum1)/float(S1)

    y2 = len(HL2)
    x2 = len(HL2[0])
    S2 = x2*y2

    sum2=0
    for i in range(y2):
		for j in range(x2):
			sum2 += LH2[i][j]
			sum2 += HL2[i][j]
			sum2 += HH2[i][j]

    f11 = float(sum2)/float(S2)

    y3 = len(HL3)
    x3 = len(HL3[0])
    S3 = x3*y3

    sum3=0
    for i in range(y3):
		for j in range(x3):
			sum3 += LH3[i][j]
			sum3 += HL3[i][j]
			sum3 += HH3[i][j]

    f12 = float(sum3)/float(S3)

    return {'f10':f10,'f11':f11, 'f12':f12,'f19':(f10+f11+f12)}

def f13_15(): #texture of S
    global S
    LL, (LH1, HL1, HH1), (LH2, HL2, HH2), (LH3, HL3, HH3) = pywt.wavedec2(S ,'db4', level=3)
    y1 = len(HL1)
    x1 = len(HL1[0])
    S1 = x1*y1

    sum1=0
    for i in range(y1):
		for j in range(x1):
			sum1 += LH1[i][j]
			sum1 += HL1[i][j]
			sum1 += HH1[i][j]

    f13 = float(sum1)/float(S1)
    
    y2 = len(HL2)
    x2 = len(HL2[0])
    S2 = x2*y2

    sum2=0
    for i in range(y2):
		for j in range(x2):
			sum2 += LH2[i][j]
			sum2 += HL2[i][j]
			sum2 += HH2[i][j]

    f14 =float(sum2)/float(S2)

    y3 = len(HL3)
    x3 = len(HL3[0])
    S3 = x3*y3

    sum3=0
    for i in range(y3):
		for j in range(x3):
			sum3 += LH3[i][j]
			sum3 += HL3[i][j]
			sum3 += HH3[i][j]

    f15= float(sum3)/float(S3)

    return {'f13':f13, 'f14':f14,'f15':f15, 'f20':(f13+f14+f15)}

def f16_18(): #texture of V
    global V
    LL, (LH1, HL1, HH1), (LH2, HL2, HH2), (LH3, HL3, HH3) = pywt.wavedec2(V ,'db4', level=3)
    y1 = len(HL1)
    x1 = len(HL1[0])
    S1 = x1*y1

    sum1=0
    for i in range(y1):
		for j in range(x1):
			sum1 += LH1[i][j]
			sum1 += HL1[i][j]
			sum1 += HH1[i][j]

    f16 = float(sum1)/float(S1)

    y2 = len(HL2)
    x2 = len(HL2[0])
    S2 = x2*y2

    sum2=0
    for i in range(y2):
		for j in range(x2):
			sum2 += LH2[i][j]
			sum2 += HL2[i][j]
			sum2 += HH2[i][j]

    f17 = float(sum2)/float(S2)

    y3 = len(HL3)
    x3 = len(HL3[0])
    S3 = x3*y3

    sum3=0
    for i in range(y3):
		for j in range(x3):
			sum3 += LH3[i][j]
			sum3 += HL3[i][j]
			sum3 += HH3[i][j]

    f18= float(sum3)/float(S3)

    return {'f16':f16, 'f17':f17,'f18':f18, 'f21':(f16+f17+f18)}

def f22(): #size
	global X,Y
	return float(X+Y)

def f23(): #aspect Ratio
	global X,Y
	return float(X)/float(Y)

def RGBtoHSV(r,g,b):
	r = float(r)/255
	g = float(g)/255
	b = float(b)/255

	min_ = min(r,g,b)
	max_ = max(r,g,b)
	V = max_

	delta = max_ - min_
	if(max_ != min_):
		S = delta / max_

		if(r == max_):
			H = ( g - b )/ delta
		elif(g == max_):
			H = 2 + ( b - r )/delta
		else :
			H = 4 + ( r - g)/delta
		H *=60  #to degrees
		if(H < 0):
			H += 360
	else:
		#r=g=b=0
		S= 0
		H = -1
	return {'hue':H, 'sat':S, 'brit':V}

def ImageRGBtoHSV():
	global R,G,B
	global H,S,V
	
	for i in range(Y):
		for j in range(X):
			hsv = RGBtoHSV( R[i][j], G[i][j], B[i][j])
			H[i][j] = hsv['hue']
			S[i][j] = hsv['sat']
			V[i][j] = hsv['brit']


def initImage(fileloc):
	global X,Y
	global R,G,B
	global H,S,V
	
	im = None
	im = Image.open(fileloc)
	im.thumbnail( (800,600) )
	
	X = im.size[0]
	Y = im.size[1]
	
	
	a = np.asarray(im)

	if(im.getbands()[0]!="L"):
		R = a[:,:,0]
		G = a[:,:,1]
		B = a[:,:,2]
	else:
		R= a[:,:]
		G= a[:,:]
		B= a[:,:]
	H =[[0 for i in range(X)] for j in range(Y)]
	S =[[0 for i in range(X)] for j in range(Y)]
	V =[[0 for i in range(X)] for j in range(Y)]
	
def getScore(fileloc):
	global X,Y
	global R,G,B
	global H,S,V
	global segLevel
	
	X, Y =0, 0
	fe1=fe3=fe7=fe10=fe11=fe12=fe13=fe14=fe15=fe16=fe17=fe18=fe19=fe20=fe21=fe22=fe23=0
	f1012=f1315=f1618=0
	R, G, B = None, None, None
	H, S, V = None, None, None
	initImage(fileloc)
	ImageRGBtoHSV()
	fe1 = f1()
	fe3 = f3()
	fe4 = f4()
	fe5 = f5()
	fe6 = f6()
	fe7 = f7()
	f1012=f10_12()
	fe10=f1012['f10']
	fe11=f1012['f11']
	fe12=f1012['f12']
	fe19=f1012['f19']
	
	f1315=f13_15()
	fe13 = f1315['f13']
	fe14 = f1315['f14']
	fe15 = f1315['f15']
	fe20 = f1315['f20']
	
	f1618=f16_18()
	fe16 = f1618['f16']
	fe17 = f1618['f17']
	fe18 = f1618['f18']
	fe21 = f1618['f21']
	
	fe22= f22()
	fe23= f23()
	
	vec=[fe1,fe3,fe4,fe5,fe6,fe7,fe10,fe11,fe12,fe13,fe14,fe15,fe16,fe17,fe18,fe19,fe20,fe21,fe22,fe23]
	scaler.transform(vec)
	vec = np.array(vec)
	return int(clf.predict(vec)[0])
		
			
def LoadModel():
	X, Y =0, 0
	R, G, B = None, None, None
	H, S, V = None, None, None
	model = joblib.load('AestheticModel\\aestheticModel.pkl')
	
	global clf, scaler
	scaler,clf= model


def main():
	LoadModel()

	print "image 1, score:",getScore(os.getcwd()+"\\test1.jpg")
	print "image 2, score:",getScore(os.getcwd()+"\\test2.jpg")
	print "image 3, score:",getScore(os.getcwd()+"\\test3.jpg")
	print "image 4, score:",getScore(os.getcwd()+"\\test4.jpg")
	print "image 5, score:",getScore(os.getcwd()+"\\test5.jpg")
	print "image 6, score:",getScore(os.getcwd()+"\\test6.jpg")
	
if __name__ == '__main__':
    main()