import os
import subprocess
import sys

import CallGraphAlgorithms
from src.eval_taintbench import is_soot_algorithm
from src.aggregate_csv_files import aggregate_all_csv
from draw_plots import drawPlots

# Get the current directory of eval_py.py
current_directory = os.path.dirname(os.path.abspath(__file__))

allowed_configurations = ['CHA', 'RTA', 'VTA', 'SPARK', 's-2c', 'M-2o', 'Z-2o', 'T-1o']

# Will be unchanged throughout the evaluation
platform_location = os.path.join(current_directory, '..', 'supporting_files/platforms')
flowdroid_jar_path = os.path.join(current_directory, '..',
                                  'supporting_files/soot-infoflow-cmd-jar-with-dependencies.jar')
mainClass = "soot.jimple.infoflow.cmd.MainClass"

# Changes to be made in these arguments
k_configuration = 2
output_directory = os.path.join(current_directory, '..', 'results/playstore_results')
source_sink_text_file = os.path.join(current_directory, '..', 'supporting_files/SourcesAndSinks.txt')
ground_truth_file = os.path.join(current_directory, '..', 'supporting_files/taintbench_results.json')


def execute_jar(program_arguments):
    command = ["java", "-cp", flowdroid_jar_path, mainClass] + program_arguments
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def construct_arguments(callgraph_algorithm, apk_location, qilin_pta):
    arguments = [
        '-a', apk_location,
        '-p', platform_location,
        '-s', source_sink_text_file,
        '-r_j', ground_truth_file,
        '-cg', callgraph_algorithm,
        '-o', output_directory,
        '-d'
    ]
    if callgraph_algorithm == "QILIN":
        arguments.extend(["-qilin_pta", qilin_pta])
    return arguments


def evaluate_all_callgraph_algorithms_for_an_apk(apk_file_path, callgraph_algorithm_list):
    qilin_pta = ""
    total_iterations = 1 * len(callgraph_algorithm_list)
    number = 1
    iteration = 0
    while iteration < total_iterations:
        for algorithm in callgraph_algorithm_list:
            if algorithm != CallGraphAlgorithms.CallgraphAlgorithm.QILIN.value:
                if is_soot_algorithm(algorithm):
                    callgraph_algorithm = algorithm
                else:
                    callgraph_algorithm = CallGraphAlgorithms.CallgraphAlgorithm.QILIN.value
                    qilin_pta = algorithm
                print(
                    f"Executing {os.path.basename(apk_file_path)} with {algorithm}, iteration {number} out of {total_iterations} iterations")
                number = number + 1
                iteration = iteration + 1
                execute_jar(
                    list(map(str, construct_arguments(callgraph_algorithm, apk_file_path, qilin_pta)))
                )


def main():
    # if len(sys.argv) > 1:
    #     arguments = sys.argv[1:]
    #     for arg in arguments:
    #         apk_path = os.path.join(current_directory, '..', 'apk', 'taintbench_apks', arg)
    #         print(f"Evaluating {apk_path}")
    #         evaluate_all_callgraph_algorithms_for_an_apk(apk_path, allowed_configurations)
    #
    # else:
    #     # Construct the path to the apks folder (assuming it's one level up from src)
    #     apks_folder = os.path.join(current_directory, '..', 'apk', 'playstore_apks')
    #     # Loop through all files in the apks folder
    #     for filename in os.listdir(apks_folder):
    #         file_path = os.path.join(apks_folder, filename)
    #         if os.path.isfile(file_path) and os.path.splitext(file_path)[1] == '.apk':
    #             print(f"Executing {os.path.basename(file_path)}")
    #             evaluate_all_callgraph_algorithms_for_an_apk(file_path, allowed_configurations)
    #
    # aggregate_all_csv()
    drawPlots()


if __name__ == "__main__":
    main()
