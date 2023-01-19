import os
from config import getConfig
from model.util import preprocess_sentence,Lang,tensorFromSentence,create_dataset
from zhon.hanzi import punctuation
import torch
import model.seq2seqModel as seq2seqModel

gConfig = {}
gConfig= getConfig.get_config()
MAX_LENGTH=gConfig['max_length']

input_lang,target_lang,_= create_dataset(gConfig['seq_data'], gConfig['max_train_data_size'])
hidden_size = 256
EOS_token=1
SOS_token=0
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def predict(sentence):
    max_length_tar=MAX_LENGTH
    encoder = seq2seqModel.Encoder(input_lang.n_words, hidden_size).to(device)
    decoder = seq2seqModel.AttentionDencoder(hidden_size, target_lang.n_words, dropout_p=0.1).to(device)
    checkpoint_dir = gConfig['weight_dir']
    checkpoint_prefix = os.path.join(checkpoint_dir, "weight.pt")
    checkpoint=torch.load(checkpoint_prefix)
    encoder.load_state_dict(checkpoint['modelA_state_dict'])
    decoder.load_state_dict(checkpoint['modelB_state_dict'])

    sentence = preprocess_sentence(sentence)
    input_tensor = tensorFromSentence(input_lang,sentence,EOS_token,device)

    input_length = input_tensor.size()[0]
    result = ''
    max_length=MAX_LENGTH
    encoder_hidden = encoder.initHidden()
    encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)
    for ei in range(input_length):
        encoder_output, encoder_hidden = encoder(input_tensor[ei],
                                                 encoder_hidden)
        encoder_outputs[ei] += encoder_output[0, 0]

    dec_input = torch.tensor([[SOS_token]], device=device)  # SOS

    dec_hidden = encoder_hidden
    #decoder_attentions = torch.zeros(max_length, max_length)
    for t in range(max_length_tar):
        predictions, dec_hidden, decoder_attentions = decoder(dec_input, dec_hidden, encoder_outputs)
        predicted_id,topi =predictions.data.topk(1)

        if topi.item() == EOS_token:
            result+='<EOS>'
            break
        else:
          result+=target_lang.index2word[topi.item()]+' '
        dec_input = topi.squeeze().detach()
    return result
