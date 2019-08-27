import os
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
import matplotlib.pyplot as plt
import math
from sklearn.metrics import mean_squared_error
from keras import optimizers
from keras.callbacks import EarlyStopping
from keras import optimizers
 
look_back = 1
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i + look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back])
    return np.array(dataX), np.array(dataY)
 
# file loader
fullpath = 'data.csv'
pandf = pd.read_csv(fullpath,  index_col=0) # 인덱스 컬럼 0번째에는 날짜 정보가 있음.
 
# convert nparray
nparr = pandf['close'].values[::-1]
nparr = nparr.astype('float32')
# print(nparr)
 
# normalization
scaler = MinMaxScaler()
# scaler = RobustScaler()
# scaler = StandardScaler()
nptf = scaler.fit_transform(nparr.reshape(-1, 1))
 
# split train, test
train_size = int(len(nptf) * 0.9)
test_size = len(nptf) - train_size
train, test = nptf[0:train_size], nptf[train_size:len(nptf)]
# print(len(train), len(test))
 
# create dataset for learning
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
 
# reshape input to be [samples, time steps, features]
trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
 
# simple lstm network learning
model = Sequential()
model.add(LSTM(3, input_shape=(1, look_back), return_sequences=False, kernel_initializer='glorot_normal'))
# model.add(Dropout(0.2))
# model.add(LSTM(4, return_sequences=True, kernel_initializer='glorot_normal'))
# model.add(Dropout(0.2))
model.add(Dense(1))
adam = optimizers.adam(lr=0.01)
model.compile(loss='mean_squared_error', optimizer=adam)

# early_stop = EarlyStopping(monitor='loss', patience=4, verbose=1)
# model.fit(trainX, trainY, epochs=30, batch_size=1, verbose=2, callbacks=[early_stop])
model.fit(trainX, trainY, epochs=30, batch_size=1, verbose=2)
 
# make prediction
testPredict = model.predict(testX)
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform(testY)
testScore = math.sqrt(mean_squared_error(testY, testPredict))
print('Train Score: %.2f RMSE' % testScore)
 
# predict last value (or tomorrow?)
lastX = nptf[-1]
lastX = np.reshape(lastX, (1, 1, 1))
lastY = model.predict(lastX)
lastY = scaler.inverse_transform(lastY)
print('Predict the Close value of final day: %d' % lastY)  # 데이터 입력 마지막 다음날 종가 예측
 
# plot
plt.plot(testPredict)
plt.plot(testY)
plt.legend(['testPredict', 'testY'])
plt.show()