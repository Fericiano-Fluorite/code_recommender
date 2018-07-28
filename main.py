from author import Author, AuthorList
import stringCompare
import os
import json
import time

###############################################################################
# list of all authors in the training dataset of a project. 
# Reset before training each project
# class AuthorList is defined in author.py
###############################################################################
authors = AuthorList()

# The parameter to control the set of test cases
skip = 1

# output filename 
f_out = ""

###############################################################################
# calculate 4 kinds of similarity scores
# Input:
#   f_now: the file name in the review that is checking now
#   f_past: the file name in the review before the being checked one
#   equ: the category of score being calculated
# Output:
#   score: the respective score
###############################################################################
def filePathSimilarity(f_now, f_past, equ):
    if equ == 0:
        return stringCompare.LCP(f_now, f_past)
    elif equ == 1:
        return stringCompare.LCSuff(f_now, f_past)
    elif equ == 2:
        return stringCompare.LCSubseq(f_now, f_past)
    elif equ == 3:
        return stringCompare.LCSubstr(f_now, f_past)
    else:
        return 0
    
###############################################################################
# Sum 4 kinds of scores up with combination technique (IV. D part of the paper), 
# and sort them to get a ranking list of all authors to be recommended to the test review
#
# Input: 
#   scoreList: A list of scores for all authors in the format of
#       [[LCP_score_i, LCS_score_i, LCSubstr_score_i, LCSubseq_score_i], author_name_i] for the (i+1)-th author
#
# Output:
#   sum_score: An descendingly ordered list of weights for each author after finishing combination technique in the format of
#       [combination_weight_i, author_name_i] for the (i+1)-th author
#   i.e. sum_score[0] is the first author to be recommended to the test review with its weight,
#        sum_score[1] is the second one,
#        sum_score[2] is the third one, etc.
###############################################################################
def getRanking(scoreList):
    global authors
    scores = [[[0.0, ""] for p in range(authors.length())] for r in range(4)]
    sum_score = [[0, authors.getName(i)] for i in range(authors.length())]
    
    # Combination technique
    for i in range(4):
        
        # reorganize the input list for the ease of sorting
        # scores[i][j][0] refers to the i-th score of (j+1)-th author. 
        #     e.g. scores[1][5][0] refers to LCS_score of 6-th author
        #     e.g. scores[3][18][0] refers to LCSubseq_score of 19-th author
        # scores[i][j][1] refers to the username of the j-th author (no matter what kind of score it is)
        #     e.g. scores[0][6][1] = scores[1][6][1] = scores[2][6][1] = scores[3][6][1] = the author name of 7-th author
        for j in range(authors.length()):
            scores[i][j][0] = scoreList[j][0][i]
            scores[i][j][1] = scoreList[j][1]
            
        # sort the list by descending order for each kind of score
        # i.e. scores[0] is a list of LCP_score for all authors in descending order
        #      scores[1] is a list of LCS_score for all authors in descending order
        #      scores[2] is a list of LCSubstr_score for all authors in descending order
        #      scores[3] is a list of LCSubseq_score for all authors in descending order
        scores[i].sort(key = lambda x: x[0], reverse = True)
        
        # Weighting algorithm in the combination technique
        M = 0
        for j in range(authors.length()):
            if scores[i][j][0] == 0:
                break
            M += 1
        for j in range(authors.length()):
            if scores[i][j][0] == 0:
                break
            name = scores[i][j][1]
            index = authors.find(name)[0]
            sum_score[index][0] += M-j
    
    # sort the weight list generated from combination technique and get the ranking
    sum_score.sort(key = lambda x: x[0], reverse = True)
    return sum_score

###############################################################################
# Given the ranking of authors to be recommended, calculate its accuracy score with top-K metric (described in V. C part in the paper)
#
# Input:
#   ranking: ranking list of authors to be recommended based on the algorithm the paper comes up
#   review: the actual review, containing the list of people who are actually related to the review
#
# Output:
#   correct: the number of related authors that are in the top K of the ranking list
#   total: the number of related authors to the given review
###############################################################################
def topKEvaluate(ranking, review):
    K = 10
    correct = 0
    total = 0
    
    for auth in review["approve_history"]:
        auth = auth["userId"]
        total += 1
        for i in range(K):
            # if the weight is 0, then all following predictions are considered wrong by default
            if ranking[i][0] == 0:
                break
            name = ranking[i][1]
            if name == auth:
                # if the actual related author is found in the top K position of the ordered ranking list
                # then the counter of all correctly predicted authors is accumulated by 1 based on the definition of the metric
                correct += 1
                break
        
    return correct, total


