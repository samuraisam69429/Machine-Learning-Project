# -*- coding: utf-8 -*-
"""ML_MINI.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eymH_s-cecZiRQZ2NgROd5kaUSBre4GY
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
np.seterr(divide = 'ignore', invalid = 'ignore')
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix
from tensorflow.keras.datasets.mnist import load_data
from sklearn.model_selection import train_test_split, KFold
from imblearn.over_sampling import SMOTE
import seaborn as sns
# %matplotlib inline

import warnings
warnings.filterwarnings('ignore')

(X_train, Y_train), (X_test, Y_test) = load_data()

def one_hot(Y):
    one_hot_Y = np.zeros((Y.size, Y.max() + 1))
    one_hot_Y[np.arange(Y.size), Y] = 1
    one_hot_Y = one_hot_Y.T
    return one_hot_Y

X_train_flattened = X_train.copy().reshape(60000, 784) / 255
X_test_flattened = X_test.copy().reshape(10000, 784) / 255
Y_train_encoded = one_hot(Y_train)
Y_test_encoded = one_hot(Y_test)

X_full = np.concatenate((X_train_flattened, X_test_flattened))
Y_encoded = np.concatenate((Y_train_encoded, Y_test_encoded), axis = 1)
Y_full = np.concatenate((Y_train, Y_test))

print(X_train_flattened.shape)
print(Y_train_encoded.shape)

print(X_full.shape)
print(Y_full.shape)

unique_vals, counts = np.unique(Y_full, return_counts = True)
print(unique_vals)
print(counts)

sm = SMOTE(random_state = 42)

X_full_smote, Y_full_smote = sm.fit_resample(X_full, Y_full)

unique_vals, counts = np.unique(Y_full_smote, return_counts = True)
print(unique_vals)
print(counts)

X_train_flattened_smote, Y_train_smote = sm.fit_resample(X_train_flattened, Y_train)

unique_vals, counts = np.unique(Y_train, return_counts = True)
print(unique_vals)
print(counts)

unique_vals, counts = np.unique(Y_train_smote, return_counts = True)
print(unique_vals)
print(counts)

plt.matshow(X_train[0])

def init_params(hidden_layers, layer_strengths):
  W = []
  B = []

  if len(layer_strengths) != 0:
    W.append(np.random.rand(layer_strengths[0], 784) - 0.5)
  else:
    W.append(np.random.rand(10, 784) - 0.5)

  for i in range(hidden_layers - 1):
    w = np.random.rand(layer_strengths[i+1], layer_strengths[i]) - 0.5
    b = np.random.rand(layer_strengths[i], 1) - 0.5
    W.append(w)
    B.append(b)

  W.append(np.random.rand(10, layer_strengths[-1]) - 0.5)
  B.append(np.random.rand(layer_strengths[-1], 1) - 0.5)
  B.append(np.random.rand(10, 1) - 0.5)

  return W, B

def ReLU(Z):
    return np.maximum(Z, 0)

def softmax(Z):
  Z -= np.max(Z)
  A = np.exp(Z) / np.sum(np.exp(Z))
  return A

def sigmoid(x):
  return 1 / (1 + np.exp(-x))

def ReLU_deriv(Z):
    return Z > 0

def forward_prop(W, B, X):
    Z = []
    A = [X]

    a = X
    for i in range(len(W)):
      z = np.add(W[i].dot(a), B[i])
      if i == len(W) - 1:
        a = sigmoid(z)
      else:
        a = ReLU(z)
      A.append(a)
      Z.append(z)

    return Z, A

def backward_prop(Z, A, W, X, Y):
    one_hot_Y = one_hot(Y)
    dz = np.subtract(A[-1], one_hot_Y)
    DW = []
    DB = []

    for i in range(len(W)):
      db = np.multiply(1 / 60000, np.sum(dz))
      dw = np.multiply(1 / 60000, dz.dot(A[-2 - i].T))

      if i != len(W) - 1:
        dz = np.multiply(W[-1 - i].T.dot(dz), ReLU_deriv(Z[-2 - i]))

      DW.append(dw)
      DB.append(db)

    DW.reverse()
    DB.reverse()

    return DW, DB

def update_params(W, B, DW, DB, alpha):
    for i in range(len(W)):
      W[i] = np.subtract(W[i], np.multiply(alpha, DW[i]))
      B[i] = np.subtract(B[i], np.multiply(alpha, DB[i]))

    return W, B

def get_predictions(A2):
    return np.argmax(A2, 0)

def get_accuracy(predictions, Y):
    return np.sum(predictions == Y) / Y.size

def gradient_descent(X, Y, alpha, iterations, hidden_layers, layer_strengths):
    W, B = init_params(hidden_layers, layer_strengths)

    for i in range(1, iterations+1):
      X_batch, _, Y_batch, _ = train_test_split(X, Y, shuffle = True, train_size = 1 / 4)
      X_batch = X_batch.T
      Z, A = forward_prop(W, B, X_batch)
      DW, DB = backward_prop(Z, A, W, X_batch, Y_batch)
      W, B = update_params(W, B, DW, DB, alpha)
      if i % 50 == 0 or i == iterations - 1:
          print("Iteration: ", i)
          predictions = get_predictions(A[-1])
          print(get_accuracy(predictions, Y_batch))
    return W, B

W_smote, B_smote = gradient_descent(X_train_flattened_smote, Y_train_smote, 0.8, 600, 2, [40, 20]) # from 8:30 min to 3:30 min

_, outputs_smote = forward_prop(W_smote, B_smote, X_test_flattened.T)

predictions_smote = get_predictions(outputs_smote[-1])

accuracy_smote = get_accuracy(predictions_smote, Y_test)

print(accuracy_smote)

cm_smote = confusion_matrix(predictions_smote, Y_test, labels = range(10))

plt.figure(figsize = (10, 5))
sns.heatmap(cm_smote, annot = True)

#KFold cross validation

def kfold_accuracy(splits):
  kf = KFold(n_splits = splits, shuffle = True)
  avg_acc = 0
  for i, (training_indices, testing_indices) in enumerate(kf.split(X_full_smote)):
    W, B = gradient_descent(X_full_smote[training_indices], Y_full_smote[training_indices], 0.8, 600, 2, [40, 20])
    _, outputs = forward_prop(W, B, X_full_smote[testing_indices].T)
    predictions = get_predictions(outputs[-1])
    acc = get_accuracy(predictions, Y_full_smote[testing_indices])
    print(f'Fold {i} accuracy: {acc}')
    avg_acc += acc / splits
  return avg_acc

kfold_acc = kfold_accuracy(7)

print(kfold_acc)

