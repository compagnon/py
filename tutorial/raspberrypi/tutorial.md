installer raspberrypi os lite ( debian arm64
avec raspberry pi imager

maj debian

sudo apt-get update
sudo apt -y upgrade

sudo apt-get install zlib1g-dev
sudo apt install -y libssl-dev python3-zarr python3-zstandard

verification de la lib zlib (mlibrairie non disponible  cf get-pip.py)

Ensure zlib is installed . By default it will be installed in /usr/lib

ls /usr/lib/libz.*

https://www.zlib.net/
wget https://www.zlib.net/zlib-1.3.1.tar.gz
tar xzf zlib-1.3.1.tar.gz
cd zlib-1.3.1
./configure --prefix=/usr/local
make
sudo make install

maj python 3 via ssh
python -V


https://help.hostry.com/knowledge-base/how-do-i-upgrade-my-python-on-debian/

Python 3.11.2

 cd ~
wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz
tar xzf Python-3.12.1.tgz

Edit /Module/Setup by uncommenting the line below "#zlib zlibmodule.c -I
 
compile the Python source
./configure => fonctionne

./configure --enable-optimizations --with-zlib-dir=/usr/local/lib



his is followed by the installation of your Python. Use the following command:
sudo make altinstall


Update your PIP
An important step for this update is to update your pip.

/usr/local/bin/python3.9 -m pip install --upgrade pip


sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.12 1


sudo update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.12 1


pip install datasets


____________________________
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo apt-get install build-essential python-dev python-setuptools python-pip python-smbus
sudo apt-get install libncursesw5-dev libgdbm-dev libc6-dev
sudo apt-get install zlib1g-dev libsqlite3-dev tk-dev
sudo apt-get install libssl-dev openssl
sudo apt-get install libffi-dev
sudo apt-get install libbz2-dev
sudo apt-get install lzma
sudo apt-get install liblzma-dev

./configure && sudo make altinstall