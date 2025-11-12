"""Tensor implementation for NexusLang AI-native features"""

import numpy as np
from typing import Union, Tuple, List, Any


class Tensor:
    """
    NexusLang Tensor - AI-native tensor type
    Wraps NumPy arrays with a clean API
    """
    
    def __init__(self, data, dtype=None):
        """Create a tensor from data"""
        if isinstance(data, Tensor):
            self.data = data.data
        elif isinstance(data, np.ndarray):
            self.data = data
        else:
            self.data = np.array(data, dtype=dtype)
    
    @property
    def shape(self) -> Tuple:
        """Get tensor shape"""
        return self.data.shape
    
    @property
    def dtype(self):
        """Get tensor data type"""
        return self.data.dtype
    
    @property
    def ndim(self) -> int:
        """Get number of dimensions"""
        return self.data.ndim
    
    @property
    def size(self) -> int:
        """Get total number of elements"""
        return self.data.size
    
    def __repr__(self) -> str:
        return f"Tensor({self.data}, shape={self.shape}, dtype={self.dtype})"
    
    def __str__(self) -> str:
        return f"Tensor({self.data})"
    
    # Arithmetic operations
    def __add__(self, other):
        """Add tensors or scalar"""
        if isinstance(other, Tensor):
            return Tensor(self.data + other.data)
        return Tensor(self.data + other)
    
    def __sub__(self, other):
        """Subtract tensors or scalar"""
        if isinstance(other, Tensor):
            return Tensor(self.data - other.data)
        return Tensor(self.data - other)
    
    def __mul__(self, other):
        """Element-wise multiply"""
        if isinstance(other, Tensor):
            return Tensor(self.data * other.data)
        return Tensor(self.data * other)
    
    def __truediv__(self, other):
        """Element-wise divide"""
        if isinstance(other, Tensor):
            return Tensor(self.data / other.data)
        return Tensor(self.data / other)
    
    def __matmul__(self, other):
        """Matrix multiplication"""
        if isinstance(other, Tensor):
            return Tensor(np.matmul(self.data, other.data))
        return Tensor(np.matmul(self.data, other))
    
    def __getitem__(self, key):
        """Index into tensor"""
        result = self.data[key]
        if isinstance(result, np.ndarray):
            return Tensor(result)
        return result
    
    def __setitem__(self, key, value):
        """Set tensor values"""
        if isinstance(value, Tensor):
            self.data[key] = value.data
        else:
            self.data[key] = value
    
    # Tensor operations
    def reshape(self, *shape):
        """Reshape tensor"""
        return Tensor(self.data.reshape(shape))
    
    def transpose(self, *axes):
        """Transpose tensor"""
        if axes:
            return Tensor(np.transpose(self.data, axes))
        return Tensor(self.data.T)
    
    def flatten(self):
        """Flatten tensor to 1D"""
        return Tensor(self.data.flatten())
    
    def sum(self, axis=None):
        """Sum tensor elements"""
        result = np.sum(self.data, axis=axis)
        if isinstance(result, np.ndarray):
            return Tensor(result)
        return result
    
    def mean(self, axis=None):
        """Mean of tensor elements"""
        result = np.mean(self.data, axis=axis)
        if isinstance(result, np.ndarray):
            return Tensor(result)
        return result
    
    def max(self, axis=None):
        """Maximum value"""
        result = np.max(self.data, axis=axis)
        if isinstance(result, np.ndarray):
            return Tensor(result)
        return result
    
    def min(self, axis=None):
        """Minimum value"""
        result = np.min(self.data, axis=axis)
        if isinstance(result, np.ndarray):
            return Tensor(result)
        return result
    
    # Activation functions
    def relu(self):
        """ReLU activation"""
        return Tensor(np.maximum(0, self.data))
    
    def sigmoid(self):
        """Sigmoid activation"""
        return Tensor(1 / (1 + np.exp(-self.data)))
    
    def tanh(self):
        """Tanh activation"""
        return Tensor(np.tanh(self.data))
    
    def softmax(self, axis=-1):
        """Softmax activation"""
        exp_data = np.exp(self.data - np.max(self.data, axis=axis, keepdims=True))
        return Tensor(exp_data / np.sum(exp_data, axis=axis, keepdims=True))
    
    # Conversion
    def numpy(self):
        """Convert to NumPy array"""
        return self.data
    
    def tolist(self):
        """Convert to Python list"""
        return self.data.tolist()


# Tensor creation functions
def tensor(data, dtype=None):
    """Create a tensor"""
    return Tensor(data, dtype=dtype)


def zeros(*shape, dtype=np.float32):
    """Create tensor of zeros"""
    return Tensor(np.zeros(shape, dtype=dtype))


def ones(*shape, dtype=np.float32):
    """Create tensor of ones"""
    return Tensor(np.ones(shape, dtype=dtype))


def randn(*shape, dtype=np.float32):
    """Create tensor with random normal values"""
    return Tensor(np.random.randn(*shape).astype(dtype))


def rand(*shape, dtype=np.float32):
    """Create tensor with random uniform values"""
    return Tensor(np.random.rand(*shape).astype(dtype))


def arange(start, stop=None, step=1, dtype=np.float32):
    """Create tensor with range of values"""
    if stop is None:
        stop = start
        start = 0
    return Tensor(np.arange(start, stop, step, dtype=dtype))


def linspace(start, stop, num=50, dtype=np.float32):
    """Create tensor with evenly spaced values"""
    return Tensor(np.linspace(start, stop, num, dtype=dtype))

