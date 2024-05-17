############################################################
# CMPSC442: Classification
############################################################

student_name = "Ryan Joseph Talalai"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
from email import message_from_file, iterators
from math import log, exp
from collections import Counter
import os

############################################################
# Section 1: Spam Filter
############################################################

def load_tokens(email_path):
    with open(email_path, "r", encoding="utf-8") as file:
        message = message_from_file(file)
        tokens = [token for line in iterators.body_line_iterator(message) for token in line.split()]

    return tokens

def log_probs(email_paths, smoothing):
    all_tokens = [token for email in email_paths for token in load_tokens(email)]
    total_tokens = len(all_tokens)
    token_counts = Counter(all_tokens)
    vocab_size = len(token_counts) + 1

    log_probs_dict = {token: log((count + smoothing) / (total_tokens + smoothing * vocab_size))
                      for token, count in token_counts.items()}
    
    log_probs_dict["<UNK>"] = log(smoothing / (total_tokens + smoothing * vocab_size))
    
    return log_probs_dict

class SpamFilter:
    def __init__(self, spam_dir, ham_dir, smoothing):
        spam_files = [os.path.join(spam_dir, file) for file in os.listdir(spam_dir)]
        ham_files = [os.path.join(ham_dir, file) for file in os.listdir(ham_dir)]
        spam_file_count = len(spam_files)
        ham_file_count = len(ham_files)
        self.p_spam = log_probs(spam_files, smoothing)
        self.p_ham = log_probs(ham_files, smoothing)
        total_files = spam_file_count + ham_file_count
        self.log_prob_spam = log(spam_file_count / total_files)
        self.log_prob_ham = log(ham_file_count / total_files)

    def is_spam(self, email_path):
        token_count = Counter(load_tokens(email_path))
        spam_score = sum((self.p_spam.get(token, self.p_spam["<UNK>"]) * count) for token, count in token_count.items())
        ham_score = sum((self.p_ham.get(token, self.p_ham["<UNK>"]) * count) for token, count in token_count.items())

        return (self.log_prob_spam + spam_score) > (self.log_prob_ham + ham_score)

    def most_indicative_spam(self, n):
        indicative_scores = {
            token: self.p_spam[token] - log(exp(self.p_spam[token]) + exp(self.p_ham.get(token, self.p_ham["<UNK>"])))
            for token in self.p_spam if token in self.p_ham and token != "<UNK>"
        }

        return sorted(indicative_scores, key=indicative_scores.get, reverse=True)[:n]

    def most_indicative_ham(self, n):
        indicative_scores = {
            token: self.p_ham[token] - log(exp(self.p_spam.get(token, self.p_spam["<UNK>"])) + exp(self.p_ham[token]))
            for token in self.p_ham if token in self.p_spam and token != "<UNK>"
        }

        return sorted(indicative_scores, key=indicative_scores.get, reverse=True)[:n]



### TEST CASES ###
    
'''
# 1
ham_dir="homework5_data/train/ham/"
print(load_tokens(ham_dir+"ham1")[200:204])
print(load_tokens(ham_dir+"ham2")[110:114])
spam_dir="homework5_data/train/spam/"
print(load_tokens(spam_dir+"spam1")[1:5])
print(load_tokens(spam_dir+"spam2")[:4])

# 2
paths=["homework5_data/train/ham/ham%d"%i for i in range(1,11)]
p=log_probs(paths,1e-5)
print(p["the"])
print(p["line"])

paths=["homework5_data/train/spam/spam%d"%i for i in range(1,11)]
p=log_probs(paths,1e-5)
print(p["Credit"])
print(p["<UNK>"])

# 4
sf=SpamFilter("homework5_data/train/spam","homework5_data/train/ham",1e-5)
print(sf.is_spam("homework5_data/train/spam/spam1"))
print(sf.is_spam("homework5_data/train/spam/spam2" ))
sf = SpamFilter("homework5_data/train/spam", "homework5_data/train/ham", 1e-5)
print(sf.is_spam("homework5_data/train/ham/ham1"))
print(sf.is_spam("homework5_data/train/ham/ham2"))

# 5
sf=SpamFilter("homework5_data/train/spam", "homework5_data/train/ham",1e-5)
print(sf.most_indicative_spam(5))
sf=SpamFilter("homework5_data/train/spam", "homework5_data/train/ham",1e-5)
print(sf.most_indicative_ham(5))

'''
