# improvednfe_research
Improvement of Malware Classification Using NFE
tensorflow_gpu==1.15.4
numpy==1.13.3
scikit_learn==0.19.1
tensorflow==1.15.4
The Malware samples Used are in the data directory.

Run the `setup.sh` to ensure that the pre-requisite libraries are installed in the environment.
```bash
$ sudo chmod +x setup.sh
$ ./setup.sh
```

Run the `main.py` with the following parameters.
```bash
usage: main.py [-h] -m MODEL -d DATASET -n NUM_EPOCHS -c PENALTY_PARAMETER -k
               CHECKPOINT_PATH -l LOG_PATH -r RESULT_PATH

Deep Learning Using Support Vector Machine for Malware Classification

optional arguments:
  -h, --help            show this help message and exit

Arguments:
  -m MODEL, --model MODEL
                        [1] CNN-SVM, [2] GRU-SVM, [3] MLP-SVM
  -d DATASET, --dataset DATASET
                        the dataset to be used
  -n NUM_EPOCHS, --num_epochs NUM_EPOCHS
                        number of epochs
  -c PENALTY_PARAMETER, --penalty_parameter PENALTY_PARAMETER
                        the SVM C penalty parameter
  -k CHECKPOINT_PATH, --checkpoint_path CHECKPOINT_PATH
                        path where to save the trained model
  -l LOG_PATH, --log_path LOG_PATH
                        path where to save the TensorBoard logs
  -r RESULT_PATH, --result_path RESULT_PATH
                        path where to save actual and predicted labels array

To run a trained model, run the `classifier.py` with the following parameters.
```bash
usage: classifier.py [-h] -m MODEL -t MODEL_PATH -d DATASET



optional arguments:
  -h, --help            show this help message and exit

Arguments:
  -m MODEL, --model MODEL
                        [1] CNN-SVM, [2] GRU-SVM, [3] MLP-SVM
  -t MODEL_PATH, --model_path MODEL_PATH
                        path where to save the trained model
  -d DATASET, --dataset DATASET
                        the dataset to be classified
```
