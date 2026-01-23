import hashlib
import os

def file_as_bytes(file):
    with file:
        return file.read()

def hash_file(fpath):
    return hashlib.md5(file_as_bytes(open(fpath, 'rb'))).hexdigest()

for fname in os.listdir('D:/Kaggle & DataSets/DataSet/GAN/GANGogh/images/VALID/'):
    name, ext = os.path.splitext(fname)
    hash = hash_file(fname)
    dst = hash + ext
    print(fname + " --> " + dst)
    os.rename(fname, dst)