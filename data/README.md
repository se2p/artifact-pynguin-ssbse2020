# Automated Unit Test Generation for Python—Experiments

This archive contains the used projects, the raw result data, and the Jupyter
Notebook used for evaluation of our work

“Automated Unit Test Generation for Python”

accepted at the 12th Symposium for Search-Based Software Engineering (SSBSE
2020), October 7–8, 2020, Bari, Italy.

If you use the [`poetry`](https://python-poetry.org) tool, you can install all
necessary dependencies and run Jupyter easily.

The `projects` folder contains the used subject systems in the versions
mentioned in the paper.
The `data` folder contains the raw data CSV files.
The `notebooks` folder contains the Jupyter notebook used for evaluation.
If you want to rerun this notebook on your system, you need to adjust the
variable `PAPER_EXPORT_PATH` in the fourth cell.

The experiment scripts in the root folder are built for the cluster system
(using the SLURM job management tool) of our chair.  You'll need to adapt this
to your computation environment to rerun the experiments.

In case of questions feel free to send us an email, we are happy to help you.
