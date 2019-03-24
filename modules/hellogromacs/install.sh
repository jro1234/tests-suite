#!/bin/bash

# Current Environment Strategy:
#     OpenMM in the root conda from fresh
#     download of PPC64le Miniconda version
#

echo "-------------------------------------------------"
echo "------- Installing GROMACS Test Platform --------"
echo ""
echo ""

# CONFIGURATION:
CWD="$(pwd)"
INSTALL_NAME="tests-gromacs"
#INSTALL_HOME="/gpfs/alpine/proj-shared/bif112/"
INSTALL_HOME="/ccs/proj/bif112/tests-summit/$INSTALL_NAME"
SHPROFILE="$INSTALL_HOME/testrc.bash"

# CREATE PLATFORM SPACE:
# Software Directory
mkdir -p $INSTALL_HOME

echo "export TESTS_HOME=\"$INSTALL_HOME\"" >> $SHPROFILE

cd "$CWD"
cp -r tests             $INSTALL_HOME
cp -r ../../joblauncher $INSTALL_HOME
cp ../../testtools*          $INSTALL_HOME/tests
cp ../../mdsystems/gromacs/* $INSTALL_HOME/tests

echo "export PATH=\"$INSTALL_HOME/joblauncher:\$PATH\"" >> $SHPROFILE

source $SHPROFILE

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
