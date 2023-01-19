# coding=utf-8
import os
from config import getConfig
from model.util import read_data
import jieba
from zhon.hanzi import punctuation
import re
import sys
import time
import torch
import model.seq2seqModel as seq2seqModel
from torch import optim


def preprocess():
    global MAX_TRAIN_DATA_SIZE
    if not os.path.exists(conv_path):
        exit()


    convs = []  
    with open(conv_path,encoding='utf-8') as f:
        one_conv = []       
        for line in f:
            line = line.strip('\n').replace('?', '')
            line=re.sub(r"[%s]+" %punctuation, "",line)
            if line == '':
                continue
            if line[0] == gConfig['e']:
                if one_conv:
                    convs.append(one_conv)
                one_conv = []
            elif line[0] == gConfig['m']:
                one_conv.append(line.split(' ')[1])
                
    seq = []        

    for conv in convs:
        if len(conv) == 1:
            continue
        if len(conv) % 2 != 0:  
            conv = conv[:-1]
        for i in range(len(conv)):
            if i % 2 == 0:
                conv[i]=" ".join(jieba.cut(conv[i]))
                conv[i+1]=" ".join(jieba.cut(conv[i+1]))
                seq.append(conv[i]+'\t'+conv[i+1])

    seq_train = open(gConfig['seq_data'],'w') 

    for i in range(len(seq)):
        seq_train.write(seq[i]+'\n')
    seq_train.close()
    MAX_TRAIN_DATA_SIZE = len(seq)
    print(MAX_TRAIN_DATA_SIZE, 'processed')


def train():
    print("Preparing data in %s" % gConfig['train_data'])
    steps_per_epoch = len(input_tensor) // gConfig['batch_size']
    print(steps_per_epoch)
    checkpoint_dir = gConfig['weight_dir']

    checkpoint_prefix = os.path.join(checkpoint_dir, "weight.pt")
    start_time = time.time()
    encoder = seq2seqModel.Encoder(input_lang.n_words, hidden_size).to(device)
    decoder = seq2seqModel.AttentionDencoder(hidden_size, target_lang.n_words, dropout_p=0.1).to(device)
    if os.path.exists(checkpoint_prefix):
        checkpoint = torch.load(checkpoint_prefix)
        encoder.load_state_dict(checkpoint['modelA_state_dict'])
        decoder.load_state_dict(checkpoint['modelB_state_dict'])
    max_data=MAX_TRAIN_DATA_SIZE
    total_loss = 0
    batch_loss=1
    while batch_loss>gConfig['min_loss']:
        start_time_epoch = time.time()
        for i in range(1,(max_data//BATCH_SIZE)):
            inp=input_tensor[(i-1)*BATCH_SIZE:i*BATCH_SIZE]
            targ=target_tensor[(i-1)*BATCH_SIZE:i*BATCH_SIZE]
            batch_loss = seq2seqModel.train_step(inp, targ,encoder,decoder,optim.SGD(encoder.parameters(),lr=0.001),optim.SGD(decoder.parameters(),lr=0.01))
            total_loss += batch_loss
            print('Total step:{} loss {:.4f}'.format(i,batch_loss ))
        step_time_epoch = (time.time() - start_time_epoch) / steps_per_epoch
        step_loss = total_loss / steps_per_epoch
        current_steps = +steps_per_epoch
        step_time_total = (time.time() - start_time) / current_steps
        print('current_steps: {} step_time_total: {}  step_time_epoch: {} batch_loss {:.4f}'.format(current_steps, step_time_total, step_time_epoch,
                                                                      batch_loss))
        torch.save({'modelA_state_dict': encoder.state_dict(),
                     'modelB_state_dict': decoder.state_dict()},checkpoint_prefix)
        sys.stdout.flush()


gConfig = {}
gConfig= getConfig.get_config()
conv_path = gConfig['resource_data']

MAX_TRAIN_DATA_SIZE = 0
# Train
getConfig.remove_config("train_output","max_train_data_size")
preprocess()
getConfig.write_config("train_output","max_train_data_size",str(MAX_TRAIN_DATA_SIZE))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
units=gConfig['layer_size']
BATCH_SIZE=gConfig['batch_size']
MAX_LENGTH=gConfig['max_length']
EOS_token = 1
input_tensor,input_lang,target_tensor,target_lang= read_data(gConfig['seq_data'], MAX_TRAIN_DATA_SIZE,EOS_token,device)
hidden_size = 256
if __name__ == '__main__':
    if len(sys.argv) - 1:
        gConfig = getConfig.get_config(sys.argv[1])
    else:
        gConfig = getConfig.get_config()

    train()
    