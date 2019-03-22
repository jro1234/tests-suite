#!/bin/bash

# Current Environment Strategy:
#     OpenMM in the root conda from fresh
#     download of PPC64le Miniconda version
#
# PACKAGES: radical.utils, saga-python, radical.pilot

echo "-------------------------------------------------"
echo "-------- Installing OpenMM Test Platform --------"
echo ""
echo ""

# CONFIGURATION:
CWD="$(pwd)"
INSTALL_NAME="tests-openmm"
INSTALL_HOME="$PROJWORK/bif112/tests-summit/$INSTALL_NAME"
#INSTALL_HOME="/gpfs/alpine/proj-shared/bif112/"
#INSTALL_HOME="/ccs/proj/bif112/"
SHPROFILE="$INSTALL_HOME/.testrc"
CONDA_VERSION="Miniconda2-latest-Linux-ppc64le.sh"

# SETUP:
PKG_HOME="$INSTALL_HOME/packages"
TEST_HOME="$INSTALL_HOME/tests"

# CREATE PLATFORM SPACE:
# Software Directory
mkdir -p $INSTALL_HOME
mkdir $PKG_HOME

# Tests Directory
mkdir $TEST_HOME

# Use CONDA
cd $INSTALL_HOME
wget "https://repo.continuum.io/miniconda/$CONDA_VERSION"
bash "$CONDA_VERSION" -b -p miniconda
rm "$CONDA_VERSION"
touch $SHPROFILE
echo "export CONDA=\"$INSTALL_HOME/miniconda\"" >> $SHPROFILE
echo "export PATH=\"\$CONDA/bin:\$PATH\"" >> $SHPROFILE
source $SHPROFILE
conda config --add channels omnia --add channels conda-forge
conda update --yes --all

# THE MAGIC line
conda install --yes -c omnia-dev/label/cuda92 openmm

echo "export TESTS_HOME=\"$INSTALL_HOME\"" >> $SHPROFILE
source $SHPROFILE

# Just import openmm
python -c "from simtk import openmm"

cd "$CWD"
cp -r tests $INSTALL_HOME
cp ../ttools.py $INSTALL_HOME/tests

echo ""
echo "-------------------------------------------------"
echo "-------------   Install is Done    --------------"
echo ""
echo "Where the tests live:"
echo ""
echo " $  echo \$TESTS_HOME"
echo " $TESTS_HOME"
echo ""
echo "To use test python, load the profile that adds"
echo "Python environment to PATH"
echo ""
echo " $  source $SHPROFILE"
echo ""
echo "Go to tests directory"
echo " $  cd $INSTALL_HOME/tests"
echo ""
echo "-------------------------------------------------"
echo "-------------------------------------------------"
