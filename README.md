# 安装 - make all 前的准备

```bash
docker pull opennetlab.azurecr.io/alphartc
docker image tag opennetlab.azurecr.io/alphartc alphartc
git clone https://github.com/OpenNetLab/AlphaRTC.git
```

在 `make all` 之前要做如下准备：

修改 `AlphaRTC/dockers/Dockerfile.compile` 中的 `RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git ${DEPOT_TOOLS}` 变成

```bash
git clone -b chrome/3865 https://chromium.googlesource.com/chromium/tools/depot_tools.git
```

一定要

```bash
git config --global user.name "John Doe"
git config --global user.email "jdoe@email.com"
git config --global core.autocrlf false
git config --global core.filemode false
```

之后再 `make all`。



# 视频操作

## 预处理

从最大的 mygo 视频，需要用 ffmpeg 调整成别的尺寸的视频，然后再用下面的命令变成 YUV。

如果需要截取一段，就需要添加形如 `--ss 00:00:10 -t 00:00:20`，表示开始时间，和**持续**时间。

视频是用 YUV 格式进行传输的。这是一种需要宽高数据的格式（https://bbs.huaweicloud.com/blogs/362969 ）。如果在 vscode 中直接查看 YUV 格式的文件，可以使用 Yuv Viewer，命令是 ```Set chroma subsampling```, ```Set width```, ```Set height```。

参照 https://blog.csdn.net/kl1411/article/details/121701003 对 YUV 和 mp4 之间进行转换。

mp4 -> YUV
```bash
ffmpeg -threads 16 -i input.mp4 -vf pp=lb -vsync 0 -pix_fmt yuv420p output.yuv
```

**注意**：必须要同时取出音频。音频的时长**必须**和视频一样。

mp4 -> wav
```bash
ffmpeg -i input.mp4 output.wav
```

YUV -> mp4
```bash
ffmpeg -threads 16 -f rawvideo -r 25 -s 320x240 -pix_fmt yuv420p -i input.yuv -c:v libx264 -preset fast -crf 18 output.mp4
```
- ```-r -25```：帧率25
- ```-s 320x240```：分辨率
- ```-crf 18```：设置常量速率因子(CRF)为18，CRF值越低，输出视频质量越高。

## 安装 vmaf + ffmpeg

Step 1. 按照（https://github.com/Netflix/vmaf/blob/master/libvmaf/README.md）先安装 `libvmaf`。

Step 2. 按照（https://github.com/Netflix/vmaf/blob/master/resource/doc/ffmpeg.md）安装 `ffmpeg+libvmaf`。其中需要注意，需要先下载 ffmpeg 的源码，再在 ffmpeg 的文件夹下输入命令：

```bash
./configure --enable-libvmaf
make -j4
make install
```

**`test.py`** 做的就是 ffmpeg+vmaf 命令行处理，里面可能会有文件路径的错误，修改开头 `parser.add_argument` 中的内容可以解决。一定要让文件夹结构是这样的：

```
make sure layout is like this:
-----------
|
|--- AlphaRTC/
|
|--- test.py
```

# 运行方式

## json 文件修改

先修改位于 `/AlphaRTC/examples/peerconnection/serverless/corpus` 中的 json 文件，`autoclose`, `height`, `width`, `fps` 都需要修改，根据视频的格式修改。

## 运行

```bash
chmod +x text.sh
python3 -m pip install virtualenv
python3 -m virtualenv .venv
source .venv/bin/activate
pip3 install -r requirementx.txt
```

再执行下述命令进行传输：

```bash
rm ./AlphaRTC/examples/peerconnection/serverless/corpus
sudo docker run -d --rm -v `pwd`/examples/peerconnection/serverless/corpus:/app -w /app --name alphartc alphartc peerconnection_serverless receiver.json
sudo docker exec alphartc peerconnection_serverless sender.json
```

传输完毕之后，

```bash
./test.sh
```


