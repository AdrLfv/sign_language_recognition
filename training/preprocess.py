from .data_augmentation import Data_augmentation
from typing import Tuple
import torch
import numpy as np
import os
import json

def remove_points(results):
    window = []
    frame = list(results)
    # pose
    for i, _ in enumerate(frame[0:33*4]):
        if i % 4 == 0:
            window.append(frame[i])
            window.append(frame[i+1])

    # left hand
    for i, _ in enumerate(frame[33*4+468*3: 33*4+468*3+21*3]):
        if i % 3 == 0:
            window.append(frame[33*4+468*3+i])
            window.append(frame[33*4+468*3+i+1])

    # right hand
    for i, _ in enumerate(frame[33*4+468*3+21*3:]):
        if i % 3 == 0:
            window.append(frame[33*4+468*3+21*3+i])
            window.append(frame[33*4+468*3+21*3+i+1])

    return window

class Preprocess():
    def __init__(self, actions, DATA_PATH: str, DIR_PATH, sequence_length: int, data_augmentation: bool, device):

        self.actions = actions
        self.DATA_PATH = DATA_PATH
        self.DIR_PATH = DIR_PATH
        self.data_augmentation = data_augmentation
        self.sequence_length = sequence_length
        self.device = device
        seq_nb_multiplier = 1
        self.nb_local_sequences = len(os.listdir(os.path.join(self.DATA_PATH, self.actions[0])))
        self.nb_processed_sequences = self.nb_local_sequences*seq_nb_multiplier if data_augmentation else self.nb_local_sequences

        if(data_augmentation):
            print("Data augmentation is on")

    def __getitem__(self, idx_seq: int) -> Tuple[torch.Tensor, int]:

        # le idx_seq est un index de la sequence actuelle, il est au nombre total du nombre d'actions * le nombre de sequences par action
        # l'indice de sequence que l'on cherche dans les fichiers va de 0 à 23 si le type de preprocess est train, de 0 à 3 s'il est un test,
        # de 0 à 3 s'il est un valid
        ind_action = int(idx_seq/self.nb_processed_sequences)
        ind_seq = idx_seq % self.nb_local_sequences

        window = []
        
        for _, frame_num in enumerate(range(self.sequence_length)):
            dataPath = open(os.path.join(self.DATA_PATH, self.actions[ind_action],
                str(ind_seq), "{}.json".format(frame_num)))
            res = json.load(dataPath)
            if (self.data_augmentation):
                res = Data_augmentation(
                    res, self.DIR_PATH).__getitem__()
            window.append(res)
        
        self.X = np.array(window)
        self.y = ind_action

        self.X = torch.tensor(self.X, dtype=torch.float)
        self.y = torch.tensor(self.y, dtype=torch.long)
        data = self.X, self.y
        return data

    def __len__(self):
        return self.nb_processed_sequences*len(self.actions)

    def get_data_length(self):
        encodedNumpyData = open(os.path.join(self.DATA_PATH, self.actions[0], str(0), "{}.json".format(0)))
        return len(json.load(encodedNumpyData))