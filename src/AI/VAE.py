#pylint: disable=C0103, C0301
"""
The custom Variational Autoencoder model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import time
import numpy as np
import tensorflow as tf
from IPython import display

#First Party Imports
from src.AI.Encoder import Encoder
from src.AI.Decoder import Decoder


class VAE(tf.keras.Model):
    """
    A Variational Autoencoder TensorFlow model for Vardia projects.

    Args:
        inputShape (tuple, optional): The resolution and color channels for the input image. Defaults to (256, 256, 3).
        inputName (str, optional): The name of the input layer. Defaults to "InputImage".
        encoder (AI.encoder.Encoder, optional): The encoder. Defaults to Encoder().
        decoder (AI.encoder.Decoder, optional): The decoder. Defaults to Decoder().
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
    """

    def __init__(self, inputShape=(256, 256, 3), latentDim=512,
                       optimizer: tf.keras.optimizers.Optimizer=tf.optimizers.Adam()):
        super(VAE, self).__init__()

        self.optimizer = optimizer

        self.encoder: Encoder = Encoder(inputShape=inputShape, outputDimension=latentDim)
        self.decoder: Decoder = Decoder(inputShape=(latentDim,))


    def call(self, inputTensor):
        mean, logvar = self.encode(inputTensor)
        z = self.reparameterize(mean, logvar)
        output = self.sample(z)

        return output.numpy()


    @tf.function
    def sample(self, eps=None):
        if eps is None:
            eps = tf.random.normal(shape=(100, self.decoder.inputShape[0]))

        return self.decode(eps, apply_sigmoid=True)


    def encode(self, x):
        mean, logvar = tf.split(self.encoder(x), num_or_size_splits=2, axis=1)

        return mean, logvar


    def reparameterize(self, mean, logvar):
        eps = tf.random.normal(shape=mean.shape)

        return eps * tf.exp(logvar * .5) + mean


    def decode(self, z, apply_sigmoid=False):
        logits = self.decoder(z)

        if apply_sigmoid:
            probs = tf.sigmoid(logits)

            return probs

        return logits


    @staticmethod
    def log_normal_pdf(sample, mean, logvar, raxis=1):
        log2pi = tf.math.log(2. * np.pi)

        return tf.reduce_sum(
            -.5 * ((sample - mean) ** 2. * tf.exp(-logvar) + logvar + log2pi),
            axis=raxis)


    def compute_loss(self, x):
        mean, logvar = self.encode(x)
        z = self.reparameterize(mean, logvar)
        x_logit = self.decode(z)
        cross_ent = tf.nn.sigmoid_cross_entropy_with_logits(logits=x_logit, labels=x)
        logpx_z = -tf.reduce_sum(cross_ent, axis=[1, 2, 3])
        logpz = self.log_normal_pdf(z, 0., 0.)
        logqz_x = self.log_normal_pdf(z, mean, logvar)

        return -tf.reduce_mean(logpx_z + logpz - logqz_x)


    @tf.function
    def train_step(self, x):
        """
        Executes one training step and returns the loss.

        This function computes the loss and gradients, and uses the latter to
        update the model's parameters.
        """

        with tf.GradientTape() as tape:
            loss = self.compute_loss(x)

        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))
        
        return loss


    def train(self, train_dataset, test_dataset=None, epochs=1):
        loss = tf.constant(np.array([0]).astype(np.float32))
        for epoch in range(1, epochs + 1):
            start_time = time.time()
            for train_x in train_dataset:
                loss = self.train_step(train_x)
            end_time = time.time()

            if test_dataset:
                loss = tf.keras.metrics.Mean()
                for test_x in test_dataset:
                    loss(self.compute_loss(test_x))
                elbo = -loss.result()
                display.clear_output(wait=False)
                print('Epoch: {}, Test set ELBO: {}, time elapse for current epoch: {}'
                        .format(epoch, elbo, end_time - start_time))
            else:
                print(f"Epoch: {epoch}, Loss: {loss}, Time: {end_time-start_time}")