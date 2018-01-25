# code from https://www.kaggle.com/jturkewitz/magic-features-0-03-gain/comments

# This code has the purpose to compute the frequency of 
# the questions with the idea that more frequenct questions 
# are more likely to be duplicates


import numpy as np
import pandas as pd
import timeit
import sys
import os

def generate_question_freq(path):
    train_orig = pd.read_csv(os.path.join(path,'train.csv'), sep=',',names = ["id", "qid1", "qid2", "question1","question2","is_duplicate"])
    test_orig =  pd.read_csv(os.path.join(path,'test.csv'), sep=',',names = ["id", "qid1", "qid2", "question1","question2"])

    tic0=timeit.default_timer()
    df1 = train_orig[['question1']].copy()
    df2 = train_orig[['question2']].copy()
    df1_test = test_orig[['question1']].copy()
    df2_test = test_orig[['question2']].copy()

    df2.rename(columns = {'question2':'question1'},inplace=True)
    df2_test.rename(columns = {'question2':'question1'},inplace=True)

    train_questions = df1.append(df2)
    train_questions = train_questions.append(df1_test)
    train_questions = train_questions.append(df2_test)
    train_questions.drop_duplicates(subset = ['question1'],inplace=True)

    train_questions.reset_index(inplace=True,drop=True)
    questions_dict = pd.Series(train_questions.index.values,index=train_questions.question1.values).to_dict()

    train_cp = train_orig.copy()
    test_cp = test_orig.copy()
    train_cp.drop(['qid1','qid2'],axis=1,inplace=True)

    test_cp['is_duplicate'] = -1
    test_cp.rename(columns={'test_id':'id'},inplace=True)
    comb = pd.concat([train_cp,test_cp])

    comb['q1_hash'] = comb['question1'].map(questions_dict)
    # print(comb['q1_hash'])
    comb['q2_hash'] = comb['question2'].map(questions_dict)

    q1_vc = comb.q1_hash.value_counts().to_dict()
    q2_vc = comb.q2_hash.value_counts().to_dict()

    def try_apply_dict(x,dict_to_apply):
        try:
            return dict_to_apply[x]
        except KeyError:
            return 0
    #map to frequency space

    comb['q1_freq'] = comb['q1_hash'].map(lambda x: try_apply_dict(x,q1_vc) + try_apply_dict(x,q2_vc))
    comb['q2_freq'] = comb['q2_hash'].map(lambda x: try_apply_dict(x,q1_vc) + try_apply_dict(x,q2_vc))

    train_comb = comb[comb['is_duplicate'] >= 0][['id','q1_hash','q2_hash','q1_freq','q2_freq','is_duplicate']]
    test_comb = comb[comb['is_duplicate'] < 0][['id','q1_hash','q2_hash','q1_freq','q2_freq']]
    corr_mat = train_comb.corr()

    print('Writing train features...')
    train_comb.to_csv(os.path.join(path,'train_question_freq.csv'), columns=['q1_freq', 'q2_freq', 'q1_hash', 'q2_hash'])
    print('Writing test features...')    
    test_comb.to_csv(os.path.join(path,'test_question_freq.csv'), columns=['q1_freq', 'q2_freq', 'q1_hash', 'q2_hash'])
    #print(corr_mat)
    #print(test_comb)
    print('CSV written ! see: ', path, " | suffix: ", "_question_freq.csv")


