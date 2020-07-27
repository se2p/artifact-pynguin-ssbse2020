#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import List, Dict, Union, Any, Set

from find_packages import find_modules

DEBUG = False


def _debug_print(string: str) -> None:
    global DEBUG
    if DEBUG:
        print(f"    [DEBUG] {string}")


def _print_red(string: str) -> None:
    print(f"\033[0;31m{string}\033[0m")


def _arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executes Pynguin as a SLURM array job"
    )
    parser.add_argument(
        "-e",
        "--experiments",
        dest="experiments",
        default="experiments.json",
        help="Path to the experiments definition JSON file",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        default=False,
        action="store_true",
        help="Activate debug mode for script, which gives more detailed outputs"
    )
    return parser


def _parse_json(file_name: Union[str, os.PathLike]) -> Dict[Any, Any]:
    with open(file_name) as in_file:
        json_data = json.load(in_file)
        return json_data


def _get_modules_per_project(
    projects: List[Dict[str, str]], default_project_path: str
) -> Dict[str, Set[str]]:
    result: Dict[str, Set[str]] = {}
    for project in projects:
        name = project["name"]
        package_name = project["package"] if "package" in project else name
        project_path = project["project_path"] if "project_path" in project else \
            default_project_path
        modules = find_modules(os.path.join(project_path, package_name))
        result[name] = modules
    return result


def _get_project_paths(
    projects: List[Dict[str, str]], default_project_path: str
) -> Dict[str, str]:
    result: Dict[str, str] = {}
    root_path = os.path.dirname(os.path.abspath(__file__))
    for project in projects:
        name = project["name"]
        project_path = project["project_path"] if "project_path" in project else \
            default_project_path
        if os.path.isabs(project_path):
            result[name] = project_path
        else:
            result[name] = os.path.join(root_path, project_path)
    return result


def _write_main_script(num_total_runs: int) -> None:
    content = [
        "#!/usr/bin/env bash",
        "# Generated automatically, DO NOT EDIT MANUALLY!",
        "",
        "SLURM_JOB_ID=0",
        "PID=$$",
        "",
        "function sig_handler {",
        "  echo \"Cancelling SLURM job...\"",
        "  if [[ \"${SLURM_JOB_ID}\" -gt 0 ]]",
        "  then",
        "    scancel \"${SLURM_JOB_ID}\"",
        "  fi",
        "  echo \"Killing ${0} including its children...\"",
        "  pkill -TERM -P ${PID}",
        "",
        "  echo -e \"Terminated: ${0}\"",
        "}",
        "trap sig_handler INT TERM HUP QUIT",
        "",
        "IFS=',' read SLURM_JOB_ID rest < <(sbatch --parsable array_job.sh)",
        "if [[ -z \"${SLURM_JOB_ID}\" ]]",
        "then",
        "  echo \"Submitting the SLURM job failed!\"",
        "  exit 1",
        "fi",
        "",
        "echo \"SLURM job with ID ${SLURM_JOB_ID} submitted!\"",
        "total=1",
        "while [[ \"${total}\" -gt 0 ]]",
        "do",
        "  pending=$(squeue --noheader --array -j \"${SLURM_JOB_ID}\" -t PD | wc -l)",
        "  running=$(squeue --noheader --array -j \"${SLURM_JOB_ID}\" -t R | wc -l)",
        "  total=$(squeue --noheader --array -j \"${SLURM_JOB_ID}\" | wc -l)",
        "  current_time=$(date)",
        f"  echo \"${{current_time}}: Job ${{SLURM_JOB_ID}}: ${{total}} runs found ("
        f"${{pending}} pending, ${{running}} running) of {num_total_runs} total "
        f"jobs.\"",
        "  if [[ \"${total}\" -gt 0 ]]",
        "  then",
        "    sleep 10",
        "  fi",
        "done",
    ]
    with open("run_cluster_job.sh", mode="w") as out_file:
        out_file.write("\n".join(content))


def _write_array_job_script(
    num_total_runs: int,
    budget: int,
    mem_limit: str,
    constraint: str,
) -> None:
    time = 2 * budget  # TODO adjust this if necessary
    content = [
        "#!/usr/bin/env bash",
        "# Generated automatically, DO NOT EDIT MANUALLY!",
        "#SBATCH --partition=anywhere",
        f"#SBATCH --constraint={constraint}",
        "#SBATCH --job-name=pynguin",
        f"#SBATCH --time=00:30:00",
        f"#SBATCH --mem={mem_limit}",
        "#SBATCH --nodes=1-1",
        "#SBATCH --ntasks=1",
        "#SBATCH --ntasks-per-socket=1",
        "#SBATCH --mem-bind=local",
        "#SBATCH --exclusive=user",
        f"#SBATCH --array=1-{num_total_runs}",
        "",
        "n=${SLURM_ARRAY_TASK_ID}",
        "",
        "function sighdl {",
        "  kill -INT \"${srunPid}\" || true",
        "}",
        "",
        "mkdir -p \"/scratch/${USER}/pynguin-runs\"",
        "OUT_FILE=\"/scratch/${USER}/pynguin-runs/${n}-out.txt\"",
        "ERR_FILE=\"/scratch/${USER}/pynguin-runs/${n}-err.txt\"",
        "",
        "srun \\",
        "  --disable-status \\",
        "  --mem-bind=local \\",
        "  --output=\"${OUT_FILE}\" \\",
        "  --error=\"${ERR_FILE}\" \\",
        "  ./run_execution-${n}.sh \\",
        "  & srunPid=$!",
        "",
        "trap sighdl INT TERM HUP QUIT",
        "",
        "while ! wait; do true; done",
    ]
    with open("array_job.sh", mode="w") as out_file:
        out_file.write("\n".join(content))


