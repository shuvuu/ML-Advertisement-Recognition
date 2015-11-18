#!/usr/bin/env python

from __future__ import print_function
from channel_loader import get_data
import sklearn
if sklearn.__version__ < '0.17':
    from sklearn.lda import LDA
else:
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA

def main():
    X_BBC, y_BBC = get_data('BBC')
    X_CNN, y_CNN = get_data('CNN')
    print('# of BBC frames = ' + str(X_BBC.shape[0]))
    print('# of CNN frames = ' + str(X_CNN.shape[0]))

    clf = LDA()
    print('Training...')
    clf.fit(X_BBC.toarray(), y_BBC)

    print('Testing...')
    score = clf.score(X_CNN.toarray(), y_CNN)
    print('score = ' + str(score))

if __name__ == '__main__':
    main()
