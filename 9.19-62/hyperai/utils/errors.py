# Copyright (c) 2014-2017, NVIDIA CORPORATION.  All rights reserved.


class HyperaiError(Exception):
    """
    hyperai custom exception
    """
    pass


class DeleteError(HyperaiError):
    """
    Errors that occur when deleting a job
    """
    pass


class LoadImageError(HyperaiError):
    """
    Errors that occur while loading an image
    """
    pass


class UnsupportedPlatformError(HyperaiError):
    """
    Errors that occur while performing tasks in unsupported platforms
    """
    pass
