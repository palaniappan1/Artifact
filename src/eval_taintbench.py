import subprocess
import sys

import CallGraphAlgorithms
import os
import glob
import Taintbench_Precision_Stats

# Get the current directory of eval_py.py
current_directory = os.path.dirname(os.path.abspath(__file__))

# Will be unchanged throughout the evaluation
platform_location = os.path.join(current_directory, '..', 'supporting_files/platforms')
flowdroid_jar_path = os.path.join(current_directory, '..',
                                  'supporting_files/soot-infoflow-cmd-jar-with-dependencies.jar')
mainClass = "soot.jimple.infoflow.cmd.MainClass"
ground_truth_taintbench_file = os.path.join(current_directory, '..', 'supporting_files/ground_truth')
source_sink_taintbench_file = os.path.join(current_directory, '..', 'supporting_files/sourceandsinks')
taintbench_results = os.path.join(current_directory, '..', 'supporting_files/taintbench_results.json')


def get_taintbench_source_sink_file(apk_location):
    file_name = os.path.basename(apk_location)

    # Remove the extension from the filename
    apk_name = os.path.splitext(file_name)[0]
    # Construct the pattern to search for files
    pattern = os.path.join(source_sink_taintbench_file, f"SourcesAndSinks_fd_{apk_name}.txt")

    # Search for files matching the pattern
    matching_files = glob.glob(pattern)

    # If a matching file is found, return its path
    if matching_files:
        return matching_files[0]  # Assuming you want the first matching file
    else:
        return None


def get_taintbench_ground_truth_file(apk_location):
    file_name = os.path.basename(apk_location)

    # Remove the extension from the filename
    apk_name = os.path.splitext(file_name)[0]
    # Construct the pattern to search for files
    pattern = os.path.join(ground_truth_taintbench_file, f"{apk_name}_findings_ground_truth.json")

    # Search for files matching the pattern
    matching_files = glob.glob(pattern)

    # If a matching file is found, return its path
    if matching_files:
        return matching_files[0]  # Assuming you want the first matching file
    else:
        return None


# Changes to be made in these arguments
k_configuration = 2
output_directory = os.path.join(current_directory, '..', 'results/taintbench_results')


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
        '-s', get_taintbench_source_sink_file(apk_location),
        '-r_s_s', get_taintbench_ground_truth_file(apk_location),
        '-r_j', taintbench_results,
        '-d',
        '-cg', callgraph_algorithm,
        '-o', output_directory,
    ]
    if callgraph_algorithm == "QILIN":
        arguments.extend(["-qilin_pta", qilin_pta])
    return arguments


def construct_callgraph_algorithms_list():
    callgraph_algorithm_list = []
    for algo in CallGraphAlgorithms.CallgraphAlgorithm:
        callgraph_algorithm_list.append(algo.value)
    for algo in CallGraphAlgorithms.NonConfigurablePTA:
        callgraph_algorithm_list.append(algo.value)
    for value in CallGraphAlgorithms.ConfigurablePTA:
        for i in range(1, k_configuration + 1):
            callgraph_algorithm_list.append(value.value.replace('k', str(i)))
    return callgraph_algorithm_list


def is_soot_algorithm(algorithm_to_check):
    for algorithm in CallGraphAlgorithms.CallgraphAlgorithm:
        if algorithm.value == algorithm_to_check:
            return True
    return False


def evaluate_all_callgraph_algorithms_for_an_apk(apk_file_path, callgraph_algorithm_list):
    qilin_pta = ""
    total_iterations = len(callgraph_algorithm_list)
    number = 1
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
            execute_jar(
                list(map(str, construct_arguments(callgraph_algorithm, apk_file_path, qilin_pta)))
            )


def main():
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        for arg in arguments:
            apk_path = os.path.join(current_directory, '..', 'apk', 'taintbench_apks', arg)
            evaluate_all_callgraph_algorithms_for_an_apk(apk_path, construct_callgraph_algorithms_list())
    else:
        # Construct the path to the apks folder (assuming it's one level up from src)
        apks_folder = os.path.join(current_directory, '..', 'apk', 'taintbench_apks')
        # Loop through all files in the apks folder
        for filename in os.listdir(apks_folder):
            file_path = os.path.join(apks_folder, filename)
            if os.path.isfile(file_path):
                print(f"Executing {os.path.basename(file_path)}")
                evaluate_all_callgraph_algorithms_for_an_apk(file_path, construct_callgraph_algorithms_list())
    # Taintbench_Precision_Stats.process_taintbench_results()


if __name__ == "__main__":
    main()
