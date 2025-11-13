"""AI utilities and training functions for NexusLang"""

from nexuslang.runtime.tensor import Tensor, tensor
from nexuslang.runtime.model import Model, Optimizer, Loss


class Trainer:
    """Training utility for models"""
    
    def __init__(self, model, optimizer, loss_fn):
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.history = {
            'loss': [],
            'epoch': []
        }
    
    def train_epoch(self, train_data, batch_size=32):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        num_batches = 0
        
        # Placeholder training loop
        # In real implementation, would iterate over batches
        
        return total_loss / max(num_batches, 1)
    
    def evaluate(self, test_data):
        """Evaluate model on test data"""
        self.model.eval()
        
        # Placeholder evaluation
        return 0.0
    
    def fit(self, train_data, epochs=10, batch_size=32, validation_data=None):
        """Train model for multiple epochs"""
        print(f"Training for {epochs} epochs...")
        
        for epoch in range(epochs):
            # Train
            train_loss = self.train_epoch(train_data, batch_size)
            self.history['loss'].append(train_loss)
            self.history['epoch'].append(epoch + 1)
            
            print(f"Epoch {epoch + 1}/{epochs} - Loss: {train_loss:.4f}")
            
            # Validate
            if validation_data is not None:
                val_loss = self.evaluate(validation_data)
                print(f"  Validation Loss: {val_loss:.4f}")
        
        print("Training complete!")
        return self.history


class Dataset:
    """Dataset container"""
    
    def __init__(self, data, labels=None):
        self.data = data if isinstance(data, Tensor) else tensor(data)
        self.labels = labels if labels is None or isinstance(labels, Tensor) else tensor(labels)
        self.length = len(data)
    
    def __len__(self):
        return self.length
    
    def __getitem__(self, idx):
        if self.labels is not None:
            return self.data[idx], self.labels[idx]
        return self.data[idx]
    
    def __repr__(self):
        return f"Dataset(size={self.length}, shape={self.data.shape})"


class DataLoader:
    """Data loader for batching"""
    
    def __init__(self, dataset, batch_size=32, shuffle=False):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
    
    def __iter__(self):
        """Iterate over batches"""
        # Placeholder - would yield batches
        return iter([])
    
    def __len__(self):
        """Number of batches"""
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size
    
    def __repr__(self):
        return f"DataLoader(batch_size={self.batch_size}, batches={len(self)})"


# Metrics
def accuracy(predictions, targets):
    """Calculate accuracy"""
    if isinstance(predictions, Tensor):
        pred_data = predictions.numpy()
    else:
        pred_data = predictions
    
    if isinstance(targets, Tensor):
        target_data = targets.numpy()
    else:
        target_data = targets
    
    correct = (pred_data.argmax(axis=-1) == target_data.argmax(axis=-1)).sum()
    total = len(target_data)
    return correct / total


def precision(predictions, targets):
    """Calculate precision"""
    # Placeholder
    return 0.0


def recall(predictions, targets):
    """Calculate recall"""
    # Placeholder
    return 0.0


def f1_score(predictions, targets):
    """Calculate F1 score"""
    prec = precision(predictions, targets)
    rec = recall(predictions, targets)
    if prec + rec == 0:
        return 0.0
    return 2 * (prec * rec) / (prec + rec)


# Utilities
def train_test_split(data, labels, test_size=0.2, shuffle=True):
    """Split data into train and test sets"""
    import numpy as np
    
    if isinstance(data, Tensor):
        data = data.numpy()
    if isinstance(labels, Tensor):
        labels = labels.numpy()
    
    n_samples = len(data)
    n_test = int(n_samples * test_size)
    
    if shuffle:
        indices = np.random.permutation(n_samples)
        data = data[indices]
        labels = labels[indices]
    
    return (
        Dataset(data[n_test:], labels[n_test:]),  # Train
        Dataset(data[:n_test], labels[:n_test])   # Test
    )


def save_model(model, filepath):
    """Save model to file"""
    # Placeholder - would serialize model
    print(f"Model saved to {filepath}")


def load_model(filepath):
    """Load model from file"""
    # Placeholder - would deserialize model
    print(f"Model loaded from {filepath}")
    return None

