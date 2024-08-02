import os
import subprocess
import sys
import csv

import CallGraphAlgorithms

# Get the current directory of eval_py.py
current_directory = os.path.dirname(os.path.abspath(__file__))

allowed_configurations = ['CHA', 'RTA', 'VTA', 'SPARK', 's-2c', '2t', 'Z-2o', '2h']

# Will be unchanged throughout the evaluation
platform_location = os.path.join(current_directory, '..', 'supporting_files/platforms')
flowdroid_jar_path = os.path.join(current_directory, '..',
                                  'supporting_files/soot-infoflow-cmd-jar-with-dependencies.jar')
flowdroid_jar_path_soot = os.path.join(current_directory, '..',
                                       'supporting_files/soot-infoflow-cmd-jar-with-dependencies-soot.jar')
mainClass = "soot.jimple.infoflow.cmd.MainClass"

# Changes to be made in these arguments
k_configuration = 2
output_directory = os.path.join(current_directory, '..', 'results/playstore_results')
source_sink_text_file = os.path.join(current_directory, '..', 'supporting_files/SourcesAndSinks.txt')
ground_truth_file = os.path.join(current_directory, '..', 'supporting_files/taintbench_results.json')
exception_file_name = os.path.join(current_directory, '..', 'results/playstore_results/exceptions.csv')


def execute_jar(program_arguments, jar_path):
    # Set the timeout to 5 hours
    timeout_seconds = 5 * 60 * 60
    command = ["java", "-XX:+UseG1GC", "-XX:+UseAdaptiveSizePolicy", "-Xmx200g", "-Xss1g", "-cp", jar_path,
               mainClass] + program_arguments
    try:
        subprocess.run(command, check=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        app_name, cg_name = get_arguments_value(command)
        write_to_csv(app_name, cg_name, "TOE")
    except subprocess.CalledProcessError as e:
        app_name, cg_name = get_arguments_value(command)
        write_to_csv(app_name, cg_name, "RE")
        print(f"Error: {e}")
    except Exception as e:
        app_name, cg_name = get_arguments_value(command)
        write_to_csv(app_name, cg_name, "RE")
        print(f"An unexpected error occurred: {e}")


def is_soot_algorithm(algorithm_to_check):
    for algorithm in CallGraphAlgorithms.CallgraphAlgorithm:
        if algorithm.value == algorithm_to_check:
            return True
    return False


def get_arguments_value(args):
    app_name = next(args[i + 1] for i, arg in enumerate(args) if arg == '-a')
    app_name = os.path.basename(app_name)
    cg_name = next(
        (args[i + 1] for i, arg in enumerate(args) if arg == '-qilin_pta'),
        next((args[i + 1] for i, arg in enumerate(args) if arg == '-cg'), None)
    )
    return app_name, cg_name


def write_to_csv(app_name, cg_name, reason):
    file_exists = os.path.isfile(exception_file_name)

    # Open the file in append mode ('a')
    with open(exception_file_name, 'a', newline='') as csvfile:
        fieldnames = ['app_name', 'cg_name', 'reason']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header if the file does not exist
        if not file_exists:
            writer.writeheader()

        # Write the data
        writer.writerow({'app_name': app_name, 'cg_name': cg_name, 'reason': reason})


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
                    jar_file_path = flowdroid_jar_path_soot
                else:
                    callgraph_algorithm = CallGraphAlgorithms.CallgraphAlgorithm.QILIN.value
                    qilin_pta = algorithm
                    jar_file_path = flowdroid_jar_path
                print(
                    f"Executing {os.path.basename(apk_file_path)} with {algorithm}, iteration {number} out of {total_iterations} iterations")
                number = number + 1
                iteration = iteration + 1
                execute_jar(
                    list(map(str, construct_arguments(callgraph_algorithm, apk_file_path, qilin_pta))), jar_file_path
                )


def main():
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        for arg in arguments:
            apk_path = os.path.join(current_directory, '..', 'apk', 'playstore_apks', arg)
            print(f"Evaluating {apk_path}")
            evaluate_all_callgraph_algorithms_for_an_apk(apk_path, allowed_configurations)

    else:
        # Construct the path to the apks folder (assuming it's one level up from src)
        apks_folder = os.path.join(current_directory, '..', 'apk', 'playstore_apks')
        # Loop through all files in the apks folder
        for filename in os.listdir(apks_folder):
            file_path = os.path.join(apks_folder, filename)
            if os.path.isfile(file_path) and os.path.splitext(file_path)[1] == '.apk':
                print(f"Executing {os.path.basename(file_path)}")
                evaluate_all_callgraph_algorithms_for_an_apk(file_path, allowed_configurations)

    # aggregate_all_csv()
    # drawPlots()


if __name__ == "__main__":
    main()
