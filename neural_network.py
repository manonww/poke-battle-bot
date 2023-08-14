import tensorflow as tf
class DriverNetwork:

    def __init__(self) -> None:
        self.model = None

    
    def initilize_random(self, input_shape:tuple, output_shape:int) -> None:
        ''' Initialize simple NN '''
        self.model =  tf.keras.models.Sequential([
    tf.keras.layers.InputLayer(input_shape=(38,)),
    tf.keras.layers.Dense(10, activation='relu'),
    tf.keras.layers.Dense(output_shape)])