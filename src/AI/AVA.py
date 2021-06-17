#pylint: disable=C0103, C0301
"""
The custom Adversarial Variational Autoencoder model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import time
import numpy as np
import tensorflow as tf

#First Party Imports
from src.AI.VAE import VAE
from src.AI.Encoder import Encoder
from src.AI.Decoder import Decoder
from src.AI.Discriminator import Discriminator


class AVA(VAE):
    """
    A Adverserial Variational Autoencoder TensorFlow model for Feryv projects.

    Args:
        inputShape (tuple, optional): The resolution and color channels for the input image. Defaults to (256, 256, 3).
        inputName (str, optional): The name of the input layer. Defaults to "InputImage".
        encoder (AI.encoder.Encoder, optional): The encoder. Defaults to None.
        decoder (AI.encoder.Decoder, optional): The decoder. Defaults to None.
        discriminator (AI.encoder.Dsicriminator, optional): The discriminator. Defaults to None.
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
    """

    def __init__(self, inputShape=(256, 256, 3), latentDim=512, encoder: Encoder=None,
                 decoder: Decoder=None, discriminator: Discriminator=None,
                 optimizer: tf.keras.optimizers.Optimizer=tf.optimizers.Adam()):
        super(AVA, self).__init__(inputShape, latentDim, encoder, decoder, optimizer)
        
        self.cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)
            
        self.discriminator: Discriminator = Discriminator(inputShape=inputShape)
        if discriminator:
            self.discriminator: Discriminator = discriminator


    def discriminator_loss(self, real_output, fake_output):
        real_loss = self.cross_entropy(tf.ones_like(real_output), real_output)
        fake_loss = self.cross_entropy(tf.zeros_like(fake_output), fake_output)
        total_loss = real_loss + fake_loss

        return total_loss


    def decoder_loss(self, fake_output):
        return self.cross_entropy(tf.ones_like(fake_output), fake_output)
    
    
    # Notice the use of `tf.function`
    # This annotation causes the function to be "compiled".
    @tf.function
    def train_step(self, images):
        super(AVA, self).train_step(images)

        with tf.GradientTape() as decoderTape, tf.GradientTape() as discriminatorTape:
            mean, logvar = self.encode(images)
            z = self.reparameterize(mean, logvar)
            generated_images = self.sample(z)

            real_output = self.discriminator(images, training=True)
            fake_output = self.discriminator(generated_images, training=True)

            decoderLoss = self.decoder_loss(fake_output)
            disc_loss = self.discriminator_loss(real_output, fake_output)

        decoderGradients = decoderTape.gradient(decoderLoss, self.decoder.trainable_variables)
        discriminatorGradients = discriminatorTape.gradient(disc_loss, self.discriminator.trainable_variables)

        self.decoder.optimizer.apply_gradients(zip(decoderGradients, self.decoder.trainable_variables))
        self.discriminator.optimizer.apply_gradients(zip(discriminatorGradients, self.discriminator.trainable_variables))


    def train(self, train_dataset, epochs):
        for epoch in range(epochs):
            start = time.time()

            for image_batch in train_dataset:
                self.train_step(image_batch)

            print ('Time for epoch {} is {} sec'.format(epoch + 1, time.time()-start))
