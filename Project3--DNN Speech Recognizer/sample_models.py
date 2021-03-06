from keras import backend as K
from keras.models import Model
from keras.layers import (BatchNormalization, Conv1D, Dense, Input, 
    TimeDistributed, Activation, Bidirectional, SimpleRNN, GRU, LSTM, MaxPooling1D)

def simple_rnn_model(input_dim, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(output_dim, return_sequences=True, 
                 implementation=2, name='rnn')(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(simp_rnn)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def rnn_model(input_dim, units, activation, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(units, activation=activation,
        return_sequences=True, implementation=2, name='rnn')(input_data)
    # TODO: Add batch normalization 
    bn_rnn = BatchNormalization(momentum = 0.9)(simp_rnn)
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model


def cnn_rnn_model(input_dim, filters, kernel_size, conv_stride,
    conv_border_mode, units, output_dim=29):
    """ Build a recurrent + convolutional network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add convolutional layer
    conv_1d = Conv1D(filters, kernel_size, 
                     strides=conv_stride, 
                     padding=conv_border_mode,
                     activation='relu',
                     name='conv1d')(input_data)
    # Add batch normalization
    bn_cnn = BatchNormalization(name='bn_conv_1d')(conv_1d)
    # Add a recurrent layer
    simp_rnn = SimpleRNN(units, activation='relu',
        return_sequences=True, implementation=2, name='rnn')(bn_cnn)
    # TODO: Add batch normalization
    bn_rnn = BatchNormalization(name='bn_rnn')(simp_rnn)
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: cnn_output_length(
        x, kernel_size, conv_border_mode, conv_stride)
    print(model.summary())
    return model

def cnn_output_length(input_length, filter_size, border_mode, stride,
                       dilation=1):
    """ Compute the length of the output sequence after 1D convolution along
        time. Note that this function is in line with the function used in
        Convolution1D class from Keras.
    Params:
        input_length (int): Length of the input sequence.
        filter_size (int): Width of the convolution kernel.
        border_mode (str): Only support `same` or `valid`.
        stride (int): Stride size used in 1D convolution.
        dilation (int)
    """
    if input_length is None:
        return None
    assert border_mode in {'same', 'valid'}
    dilated_filter_size = filter_size + (filter_size - 1) * (dilation - 1)
    if border_mode == 'same':
        output_length = input_length
    elif border_mode == 'valid':
        output_length = input_length - dilated_filter_size + 1
    return (output_length + stride - 1) // stride

def deep_rnn_model(input_dim, units, recur_layers, output_dim=29):
    """ Build a deep recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    rnn = GRU(units, activation='relu',
                return_sequences=True, implementation=2, name = 'rnn_1')(input_data)
    # batch normalization 
    bn_rnn = BatchNormalization(name = 'bn_rnn_1')(rnn)
    i = 1
    # TODO: Add recurrent layers, each with batch normalization
    while i < recur_layers:
        rnn = GRU(units, activation='relu',
                    return_sequences=True, implementation=2, name = 'rnn_' + str(i+1))(bn_rnn)
        # batch normalization 
        bn_rnn = BatchNormalization(name = 'bn_rnn_' + str(i+1))(rnn)
        i += 1
    #second rnn layer + batch normalization
    #rnn_2 = GRU(units, activation='relu',
     #           return_sequences=True, implementation=2, name='rnn_2')(bn_rnn_1)
    #bn_rnn_2 = BatchNormalization(name = 'bn_rnn_2', momentum = 0.9)(rnn_2)
    
    #third rnn layer + batch normalization
    #rnn_3 = GRU(units, activation='relu',
     #           return_sequences=True, implementation=2, name='rnn_3')(bn_rnn_2)
    #bn_rnn_3 = BatchNormalization(name = 'bn_rnn_3', momentum = 0.9)(rnn_3)
    
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    
    time_dense = TimeDistributed(Dense(output_dim))(bn_rnn)
                
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def bidirectional_rnn_model(input_dim, units, output_dim=29):
    """ Build a bidirectional recurrent network for speech
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Add bidirectional recurrent layer
    bidir_rnn = Bidirectional(GRU(units, activation='relu',
                return_sequences=True, implementation=2))(input_data)
    # TODO: Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bidir_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

def final_model(input_dim, filters, kernel_size, conv_stride,
    conv_border_mode, pool_size, units, output_dim=29):
    """ Build a deep network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Specify the layers in your network
    #Convolutional layer
    conv_1d = Conv1D(filters, kernel_size,
                     strides = conv_stride,
                     padding = conv_border_mode,
                     activation = 'relu',
                     name = 'conv_1d')(input_data)
    #Max Pooling
    mp_cnn = MaxPooling1D(pool_size = pool_size, padding = conv_border_mode, name = 'max_pooling')(conv_1d)
    #Batch Norm
    bn_cnn = BatchNormalization(name = 'bn_cnn')(mp_cnn)
    
    #Bidirctional RNN
    bidri_rnn_1 = Bidirectional(GRU(units, activation = 'relu',
                                 return_sequences = 'True', implementation = 2,
                                 dropout = 0.2, name = 'bidri_rnn_1'))(bn_cnn)
    #Batch Norm
    bn_bidri_rnn_1 = BatchNormalization(name = 'bn_bidri_rnn_1')(bidri_rnn_1)
    
    #Bidirctional RNN
    bidri_rnn_2 = Bidirectional(GRU(units, activation = 'relu',
                                 return_sequences = 'True', implementation = 2,
                                 dropout = 0.2, name = 'bidri_rnn_2'))(bn_bidri_rnn_1)
    #Batch Norm
    bn_bidri_rnn_2 = BatchNormalization(name = 'bn_bidri_rnn_2')(bidri_rnn_2)
    
    #RNN
    rnn = GRU(units, activation = 'relu',
              return_sequences = 'True', implementation = 2,
              dropout = 0.2, name = 'rnn')(bn_bidri_rnn_2)
    bn_rnn = BatchNormalization(name = 'bn_rnn')(rnn)
    # TODO: Add softmax activation layer
    y_pred = Activation('softmax', name = 'softmax')(bn_rnn)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    # TODO: Specify model.output_length
    model.output_length = lambda x: mp_output_length(
        x, kernel_size, conv_border_mode, conv_stride, pool_size)
    print(model.summary())
    return model
     
def mp_output_length(input_length, filter_size, border_mode, stride, pool):
    
    if input_length is None:
        return None
    
    #cnn_output = cnn_output_length(input_length, filter_size, border_mode, stride)
    
    assert border_mode in {'same', 'valid'}
    
    if border_mode == 'same':
        output_length = cnn_output_length(input_length, filter_size, border_mode, stride)
    elif border_mode == 'valid':
        output_length = cnn_output_length(input_length, filter_size, border_mode, stride) - pool + 1
    return output_length // pool  
