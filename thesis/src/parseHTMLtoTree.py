import os
import re

import anytree as at
from anytree.exporter import DotExporter
from bs4 import BeautifulSoup

START_PAGE = 10
END_PAGE = 104
def getTree (filepath):
    absFilepath = os.path.abspath(filepath)
    ROOT = at.Node("ROOT", topic="ROOT")
    sectionIndex = 0
    subsectionIndex = 0
    nodeIndex = 0

    with open(absFilepath, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    allDivs = soup.find_all('div')

    sectionNode = None
    subsectionNode = None
    textNode = None
    allTopics = []
    pageNum = 0

    for div in allDivs:
        pageNum = _getPageNumber(div, pageNum)

        if pageNum < START_PAGE:
            continue
        elif pageNum > END_PAGE:
            break

        className = div.get('class')
        if className is None:
            continue
        pattern = re.compile("(fs)(\d+|a)")
        classString = " ".join(className)
        foundHeadline = re.search(pattern, classString)

        if foundHeadline:
            result = foundHeadline.group(2)
            if result == '6':  # Chapter Headline
                sectionNode = None
            elif result == '8':  # Section Headline
                subsectionNode = None
                textNode = None
                subsectionIndex = 0
                nodeIndex = 0
                sectionIndex += 1
                currentTopic = f"{div.getText()}"
                if currentTopic.strip() not in allTopics:
                    allTopics.append(currentTopic.strip())
                sectionNode = at.Node(f"{div.getText()}", parent=ROOT, data=div, topic=currentTopic)
            elif result == 'a' and sectionNode != None:  # Subsection Headline
                textNode = None
                subsectionIndex += 1
                currentTopic = f"{div.getText()}"
                if currentTopic.strip() not in allTopics:
                    allTopics.append(currentTopic.strip())
                subsectionNode = at.Node(f"{div.getText()}", parent=sectionNode, data=div, topic=currentTopic)
            elif sectionNode is not None or subsectionNode is not None:
                nodeIndex += 1
                if textNode == None:
                    appendToNode = subsectionNode if subsectionNode is not None else sectionNode
                else:
                    appendToNode = textNode
                textNode = at.Node(f"{sectionIndex}.{subsectionIndex}.{nodeIndex}", parent=appendToNode, data=div, topic=currentTopic)
    return ROOT, allTopics


def _getPageNumber(div, currentNum):
    dataPageNumAttr = div.get('data-page-no')
    if dataPageNumAttr is not None:
        pattern = re.compile("\d*[a-f]*")
        foundPage = re.search(pattern, dataPageNumAttr)
        pageNum = int(foundPage.group(0), 16)
        return pageNum
    else:
        return currentNum
# Example Usage
# firstHeadline = ROOT.children[0]
# names = [node.data.getText() for node in PreOrderIter(firstHeadline)]

if __name__ == '__main__':
        filepath = '../manuals/html/printer/printerManual.html'
        tree, _ = getTree(filepath)
        DotExporter(tree).to_picture("test.png")
