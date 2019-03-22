#!/bin/bash

# Current Environment Strategy:
#     Virtualenv over the root conda from fresh
#     download of PPC64le Miniconda version
#
# PACKAGES: radical.utils, saga-python, radical.pilot

echo "-------------------------------------------------"
echo "---------- Installing RP Test Platform ----------"
echo ""
echo "If you are using Summit or a PowerPC architecture"
echo "you will have to modify this setup to provide some"
echo "mechanism of getting MongoDB compatible with the"
echo "hardware, or tunneling to off-site instance."
echo "Mongo for PowerPC has a restrictive license and"
echo "cannot be downloaded with with a command."
echo ""
sleep 10

# CONFIGURATION:
CWD="$(pwd)"
INSTALL_NAME="tests-rp"
INSTALL_HOME="$PROJWORK/bif112/tests-summit/$INSTALL_NAME"
#INSTALL_HOME="/gpfs/alpine/proj-shared/bif112/"
#INSTALL_HOME="/ccs/proj/bif112/"
SHPROFILE="$INSTALL_HOME/.testrc"
MONGO_VERSION="mongodb-linux-x86_64-3.6.11"
CONDA_VERSION="Miniconda2-latest-Linux-ppc64le.sh"
#DATA_DRIVE="/gpfs/alpine/proj-shared/bif112/$USER"

# SETUP:
ENV_HOME="$INSTALL_HOME/virtualenv"
PKG_HOME="$INSTALL_HOME/packages"
TEST_HOME="$INSTALL_HOME/tests"
#DATA_HOME="$DATA_DRIVE/$INSTALL_NAME"

# CREATE PLATFORM SPACE:
# Software Directory
mkdir -p $INSTALL_HOME
mkdir $PKG_HOME

# Tests Directory
#mkdir -p $DATA_HOME
mkdir $TEST_HOME

# MongoDB
cd $INSTALL_HOME
if [ -z "$(command -v mongod)" ]; then
  wget "https://fastdl.mongodb.org/linux/${MONGO_VERSION}.tgz"
  tar -zxvf ${MONGO_VERSION}.tgz
  mkdir mongodb
  mv $MONGO_VERSION mongodb
  rm ${MONGO_VERSION}.tgz
  echo "export PATH=\"$INSTALL_HOME/mongodb/$MONGO_VERSION/bin:\$PATH\"" >> $SHPROFILE
fi

# Use CONDA
cd $INSTALL_HOME
if [ -z "$(command -v conda)" ]; then
  wget "https://repo.continuum.io/miniconda/$CONDA_VERSION"
  bash "$CONDA_VERSION" -b -p miniconda
  rm "$CONDA_VERSION"
  touch $SHPROFILE
  echo "export CONDA=\"$INSTALL_HOME/miniconda\"" >> $SHPROFILE
  echo "export PATH=\"\$CONDA/bin:\$PATH\"" >> $SHPROFILE
  source $SHPROFILE
  conda config --add channels omnia --add channels conda-forge
  conda update --yes --all
  conda install -y virtualenv
fi

# Create the virtualenv home for RP
virtualenv $ENV_HOME
echo "export ENV_ACTIVATE=\"$ENV_HOME/bin/activate\"" >> $SHPROFILE
source $SHPROFILE
source $ENV_ACTIVATE

# Install RP Packages
# TODO whenever pip installs just work...
#pip install radical.utils
#pip install saga-python

cd $PKG_HOME
git clone https://github.com/radical-cybertools/radical.utils
cd radical.utils
pip install .

cd $PKG_HOME
git clone https://github.com/radical-cybertools/saga-python
cd saga-python
pip install .

cd $PKG_HOME
echo ""
echo "-------------------------------------"
echo "-- THIS WILL FAIL (as of 03-20-19) --"
echo ""
echo "Radical Pilot setup file has wrong"
echo "name for radical saga package"
echo " --> doign this before pip install"
echo " $  sed -i 's/saga-python/radical.saga/g' setup.py"
echo ""
echo "------------------------------------"
echo ""
git clone https://github.com/radical-cybertools/radical.pilot
git checkout fix/issue_1830
cd radical.pilot
sed -i 's/saga-python/radical.saga/g' setup.py
pip install .

echo "export RADICAL_PILOT_DBURL=\"mongodb://0.0.0.0:27017/rp\"" >> $SHPROFILE
echo "export RADICAL_SAGA_PTY_VERBOSE=\"DEBUG\"" >> $SHPROFILE
echo "export RADICAL_VERBOSE=\"DEBUG\"" >> $SHPROFILE
echo "export RADICAL_PILOT_PROFILE=\"True\"" >> $SHPROFILE
echo "export RADICAL_PROFILE=\"True\"" >> $SHPROFILE
echo "export TESTS_HOME=\"$INSTALL_HOME\"" >> $SHPROFILE

cd "$CWD"
cp -r tests $INSTALL_HOME
cp ../ttools.py $INSTALL_HOME/tests
cp -r ../hellogpu $INSTALL_HOME
cd $INSTALL_HOME/hellogpu
./install.sh
cd "$CWD"

echo ""
echo "-------------------------------------------------"
echo "-------------   Install is Done    --------------"
echo ""
echo "Where the tests live:"
echo ""
echo " $  echo \$TESTS_HOME"
echo " $TESTS_HOME"
echo ""
echo "To read environment profile, use"
echo ""
echo " $  source $SHPROFILE"
echo ""
echo "and to activate Python environment"
echo "with test stack installed, use"
echo ""
echo " $  source \$ENV_ACTIVATE"
echo ""
echo "Go to tests directory"
echo " $  cd $INSTALL_HOME/tests"
echo ""
echo "-------------------------------------------------"
echo "-------------------------------------------------"
