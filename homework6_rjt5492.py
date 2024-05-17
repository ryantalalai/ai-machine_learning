############################################################
# CMPSC 442: Hidden Markov Models
############################################################

student_name = "Ryan Joseph Talalai"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
# No imports used

############################################################
# Section 1: Hidden Markov Models
############################################################

def load_corpus(path):
    corpus = []

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            pairs = [tuple(word.split('=')) for word in line.split()]
            corpus.append(pairs)

    return corpus


class Tagger(object):

    def __init__(self, sentences):
        self.tags = ["NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "NUM", "CONJ", "PRT", ".", "X"]
        self.tag_dict = {tag: index for index, tag in enumerate(self.tags)}
        self.vocab = {}
        self.transition_prob = [[0 for _ in self.tags] for _ in self.tags]
        self.tags_init_prob = {tag: 0 for tag in self.tags}
        self.tags_total_count = {tag: 0 for tag in self.tags}

        for sen in sentences:
            for i, (word, tag) in enumerate(sen):
                if word not in self.vocab:
                    self.vocab[word] = [0] * len(self.tags)
                self.vocab[word][self.tag_dict[tag]] += 1
                if i < len(sen) - 1:
                    next_tag = sen[i + 1][1]
                    self.transition_prob[self.tag_dict[tag]][self.tag_dict[next_tag]] += 1
                if i == 0:
                    self.tags_init_prob[tag] += 1
                self.tags_total_count[tag] += 1

        total_sentences = len(sentences)

        for tag in self.tags:
            self.tags_init_prob[tag] = (self.tags_init_prob[tag] + 1) / (total_sentences + len(self.tags))
            self.transition_prob[self.tag_dict[tag]] = [(count + 1) / (self.tags_total_count[tag] + len(self.tags)) for count in self.transition_prob[self.tag_dict[tag]]]

        self.vocab["<UNK>"] = [1 / len(self.vocab) for _ in self.tags]

        for word, counts in self.vocab.items():
            self.vocab[word] = [(count + 1) / (self.tags_total_count[tag] + len(self.vocab)) for tag, count in zip(self.tags, counts)]


    def most_probable_tags(self, tokens):
        result = []

        for token in tokens:
            word_probs = self.vocab.get(token, self.vocab["<UNK>"])
            _, max_tag = max(zip(word_probs, self.tags))
            result.append(max_tag)

        return result
    

    def viterbi_tags(self, tokens):
        dp = [[0] * len(self.tags) for _ in tokens]
        backpointer = [[None] * len(self.tags) for _ in tokens]
        first_token_probs = self.vocab.get(tokens[0], self.vocab["<UNK>"])

        for tag_index, tag in enumerate(self.tags):
            dp[0][tag_index] = self.tags_init_prob[tag] * first_token_probs[tag_index]

        for i in range(1, len(tokens)):
            current_token_probs = self.vocab.get(tokens[i], self.vocab["<UNK>"])
            for j in range(len(self.tags)):
                max_prob, best_tag = max((dp[i-1][k] * self.transition_prob[k][j], k) for k in range(len(self.tags)))
                dp[i][j] = max_prob * current_token_probs[j]
                backpointer[i][j] = best_tag

        last_token_best_tag = max(range(len(self.tags)), key=lambda j: dp[-1][j])
        best_sequence = [self.tags[last_token_best_tag]]

        for i in range(len(tokens) - 1, 0, -1):
            last_token_best_tag = backpointer[i][last_token_best_tag]
            best_sequence.append(self.tags[last_token_best_tag])

        best_sequence.reverse()

        return best_sequence



### Test Code ###

'''

# 1
c = load_corpus("brown_corpus.txt")
print(c[1402])
c = load_corpus("brown_corpus.txt")
print(c[1799])

# 3
c = load_corpus("brown_corpus.txt")
t = Tagger(c)
print(t.most_probable_tags(["The", "man", "walks", "."]))
c = load_corpus("brown_corpus.txt")
t = Tagger(c)
print(t.most_probable_tags(["The", "blue", "bird", "sings"]))


# 4
c = load_corpus("brown_corpus.txt")
t = Tagger(c)
s = "I am waiting to reply".split()
print(t.most_probable_tags(s))
print(t.viterbi_tags(s))

c = load_corpus("brown_corpus.txt")
t = Tagger(c)
s = "I saw the play".split()
print(t.most_probable_tags(s))
print(t.viterbi_tags(s))

'''
