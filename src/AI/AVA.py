#pylint: disable=C0103, C0301
"""
The custom Adversarial Variational Autoencoder model for TFModel
"""
__author__ = "Noupin"

#Third Party Imports
import os
import time
from typing import Tuple
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
        decoder (AI.decoder.Decoder, optional): The decoder. Defaults to None.
        discriminator (AI.discriminator.Dsicriminator, optional): The discriminator. Defaults to None.
        optimizer (tf.optimizers.Optimizer, optional): The optimizer to use when compiling the model. Defaults to tf.optimizers.Adam().
        loss (function, optional): The loss function to use when compiling the model. Defaults to tf.losses.mean_absolute_error.
    """

    def __init__(self, inputShape=(256, 256, 3), latentDim=512, encoder: Encoder=None,
                 decoder: Decoder=None, discriminator: Discriminator=None,
                 optimizer: tf.keras.optimizers.Optimizer=tf.optimizers.Adam,
                 discriminatorSteps: int=5):
        super(AVA, self).__init__(inputShape=inputShape, latentDim=latentDim,
                                  encoder=encoder, decoder=decoder, optimizer=optimizer)
        
        self.loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)
        self.discriminatorSteps = discriminatorSteps
        self.clipConstant = 0.01
            
        self.discriminator: Discriminator = Discriminator(inputShape=inputShape,
                                                          optimizer=optimizer)
        if discriminator:
            self.discriminator: Discriminator = discriminator
    
    
    def compileModel(self, optimizer: tf.optimizers.Optimizer=None, loss=None) -> None:
        """
        Compiles self.model.

        Args:
            optimizer (tf.optimizers.Optimizer, optional): The optimizer to apply to self.model. Defaults to None.
            loss (function, optional): The loss to apply to self.model. Defaults to None.
        """
        
        super(AVA, self).compileModel(optimizer=optimizer, loss=loss)

        self.discriminator.compileModel(optimizer=optimizer, loss=loss)
    
    
    def saveModel(self, path: str, **kwargs):
        """
        Saves the weights of the models to be loaded in to path.

        Args:
            path (str): The path to save the weights to.
            kwargs: The keyword arguments to pass to tf.Model.save_weights.
        """

        super(AVA, self).saveModel(path, **kwargs)
        
        self.discriminator.saveModel(os.path.join(path, "discriminator"))


    def loadModel(self, path: str, **kwargs):
        """
        Loads the encoder, decoder, and discriminator to be used again.

        Args:
            path (str): The path to load the models from.
            kwargs: The keyword arguments to pass to TFModel.load.
        """
        
        super(AVA, self).loadModel(path, **kwargs)
        
        self.discriminator.loadModel(os.path.join(path, "discriminator"), **kwargs)


    def decoderLoss(self, generatedDiscOutput):
        generatedLoss = self.loss(tf.ones_like(generatedDiscOutput), generatedDiscOutput)

        return -tf.reduce_mean(generatedLoss)


    def discriminatorLoss(self, realDiscOutput, generatedDiscOutput):
        realLoss = self.loss(tf.ones_like(realDiscOutput), realDiscOutput)
        generatedLoss = self.loss(tf.zeros_like(generatedDiscOutput), generatedDiscOutput)

        return tf.reduce_mean(realLoss) - tf.reduce_mean(generatedLoss)


    @tf.function
    def train_step(self, images) -> Tuple[float, float, float]:
        for _ in range(self.discriminatorSteps):
            with tf.GradientTape() as discriminatorTape:
                #Get generated image from VAE
                mean, logvar = self.encode(images, training=True)
                z = self.reparameterize(mean, logvar)
                generatedImages: tf.Tensor = self.sample(z, training=True)

                realDiscOutput = self.discriminator(images, training=True)
                generatedDiscOutput = self.discriminator(generatedImages, training=True)

                discriminatorLoss = self.discriminatorLoss(realDiscOutput,
                                                           generatedDiscOutput)

                discriminatorGradients = discriminatorTape.gradient(discriminatorLoss,
                                                                    self.discriminator.trainable_variables)
                self.discriminator.optimizer.apply_gradients(
                    zip(discriminatorGradients, self.discriminator.trainable_variables)
                )
                
                for weight in self.discriminator.trainable_variables:
                    weight.assign(tf.clip_by_value(weight, -self.clipConstant, self.clipConstant))

        with tf.GradientTape() as decoderTape:
            #Get generated image from VAE
            mean, logvar = self.encode(images, training=True)
            z = self.reparameterize(mean, logvar)
            generatedImages: tf.Tensor = self.sample(z, training=True)
            
            generatedDiscOutput = self.discriminator(generatedImages, training=True)
            decoderLoss = self.decoderLoss(generatedDiscOutput)

            decoderGradients = decoderTape.gradient(decoderLoss, self.decoder.trainable_variables)
            self.decoder.optimizer.apply_gradients(
                zip(decoderGradients, self.decoder.trainable_variables)
            )
        
        VAELoss = super(AVA, self).train_step(images)

        return VAELoss, decoderLoss, discriminatorLoss


    def train(self, trainDataset: tf.data.Dataset, epochs=1) -> None:
        for epoch in range(epochs):
            start = time.time()

            for batch, image_batch in enumerate(trainDataset):
                batchStart = time.time()
                VAELoss, decoderLoss, discriminatorLoss = self.train_step(image_batch)
                print (f"Batch {batch+1}, VAE Loss {VAELoss:.5}, Decoder Loss {decoderLoss:.5}, \
Dicriminator Loss {discriminatorLoss:.5}, in {time.time()-batchStart:.5} sec")

            print (f"Epoch {epoch+1}, VAE Loss {VAELoss:.5}, Decoder Loss {decoderLoss:.5}, \
Dicriminator Loss {discriminatorLoss:.5}, in {time.time()-start:.5} sec")
