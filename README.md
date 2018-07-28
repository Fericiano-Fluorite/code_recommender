# code_recommender
===================================================
1. What is this?
  This is a code recommender training/testing demo based on the paper 
  @inproceedings{ThongtanunamSANER2015,
    	Author={Patanamon Thongtanunam and  Chakkrit Tantithamthavorn and  Raula Gaikovina Kula and  Norihiro Yoshida and  Hajimu Iida and  Ken-ichi Matsumoto},
    	Title = {Who Should Review My Code? A File Location-Based Code-Reviewer Recommendation Approach for Modern Code Review},
    	Booktitle = {the 22nd IEEE International Conference on Software Analysis, Evolution, and Reengineering (SANER)},
    	Pages = {to be appear},
    	Year = {2015}
    }
---------------------------------------------------
2. How to use it?
  Run main.py
---------------------------------------------------
3. What are two inputs of main.py?
  a. The path of .json data files to be loaded & tested. If there exist multiple .json files, all of them will be tested
  b. The positive integer parameter skip, which helps determine the testing dataset: pick every skip-th review in the data as a testcase. 
     e.g. skip=5, then the 5th, 10th, 15th, 20th... review will be used to test the score (acc) of the algorithm
     Note that no matter what value skip is, all data will be used as reference in the algorithm to get the result of the testcase.
---------------------------------------------------
4. What are outputs of main.py?
  Top-K & MRR score value, which was explained in V. C part of the paper. 
