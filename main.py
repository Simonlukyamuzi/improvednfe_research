from sys import argv
large_dataset = "--small" not in argv
if large_dataset:
    malware_data_dir = argv[1]
    labels_dir = "csv" 
    benign_dir = malware_data_dir + "/Benign"

import torch as tr
from torch import nn as nn
from torch.nn import functional as F
from torch import optim as optim
from torch.utils.data import DataLoader
from time import time
from torch.autograd import Variable
if large_dataset:
    from large_dataset_utils import ExecDataset, PAD_IDX
else:
    from small_dataset_utils import ExecDataset, PAD_IDX
from torch.utils.data.sampler import SubsetRandomSampler


class GatedConvolution(nn.Module):
    def __init__(self, use_batch_norm=False, use_dropout=False, dropout_prob=0.1):
        super(GatedConvolution, self).__init__()
        self.conv = nn.Conv1d(4, 128, 500, stride=500)
        self.convg = nn.Conv1d(4, 128, 500, stride=500)
        self.__use_bn = use_batch_norm
        self.__use_do = use_dropout
        if use_batch_norm:
            self.bn_c = nn.BatchNorm1d(128)
            self.bn_g = nn.BatchNorm1d(128)
        if use_dropout:
            self.dropout = nn.Dropout2d(dropout_prob)

    def forward(self, x):
        """

        :param x:
        :type x: tr.Tensor
        :return:
        """
        x.transpose_(-1, -2)
        c = self.conv(x.narrow(-2, 0, 4))
        g = self.convg(x.narrow(-2, 4, 4))

        if self.__use_bn:

            c = self.bn_c(c)
            g = self.bn_g(g)

        g = F.sigmoid(g)
        x = F.relu(g * c)

        if self.__use_do:
            x = self.dropout(x)

        return F.max_pool1d(x, x.size()[2:]).view(-1, 128)


def accuracy_on(net, dev_loader, loss_fn, device):
    total_loss = good = 0.0
    net.eval()
    for x, y in dev_loader:
        if device is not None:
            x, y = x.to(device), y.to(device)
        out = net(x)
        loss = loss_fn(out, y)
        total_loss += loss.item()
        good += (tr.argmax(out, 1) == y).sum().item()
    return total_loss / len(dev_loader.sampler), good / len(dev_loader.sampler) * 100.0


def train_on(net, optimizer, loss_fn, train_loader, dev_loader, epochs=5, device=None):
    for i in xrange(epochs):
        print "#" * 10 + " epoch #{} ".format(i+1) + "#" * 10
        start = time()
        total = good = total_loss = 0.0
        net.train()
        for j, (x, y) in enumerate(train_loader):
            optimizer.zero_grad()
            total += y.shape[0]
            if device is not None:
                x, y = x.to(device), y.to(device)
            out = net(x)
            loss = loss_fn(out, y)
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
            good += (tr.argmax(out, 1) == y).sum().item()
            if j % 5 == 4:
                print "gone over {} batches / {} with {}% train accuracy and {} loss in {}s".format(
                    j+1, len(train_loader), 100.0 * good / total, total_loss / total, time() - start)
        dev_loss, dev_acc = accuracy_on(net, dev_loader, loss_fn, device)
        print "=" * 25
        print "epoch, epoch time, train avg. loss, train accuracy, dev avg. loss, dev accuracy"
        print "{:^5}, {:^10.5f}, {:^15f}, {:^14f}%, {:^13f}, {:^12f}%".format(
            i+1, time() - start, total_loss / len(train_loader.sampler), good / len(train_loader.sampler) * 100.0,
            dev_loss, dev_acc)
        print ""


def main():
    batch = 50
    workers = 6 # 10
    num_classes = 2 if "--b" in argv else 10
    epochs = 6
    lr = 0.001
    use_bn = False
    use_dropout = True
    dropout = 0.3


    if not large_dataset:
        data_set = ExecDataset("trainLabels.csv", "files/train50", "files/benign50", binary=(num_classes==2))
    else:
        data_set = ExecDataset(labels_dir + "/allLabels.csv", malware_data_dir, benign_dir, binary=(num_classes==2), only_use=[9, 5, 2, 6])

    test_indices = data_set.get_test_indices(0.2)
    train_indices = [i for i in range(len(data_set)) if i not in test_indices]
    test_sampler = SubsetRandomSampler(test_indices)
    train_sampler = SubsetRandomSampler(train_indices)

    test_loader = DataLoader(data_set, batch_size=batch, sampler=test_sampler, num_workers=workers)
    train_loader = DataLoader(data_set, batch_size=batch, sampler=train_sampler, num_workers=workers)

    modules = [nn.Embedding(257, 8, padding_idx=PAD_IDX),
               GatedConvolution(use_batch_norm=use_bn, use_dropout=use_dropout),
               nn.Linear(128, 128), nn.ReLU(),
               # nn.Linear(128, 128), nn.ReLU(),
               nn.Linear(128, num_classes)]
    if use_bn:
        modules.insert(3, nn.BatchNorm1d(128))
    if use_dropout:
        if use_bn:
            modules.insert(5, nn.Dropout(dropout))
        else:
            modules.insert(4, nn.Dropout(dropout))

    net = nn.Sequential(*modules)
    device = None
    if tr.cuda.is_available() and tr.cuda.device_count() > 0:
        device = tr.device("cuda:0")
        net = nn.DataParallel(net)
        net.to(device)

    loss_fn = nn.CrossEntropyLoss(size_average=False)

    optimizer = optim.Adam(net.parameters(), lr=lr)

    print "&" * 50
    print "Train examples: {}  |  Validation examples: {}".format(len(train_sampler), len(test_sampler))
    print "Training for {} epochs".format(epochs)
    print "Training with Adam using {} learning rate".format(lr)
    print "Batch Normalization set to {}".format(use_bn)
    print "Dropout set to {}{}".format(use_dropout, " with {} probability".format(dropout) if use_dropout else "")
    print "&" * 50 + "\n"


    train_on(net, optimizer, loss_fn, train_loader, test_loader, epochs=epochs, device=device)


if __name__ == '__main__':
    main()