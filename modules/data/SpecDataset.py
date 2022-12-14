import torch 
from .SimpleDataset import SimpleDataset
import warnings

class SpecDataset(SimpleDataset):
    """
    Initialized in the same way as SimpleDataset
    Only overwrites the __getitem__ method to load
    a spectrogram from memory instead of an .ogg file
    """
    def __getitem__(self, idx, debug=False):
        """
        Load a file and take the union of the primary and secondary labels as a label
        """
        path = f"""{self.data_path}{
            self.df.loc[idx, 'filename'].replace('.ogg', '.pt')
        }"""
        label = self.get_label(idx)
        
        if debug: print(path)

        try:
            spectrogram = torch.load(path)
        except:
            warnings.warn(f'Warning! Possibly corrupted file: {path}. Using unsafe solution')
            spectrogram = torch.zeros((64, 1111)) 
        

        return spectrogram, label, path