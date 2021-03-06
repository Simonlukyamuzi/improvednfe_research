import  os
from torch.utils.data import Dataset
import csv
from itertools import chain 
from torch import tensor
import numpy as np
import random

PAD_IDX = 256


class ExecDataset(Dataset):
    def __init__(self, labels_csv, malicious_dir, benign_dir, max_input_size=2*(10**6), binary=False, only_use=None):
        if not binary:
            with open(malicious_dir + "/" + labels_csv, "rb") as f:
                self.labels_dict = {row[0]: row[1] for row in csv.reader(f, delimiter=' ')}
        else:
            self.labels_dict = None
        self.malicious_dir = malicious_dir
        self.benign_dir = benign_dir
        self.benign_tag = 0
        self.tags = range(2 if binary else 10)
        self.max_size = max_input_size

        l = [str(i) for i in range(10)] + ["A", "B", "C", "D", "a", "b", "c", "d", "E", "F", "e", "f"]
        self.string_bytes = [x+y for x, y in zip(l, l)]

        self.files = get_files_from_malware_data_dir(malicious_dir, self.labels_dict)
        self.files += [(x, self.benign_tag) for x in os.listdir(self.benign_dir) if x.endswith(".bytes")]

        if only_use is not None:
            self.files = filter(lambda (_, c): c in only_use, self.files)
            mymap = {i: j+1 for i, j in zip(only_use, range(len(only_use)))}
            mymap[self.benign_tag] = self.benign_tag
            self.tags = range(len(only_use) + 1)
            self.files = map(lambda (f,c): (f, mymap[c]), self.files)

        random.shuffle(self.files)

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        f, tag = self.files[idx]
        d = self.malicious_dir if tag != self.benign_tag else self.benign_dir
        bytes = [[int(s, 16) for s in line.split()[1:] if s in self.string_bytes]
                 for line in file(d + "/" + f) if line !="\n"]
        bytes = list(chain.from_iterable(bytes))
        if len(bytes) > self.max_size:  # cut if bigger than max todo decide if to keep
            bytes = bytes[:self.max_size]
        else:
            bytes += [PAD_IDX] * (self.max_size - len(bytes))

        return tensor(bytes), tensor(tag)

    def get_test_indices(self, test_precent):
        files = self.files
        test_size = int(len(self.files) * test_precent)
        examples_by_class = int(float(test_size) /len(self.tags))
        indices = []

        counters = {i: 0 for i in self.tags}
        for i, (f, tag) in enumerate(files):
            if counters[tag] < examples_by_class:
                indices.append(i)
                counters[tag] += 1
        return indices


def get_files_from_malware_data_dir(malware_data_dir, labels_dict=None):
    files = []
    for d in os.listdir(malware_data_dir):
        if "." in d: continue
        curr_dir = malware_data_dir + "/" + d
        if labels_dict is None:  # binary classification
            curr_files = map(lambda x: (d+"/"+x, 1), filter(lambda x: x.endswith(".bytes"),os.listdir(curr_dir)))
        else:
            curr_files = map(lambda x: (d + "/" + x, int(labels_dict[x])),
                             filter(lambda x: x.endswith(".bytes"), os.listdir(curr_dir)))
        files.extend(curr_files)
    return files
