import os
import glob
import re
from bs4 import BeautifulSoup
import anytree as at
from anytree.exporter import DotExporter
from anytree.iterators import PreOrderIter

def getTree (filepath):
	absFilepath = os.path.abspath(filepath)
	ROOT = at.Node("ROOT")
	topIndex = 0
	index = 0
	subIndex = 0

	with open(absFilepath, 'r') as f:
		soup = BeautifulSoup(f.read(), 'html.parser')

	allDivs = soup.find_all('div')
	prevNode = None
	currTopNode = None
	appendNext = False

	for div in allDivs:
		className = div.get('class')
		if className is None:
			continue
		pattern = re.compile("(fs)(\d+|a)")
		classString = " ".join(className)
		foundHeadline = re.search(pattern, classString)
		if foundHeadline:
			result = foundHeadline.group(2)
			if result == '8':
				topIndex += 1
				index = 0
				subIndex = 0
				appendNext = True
				prevNode = None
				currTopNode = at.Node(f"{div.getText()}", parent=ROOT, data=div)
			elif result == 'a':
				index += 1
				appendNext = True
				prevNode = at.Node(f"{div.getText()}", parent=currTopNode, data=div)
		if appendNext:
			subIndex += 1
			appendToNode = prevNode if prevNode is not None else currTopNode
			prevNode = at.Node(f"{topIndex}.{index}.{subIndex}", parent=appendToNode, data=div)
	return ROOT

# Example Usage
# firstHeadline = ROOT.children[0]
# names = [node.data.getText() for node in PreOrderIter(firstHeadline)]

if __name__ == '__main__':
    filepath = './manuals/html/printer/printerManual.html'
    tree = getTree(filepath)
    DotExporter(tree).to_picture("test.png")
