# code_recommender

1. What is this? <br/>
  This is a code recommender training/testing demo based on the following paper <br/>
  `Thongtanunam P, Tantithamthavorn C, Kula R G, et al. Who should review my code? A file location-based code-reviewer recommendation approach for Modern Code Review[C]// IEEE, International Conference on Software Analysis, Evolution and Reengineering. IEEE, 2015:141-150.`
---------------------------------------------------
2. How to use it? <br/>
  Run main.py
---------------------------------------------------
3. What are two inputs of main.py?<br/>
  * The folder path where .json data files to be loaded & tested exist. If there exist multiple .json files in the folder, all of them will be tested <br/>
  * The positive integer parameter skip, which helps determine the testing dataset: pick every skip-th review in the data as a testcase. <br/> 
    * e.g. skip=5, then the 5th, 10th, 15th, 20th... review will be used to test the score (acc) of the algorithm <br/>
    * Note that no matter what value skip is, all data will be used as reference in the algorithm to get the result of the testcase.
---------------------------------------------------
4. What are outputs of main.py? <br/>
  Top-K & MRR score value, which was explained in V. C part of the paper. 
