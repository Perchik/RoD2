import sys
import os
from PIL import Image
import numpy as np
import pywt
import math

i = None
X, Y =0, 0
R, G, B = None, None, None
H, S, V = None, None, None
CIE_L, CIE_U, CIE_V = None, None, None

def f1(): #pixel intensity
    sum_ = 0
    for i in range(Y):
        for j in range(X):
            sum_ += V[i][j]
    return sum_/(X*Y)

def f3(): #pixel intensity
	sum_ = 0
	for i in range(Y):
		for j in range(X):
			sum_ += S[i][j]
	return sum_/(X*Y)

def f6(): #rule of thirds
	sum_=0
	for i in range(Y/3, (2*Y)/3):
		for j in range(X/3, (2*X)/3):
			sum_ += S[i][j]
	return sum_*9/(X*Y)

def f10_12(): #texture of H
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

    f9 = sum1/S1

    y2 = len(HL2)
    x2 = len(HL2[0])
    S2 = x2*y2

    sum2=0
    for i in range(y2):
		for j in range(x2):
			sum2 += LH2[i][j]
			sum2 += HL2[i][j]
			sum2 += HH2[i][j]

    f10 = sum2/S2

    y3 = len(HL3)
    x3 = len(HL3[0])
    S3 = x3*y3

    sum3=0
    for i in range(y3):
		for j in range(x3):
			sum3 += LH3[i][j]
			sum3 += HL3[i][j]
			sum3 += HH3[i][j]

    f11 = sum3/S3

    return {'f9':f9, 'f10':f10,'f11':f11, 'f19':(f9+f10+f11)}

def f13_15(): #texture of S
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

    f13 = sum1/S1

    y2 = len(HL2)
    x2 = len(HL2[0])
    S2 = x2*y2

    sum2=0
    for i in range(y2):
		for j in range(x2):
			sum2 += LH2[i][j]
			sum2 += HL2[i][j]
			sum2 += HH2[i][j]

    f14 = sum2/S2

    y3 = len(HL3)
    x3 = len(HL3[0])
    S3 = x3*y3

    sum3=0
    for i in range(y3):
		for j in range(x3):
			sum3 += LH3[i][j]
			sum3 += HL3[i][j]
			sum3 += HH3[i][j]

    f15= sum3/S3

    return {'f13':f13, 'f14':f14,'f15':f15, 'f20':(f13+f14+f15)}

def f16_18(): #texture of V
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

    f16 = sum1/S1

    y2 = len(HL2)
    x2 = len(HL2[0])
    S2 = x2*y2

    sum2=0
    for i in range(y2):
		for j in range(x2):
			sum2 += LH2[i][j]
			sum2 += HL2[i][j]
			sum2 += HH2[i][j]

    f17 = sum2/S2

    y3 = len(HL3)
    x3 = len(HL3[0])
    S3 = x3*y3

    sum3=0
    for i in range(y3):
		for j in range(x3):
			sum3 += LH3[i][j]
			sum3 += HL3[i][j]
			sum3 += HH3[i][j]

    f18= sum3/S3

    return {'f16':f16, 'f17':f17,'f18':f18, 'f21':(f16+f17+f18)}

def f22(): #size
	return X+Y

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
	for i in range(Y):
		for j in range(X):
			hsv = RGBtoHSV( R[i][j], G[i][j], B[i][j])
			H[i][j] = hsv['hue']
			S[i][j] = hsv['sat']
			V[i][j] = hsv['brit']

def ImageRGBtoLUV():
	#http://software.intel.com/sites/products/documentation/hpc/ipp/ippi/ippi_ch6/ch6_color_models.html
	CIE_X = CIE_Y = CIE_Z =[[0 for i in range(X)] for j in range(Y)]
	global CIE_L, CIE_U, CIE_V
	CIE_L = CIE_U = CIE_Z = [[0 for i in range(X)] for j in range(Y)]
	for i in range(Y):
		for j in range(X):
			CIE_X = 0.412453*(R[i][j]/255) + 0.35758*(G[i][j]/255) + 0.180423*(B[i][j]/255)
			CIE_Y = 0.212671*(R[i][j]/255) + 0.71516*(G[i][j]/255) + 0.072169*(B[i][j]/255)
			CIE_Z = 0.019334*(R[i][j]/255) + 0.119193*(G[i][j]/255) + 0.950227*(B[i][j]/255)

	#here xn and yn are the CIE chromaticity coordinates of the D65 white point. Yn =1 is the luminance
	#from http://en.wikipedia.org/wiki/CIELUV#The_forward_transformation and
	#http://software.intel.com/sites/products/documentation/hpc/ipp/ippi/ippi_ch6/ch6_color_models.html
	xn = .312713
	yn = .329016
	Yn = 1
	for i in range(Y):
		for j in range(X):
			if( CIE_Y[i][j]/Yn  <= 0.00885645168):
				CIE_L[i][j] = 903.296296 * (CIE_Y[i][j]/Yn)
			else:
				CIE_L[i][j] = 116* math.pow( (CIE_Y[i][j]/Yn), (1/3)) - 16
			u = 4. * CIE_X[i][j]  / ( CIE_X[i][j] + 15.*CIE_Y[i][j] + 3.*CIE_Z[i][j])
			v = 9. * CIE_Y[i][j]  / ( CIE_X[i][j] + 15.*CIE_Y[i][j] + 3.*CIE_Z[i][j])
			un = 4. *  CIE_X[i][j] / ( -2.*xn + 12.*yn + 3.)
			vn = 9. *  CIE_Y[i][j] / ( -2.*xn + 12.*yn + 3.)
			CIE_U[i][j] = 13 * CIE_L[i][j] * (u - un)
			CIE_V[i][j] = 13 * CIE_L[i][j] * (v - vn)

def initImage(fileloc):
    global X,Y
    global R,G,B
    global H,S,V

    i = Image.open(fileloc)
    X = i.size[0]
    Y = i.size[1]
    print "X:",X,"  Y:",Y
    a = np.asarray(i)

    R = a[:,:,0]
    G = a[:,:,1]
    B = a[:,:,2]

    H =[[0 for i in range(X)] for j in range(Y)]
    S =[[0 for i in range(X)] for j in range(Y)]
    V =[[0 for i in range(X)] for j in range(Y)]

def main():
    print "Initialisation"
    initImage(os.getcwd()+"\\Images\\training_images\\000001.jpg")
    ImageRGBtoHSV()
    print "f1",f1()
    print "f3",f3()
    print "f6",f6()
    print "f10,f11,f12,f19",f10_12()
    print "f13,f14,f15,f20",f13_15()
    print "f16,f17,f17,f18",f16_18()
    print "f22",f22()

if __name__ == '__main__':
	main()
