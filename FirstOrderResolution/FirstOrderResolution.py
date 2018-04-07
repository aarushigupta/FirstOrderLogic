import copy

def readInput(filename = 'input.txt'):
    lines =[]
    with open(filename, 'r') as f:
        lines = f.readlines()


    noOfQueries = int(lines[0].strip())
    noOfKBSentences = int(lines[noOfQueries+1].strip())

    rawQuerySentences= []
    for line in lines[1:noOfQueries + 1]:
        rawQuerySentences.append(line.strip())

    rawKBSentences = []
    for line in lines[noOfQueries+2:noOfKBSentences + 1 + noOfQueries + 1]:
        rawKBSentences.append(line.strip())

    return noOfQueries, noOfKBSentences, rawQuerySentences, rawKBSentences


class Literal(object):
    def __init__(self, literal):
        self.predicate = literal[:literal.find('(')]
        self.parameters = self.storeParameters(literal)
        
    def negate(self):
        raw_literal = self.formRawLiteral()
        if raw_literal[0] == '~':
            raw_literal = raw_literal[1:]
        else:
            raw_literal = '~' + raw_literal
        return Literal(raw_literal)
    
    def isResolvable(self, otherLiteral):
        isPredicateSame = self.isPredicateSame(otherLiteral)
        if isPredicateSame == False:
            return False
        areParametersResolvable = self.areParametersResolvable(otherLiteral)
        #print "Param 1: ", self, " Param2: ", otherLiteral
        #print isPredicateSame, areParametersResolvable
        return isPredicateSame and areParametersResolvable
    
    def areParametersConstants(self, otherLiteral):
        for index in range(len(self.parameters)):
            if self.parameters[index][0].isupper() and otherLiteral.parameters[index][0].isupper():
                continue
            else:
                return False
        return True

    def replace(self, variable, paramToReplaceWith):
        self.parameters = [paramToReplaceWith if parameter == variable else parameter for parameter in self.parameters]
    
    
    # Private Functions

    def isPredicateSame(self, otherLiteral):
        return self.predicate == otherLiteral.predicate

    def isParameterEqual(self, parameter1, parameter2):
        if parameter1 != parameter2:
            if parameter1[0].isupper() and parameter2[0].isupper(): return False 
        return True
    
    def areParametersResolvable(self, otherLiteral):
        print "self.raw_literal: ", self, " otherLiteral: ", otherLiteral
        for index in range(len(self.parameters)):
            if not self.isParameterEqual(self.parameters[index], otherLiteral.parameters[index]):
                return False
        return True
    
    def storeParameters(self, literal):
        raw_parameters = literal[literal.find('(')+1 :].rstrip(')').split(',')
        return raw_parameters
    
    def formRawLiteral(self):
        output = self.predicate + '('
        output += ','.join(self.parameters)
        output += ')'
        return output
            
    def __str__(self):
        return self.formRawLiteral()
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, otherLiteral):
        if otherLiteral == None:
            return False
        if self.predicate != otherLiteral.predicate:
            return False
        for index, param in enumerate(self.parameters):
            if param != otherLiteral.parameters[index]:
                return False
        return True



            
