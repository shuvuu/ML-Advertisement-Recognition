#!/usr/bin/env python

from __future__ import division, print_function
from time import clock, time
from sys import platform

import numpy as np
from sklearn.datasets import load_svmlight_file
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import sklearn
if sklearn.__version__ < '0.17':
    from sklearn.lda import LDA
else:
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.cross_validation import StratifiedKFold
from prototype_selection import PrototypeSelector


def main():
    channels = ( 'NDTV', 'CNN', 'BBC', 'TIMESNOW', 'CNNIBN' )
    learn_methods = (
            { 'class': KNeighborsClassifier, 'name': 'kNN',
                'params': {'n_neighbors': 5}, 'dense_X': False },
            { 'class': LDA, 'name': 'LDA', 'params': {}, 'dense_X': True },
            { 'class': SVC, 'name': 'SVM', 'params': {}, 'dense_X': False },
            { 'class': RandomForestClassifier, 'name': 'Random forest',
                'params': {'n_estimators': 50}, 'dense_X': False },
            { 'class': GradientBoostingClassifier,
                'name': 'Gradient tree boosting',
                'params': {'n_estimators': 100}, 'dense_X': True }
    )

    timer = clock if platform == 'win32' else time

    for channel in channels:
        X, y = load_svmlight_file('../../Dataset/%s.txt' % channel)
        print('Loaded %s dataset...' % channel)
        partition = StratifiedKFold(y, 10)
        reduction_rates = []
        ps_times = []
        
        for method in learn_methods:
            method_class = method['class']
            method_params = method['params']
            train_times = []
            scores = []
            print('Testing with %s...' % method['name'])

            index = 0
            for train, test in partition:
                print('Partition #%d' % index)
                X_train, X_test, y_train, y_test = (X[train], X[test],
                        y[train], y[test])
                X_train = X_train.toarray()
                X_test = X_test.toarray() if method['dense_X'] else X_test
                start_time = timer()
                print(X_train.shape[0])
                ps = PrototypeSelector(X_train, y_train.astype(np.int))
                X_train_red, y_train_red = ps.fcnn_reduce(1)
                # X_train_red, y_train_red = FCNN(n_neighbors=2).reduce_data(
                        # X_train, y_train)
                end_time = timer()
                ps_times.append(end_time - start_time)
                # reduction_rates.append(X_train.shape[0] / X_train_red.shape[0])
                reduction_rates.append(ps.reduction_ratio)
        
                clf = method['class'](**method['params'])
                start_time = timer()
                clf.fit(X_train_red, y_train_red)
                end_time = timer()
                train_times.append(end_time - start_time)

                scores.append(clf.score(X_test, y_test))
                index += 1

            mean_score = mean(scores)
            score_variance = var(scores)
            mean_train_time = mean(train_times)
            train_time_variance = var(train_times)

            print('%s, %s: Q = %f +/- %f, Ttr = %f +/- %f' % (
                channel, method['name'], mean_score, score_variance,
                mean_train_time, train_time_variance))

        mean_reduction_rate = mean(reduction_rates)
        reduction_rate_variance = var(reduction_rates)
        mean_ps_time = mean(ps_times)
        ps_time_variance = var(ps_times)

        print('R = %f +/- %f, Tps = %f +/- %f' % (mean_reduction_rate,
            reduction_rate_variance, mean_ps_time, ps_time_variance))


if __name__ == '__main__':
    main()
