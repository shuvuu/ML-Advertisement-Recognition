#!/usr/bin/env python

from __future__ import print_function
from channel_loader import get_small_data
from randforest_selection import do_randfor_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn import decomposition, cross_validation
import time, numpy as np, matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier
import sklearn
if sklearn.__version__ < '0.17':
    from sklearn.lda import LDA
else:
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn import neighbors
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
def test_method(clf, name):

    channels = ( 'NDTV', 'TIMESNOW', 'CNNIBN', 'CNN', 'BBC' )

    for channel in channels:
        print('\nProcessing channel {} with method {}'.format(channel, name))
        #f.write('\nProcessing channel {}\n'.format(channel))
        X, y = get_small_data(channel)

        n_features = list()
        for i in range(1,21):
            n_features.append(i*10)
        n_features.append(X.shape[1])

        selector = RandomForestClassifier(n_estimators=60)
        selector.fit(X, y)

        t0 = time.clock()
        result = do_randfor_selection(clf, X.toarray(), y, n_features, selector.feature_importances_)
        testTime = time.clock() - t0
        print('Total time: ' + str(testTime))
        scores = result[0]
        scores_std = result[1]
        times = result[2]

        f = open('RFS-{}-{}.log'.format(name, channel), 'at')
        #f.write('N_features; mean_score; std error; mean training time\n')
        for i in range(0, len(n_features)):
            f.write('{}; {}; {}; {}\n'.format(n_features[i], scores[i], scores_std[i], times[i]))

        f.close()

        plt.clf()
        plt.plot(n_features, scores)
        plt.plot(n_features, np.array(scores) + np.array(scores_std), 'b--')
        plt.plot(n_features, np.array(scores) - np.array(scores_std), 'b--')
        locs, labels = plt.yticks()
        plt.yticks(locs, list(map(lambda x: "%g" % x, locs)))
        plt.ylabel('CV score')
        plt.xlabel('Parameter N')
        #plt.show()
        plt.savefig('{}_{}_r_selection.png'.format(name, channel))

        plt.clf()
        plt.plot(n_features, times)
        locs, labels = plt.yticks()
        plt.yticks(locs, list(map(lambda x: "%g" % x, locs)))
        plt.ylabel('Mean learning time')
        plt.xlabel('Parameter N')
        plt.savefig('{}_{}_r_selection_time.png'.format(name, channel))

def main():

    clf = LDA()
    name = 'LDA'
    test_method(clf, name)

    clf = neighbors.KNeighborsClassifier(n_neighbors = 15)
    name = 'KNN'
    test_method(clf, name)

    svm = SVC(C=4.0)
    clf = Pipeline([('scaler', StandardScaler()), ('svm', svm)])
    name = 'SVM'
    test_method(clf, name)

    
    clf = RandomForestClassifier(n_estimators=60)
    name = 'randforest'
    test_method(clf, name)

    clf = GradientBoostingClassifier(n_estimators=100)
    name = 'gradboosting'
    test_method(clf, name)

if __name__ == '__main__':
    main()