def _write_run_script(
    modules_per_project: Dict[str, Set[str]],
    configurations: List[Dict[str, Any]],
    budget: int,
    output_variables: str,
    project_paths: Dict[str, Union[str, os.PathLike]],
    docker_container_path: Union[str, os.PathLike],
    docker_container_id: str,
) -> None:
    i = 1
    for config_id, configuration in enumerate(configurations):
        for project_name, modules in modules_per_project.items():
            for module in modules:
                content = [
                    "#!/usr/bin/env bash",
                    "# Generated automatically.  DO NOT EDIT MANUALLY!",
                    "",
                    "MIN_ASSIGNED_PROCESSOR_ID=0",
                    "",
                    "LOCAL_DIR=\"/tmp/local/${USER}\"",
                    "SCRATCH_DIR=\"/tmp/${USER}\"",
                    f"SCRATCH_RESULTS_DIR=${{SCRATCH_DIR}}/pynguin-results/"
                    f"{project_name}",
                    "WORK_DIR=$(mktemp -d)", 
                    f"INPUT_DIR=\"{project_paths[project_name]}/{project_name}\"",
                    f"OUTPUT_DIR=\"${{WORK_DIR}}/pynguin-report\"",
                    "PACKAGE_DIR=\"${WORK_DIR}\"",
                    f"echo \"{project_name}\" > \"${{PACKAGE_DIR}}/package.txt\"",
                    "LOCAL_DOCKER_ROOT=\"${WORK_DIR}/docker-root-${"
                    "MIN_ASSIGNED_PROCESSOR_ID}\"",
                    f"DOCKER_IMAGE_TO_LOAD=\"{docker_container_path}/pynguin.tar\"",
                    "CWD=$(pwd)",
                    "",
                    "mkdir -p ${OUTPUT_DIR}",
                    "mkdir -p ${SCRATCH_RESULTS_DIR}",
                    "mkdir -p ${LOCAL_DOCKER_ROOT}",
                    "",
                    "cleanup () {",
                    "  rm -rf ${WORK_DIR}",
                    "}",
                    "trap cleanup INT TERM HUP QUIT",
                    "",
                    "cd \"${WORK_DIR}\" || exit",
                    "export HOME=\"${WORK_DIR}\"",
                    "",
                    "  docker run \\",
                    f"    --name=\"pynguin-{i}\" \\",
                    "    -v ${INPUT_DIR}:/input:ro \\",
                    "    -v ${OUTPUT_DIR}:/output \\",
                    "    -v ${PACKAGE_DIR}:/package:ro \\",
                    f"    pynguin:{docker_container_id} \\",
                    "      -q \\",
                    f"      --algorithm {configuration['algorithm']} \\",
                    f"      --type_inference_strategy "
                    f"{configuration['type_inference_strategy']} \\",
                    f"      --configuration_id {configuration['name']} \\",
                    "      --project_path /input \\",
                    f"      --module_name {module} \\",
                    "      --output_path /output \\",
                    f"      --budget {budget} \\",
                    f"      --output_variables {output_variables} \\",
                    f"      --constant_seeding {configuration['seeding']} \\",
                    # f"      --guess_unknown_types"
                    # f" {configuration['guess_unknown_types']} \\",
                    #"  --stopping_condition MAX_ITERATIONS \\",
                    #"  --algorithm_iterations 2500 \\",
                    "      --report_dir /output",
                    "",
                    f"mv \"${{OUTPUT_DIR}}/statistics.csv\" "
                    f"\"${{SCRATCH_RESULTS_DIR}}/statistics-{i}.csv\"",
                    "",
                    "export HOME=\"/home/${USER}\"",
                    "cd \"${CWD}\" || exit",
                    "cleanup",
                ]
                with open(f"run_execution-{i}.sh", mode="w") as out_file:
                    out_file.write("\n".join(content))
                i += 1


def _exclude_modules(
    modules: Dict[str, Set[str]], excludes: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    excludes_map = {
        mapping["project"]: mapping["modules"] for mapping in excludes
    }
    result = {}
    for project, module_names in modules.items():
        if project in excludes_map:
            result[project] = {e for e in module_names if e not in excludes_map[project]}
        else:
            result[project] = module_names
    return result


def main(args: List[str]) -> int:
    if len(args) < 1:
        _print_red("Wrong parameter count")
        return -1
    config = _arg_parser().parse_args(args[1:])
    if config.debug:
        global DEBUG
        DEBUG = True
    json_data = _parse_json(config.experiments)
    modules_per_project = _exclude_modules(
        _get_modules_per_project(
            json_data["projects"], json_data["project_path"]
        ),
        json_data["exclude"]
    )
    configurations = json_data["configurations"]
    budget = int(json_data["budget"])
    mem_limit = json_data["mem_limit"] if "mem_limit" in json_data else "4GB"
    constraint = json_data["constraint"]
    docker_container_path = json_data["docker_container_path"]
    docker_container_id = json_data["docker_container_id"]
    output_variables = json_data["output_variables"]
    project_paths = _get_project_paths(json_data["projects"], json_data["project_path"])
    number_of_modules = sum([len(modules) for modules in modules_per_project.values()])
    number_of_configurations = len(configurations)

    _write_main_script(number_of_configurations * number_of_modules)
    _write_array_job_script(
        number_of_configurations * number_of_modules,
        budget,
        mem_limit,
        constraint,
    )
    _write_run_script(
        modules_per_project,
        configurations,
        budget,
        output_variables,
        project_paths,
        docker_container_path,
        docker_container_id,
    )

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
