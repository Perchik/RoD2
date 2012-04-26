#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     
#
# Author:      PSDUKES
#
# Created:     24/04/2012
# Copyright:   (c) PSDUKES 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------


from sklearn import svm
from sklearn import cross_validation
from sklearn import metrics
import numpy as np
import pylab as pl
import math
from buzhug import Base
import os

from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.svm import SVC

from sklearn.ensemble import ExtraTreesClassifier
from sklearn.externals import joblib
from sklearn.preprocessing import Scaler
from sklearn.cross_validation import StratifiedKFold, KFold
###############################################################################

def main():
	X =[]
	Y=[]
	featuresDB = Base(os.getcwd()+"\\Databases\\features.db")
	featuresDB.open()
	print "features open"
 
	for rec in featuresDB:
		vec = []
		vec.append(rec.f1)
		vec.append(rec.f3)
		vec.append(rec.f4)
		vec.append(rec.f5)
		vec.append(rec.f6)
		vec.append(rec.f7)
		vec.append(rec.f10)
		vec.append(rec.f11)
		vec.append(rec.f12)
		vec.append(rec.f13)
		vec.append(rec.f14)
		vec.append(rec.f15)
		vec.append(rec.f16)
		vec.append(rec.f17)
		vec.append(rec.f18)
		vec.append(rec.f19)
		vec.append(rec.f20)
		vec.append(rec.f21)
		vec.append(rec.f22)
		vec.append(rec.f23)
		X.append(vec)
		Y.append(rec.score)
	print "building classifier"	

	Y = np.array(Y)
	ybar = Y.mean()
	for i in range(len(Y)):
		if Y[i]<ybar: 
			Y[i]=1
		else:
			 Y[i]=2
	scaler = Scaler().fit(X)
	X = scaler.transform(X)
	
	X= np.array(X)
	Y=np.array(Y)

	skf = cross_validation.StratifiedKFold(Y,k=2)
	for train, test in skf:
		X_train, X_test = X[train], X[test]
		y_train, y_test = Y[train], Y[test]

	
	clf = ExtraTreesClassifier(n_estimators=8,max_depth=None,min_split=1,random_state=0,compute_importances=True)
	scores = cross_validation.cross_val_score(clf,X_train,y_train,cv=5)
	
	clf.fit_transform(X_train,y_train)
	print "Accuracy: %0.4f (+/- %0.2f)" % (scores.mean(), scores.std() / 2)
	print clf.feature_importances_

	y_pred =clf.predict(X_test)
	print	classification_report(y_test,y_pred)
	
	model=(scaler,clf)
	joblib.dump(model,'AestheticModel\\aestheticModel.pkl')
	
	print "Done"
	
if __name__ == '__main__':
    main()
