"""API Config, including MobileNet model storage."""

from django.apps import AppConfig

import tensorflow as tf


def _build_base():
    """Base MobileNet model."""
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=[224, 224, 3], include_top=False, weights='imagenet')
    base_model.trainable = False

    return tf.keras.models.Sequential([
        base_model,
        tf.keras.layers.AveragePooling2D(pool_size=(7, 7)),
        tf.keras.layers.Flatten()])


class ApiConfig(AppConfig):
    """App config.

    Attributes
    ----------
    mobilenet : tf.keras.models.Model
        MobileNet with average pool head pre attached.
    """

    name = 'api'
    mobilenet = _build_base()
