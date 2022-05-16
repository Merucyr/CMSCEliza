# Name: Miles Raleigh
# Class: Intro to Natural Language Processing

#Call our "runner" which is our main function
#We input sentences into the runner, if it's any of our quitKeywords it just terminates program
#If it's not a quitkeyword we have a 1/10 chance of prepending the username to our response message
#The Eliza INIT function sets up Eliza's key:value response table lists, I don't know why I couldn't get this working as just regular global vars but whatever, annoying
#We call the .reply function with the input the user sent in, and it regex checks the input with all of the keys that Eliza has (the reToResponseTable[0])
#The reply function uses a regex search, if there was a hit (which there always is at worst an anything-regex at the end), we then check for any %1/%2/%ns, and replace those
#The replacement for things like "I" to "You" happens in the trans function which is called, which just lowercases the word(s) and swaps them/transforms them
#For example, on inputting "hello" you would receive a message of "Well howdy there pardner", and on inputting "I am sad", you may receive any number of possible outputs such as "Did you come to me becuase you are sad"
#Linked below is an nltk article where I saw the idea of doing multiple outputs, and implementing it ended up being a similar idea that I do when I do game modding, so instead of just making it a 1;1 array it's an array [RExpression, [Responses]]
#One of the ways we do layer-selection for items was insanely close to how I did this here but with Squirrel K:V pairs rather than in Python haivng to make a lambda to set up the K:V stuff. 

#Usage: To run or call the program you can execute a simple 'python eliza.py' in a terminal of choice

#Example Run, we see that the same input can generate multiple outputs and that on a sentence that is not understood we receive a message that essentially changes the topic
#For note, the > Miles is a user input, after this all user input is labeled [Miles] > to show who is currently chatting
# [Eliza] > Hi, I'm a psychotherapist. What is your name?
# > Miles
# [Eliza] > When you are done messaging me, please type either quit or exit.
# [Eliza] > Hello there Miles, tell me something about yourself.
# [Miles] > I'm sad
# [Eliza] > Did you come to me because you are sad?
# [Miles] > I'm sad
# [Eliza] > How long have you been sad?
# [Miles] > A very long time
# [Eliza] > <Kssh> My processor is overheating, could you please tell me something simpler.

import string
import re
import random

userName = ""

quitKeywords = ['quit', 'exit', 'leave', 'stop', 'halt', 'done', 'goodbye', 'bye']

# Key:Value dict of words we want to swap when making sentences, e.g. we swap I to You in some responses
#I might be missing a few here but I swap things like "i" into "you", "i've" into "i have", etc, mostly just because these are common and I could think of them. Just plugged some in as I went.
swapPersonRefTable = {
  "i"    : "you",
  "was"  : "were",
  "i've"  : "you have",
  "am"   : "are",
  "my"  : "your",
  "your"  : "my",
  "are"  : "am",
  "i'll"  : "you will",
  "you've": "I have",
  "me"  : "you",
  "yours"  : "mine",
  "you"  : "me"
}

#After I had 1 to 1 stuff I saw some dude had a table of responses + tables are kinda based, god I love tables. So I converted to that similar idea
#The conversion mostly just meant adding in a second mapped list of the responseTable[1] rather than responseTable[0] only
#Yoinked the idea of multi-responses from https://www.nltk.org/_modules/nltk/chat/eliza.html 
#Stole some of their response lines becuase I thought they were good, these are ones like "Tell me more about your father" but before I generalized the parents
#I stole some specific popular keywords from https://chatbotsmagazine.com/10-most-popular-words-users-send-to-chatbots-98fc18a80b4a but these are general keywords and not just eliza-specific, so we only incorporated a couple of them

#Spotted Words: "Fun" Words/Less Than Essential Words: the two hotline words, Help, Thanks, I love you, .. a joke ..
# Serious words: I ('m in) need, I am/I'm, .. I think I .., I can't/Can, What/Why/How/Because... , etc
# Most serious words are just common modifiers that I'd type to a therapist. I need help, I need money, I'm sad, I am h appy, What [do you think of..], Why [can i not get..], etc