class KnowledgeBase(object):
    def __init__(self):
        self.sentences = []
        
    def addSentence(self, sentence):
        literals = map(lambda raw_literal: Literal(raw_literal.strip()), sentence.split('|'))
        self.sentences.append(literals)
        
    def proveQuery(self, raw_query):
        query = Literal(raw_query)
        query = query.negate()
        self.findSentence([query])
        print "sentences: ", self.sentences
    #private functions
    def findSentence(self, querySentence):
        querySentenceStore = []
        querySentenceStore.append(querySentence)
        print self.assignWeightsToKBSentences(querySentence, querySentenceStore)
        #print "Called"

    
    def findMatchingSentence(self,querySentence, querySentenceStore):



    def assignWeightsToKBSentences(self, querySentence, querySentenceStore):
        print "Beginning of recursion:"
        if len(querySentence) == 0:
            return True                     #Change it accordingly
        weightsMapping = {}
        # if querySentence in querySentenceStore:
        #     print "infinite loop"
        #     return False
        isSuccess = False
        for index, kBSentence in enumerate(self.sentences):
            weight, matchedLiteralIndex = self.compareSentences(querySentence, kBSentence)
            weightsMapping[index] = (weight, matchedLiteralIndex)
        

        for index, (weight, literalMatchedIndex)  in sorted(weightsMapping.iteritems(), key=lambda (k,v): (v[0],k), reverse = True):
            #Hanle the case where weight is 0
            #print "Weight is: ", weight
            weight, matchedLiteralIndex = self.compareSentences(querySentence, kBSentence)
            sentenceMarker = []
            if weight == 0:
                #print "Weight is 0"
                continue
            duplicateQuerySentence = copy.deepcopy(querySentence)
            duplicateSentenceToUse = copy.deepcopy(self.sentences[index])
            sentenceMarker[index] += 1
            print "duplicateSentenceToUse: ", duplicateSentenceToUse
            unifiedSentence, querySentencefromUnification = self.unification(duplicateQuerySentence, duplicateSentenceToUse, literalMatchedIndex)
            print "querySentencefromUnification: ", querySentencefromUnification
            print "unifiedSentence: ", unifiedSentence

            resolvedSentence = self.resolution(querySentencefromUnification, unifiedSentence)
            print "resolvedSentence: ", resolvedSentence
            if resolvedSentence in querySentenceStore:
                print "infinite loop"
                #return False
                continue
            else:
                querySentenceStore.append(resolvedSentence)
                isSuccess = self.assignWeightsToKBSentences(resolvedSentence, querySentenceStore)
            #break
            if isSuccess:
                return True
        return False

            
    def compareSentences(self, querySentence, kBSentence):
        weight = 0
        matchedLiteralIndex = 0
        queryLiteralCount = len(querySentence)
        for index, queryLiteral in enumerate(querySentence):
            negatedQueryLiteral = queryLiteral.negate()
            
            for kBLiteral in kBSentence:
                #print "Comparing: ", negatedQueryLiteral, " with ", kBLiteral
                if negatedQueryLiteral.isResolvable(kBLiteral):
                    #print "Matched: ", negatedQueryLiteral, " with ", kBLiteral
                    if negatedQueryLiteral.areParametersConstants(kBLiteral):
                        weight += 1000
                        return weight, index
                    else:
                        weight += 1
                        matchedLiteralIndex = index
                    break

        return weight, matchedLiteralIndex




    def unification(self, querySentence, sentenceToUse, literalMatchedIndex):
        unifiedSentence = []
        constantIn = []
        variables = []
        bindVariables = {}
        print "sentenceToUse: ", sentenceToUse

        for index, literal in enumerate(querySentence):
            querySentence[index] = literal.negate()
        #print "querySentence in unification after negation: ", querySentence

        for literal in sentenceToUse:
            if literal.predicate == querySentence[literalMatchedIndex].predicate:
                for index, param in enumerate(literal.parameters):
                    if not param in bindVariables:
                        if param[0].islower():
                            bindVariables[param] = querySentence[literalMatchedIndex].parameters[index]
                        else:
                            bindVariables[querySentence[literalMatchedIndex].parameters[index]] = param
                break

        sentenceToUseModified = copy.deepcopy(sentenceToUse)

        for variable in bindVariables:
            for literal in sentenceToUseModified:
                literal.replace(variable, bindVariables[variable])
            for literal in querySentence:
                literal.replace(variable, bindVariables[variable])
        print "bindVariables: ", bindVariables
        print querySentence
        for index, literal in enumerate(querySentence):
            querySentence[index] = literal.negate()
        return sentenceToUseModified, querySentence

    
    def resolution(self, querySentence, unifiedSentence):
        negatedQuerySentence = []
        for literal in querySentence:
            negatedQuerySentence.append(literal.negate())

        for negatedIndex, negatedQueryLiteral in enumerate(negatedQuerySentence):
            if negatedQueryLiteral == None:
                continue
            for unifiedIndex, unifiedLiteral in enumerate(unifiedSentence):
                if unifiedLiteral == None:
                    continue
                print "unifiedLiteral: ", unifiedLiteral, " negatedQueryLiteral: ", negatedQueryLiteral
                if negatedQueryLiteral == unifiedLiteral:
                    print "unifiedLiteral: ", unifiedLiteral, " negatedQueryLiteral: ", negatedQueryLiteral
                    unifiedSentence[unifiedIndex] = None
                    querySentence[negatedIndex] = None
                    negatedQuerySentence[negatedIndex] = None
                    print "unifiedSentence: ", unifiedSentence
                    print "querySentence: ", querySentence
                    print "negatedQuerySentence: ", negatedQuerySentence

        resolvedSentence = []
        for literal in querySentence:
            if literal != None:
                resolvedSentence.append(literal)
        for literal in unifiedSentence:
            if literal != None:
                resolvedSentence.append(literal)

        print "resolvedSentence: ", resolvedSentence
        
        #resolvedSentence = [literal if literal != None else None for literal in querySentence + unifiedSentence]
        return resolvedSentence  
        
if __name__ == '__main__':
    noOfQueries, noOfKBSentences, rawQuerySentences, rawKBSentences = readInput()
    print "rawKBSentences: ", rawKBSentences

    knowledgeBase = KnowledgeBase()
    for rawKBSentence in rawKBSentences:
        knowledgeBase.addSentence(rawKBSentence)

    for rawQuerySentence in rawQuerySentences[0:1]:
        knowledgeBase.proveQuery(rawQuerySentence)
        #Do some operation and print output


'''Aarushi's messed up Code begins here:'''


        
# def negateQuery(query):
#     if query[0] == '~':
#         negatedQuery = query[1:]
#     else:
#         negatedQuery = '~' + query
#     print "Negated Query: ", negatedQuery
#     return [negatedQuery]

# def checkIfConstant(parameter):
#         #for parameter in parameters:
#         if parameter[0].isupper():
#             return True #constant
#         else:
#             return False #variable

# def getPredicate(literal):
#     predicateEndIndex = literal.find('(')
#     predicate = literal[:predicateEndIndex]
#     return predicate

