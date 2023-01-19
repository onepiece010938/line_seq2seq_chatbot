import io
import torch
from torch import optim


def preprocess_sentence(w):
    w ='start '+ w + ' end'
    #print(w)
    return w

def create_dataset(path, num_examples):
    lines = io.open(path, encoding='UTF-8').read().strip().split('\n')
    pairs = [[preprocess_sentence(w)for w in l.split('\t')] for l in lines[:num_examples]]
    input_lang=Lang("ans")
    output_lang=Lang("ask")
    pairs = [list(reversed(p)) for p in pairs]
    for pair in pairs:
        input_lang.addSentence(pair[0])
        output_lang.addSentence(pair[1])

    return input_lang,output_lang,pairs

def max_length(tensor):
    return max(len(t) for t in tensor)
class Lang:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "start", 1: "end"}
        self.n_words = 2  # Count start and end

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1


def indexesFromSentence(lang, sentence):
    return [lang.word2index[word] for word in sentence.split(' ')]

def tensorFromSentence(lang, sentence,EOS_token,device):

    indexes = indexesFromSentence(lang, sentence)
    indexes.append(EOS_token)

    return torch.tensor(indexes, dtype=torch.long, device=device).view(-1, 1)


def read_data(path,num_examples,EOS_token,device):
    input_tensors=[]
    target_tensors=[]
    input_lang,target_lang,pairs=create_dataset(path,num_examples)
    for i in range(0,num_examples-1):
        input_tensor = tensorFromSentence(input_lang, pairs[i][0],EOS_token,device)
        target_tensor = tensorFromSentence(target_lang, pairs[i][1],EOS_token,device)
        input_tensors.append(input_tensor)
        target_tensors.append(target_tensor)
    return input_tensors,input_lang,target_tensors,target_lang