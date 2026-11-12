# swot_miz_eddy

Model, dataset, tools and scripts for the automated detection and analysis of ocean eddies in the
marginal ice zone (MIZ) from SWOT Level-2 KaRIn L2_LR_SSH (version D) data.

## Installation

**Python ≥ 3.10** is required. Create the environment and install this package into it with pip. Conda is recommended (for gdal installation).

```bash
git clone https://github.com/Galasnow/swot_miz_eddy.git
cd swot_miz_eddy

# 1. environment with GDAL (python 3.12; any version >= 3.10)
conda create -n swot-miz-eddy python=3.12
conda activate swot-miz-eddy
conda install gdal

# 2. this package: editable for development, plain install otherwise
pip install -e .
# or: uv pip install -e .
```

Check that the package resolves:

```bash
python -c "import swot_miz_eddy; print(swot_miz_eddy.__version__)"
# 0.1.0
```