reToResponseTable = [

  [r'(.*) suicidal|kill(.*)', #this really wouldn't be triggered but like it's kind of the most important key:value 
  [ "Triggered on a serious keyword: If you are feeling suicidal you may wish to call an actual hotline at 800-273-8255"]],
  
  [r'^Help',
  [ "[SYSTEM MESSAGE] : If you would like to exit the program use any number of the keywords to exit, otherwise chat away."]],
  
  [r'^Thanks',
  [ "You are welcome.", "You're welcome", "It is my pleasure"]],

  [r'^I love you(.*)',
  [ "Wow, *twirls hair*, I love you too. Would you like to get married?"]],

  [r'I need (.*)',
  [  "Why do you say you need %1?",
    "Does %1 really benefit you?",
    "What makes %1 necessary?",
    "%1? Are you certain?",
    "Why do you need %1"]],

  [r'I\'m in need (.*)',
  [  "Why do you say you need %1?",
    "Does %1 really benefit you?",
    "What makes %1 necessary?",
    "%1? Are you certain?",
    "Why do you need %1"]],

  [r'I am (.*)',
  [  "Did you come to me because you are %1?",
    "How long have you been %1?",
    "How do you feel about being %1?",
    "How does being %1 make you feel?",
    "Do you enjoy being %1?",
    "Why do you tell me you're %1?",
    "Why do you think you're %1?",
    "What makes you say that you are %1",
    "Are you sure you are %1",
    "Would other people say you are %1"]],

  [r'I\'m (.*)',
  [  "Did you come to me because you are %1?",
    "How long have you been %1?",
    "How do you feel about being %1?",
    "How does being %1 make you feel?",
    "Do you enjoy being %1?",
    "Why do you tell me you're %1?",
    "Why do you think you're %1?",
    "What makes you say that you are %1",
    "Are you sure you are %1",
    "Would other people say you are %1"]],

  [r'(.*)I think I (.*)',
  [ "You think that you %2?",
    "Why do you claim that you %2" ]],

  [r'How are you', 
  [ "I am fine, please tell me about yourself."]],

  [r'I can\'?t (.*)',
  [  "How do you know you can't %1?",
    "Perhaps you could %1 if you tried.",
    "What would it take for you to %1?"]],

  [r'I can (.*)',
  [  "How do you know you can %1?",
    "Perhaps you could %1.",
    "How do you %1?"]],

  [r'Why don\'?t you (.*)',
  [  "Do you think I don't %1 already?",
    "Maybe I will %1."]],

  [r'Why can\'?t I (.*)',
  [  "Do you think you should be able to %1?",
    "If you could %1, what would you do?",
    "I don't know -- why can't you %1?",
    "Have you really tried?"]],

  [r'Are you (.*)',
  [  "Does it matter whether I am %1 or not?",
    "Would you like me to be %1?",
    "Perhaps you believe I am %1.",
    "Could you be projecting that I am %1?"]],

  [r'What (.*)',
  [  "Why do you ask?",
    "Does it help you to have an answer to that?",
    "Do you have any thoughts on the matter?"]],

  [r'Why (.*)',
  [  "Why don't you tell me the reason why %1?",
    "Why do you think %1?" ]],

  [r'How (.*)',
  [  "What do you think about it?",
    "Have you tried to answer your own question?",
    "What is it you're really asking?"]],

  [r'Because (.*)',
  [  "Is that the real reason?",
    "Can you think of any other reasons?",
    "Does that reason apply to anything else?",
    "If %1, is true then what else is?"]],

  [r'(.*) sorry (.*)',
  [  "You do not need to apologize, it's normal to have feelings.",
    "What feelings does apologizing give you?"]],

  [r'Hello(.*)',
  [  "Well howdy there pardner"]],

  [r'(.*)I think(?: that | )I (.*)', #VERY ugly "i think (that)?"
  [  "Do you really think so?",
    "Are you sure?",
    "Could you tell me why you think that %1?"]],

  [r'(.*) friend (.*)',
  [  "Tell me more about your friends.",
    "When you think of a friend, who or what comes to mind?",
    "Why don't you tell me about a childhood friend?",
    "Would you say you have close friends?"]],

  [r'^Yes|No', #By here we probably can't trigger it without just having it be yes/no, but just to be safe I add in a mandatory start of line, so we don't get something like "I think yes is a great color" and it says You seem certain
  [  "You seem certain.",
    "Could you elaborate if it is possible."]],

  [r'Is it (.*)',
  [  "Do you think that it's %1?",
    "Would it being %1 affect you?",
    "Would you like it to be %1?",
    "Does it being %1 make you do anything?"]],

  [r'It is (.*)',
  [  "You seem very certain.",
    "If I told you that it probably isn't %1, what would you feel?"]],

  [r'Can you (.*)',
  [  "What makes you think I can't %1?",
    "If I could %1, then what?",
    "Why do you ask if I can %1?"]],

  [r'Can I (.*)',
  [  "Perhaps you don't want to %1.",
    "Do you want to be able to %1?",
    "You decide whether or not you can %1, not me."]],

  [r'You are (.*)',
  [  "Why do you think I am %1?",
    "Do you think you're projecting %1 on me?",
    "Maybe I am %1, why do you think I am?"]],

  [r'You\'?re (.*)',
  [  "You think that I'm %1?",
    "We should be talking about you, not me."]],

  [r'I don\'?t (.*)',
  [  "Do you really not %1?",
    "Why do you not %1?",
    "Would you like to %1?"]],

  [r'I feel (.*)',
  [  "Good, tell me more about these feelings.",
    "How often do you feel %1?",
    "Do you feel %1 at certain times of the day?",
    "Do specific people make you feel %1?",
    "Is there any reason you feel %1?",
    "How do you feel about these feelings?"]],

  [r'I have (.*)',
  [  "Why %1?",
    "Did you really %1?",
    "What will you do now that you %1?"]],

  [r'I would (.*)',
  [  "Tell me why you'd %1?",
    "Why %1?",
    "Does anyone else know that you would %1?"]],

  [r'Is there (.*)',
  [  "Do you think there is %1?",
    "There might be a(n) %1, what do you think?.",
    "How would you feel if there was %1?"]],

  [r'Are there (.*)',
  [  "Do you think there are %1?",
    "There might be %1, what do you think?.",
    "How would you feel if there was %1?"]],

  [r'I want (.*)',
  [  "What would it mean to you if you got %1?",
    "Why do you want %1?",
    "What would you do if you got %1?",
    "If you got %1, then what would you do?"]],
  
  [r'^My (.*)',
  [  "I see, your %1.",
    "Why do you say that your %1?",
    "When your %1, how do you feel?"]],

  [r'(.*) mother|father(.*)', #Generalized and wrapped up mother/father here
  ["Tell me more about them", 
  "What was your relationship with them like?", 
  "How do you feel about them", 
  "How does this relate to your feelings today?", 
  "Do you have trouble showing affection with your family?", 
  "Family matters are important, don't you agree?"]],
  
  [r'(.*)child(.*)',
  [  "Did you have close friends as a child?",
    "What is your favorite childhood memory?",
    "Do you remember any dreams or nightmares from childhood?",
    "Did the other children bully you?",
    "How do you think your childhood experiences relate to your feelings today?",
    "How was your household when you were a child?",
    "Do you resent your childhood?",
    "I don't know man this is just some random line that I needed as a placeholder for a kid"]],

  [r'You (.*)',
  [  "We should be discussing you, not me.",
    "Why do you say that about me?",
    "Why do you care whether I %1?"]],

  [r'(.*) a joke(.*)?', #Only triggered when you say something like [Tell me] [a joke] [please]
  [ "I'm not a very funny therapist, my apologies.",
    "What do you call a deer with no eyes? No eye-deer."]],

  [r'(.*)\?', #On any question that we didn't understand
  [  "Why do you ask?",
    "Perhaps you should look within.",
    "My apologies, I'm not in a field that can answer that question.",
    "I believe I'm more suited to ask questions rather than give answers."]],

  [r'(.*)', #On anything we didn't understand
  [  "Interesting.",
    "%1.",
    "I see.  And what does that tell you?",
    "How does that make you feel?",
    "How do you feel when you say that?",
    "I don't quite follow, could you elaborate?",
    "Does this have some impact on you right now?",
    "Please go on.",
    "I'm sorry I don't understand, could you please repeat that?",
    "<Kssh> My processor is overheating, could you please tell me something simpler."]]
  ]

