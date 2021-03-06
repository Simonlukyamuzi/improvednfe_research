import  os
from torch.utils.data import Dataset
import csv
from itertools import chain
from torch import tensor
import numpy as np
import random

PAD_IDX = 256 


class ExecDataset(Dataset):
    def __init__(self, labels_csv, malicious_dir, benign_dir, max_input_size=10**6, binary=False):
        if not binary:
            with open(malicious_dir + "/" + labels_csv, "rb") as f:
                self.labels_dict = {row[0]: row[1] for row in csv.reader(f, delimiter=',')}
        self.malicious_dir = malicious_dir
        self.benign_dir = benign_dir
        self.benign_tag = 0
        self.tags = range(2 if binary else 10)
        self.max_size = max_input_size

        l = [str(i) for i in range(10)] + ["A", "B", "C", "D", "a", "b", "c", "d", "E", "F", "e", "f"]
        self.string_bytes = [x+y for x, y in zip(l, l)]

        if not binary:
            self.files = [(x, int(self.labels_dict[x[:-6]]))
                      for x in os.listdir(self.malicious_dir) if x.endswith(".bytes")]
        else:
            self.files = [(x, 1)
                          for x in os.listdir(self.malicious_dir) if x.endswith(".bytes")]
        self.files += [(x, 0) for x in os.listdir(self.benign_dir) if x.endswith(".bytes")]
        random.shuffle(self.files)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        f, tag = self.files[idx]
        d = self.malicious_dir if tag != 0 else self.benign_dir
        bytes = [[int(s, 16) for s in line.split()[1:] if s in self.string_bytes]
                 for i, line in enumerate(file(d + "/" + f)) if line !="\n"]
        bytes = list(chain.from_iterable(bytes))
        bytes += [PAD_IDX] * (self.max_size - len(bytes))
        return np.array(bytes), np.array(tag)

    def split_train_and_test(self):
        files= self.files
        random.shuffle(files)


    def get_test_indices(self, test_precent):
        files = self.files
        test_size = int(len(self.files) * test_precent)
        examples_by_class = int(test_size/len(self.tags))
        indices = []

        counters = {i: 0 for i in self.tags}
        for i, (f, tag) in enumerate(files):
            if counters[tag] < examples_by_class:
                indices.append(i)
                counters[tag] += 1
        return indices