# def getParameters(literal):
#     parameterStartIndex = literal.find('(') + 1
#     parameters = literal[parameterStartIndex:].rstrip(')').split(',')
#     return parameters


# def findSentence(negatedQuery, kb):
#     for query in negatedQuery:
#         findCorresponding = negateQuery(query)
#         print "Find Corresponding: ", findCorresponding
#         print "Negated query in Find Corresponding: ", query
#         #beforeBraces = findCorresponding.find('(')
#         #predicateOfQuery = findCorresponding[:beforeBraces]
#         predicateOfQuery = getPredicate(findCorresponding[0])
#         parametersOfQuery = getParameters(findCorresponding[0])

#         flag = 0
#         useSentence = []
#         for sentence in kb:
#             for literal in sentence:
#                 #prdicateBracesKB = predicateInKb.find('(')
#                 predicateInKb = getPredicate(literal)
#                 if predicateInKb == predicateOfQuery:
#                     parameterInKb = getParameters(literal)
#                     for index in range(len(parameterInKb)):
#                         if checkIfConstant(parametersOfQuery[index]):
#                             if checkIfConstant(parameterInKb[index]):
#                                 if parametersOfQuery[index] == parameterInKb[index]:
#                                     flag = 1
#                                     #continue
#                                 else:
#                                     flag = 2
#                                     break
#                         if flag == 0:
#                             useSentence = sentence
#                             literalMatched = literal
                    
#                     if flag == 1:
#                         useSentence = sentence
#                         literalMatched = literal
#                         break                   

#                 if flag == 2:
#                     flag = 0
#                     break
                    

#                     #useSentence = sentence
#                     #flag = 1
#                     #break
#             if flag == 1:
#                 break
#         if useSentence != None:
#             break

#     print useSentence
#     return useSentence, literalMatched

# def unification(negatedQuery, sentenceToUse, literalMatched, kb):
#     unifiedSentence = []
#     constantIn = []
#     variables = []
#     print "In Unification"
#     print "literalMatched: ", literalMatched
#     predicateOfLiteralMatched = getPredicate(literalMatched)
#     print "predicateOfLiteralMatched: ", predicateOfLiteralMatched
#     #negatedQuery = negateQuery(literalMatched)
#     print "NegatedQuery in Unification: ", negatedQuery
#     for query in negatedQuery:
#         pofq = getPredicate(negateQuery(query)[0])
#         print "pofq: ", pofq
#         if pofq == predicateOfLiteralMatched:
#             constantsofQuery =  getParameters(query)
#             predicateOfQuery = pofq
#             break
    
#     print "predicateOfQuery: ", predicateOfQuery
#     print "Constants of Query: ", constantsofQuery
#     bindVariables = {}

#     for literal in sentenceToUse:
#         predicateOfLiteral = getPredicate(literal)
#         if predicateOfLiteral == predicateOfQuery:
#             variablesOfLiteral = getParameters(literal)
#             for index in range(len(variablesOfLiteral)):
#                 if not(checkIfConstant(variablesOfLiteral[index])):
#                     if not variablesOfLiteral[index] in bindVariables:
#                         bindVariables[variablesOfLiteral[index]] = constantsofQuery[index]


#     print "DICT: ", bindVariables
#     newUnifiedSentence = []
#     for literal in sentenceToUse :
#         variables = getParameters(literal)
#         predicate = getPredicate(literal)
#         newLiteral = predicate + "("
#         print "variables: ", variables
#         for variable in variables:
#             if not (checkIfConstant(variable)):
#                 if variable in bindVariables:
#                     print "Dict: ", variable, bindVariables[variable]
#                     print "Variable to replace:", variables, literal
#                     newLiteral += bindVariables[variable] + ","
#                     #literal = literal.replace(variable,bindVariables[variable])
#                 else:
#                     newLiteral += variable + ","
#         newLiteral = newLiteral.rstrip(",") + ")"
#         newUnifiedSentence.append(newLiteral)
#         #unifiedSentence.append(literal)

#     print unifiedSentence
#     print "New Unified Sentence: ", newUnifiedSentence
#     return newUnifiedSentence


# def resolution(negatedQuery, unifiedSentence, kb):
#     for literal in unifiedSentence:
#         for query in negatedQuery:
#             if (literal == '' + query) or ('' + literal == query):
#                 unifiedSentence.remove(literal)
#                 negatedQuery.remove(query)

#     unifiedSentence += negatedQuery
#     print "Unified Sentence: " , unifiedSentence
#     return unifiedSentence




# count , noOfQueries, size_kb, query, kb = readInput()
# negatedQuery = negateQuery(query[0])
# mainNegatedQuery = negatedQuery
# while True:

#     sentenceToUse, literalMatched = findSentence(negatedQuery, kb)
#     unifiedSentence = unification(negatedQuery, sentenceToUse, literalMatched, kb)
#     resolvedSentence = resolution(negatedQuery, unifiedSentence, kb)
#     negatedQuery = resolvedSentence
#         #if resolvedSentence[0] == mainNegatedQuery:
#         #   print "False"
#         #   break
#     if resolvedSentence == None:
#         print "True"
#         break





