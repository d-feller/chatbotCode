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

	index = 0
	subIndex = 0

	with open(absFilepath, 'r') as f:
		soup = BeautifulSoup(f.read(), 'html.parser')

	allDivs = soup.find_all('div')
	prevNode = None
	appendNext = False

	for div in allDivs:
		if index == 5:
			break
		className = div.get('class')
		if className is None:
			continue
		pattern = re.compile("(fs)(\d+|a)")
		classString = " ".join(className)
		foundHeadline = re.search(pattern, classString)
		if foundHeadline:
			result = foundHeadline.group(2)
			if result == 'a':
				index += 1
				appendNext = True
				prevNode = at.Node(f"{index}", parent=ROOT, data=div)
		if appendNext:
			subIndex += 1
			prevNode = at.Node(f"{index}.{subIndex}", parent=prevNode, data=div)
	return ROOT

# Example Usage
# firstHeadline = ROOT.children[0]
# names = [node.data.getText() for node in PreOrderIter(firstHeadline)]
# DotExporter(ROOT).to_picture("test.png")

if __name__ == '__main__':
#	filepath = './manuals/html/printer/printerManual.html'
#	tree = getTree(filepath)
#	print(at.RenderTree(tree))
	
