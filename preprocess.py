# This takes sentences generated by generate_sentences.py and converts it to raw text
# While also keeping track of sentence lengths and creating a dictionary of words 
import os 
import nltk 
import json 
import random

dictionary = {}
mapped_dictionary = {}
max_sentence_length = 0 
most_frequent_word = ""
most_frequent_word_freq = 0
total_words = 0 

def randomize_words_in_sentence(filename):
    data = []
    open("data/txt/incoherent_sentences_randomized_words.txt", 'w') # Clear contents of file 
    randomized_file = open("data/txt/incoherent_sentences_randomized_words.txt", 'a+')

    for line in open("data/json/" + filename, 'r'):
        data.append(json.loads(line))

    for line in data:
        sentence = line['Arg1Raw'] + " " + line['ConnectiveRaw'] + " " + line['Arg2Raw'] + "\n"
        word_sentence = nltk.word_tokenize(sentence.lower())
        random.shuffle(word_sentence)
        for word in word_sentence:
            randomized_file.write(word.encode('ascii', 'ignore') + " ")
        randomized_file.write('\n')


# Stats output file
open("data/corpus_stats.txt", 'w') # Clear contents of file 
stats_file = open("data/corpus_stats.txt", 'a+')

# Build dictionary and convert sentences to raw text 
print("Converting to raw text")
for filename in os.listdir(os.getcwd()+ "/data/json"):
    # Variables for file-specific data 
    file_max_sentence_length = 0
    file_num_sentences = 0
    file_dict = {}

    # Import data as a JSON object 
    data = []
    for line in open("data/json/" + filename, 'r'):
        data.append(json.loads(line))
        file_num_sentences += 1 

    output_file = "data/txt/" + filename[:-5] + ".txt"
    open(output_file, 'w') # Clear contents of file 
    out = open(output_file, 'a+')

    for line in data:
        # Convert to raw text
        sentence = line['Arg1Raw'] + " " + line['ConnectiveRaw'] + " " + line['Arg2Raw'] + "\n"
        out.write(sentence.encode('ascii', 'ignore')) 

        # Tokenize sentence and build dictionary + corpus stats 
        word_sentence = nltk.word_tokenize(sentence.lower())

        # Find maximum sentence length
        if len(word_sentence) > max_sentence_length:
            max_sentence_length = len(word_sentence)
        if len(word_sentence) > file_max_sentence_length:
            file_max_sentence_length = len(word_sentence)

        for word in word_sentence:
            try: 
                word = word.decode('utf8').encode('ascii', errors='ignore')
            except UnicodeEncodeError:
                stripped = (c for c in word if 0 < ord(c) < 127)
                word = ''.join(stripped)
            total_words += 1
            if word not in dictionary:
                dictionary[word] = 1
            else:
                dictionary[word] += 1 
                if dictionary[word] > most_frequent_word_freq:
                    most_frequent_word = word
                    most_frequent_word_freq = dictionary[word]

            if word not in file_dict:
                file_dict[word] = True 

    if filename == 'incoherent_sentences_arg2_diff_sense.json':
        randomize_words_in_sentence(filename)

    # Output File Stats 
    stats_file.write(filename + " stats:\n")
    stats_file.write("# words: " + str(len(file_dict.keys())) + "\n")
    stats_file.write("# sentences: " + str(file_num_sentences) + "\n")
    stats_file.write("Max sentence length: " + str(file_max_sentence_length) + "\n")

# Output dictionary and create mapping of terms to integers
index = 1
open("data/dictionary.txt", 'w') # Clear contents of file 
dict_file = open("data/dictionary.txt", 'a+')
# Used for padding sentences to max_sentence_length
mapped_dictionary["<pad>"] = 0
dict_file.write("0 <pad> -1\n")

# Print all terms from dictionary and map them to integers in mapped_dictionary
for key in sorted(dictionary.keys()):
    mapped_dictionary[key.lower()] = index
    entry = str(index) + " " + key + " " + str(dictionary[key]) + "\n"
    dict_file.write(entry)
    index += 1 


# Output corpus stats
stats_file.write("Total words: " + str(total_words) + "\n")
stats_file.write("Most frequent word: " + str(most_frequent_word) + "\n")
stats_file.write("Most frequent word frequency: " + str(most_frequent_word_freq) + "\n")
stats_file.write("Unique terms in dictionary: " + str(len(dictionary.keys())) + "\n")
stats_file.write("Max sentence length: " + str(max_sentence_length) + "\n")


print("Converting to integer")
# Not really needed because Tensorflow does it. 
# Pad all sentences to max_sentence_length and covert sentences to integer representation
for filename in os.listdir(os.getcwd()+ "/data/txt"):
    # Import data as a JSON object 
    data = []
    for line in open("data/txt/" + filename, 'r'):
        tokenized_line = nltk.word_tokenize(line.lower())

        # Pad sentences
        while (len(tokenized_line) < max_sentence_length):
            tokenized_line.append("<pad>")
        data.append(tokenized_line)

    # Output padded sentences
    output_file = "data/padded/" + filename[:-4] + ".txt"
    open(output_file, 'w') # Clear contents of file 
    out = open(output_file, 'a+')

    for sentence in data:
        for word in sentence:
            out.write(word.lower() + " ")
        out.write("\n") 

    # Output integer sentences
    output_file = "data/integers/" + filename[:-4] + ".txt"
    open(output_file, 'w') # Clear contents of file 
    out = open(output_file, 'a+')    
    for sentence in data:
        for word in sentence:
            out.write(str(mapped_dictionary[word.lower()]) + " ")
        out.write("\n")