###############################################################################
# Given the ranking of authors to be recommended, calculate its accuracy score with MRR metric (described in V. C part in the paper)
#
# Input:
#   ranking: ranking list of authors to be recommended based on the algorithm the paper comes up
#   review: the actual review, containing the list of people who are actually related to the review
#
# Output:
#   score: the sum of all scores earned based on MRR metric
#   total: the number of related authors to the given review
###############################################################################
def MRREvaluate(ranking, review):
    score = 0.0
    total = 0
    for auth in review["approve_history"]:
        auth = auth["userId"]
        total += 1
        for i in range(len(ranking)):
            # if the weight is 0, then all following predictions are considered non-sense by default
            if ranking[i][0] == 0:
                break
            name = ranking[i][1]
            if name == auth:
                # if the actual related author is found in the (i+1)-th position of the ordered ranking list,
                # then the MRR score is accumulated by 1/(i+1) based on the definition of the metric
                score += 1/float(i+1)
                break
    
    return score, total

def Run(file):
    global authors, skip, f_out
    
    # Reinitialize author name list before training/testing each project
    authors.clear()
    
    f = open(file,'r',errors='ignore')
    
    # Reinitialize list of all reviews
    reviews = []
    
    # For each line in the dataset file
    for line in f:
        review = json.loads(line.strip())
        
        # Get all usernames from each piece of review & add it to the author name list
        for hist in review["approve_history"]:
            au = Author(hist["userId"])
            authors.add(au)
            
        # Add the review into the review list
        reviews.append(review)
        
    # Sort the review list by submission date 
    reviews.sort(key = lambda x: x["submit_date"])
    
    # Reinitialize acc parameters
    topK_acc = 0.0
    MRR_acc = 0.0
    
    topK_sum = 0
    MRR_sum = 0
    
    # Test reviews
    for i, review in enumerate(reviews):
        
        ### Testcase selection & data initialization
        
        # the 1st review is not tested because there is no reference to do the test
        if i < 1:
            continue
        
        # selection of test cases      
        if i % skip > 0:
            continue
        
        # print the progress bar when necessary
        if i % 1000 == 0:
            print ("Progress: ", i*100/len(reviews), "%") 
            
        # get the file list in the currently tested review
        files_now = review["files"]
        
        # code-reviewer scores in the format of [[LCP_score_i, LCS_score_i, LCSubstr_score_i, LCSubseq_score_i], author_name_i] for the (i+1)-th author in the author list
        CRscores = [[[0.0 for k in range(4)], authors.getName(q)] for q in range(authors.length())]
        
        ### Algorithm
        # check all reviews submitted before the current one
        for j in range(i):
            
            # get the file list in the j-th review, which is earlier submitted than the currently tested one
            pastReview = reviews[j]
            files_past = pastReview["files"]
            
            # [LCP_score, LCS_score, LCSubstr_score, LCSubseq_score] calculated between the (i+1)-th (current) and the (j+1)-th (past) reviews
            score_p = [0.0 for k in range(4)]
            for f_now in files_now:
                for f_past in files_past:
                    for equ in range(4):
                        score_p[equ] += filePathSimilarity(f_now, f_past, equ)
            
            # Normalize scores calculated above
            for equ in range(4):
                score_p[equ] /= float(len(files_now)*len(files_past))
            
            # add scores for each author related
            for auth in pastReview["approve_history"]:
                auth = auth["userId"]
                index = authors.find(auth)[0]
                for equ in range(4):
                    CRscores[index][0][equ] += score_p[equ]
            
        # Get the ranking list based on all author scores accumulated above 
        ranking = getRanking(CRscores)
        
        ### Scoring the test result 
        a,b = topKEvaluate(ranking, review)
        topK_acc += a
        topK_sum += b
        a,b = MRREvaluate(ranking, review)
        MRR_acc += a
        MRR_sum += b
        
    # Print the overall result for the project
    print ("Scores for the project: Top-K: ", topK_acc/topK_sum, " MRR: ", MRR_acc/MRR_sum, file=f_out)
    
    return 0
            


if __name__ == "__main__":
    
    # Get all project folders in the list
    projects = []
    
    # Input file path and skip parameter (described in README)
    file_dir = input("Please input the path where dataset files (in .json format) exist: ")
    skip = input("Please input the parameter skip (an integer larger than 0): ")
    skip = int(skip)
    if (skip <= 0):
        skip = 1
        
    # get all project file names
    for root, dirs, files in os.walk(file_dir):
        for f in files:
            if (f.split(".")[-1] == "json"):
                projects.append(os.path.join(root, f))
                
    f_out = open("TOP10_"+"DIR="+file_dir+"_SKIP="+str(skip)+".txt", "w")
    
    # process each project
    for each in projects:
        print (each, file=f_out)
        Run(each)
        #break
    
    f_out.close()