echo "export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export LANGUAGE=C.UTF-8" >> ~/.bashrc
source ~/.bashrc
alias python=python3
alias pip=pip3
cd ./pip
pip3 install *
rm -f *
cd ..

apt update && apt install -y libsm6 libxext6  libxrender1 libfontconfig1
pip3 install -r req.txt
cd detect/utils/bbox
rm  -f bbox.cpython-37m-x86_64-linux-gnu.so
rm -f nms.cpython-37m-x86_64-linux-gnu.so
chmod +x make.sh
./make.sh
