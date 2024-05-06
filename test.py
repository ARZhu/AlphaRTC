import subprocess
import argparse
import sys
import json
import os

parser = argparse.ArgumentParser(description="A program that tests yuv videos by vmaf.")

parser.add_argument("-m", "--mode",
                    help="Estimator mode: PyInfer or ONNXInfer",
                    type=str,
                    default="ONNXInfer")

parser.add_argument("-t", "--test-path",
                    help="Path for test data",
                    type=str,
                    default="./test_data/")

# This for compile from scratch
# parser.add_argument("-s", "--source-path",
#                     help="Path for source data which the previous lab has generated",
#                     type=str,
#                     default="./AlphaRTC/rundir/runtime/")

parser.add_argument("-s", "--source-path",
                    help="Path for source data which the previous lab has generated",
                    type=str,
                    default="./AlphaRTC/examples/peerconnection/serverless/corpus")

parser.add_argument("-o", "--output-path",
                    help="Path for output data of vmaf",
                    type=str,
                    default="output.json")

parser.add_argument("--format",
                    help="Format for yuv videos, options are yuv420p/yuv422p/yuv444p",
                    type=str,
                    default="yuv420p")

parser.add_argument("---out-fmt",
                    help="Output format can be one of: text/xml/json",
                    type=str,
                    default="json")


def runcmd(command):
    ret = subprocess.run(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=30)
    if ret.returncode == 0:
        print("success:",ret)
    else:
        print("error:",ret)
        sys.exit(ret.returncode)


def Run_vmaf(fmt, height, width, fps, reference_path, distorted_path, output_format, output_path):
    command = [
        "ffmpeg", 
        
        # "-video_size", f"{width}x{height}", 
        # "-r", str(fps),
        # "-pixel_format", fmt,
        "-i", distorted_path,

        "-video_size", f"{width}x{height}", 
        "-r", str(fps),
        "-pixel_format", fmt,
        "-i", reference_path,

        "-lavfi",
        f"libvmaf=log_fmt={output_format}:log_path=/dev/stdout",
        "-f", "null", "-"
    ]
    # ffmpeg -video_size 640x480 -r 24 -pixel_format yuv420p -i ./test_data/outvideo.yuv 
    # -video_size 640x480 -r 24 -pixel_format yuv420p -i ./test_data/testmedia/test.yuv 
    # -lavfi libvmaf=log_fmt=json:log_path=output.json -f null -

    # Old version ↓
    # command = [
    #     './python/vmaf/script/run_vmaf.py',
    #     fmt,
    #     str(width),
    #     str(height),
    #     reference_path,
    #     distorted_path,
    #     '--out-fmt',
    #     output_format,
    # ]    
    # PYTHONPATH=python ./python/vmaf/script/run_vmaf.py yuv420p 640 480 ./test_data/testmedia/test.yuv ./test_data/outvideo.yuv
    # vmaf -p 420 -w 640 -h 480 -b 8  -r ./test_data/testmedia/test.yuv -d ./test_data/outvideo.yuv



    ret = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if ret.returncode == 0:
        try:
            output_json = json.loads(ret.stdout)
            with open(output_path, 'w') as f:
                json.dump(output_json, f, indent=4)
            
            print("Json file has been written.")
        except json.JSONDecodeError:
            print("The output of vmaf is not json.")
    else:
        print("error:",ret)
        sys.exit(ret.returncode)


args = parser.parse_args()

# Copy the videos from the lab of Video Transmission
runcmd("mkdir -p " + args.test_path)
runcmd("cp -r "+ args.source_path.rstrip('/')+"/* " + args.test_path)

# For handling both ./test/ and ./test
test_path = args.test_path.rstrip('/')+"/"

if args.mode == "ONNXInfer":
    print(args.mode)
    with open(test_path + "sender.json", 'r') as file:
        sender_json = json.load(file)
    with open(test_path + "receiver.json", 'r') as file:
        receiver_json = json.load(file)
    enabled, height, width, fps, reference_file_path = sender_json["video_source"]["video_file"].values()
    print(height)
    print(width)
    distorted_file_path = receiver_json["save_to_file"]["video"]["file_path"]
    reference_path = test_path + reference_file_path
    distorted_path = test_path + distorted_file_path

    runcmd(f"ffmpeg -y -r {fps} -i {distorted_path} -vf scale=in_range=limited:out_range=full \
        -color_range 2 -pix_fmt {args.format} {test_path}outvideo.mp4")
    runcmd(f"ffmpeg -y -i {test_path}outvideo.mp4 -i {test_path}outaudio.wav \
        -c:v copy -c:a aac -shortest {test_path}output.mp4")
    
    Run_vmaf(
        fmt=args.format, 
        height=height, 
        width=width, 
        fps=fps,
        reference_path=reference_path, 
        distorted_path=distorted_path,
        output_format=args.out_fmt,
        output_path=args.output_path
    )
    
    
