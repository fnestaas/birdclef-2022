import torch 
import torch.nn as nn
from torch.utils.data import DataLoader 
from typing import Callable
from .Metric import Metric
from .Logging import *
from .Validator import Validator

class Trainer(nn.Module):
    def __init__(
        self, 
        model: nn.Module, 
        data_pipeline_train: nn.Module, 
        data_pipeline_val: nn.Module, 
        validator: Validator, 
        model_saver, 
        criterion: Callable, 
        optimizer: torch.optim.Optimizer, 
        device: str, 
        metrics: list[Metric],
        keep_epochs: bool=False,
        use_wandb: bool=True,
        validate_every: int=-1,
        wandb_args={}, 
    ):
        """
        A trainer that trains a pipeline. 
        Gets the model (full pipeline) as well as data pipelines for training
        and validation, as well as other training modules to train this model.
        See train.py for an example.
        Furthermore,  
        """
        super().__init__()
        self.model = model
        self.data_pipeline_train = data_pipeline_train
        self.data_pipeline_val = data_pipeline_val
        self.model_saver = model_saver
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.validate_every = validate_every
        self.validator = validator
        self.train_logger = TrainLogger(self, metrics=metrics, use_wandb=use_wandb, keep_epochs=keep_epochs, **wandb_args)
    
    def to_device(self, d: dict):
        """
        Send all tensors in dict d to self.device
        """
        for k, v in d.items():
            if isinstance(v, torch.Tensor):
                d[k] = v.to(self.device)
        return d

    def forward_item(self, d: dict):
        """
        Get logits (model output) and labels from a dictionary d provided by a data loader
        """
        d = self.to_device(d)
        d = self.data_pipeline_train(d)
        x, y = d['x'], d['y'].float()
        logits = self.model(x)
        return logits, y

    def validate(
        self, 
        epoch_logger: EpochLogger, 
        val_loader: DataLoader, 
        i: int
    ):
        """
        Perform validation and log it to the epoch_logger
        """
        
        with torch.no_grad():
            self.model.eval()
            for d_v in val_loader:
                y_v_logits, y_v = self.validator(d_v)
                y_v_pred = torch.sigmoid(y_v_logits)
                epoch_logger.register_val(i, y_v_pred, y_v) 

        epoch_logger.val_report(i)
        self.model.train()

    def validate_train(
        self,
        epoch_logger: EpochLogger,
        train_loader: DataLoader,
        i: int
    ):
        """
        Perform validation and log it to the epoch_logger
        """
        with torch.no_grad():
            self.model.eval()
            for d_t in train_loader:
                y_t_logits, y_t = self.validator(d_t)
                y_t_pred = torch.sigmoid(y_t_logits)
                epoch_logger.register_train(i, y_t_pred, y_t)

        epoch_logger.train_report_metrics(i)
        self.model.train()

    def step(self, d):
        logits, y = self.forward_item(d)
        y_pred = torch.sigmoid(logits)
        self.optimizer.zero_grad()
        loss = self.criterion(y_pred, y)
        loss.backward()
        self.optimizer.step()
        return loss

    def train(
        self, 
        train_loader: DataLoader, 
        val_loader: DataLoader, 
        epochs: int=1,
    ):
        """
        Train for some epochs using the train and validation loaders
        """
        self.train_logger.start_training()
        validate_every = self.validate_every

        for epoch in range(epochs):

            epoch_logger = self.train_logger.start_epoch(epoch)
            

            for i, d in enumerate(train_loader):
                assert epoch_logger.i == i, print(f'{i=}{epoch_logger.i=}')
                
                # optimization step
                loss = self.step(d)
                epoch_logger.train_update(loss)

                # reporting etc
                if i % validate_every == validate_every-1 and validate_every > 0: 
                    epoch_logger.train_report()
                    self.validate(epoch_logger, val_loader, i)
                    self.validate_train(epoch_logger, train_loader, i)
                    self.train_logger.wandb_report() # report to wandb etc 
                    
            if validate_every == -1 or i < validate_every + 1:
              epoch_logger.train_report()
              self.validate(epoch_logger, val_loader, validate_every)
              self.validate_train(epoch_logger, train_loader, validate_every)
                
            if self.model_saver != None:
                self.model_saver.save_best_model(epoch_logger.validation_loss(), epoch, self.model, self.optimizer, self.criterion)

            epoch_logger.finish_epoch(train_loader) # report final loss for this epoch
            self.train_logger.wandb_report() # report to wandb etc 
            self.train_logger.finish_epoch() # report to wandb etc 

        # At the end of training: Save model and training curve
        self.model_saver.save_final_model(epochs, self.model, self.optimizer, self.criterion)
        self.train_logger.finish_run()

  


