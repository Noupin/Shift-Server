#pylint: disable=C0103, C0301
"""
The custom Variational Autoencoder model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import os
import time
import numpy as np
import tensorflow as tf
from typing import Union

#First Party Imports
from src.AI.Encoder import Encoder
from src.AI.Decoder import Decoder


class VAE(tf.keras.Model):
    """
    A Variational Autoencoder TensorFlow model for Feryv projects.

    Args:
        inputShape (tuple, optional): The resolution and color channels for the input image. Defaults to (256, 256, 3).
        inputName (str, optional): The name of the input layer. Defaults to "InputImage".
        encoder (AI.encoder.Encoder, optional): The encoder. Defaults to Encoder().
        decoder (AI.encoder.Decoder, optional): The decoder. Defaults to Decoder().
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
    """

    def __init__(self, inputShape=(256, 256, 3), latentDim=512,
                 encoder: Encoder=None, decoder: Decoder=None,
                 optimizer: tf.keras.optimizers.Optimizer=tf.optimizers.Adam):
        super(VAE, self).__init__()

        self.latentDim = int(latentDim*2)

        self.encoder: Encoder = Encoder(inputShape=inputShape, outputDimension=latentDim,
                                        optimizer=optimizer)
        if encoder:
            self.encoder: Encoder = encoder

        self.decoder: Decoder = Decoder(inputShape=(latentDim,), optimizer=optimizer)
        if decoder:
            self.decoder: Decoder = decoder
            self.latentDim = self.decoder.inputShape[0]


    def call(self, tensor: tf.Tensor, **kwargs) -> tf.Tensor:
        mu, logvar = self.encode(tensor, **kwargs)
        z = self.reparameterize(mu, logvar)
        output = self.sample(z, **kwargs)

        return output
    
    
    def inference(self, tensor: tf.Tensor, asNumpy=True, **kwargs) -> Union[tf.Tensor, np.ndarray]:
        """
        The method TensorFlow uses when calling the class as a tf.keras.Model

        Args:
            tensor (tf.Tensor): The the tensor to inference with.
            asNumpy (bool, optional): Whether or not to return as a numpy array. Defaults to True.
            kwargs: The keyword arguments to pass to the self.call function.

        Returns:
            tf.Tensor or np.ndarray: The inferenced output.
        """
        
        training = False
        if kwargs.get("training"):
            kwargs.pop("training")

        if asNumpy:
            return self.call(tensor, training=training, **kwargs).numpy()
        else:
            return self.call(tensor, training=training, **kwargs)


    def compileModel(self, optimizer: tf.optimizers.Optimizer=None, loss=None) -> None:
        """
        Compiles self.model.

        Args:
            optimizer (tf.optimizers.Optimizer, optional): The optimizer to apply to self.model. Defaults to None.
            loss (function, optional): The loss to apply to self.model. Defaults to None.
        """
        
        self.encoder.compileModel(optimizer=optimizer, loss=loss)
        self.decoder.compileModel(optimizer=optimizer, loss=loss)
    
    
    def saveModel(self, path: str, **kwargs) -> None:
        """
        Saves the weights of the models to be loaded in to path.

        Args:
            path (str): The path to save the weights to.
            kwargs: The keyword arguments to pass to TFModel.saveModel.
        """
        
        self.encoder.saveModel(os.path.join(path, "encoder"), **kwargs)
        self.decoder.saveModel(os.path.join(path, "decoder"), **kwargs)
    
    
    def loadModel(self, path: str, **kwargs):
        """
        Loads the encoder and decoder to be used again.

        Args:
            path (str): The path to load the models from.
            kwargs: The keyword arguments to pass to TFModel.load.
        """
        
        self.encoder.loadModel(os.path.join(path, "encoder"), **kwargs)
        self.decoder.loadModel(os.path.join(path, "decoder"),
                               inputShape=(int(self.latentDim),), **kwargs)


    @tf.function
    def sample(self, eps=None, training=False, **kwargs):
        if eps is None:
            eps = tf.random.normal(shape=(100, self.latentDim))

        return self.decode(eps, apply_sigmoid=True, training=training, **kwargs)


    @staticmethod
    def reparameterize(mu, logvar) -> float:
        eps = tf.random.normal(shape=(mu.shape))

        return (eps * tf.exp(logvar * .5)) + mu


    def encode(self, x, training=False):
        mu, logvar = tf.split(self.encoder(x, training=training), num_or_size_splits=2, axis=1)

        return mu, logvar


    def encodeData(self, x, training=False):
        mu, logvar = self.encode(x, training)
        encoded = self.reparameterize(mu, logvar)
        
        return encoded


    def decode(self, z, apply_sigmoid=False, training=False):
        logits = self.decoder(z, training=training)

        if apply_sigmoid:
            probs = tf.sigmoid(logits)

            return probs

        return logits


    @staticmethod
    def log_normal_pdf(sample, mu, logvar, raxis=1) -> float:
        log2pi = tf.math.log(2. * np.pi)

        return tf.reduce_sum(
            -.5 * ((sample - mu) ** 2. * tf.exp(-logvar) + logvar + log2pi),
            axis=raxis)


    def compute_loss(self, x) -> float:
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_logit = self.decode(z)

        cross_ent = tf.nn.sigmoid_cross_entropy_with_logits(logits=x_logit, labels=x)
        logpx_z = -tf.reduce_sum(cross_ent, axis=[1, 2, 3])
        logpz = self.log_normal_pdf(z, 0., 0.)
        logqz_x = self.log_normal_pdf(z, mu, logvar)

        return -tf.reduce_mean(logpx_z + logpz - logqz_x)


    @tf.function
    def train_step(self, x) -> float:
        """
        Executes one training step and returns the loss.

        This function computes the loss and gradients, and uses the latter to
        update the model's parameters.
        """

        with tf.GradientTape() as encoderTape, tf.GradientTape() as decoderTape:
            loss = self.compute_loss(x)

            encoderGradients = encoderTape.gradient(loss, self.encoder.trainable_variables)
            decoderGradients = decoderTape.gradient(loss, self.decoder.trainable_variables)

            self.encoder.optimizer.apply_gradients(zip(encoderGradients, self.encoder.trainable_variables))
            self.decoder.optimizer.apply_gradients(zip(decoderGradients, self.decoder.trainable_variables))
        
        return loss / 100000.


    def train(self, trainDataset: tf.data.Dataset, testDataset: tf.data.Dataset=None, epochs=1) -> None:
        loss = tf.constant(np.array([0]).astype(np.float32))

        for epoch in range(1, epochs + 1):
            start_time = time.time()
            for train_x in trainDataset:
                loss = self.train_step(train_x)
            end_time = time.time()

            if testDataset:
                loss = tf.keras.metrics.Mean()
                for test_x in testDataset:
                    loss(self.compute_loss(test_x))
                elbo = -loss.result()
                print('Epoch: {}, Test set ELBO: {}, time elapse for current epoch: {}'
                        .format(epoch, elbo, end_time - start_time))
            else:
                print(f"Epoch: {epoch}, Loss: {loss}, Time: {end_time-start_time}")
