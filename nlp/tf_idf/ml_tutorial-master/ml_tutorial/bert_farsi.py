# AUTOGENERATED! DO NOT EDIT! File to edit: 10_bert_farsi_sentiment.ipynb (unless otherwise specified).

__all__ = ['load_data', 'file_name', 'df', 'create_small_dataset', 'remove_emoji', 'convert_data_into_input_example',
           'my_solution', 'example_to_features', 'plot_history', 'example_to_features_predict', 'get_prediction']

# Cell
import csv
import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow_datasets as tfds

from sklearn.model_selection import train_test_split
from transformers import BertTokenizer, BasicTokenizer
from transformers import TFBertModel, TFBertPreTrainedModel, TFBertForSequenceClassification
from transformers import glue_convert_examples_to_features, InputExample

# Cell
def load_data(file_name):
    """
        Read the CSV and creates a Panda dataframe fro the file content.
    """
    f = open(file_name, 'r')
    data = pd.read_csv(f, delimiter=',', encoding='utf-8')
    return data


file_name = os.path.join('data','taghche.csv')
df = load_data(file_name)
df.head()

# Cell
def create_small_dataset(df_pos, df_neg, n_samples):
    """ Create a custom dataset of size `n_samples` from positive `df_pos` and negative `df-neg`
        examples.
    """
    duplicates = set()
    counter = 0
    data = {}
    data['comment'] = []
    data['polarity'] = []
    while counter < n_samples:
        index = np.random.randint(0, len(df_pos))
        if index in duplicates:
            continue
        row = df_pos.iloc[index]
        comment = remove_emoji(row['comment'])
        label = row['label']
        data['comment'].append(comment)
        data['polarity'].append(label)
        duplicates.add(index)
        counter += 1

    duplicates.clear()
    counter = 0
    while counter < n_samples:
        index = np.random.randint(0, len(df_neg))
        if index in duplicates:
            continue
        row = df_neg.iloc[index]
        comment = remove_emoji(row['comment'])
        label = row['label']
        data['comment'].append(comment)
        data['polarity'].append(label)
        duplicates.add(index)
        counter += 1
    return pd.DataFrame.from_dict(data)

def remove_emoji(text):
    """ Remove a number of emojis from text."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    text = re.sub(emoji_pattern, ' ', text).replace('.','')
    return re.sub(r'[a-z]+[A-Z]+', '', text, re.I)


# Cell
def convert_data_into_input_example(data):
    """ Covert the list of examples into a list of `InputExample` objects that is suitable
        for BERT model."""
    input_examples = []
    for i in range(len(data)):
        example = InputExample(
            guid= None,
            text_a= data.iloc[i]['comment'],
            text_b= None,
            label= data.iloc[i]['polarity']
        )
        input_examples.append(example)
    return input_examples

# Cell
def my_solution(bdset):
    """ Create a list of input tensors required to be in the first argument of the
        model call function for training. e.g. `model([input_ids, attention_mask, token_type_ids])`.
    """
    input_ids, attention_mask, token_type_ids, label = [], [], [], []
    for in_ex in bdset:
        input_ids.append(in_ex.input_ids)
        attention_mask.append(in_ex.attention_mask)
        token_type_ids.append(in_ex.token_type_ids)
        label.append(in_ex.label)

    input_ids = np.vstack(input_ids)
    attention_mask = np.vstack(attention_mask)
    token_type_ids = np.vstack(token_type_ids)
    label = np.vstack(label)
    return ([input_ids, attention_mask, token_type_ids], label)

def example_to_features(input_ids, attention_masks, token_type_ids, y):
    """ Convert a training example into the Bert compatible format."""
    return {"input_ids": input_ids,
            "attention_mask": attention_masks,
            "token_type_ids": token_type_ids},y

# Cell
def plot_history(history):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    x = range(1, len(acc) + 1)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(x, acc, 'b', label='Training acc')
    plt.plot(x, val_acc, 'r', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(x, loss, 'b', label='Training loss')
    plt.plot(x, val_loss, 'r', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()

# Cell
def example_to_features_predict(input_ids, attention_masks, token_type_ids):
    """
        Convert the test examples into Bert compatible format.
    """
    return {"input_ids": input_ids,
            "attention_mask": attention_masks,
            "token_type_ids": token_type_ids}


def get_prediction(in_sentences):
    """
        Prepare the test comments and return the predictions.
    """
    labels = ["0", "1"]
    input_examples = [InputExample(guid="", text_a = x, text_b = None, label = '0') for x in in_sentences] # here, "" is just a dummy label
    predict_input_fn = glue_convert_examples_to_features(examples=input_examples, tokenizer=tokenizer, max_length=MAX_SEQ_LENGTH, task='mrpc', label_list=label_list)
    x_test_input, y_test_input = my_solution(predict_input_fn)
    test_ds   = tf.data.Dataset.from_tensor_slices((x_test_input[0], x_test_input[1], x_test_input[2])).map(example_to_features_predict).batch(32)

    predictions = model.predict(test_ds)
    #   print('predictions:', predictions[0].shape)
    predictions_classes = np.argmax(predictions[0], axis = 1)
    return [(sentence, prediction) for sentence, prediction in zip(in_sentences, predictions_classes)]