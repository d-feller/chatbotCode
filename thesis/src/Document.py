import preprocess as prep
from parseHTMLtoTree import *


class Document():
    def __init__(self, filepath):
        self.docList = []
        self.nodeList = []
        self.tree, allTopics = getTree(filepath)
        self.allTopics = list(allTopics)
        for topic in self.tree.children:
            if len(topic.children) == 1:
                chain = [node.data.getText(" ") for node in PreOrderIter(topic)]
                textList = " ".join(chain)
                self.docList.append(prep.preprocessTextInput(textList))
                self.nodeList.append([node for node in PreOrderIter(topic)])
            if len(topic.children) > 1:
                for subtopic in topic.children:
                    chain = [node.data.getText(" ") for node in PreOrderIter(subtopic)]
                    textList = " ".join(chain)
                    self.docList.append(prep.preprocessTextInput(textList))
                    self.nodeList.append([node for node in PreOrderIter(subtopic)])
