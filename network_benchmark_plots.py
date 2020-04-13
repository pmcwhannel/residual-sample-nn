import sys
sys.path.insert(0,'C:\\Users\\pmcw9\\Winter 2020\\CS 698\\Project Final Folder\\network files')
import Class_Network as Network
import Class_generate_data as generate_data
from sklearn.model_selection import KFold
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras import optimizers
from keras import regularizers
import configparser


def keras_test(X_train, X_test, y_train, y_test, h_nodes, epochs, batch_size, lr, weight_decay, type):
    """
    Trains a regular 3-layer neural net in keras, and returns the accuracy results.

    :param X_train: numpy array/pandas dataframe, data for the keras model.
    :param X_test: numpy array/pandas dataframe, data for the keras model.
    :param y_train: numpy array/pandas dataframe, data for the keras model.
    :param y_test: numpy array/pandas dataframe, data for the keras model.
    :param h_nodes: int, number of nodes in the hidden layer.
    :param epochs: int, number of epochs to train the NN.
    :param batch_size: int, size of a batch when training.
    :param lr: float, learning rate for training.
    :param weight_decay: float, l2-norm weight decay constant.
    :param type: string, select type of loss function.
    :return: (training_acc, test_acc), lists of training/testing accuracies.
    """

    in_dim = X_train.shape[1]
    out_dim = y_train.shape[1]

    keras_model = Sequential()
    keras_model.add(Dense(h_nodes, input_dim=in_dim, activation='sigmoid',
                          kernel_regularizer=regularizers.l2(weight_decay)))
    keras_model.add(Dense(out_dim, activation='sigmoid',
                          kernel_regularizer=regularizers.l2(weight_decay)))

    optimizer = optimizers.SGD(lr=lr)
    keras_model.compile(loss=type, optimizer=optimizer, metrics=['accuracy'])

    history = keras_model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
                              validation_data=(X_test, y_test))

    return (history.history['accuracy'], history.history['val_accuracy'])


def RSNN(X_train, X_test, y_train, y_test, h_nodes, epochs, lr, times, threshold, coefficient, type):
    """
    Trains a regular 3-layer our NN, and returns the accuracy results

    :param X_train: Numpy array/pandas dataframe, data for the keras model.
    :param X_test: Numpy array/pandas dataframe, data for the keras model.
    :param y_train: Numpy array/pandas dataframe, data for the keras model.
    :param y_test: Numpy array/pandas dataframe, data for the keras model.
    :param h_nodes: Int, number of nodes in the hidden layer.
    :param epochs: Int, number of epochs to train the NN.
    :param lr: Float, learning rate for training.
    :param times: Integer, number of times to MC sample.
    :param threshold: Integer, used as threshold for forming residual to sample from.
    :param coefficient: Float, used as the ratio for updating the variance.
    :param type: string, select type of loss function.
    :return: (training_acc, test_acc), lists of training/testing accuracies
    """
    in_dim = X_train.shape[1]
    out_dim = y_train.shape[1]

    #Initialize the network
    net = Network.Network([in_dim, h_nodes, out_dim], type = type, pdw = ['gaussian']*2, pdb = ['gaussian']*2)
    acc_train = [0]*epochs # For storing training accuracy.
    acc_test = [0]*epochs # For storing test accuracy.
    for i in range(0, epochs):
        net.Learn(X_train, y_train, epochs=1, lrate = lr, times = times, threshold = threshold, bootstrap = False, coefficient = coefficient)
        acc_train[i] = net.ClassificationAccuracy(X_train, y_train)
        acc_test[i] = net.ClassificationAccuracy(X_test, y_test)

    return(acc_train, acc_test)


def network_benchmark_plots(X_train, X_test, y_train, y_test, rs_nn_params, keras_params, decay_params):
    """
    Train a dataset with 3 different models.
    1. A Residual Sample Neural Network
    2. A regular neural net in keras
    3. A regular neural net in keras with weight decay

    Then plots are created and saved to the working directory comparing training/test accuracies during the training
    process for each neural network.

    :param X_train: numpy array/pandas dataframe, input data to train
    :param X_test: numpy array/pandas dataframe, input data to test
    :param y_train: numpy array/pandas dataframe, target data to train
    :param y_test: numpy array/pandas dataframe, target data to test
    :param rs_nn_params: Dict, parameters used to create and train the residual sameple neural net
    :param keras_params: Dict, parameters used to create and train the keras neural net
    :param decay_params: Dict, parameters used to create and train the keras neural net with decay
    :return:
    """
    # Train a RS-NN
    (RSNN_train_acc, RSNN_test_acc) = RSNN(X_train, X_test, y_train, y_test, int(rs_nn_params['h_nodes']), int(rs_nn_params['epochs']), float(rs_nn_params['lr']), int(rs_nn_params['times']),float(rs_nn_params['threshold']), float(rs_nn_params['coefficient']),type= rs_nn_params['type'])

    # Train a regular NN
    (keras_train_acc, keras_test_acc) = keras_test(X_train, X_test, y_train, y_test, int(keras_params['h_nodes']),
                                                   int(keras_params['epochs']), int(keras_params['batch_size']),
                                                   float(keras_params['lr']), weight_decay=0,type= keras_params['type'])

    # Train a regular NN with weight decay
    (decay_train_acc, decay_test_acc) = keras_test(X_train, X_test, y_train, y_test, int(decay_params['h_nodes']),
                                                   int(decay_params['epochs']), int(decay_params['batch_size']),
                                                   float(decay_params['lr']), float(decay_params['weight_decay']),type=decay_params['type'])

    # Plot the accuracies
    rsnn_eps = np.arange(1, int(rs_nn_params['epochs']) + 1)
    keras_eps = np.arange(1, int(keras_params['epochs']) + 1)
    decay_eps = np.arange(1, int(decay_params['epochs']) + 1)

    plt.figure(0)
    plt.title("Training Accuracy vs. Epochs)")
    plt.plot(rsnn_eps, RSNN_train_acc)
    plt.plot(keras_eps, keras_train_acc)
    plt.plot(decay_eps,decay_train_acc)
    plt.legend(['RSNN', 'Normal NN','NN with decay'])
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.show()

    plt.figure(1)
    plt.title("Test Accuracy vs. Epochs)")
    plt.plot(rsnn_eps, RSNN_test_acc)
    plt.plot(keras_eps, keras_test_acc)
    plt.plot(decay_eps, decay_test_acc)
    plt.legend(['RSNN', 'Normal NN', 'NN with decay'])
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.show()


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # select correct data
    train_size = int(config['DATA']['train_size'])
    test_size = int(config['DATA']['test_size'])

    if config['DATA']['dataset'] == "simulated":
        generator = generate_data.generate_data(0, 3, 5, 2, 2.5) # Maybe add to config file..
        num_covariates = 2 # number of covariates
        X_train, y_train, yt = generator.generate(n=train_size, p=num_covariates)
        X_test,y_test,yt = generator.generate(n=test_size, p=num_covariates)


    if config['DATA']['dataset'] == "mnist":
        import mnist_loader
        train_full, validate_full, test_full = mnist_loader.load_data_wrapper() # we wont need validate dataset
        X_train = np.array(train_full[0][:train_size])
        y_train = np.array(train_full[1][:train_size])
        X_test = np.array(test_full[0][:test_size])
        y_test = np.array(test_full[1][:test_size])

    # run benchmarking function
    network_benchmark_plots(X_train, X_test, y_train, y_test, config['RS NN PARAMS'], config['KERAS PARAMS'],
                            config['DECAY PARAMS'])

if __name__ == "__main__":
    main()