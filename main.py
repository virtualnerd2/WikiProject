import requests
import sys 

prevLinks = set()

def fixPageText(pageText):
	temp = pageText.split("\n")
	badList = set(("{", "|", "*", "<", "-", "}", "="))
	badList4 = set(("File:", "rect "))
	
	while (True):
		if(len(temp) == 0 ):
			return None
		elif(temp[0] == ""):
			temp.remove(temp[0])
		elif temp[0][0] in badList:
			temp.remove(temp[0])
		elif temp[0][0:5] in badList4:
			temp.remove(temp[0])
		else:
			return "/n".join(temp)

def removeFile(pageText):
	pageText = pageText[2:]
	start = 1
	end = 0
	
	for i in range(len(pageText)):
		if(pageText[i:i+2] == "[["):
			start = start + 1
			
		elif(pageText[i:i+2] == "]]"):
			end = end + 1

		if(end == start):
			return pageText[i+2:]

def removeBracket(pageText):
	pageText = pageText[2:]
	start = 1
	end = 0
	
	for i in range(len(pageText)):
		if(pageText[i:i+2] == "{{"):
			start = start + 1
			
		elif(pageText[i:i+2] == "}}"):
			end = end + 1

		if(end == start):
			return pageText[i+2:]
		
def removeParenthesis(pageText):
	pageText = pageText[1:]
	start = 1
	end = 0
	
	for i in range(len(pageText)):
		if(pageText[i:i+1] == "("):
			start = start + 1
			
		elif(pageText[i:i+1] == ")"):
			end = end + 1

		if(end == start):
			return pageText[i+1:]


def getFirstLink(pageText):
	#print(pageText[0:10000])
	if(pageText== None):
		return "NONE"

	firstBraquet = pageText.find("[[")
	secondBraquet = pageText.find("]]")
	firstParenthesis = pageText.find("(")
	firtCurly = pageText.find("{{")

	if(firstParenthesis == -1):
		firstParenthesis = 100000000000
	if(firtCurly == -1):
		firtCurly = 100000000000

	if(firstParenthesis > firstBraquet  and firtCurly > firstBraquet):
		if(pageText.lower()[firstBraquet:firstBraquet+7] != "[[file:" and pageText[firstBraquet:firstBraquet+8].lower() != "[[image:"):
			ret = pageText[firstBraquet+2:secondBraquet]
			#print(ret)
			#not checked
			if(ret.lower().find("#") != -1 ):
				return ret[0: ret.find("#")]
			if(ret.lower().find(":") != -1 and ret.lower().find("+") == -1):
				return getFirstLink(pageText[secondBraquet+2:])
			if(ret.find("|") != -1):
					return ret[0: ret.find("|")]
			return ret

		else:
			return getFirstLink(removeFile(pageText[firstBraquet:]))
	if(firstParenthesis < firtCurly):
		return getFirstLink(removeParenthesis(pageText[firstParenthesis:]))
	else:
		return getFirstLink(removeBracket(pageText[firtCurly:]))

def startChain(firstLink, p):
	prevLinks.add(firstLink)
	S = requests.Session()
	URL = "https://en.wikipedia.org/w/api.php"

	Query = {
		"action": "parse",
		"format": "json",
		"page": firstLink,
		"prop": "wikitext",
		"formatversion": "2"
		}

	result = S.get("https://en.wikipedia.org/wiki/" + firstLink)
	if result.status_code == 404:
		return "DOES NOT EXIST"

	R = S.get(url=URL, params=Query)
	DATA = R.json()
	pageText = DATA["parse"]["wikitext"]
	pageText = fixPageText(pageText)
	
	newLink = getFirstLink(pageText)
	
	if(p):
		print(firstLink, "----->",newLink)
	#return "hi"
  
	if(newLink in prevLinks):
		return newLink
	elif(newLink[0:9] == "Category:"):
		return "Categories:"
	elif len(prevLinks) > 100:
		return "FAIL"
	else:
		#return newLink
		return startChain(newLink, p)

test = False
if(test):
	prevLinks = set()
	lastChain = startChain("myth", True)
	sys.exit()
	

S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"
n = 100

PARAMS = {
    "action": "query",
		"rnnamespace": "0",
    "format": "json",
    "list": "random",
    "rnlimit": ("%d", n)
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()
RANDOMS = DATA["query"]["random"]

x = 0

finalLinks = {}
if(n > 1000):
	for r in RANDOMS:
		print(x)
		x = x + 1

		prevLinks = set()
		lastChain = startChain(r["title"], False)

		if(lastChain in finalLinks):
			finalLinks[lastChain] = (finalLinks[lastChain][0] + 1, finalLinks[lastChain][1] + len(prevLinks))
		else:
			finalLinks[lastChain] = (1, len(prevLinks))

else:
	for r in RANDOMS:
		print(x)
		x = x + 1

		prevLinks = set()
		lastChain = startChain(r["title"], True)

		if(lastChain in finalLinks):
			finalLinks[lastChain] = (finalLinks[lastChain][0] + 1, finalLinks[lastChain][1] + len(prevLinks))
		else:
			finalLinks[lastChain] = (1, len(prevLinks))

		print("\nCOMPLETE")
		print("Size:", len(prevLinks))
		print("Last Chain:", lastChain)
		print("")

print("SAMPLE SIZE:", n, "\n")

for key, value in finalLinks.items():
	if(n < 10 or value[0]/n > 1/n):
		print ("Final Link:", key)
		print ("Average Lenght:", (value[1]/value[0]))
		print ("Percentage:", '{:.1%}'.format(value[0]/n), "\n")
