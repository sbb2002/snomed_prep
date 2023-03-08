import pickle

with open('dict_ix350.pickle', 'rb') as f:
    pk = pickle.load(f)

print(pk)