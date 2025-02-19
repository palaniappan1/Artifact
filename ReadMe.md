This is the artifact for our paper "Choose Your Call Graph Wisely: On Scaling IFDS-Based Data-Flow Analyses".

The artifact is divided into 5 different folders,

* apk -> It contains all the APK's we used for evaluation. We used 39 APK's from [Taintbench](https://taintbench.github.io/)  and 20 real world APK's for evaluation.
* plots -> The folder for the generated plots
* results -> Stores the results obtained from the evaluation of FlowDroid in the CSV format 
* src -> All the python scripts for evaluation
* supporting_files -> Supporting files needed for evaluation such as SourceSink files for Flowdroid, Flowdroid jar for execution.

The paper consists of two phases of results.

**Phase 1:** 
 
This phase is to check the call graph precision. We utilized 39 Taintbench applications for this purpose.
We ran these 39 applications using 32 different call graph generation techniques, and documented its precision, recall, and other metrics.

Make sure you have all the necessary packages installed

``pip3 install pandas matplotlib``

This whole evaluation might take a couple of hours. To run the whole evaluation for Phase 1. Execute this command from your root folder of this project

``python3 src/eval_taintbench.py``

For just checking the artifact evaluation, try running them with only subset of APK's, use this command

``python src/eval_taintbench.py backflash.apk chulia.apl roidsec.apk``

This should be done in a couple of minutes. All the individual results of these applications will be inside the results/taintbench_results folder.
There will be one file for each APK with the results.

**Phase 2:**

This is the main evaluation of the paper. We chose top performing 8 call graph techniques from the evaluation of Phase 1.
We ran all the 20 real world APK's using these 8 call graph configurations, for 3 iterations and averaged them.

Running these evaluation took almost two weeks. In order to test this evaluation (we can use the smallest of the APK's), run the command

``python3 src/eval_playstore.py gsearchlite.apk``

This command will place the result in a CSV format in the results/playstore_results, and the plots for runtime, memory consumption and correlation between memory and runtime, and between interprocedural edges and number of propagations, 
in the plots folder.