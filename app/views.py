from flask import render_template, flash, jsonify, redirect, session, url_for, request, g
from app import app
from collections import Counter
from flask.ext.wtf import Form
from wtforms import TextAreaField, StringField
from app.storydata import default_story
import nltk
from nltk import FreqDist
import string

# Using a flask form to auto-populate the text field containing our default story, Alice in Wonderland.
class StoryForm(Form):
    story = TextAreaField('story', default=default_story)

# The frequency count of words needs to be scaled to something that will fit on the screen when displaying
# the value as a horizontal bar chart.
def scale_range(low=1, high=100, new_low=150, new_high=800, value=1):
    scale = float(float((high-low))/float((new_high-new_low)))
    if scale == 0:
      return new_low
    result = new_low+(value-low)/float(scale)
    return int(result)

# Python flask view handlers
@app.route('/')
@app.route('/index')
def index():
    form = StoryForm()
    return render_template('index.html',
                           title='Enphase Homework',
                           form=form)

# Does our frequency calculation and returns the data as json, to then be displayed as a horizontal bar char.
@app.route('/update', methods=['POST'])
def update():

    max_top = int(request.form['maxtop'])
    nouns = request.form['nouns']

    if max_top <= 1:
        max_top = 1;
    # Little ugliness to coerce the string data into ints.  Python Flask forms could be used to control the data type,
    # But I want UI spinners and WTF flask doesn't provide those.
    story = request.form['story']
    try:
        minword = int(request.form['minword'])
    except:
        minword = 1
    try:
        minfreq = int(request.form['minfreq'])
    except:
        minfreq = 0
    try:
        maxfreq = int(request.form['maxfreq'])
    except:
        maxfreq = 0

    word_data = {"words":[]}

    # This top code dosn't run, but it is a more traditional way to tokenize a string and count the words.
    # Not using this, in favor of the more interesting NLTK library.
    if False:
        c = Counter(story.lower().split())
        print c
        most_common = c.most_common(max_top)
    else:
        # This is a natural language toolkit.  I'm only using the fastest routines which do not do anything amazing.
        # However, this library would be a good fit to further process the word frequency. For example, some ideas I had
        # were to add UI controls to only find Names, or verbs, or associated words. More study on this lib is needed but
        # it might be a good solution rather than invent a heuristic to identify the more meaningful words in the story.
        
        # Saving this for reference. Different tokenizers parse words differently.  Alice and Alice's can be counted 
        # together or separately depending on the tokenizer you use.
        #from nltk.tokenize import WhitespaceTokenizer
        # words = nltk.tokenize.word_tokenize(story.lower())
        # words = [w.strip(string.punctuation) for w in words]

        # # Oh hello, this will come in handy.  Some extra filtering that can be controlled from the UI
        # # to limit based on word size or frequency count.
        if nouns=="true":
            words = get_most_common_nouns(story)
        else:
            words = get_most_common_fast(story)

        fdist = FreqDist(words)
        words = [w for w in words if len(w) >= minword and ((fdist[w] >= minfreq) and (fdist[w] <= maxfreq))] 
        most_common = FreqDist(words).most_common(max_top)

        # most_common = get_most_common_fast(story)

    # Create a data struct to be converted to json.  FYI: rank is not used because I hard-coded 10 ranks.  I would
    # probably uses this later if I implement dynamic number of ranks.
    if len(most_common) > 0:
      largest_count = most_common[0][1]
      rank=1
      for w in most_common:
        word_data['words'].append({"rank": rank, "name": w[0], "true_value": w[1], "value":scale_range(high=largest_count, new_high=500, value=w[1]) })
        rank += 1

    # Make JSON for me. This is processed by the javasript AJAX call.
    return jsonify(word_data)


def get_most_common_fast(story):
    words = nltk.tokenize.word_tokenize(story.lower())
    words = [w.strip(string.punctuation) for w in words]

    return words
    # Oh hello, this will come in handy.  Some extra filtering that can be controlled from the UI
    # to limit based on word size or frequency count.
    # fdist = FreqDist(words)
    # words = [w for w in words if len(w) >= minword and ((fdist[w] >= minfreq) and (fdist[w] <= maxfreq))] 
    # most_common = FreqDist(words).most_common(max_top)

def get_most_common_nouns(story):
    words= nltk.word_tokenize(story.lower())
    words = [w.strip(string.punctuation) for w in words]
    tagged_sent = nltk.pos_tag(words)
    nouns= []
    for word, pos in tagged_sent:
        if pos in ['NN',"NNP"]:
            nouns.append(word)
    # freq_nouns = nltk.FreqDist(nouns).most_common(20)
    # return freq_nouns
    return nouns