#Just a generic class
class Eliza:

  #Init when doing the var = Eliza()
  def __init__(self):
    #Maps all of our actual regular expressions to specific keys/values, sorta bastardized way of doing key/table pairs than I would've done in game modding. 
    self.k = list(map(lambda k: re.compile(k[0], re.IGNORECASE), reToResponseTable))
    self.v = list(map(lambda v: v[1], reToResponseTable))
 
  #Does the actual text translation
  #It feels awful not being able to use 'input' as a key word and becuase of squirrel I'm so tempted to do _self, _input, _reftable
  def trans(self, inp, reftable):
    # print(inp) #debugging test
    w = inp.lower().split() #Converts our input to lowercase, 'i', 'you', etc
    k = reftable.keys()     #because we passed the swapPersonRefTable in we only care abt scanning the keys to it
    for i in range(0, len(w)): #iterate for all of our w input, check if it's in reftable, if it is we swap it
      if w[i] in k:
        w[i] = reftable[w[i]]
    return w #either have to do a ' '.join here or back where we call this, annoying but it works

  def reply(self, userInput):
    #Scan keys for a regex hit, nothing is multiline so you could use .match also I think
    for i in range(0, len(self.k)):
      match = self.k[i].search(userInput)
      if match:
        #Picks any random value pair from the same [i] as our key got selected, bc the lists share the same indices kinda
        output = random.choice(self.v[i])

        #Only worry about this if we have a %1/2/..n 
        pos = output.find('%')
        while pos > -1:
          #We already grabbed the index of the % then we replace the %1 with our stuff in the swpPersonRefTable, e.g. for things like 'i' to 'you' 
          #n is our regex group no. that we're on for match.group purposes
          n = int(output[pos+1:pos+2])
          output = output[:pos] + \
            ' '.join(self.trans(match.group(n), swapPersonRefTable)) + \
            output[pos+2:]
          pos = output.find('%')
          #Maybe keep finding %'s, when we're done with this we're done and can return
        return output
    return '[ERROR] Failed to find a match entirely, what goofball let this happen?'

# Essentially the scripts "main" function, creates the Eliza object within it and terminates on quit/exit
def eliza_runner():
  print('[Eliza] > Hi, I\'m a psychotherapist. What is your name?')
  userName = input('> ')
  print('[Eliza] > When you are done messaging me, please type either quit or exit.')
  print('[Eliza] > Hello there ' + userName + ', tell me something about yourself.')

  msg = ''
  eliza = Eliza();
  while True:
    try:
      msg = input('[' + userName + '] > ')
    except EOFError: #triggered on no input
      msg = 'exit'
    lowercaseMsg = msg.lower()
    if lowercaseMsg not in quitKeywords: #if not in quit keyword list 1/10 chance to attatch name to the beginning, doesn't decapitalize the first letter though bc i'm lazy
      if lowercaseMsg != "":
        if random.randint(1, 10) == 10:
          print('[Eliza] > ' + userName + ', ' + eliza.reply(msg))
        else:
          print('[Eliza] > ' + eliza.reply(msg))
    else:
      print('[Eliza] > Thank you for chatting with me today. The secretary will handle your bill.')
      break


# I don't really get how python works exactly in this regard but we use this to trigger our eliza_runner
if __name__ == "__main__":
  eliza_runner()
