



def getActualResultsFromSplunk(jresponse):
    actualResultsList = []
    elementList = jresponse
    for dictionary in elementList:
        isPreview = dictionary['preview']
        if not isPreview:
            if 'result' in dictionary.keys():
                resultsDict = dictionary['result']
                actualResultsList.append(resultsDict)
    return actualResultsList








