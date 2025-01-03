import struct
import argparse

def modify_mp4_duration(input_file, output_file, new_duration):
    """
    修改 MP4 文件 mvhd atom 的 duration 值，并保存修改后的内容。

    Args:
        input_file: 输入 MP4 文件路径。
        output_file: 输出 MP4 文件路径。
        new_duration: 新的 duration 值（以秒为单位）。
    """
    def read_int(data, offset, size):
        if size == 4:
            return struct.unpack(">I", data[offset:offset+4])[0]
        elif size == 8:
            return struct.unpack(">Q", data[offset:offset+8])[0]
        raise ValueError("Unsupported integer size")

    def write_int(data, offset, size, value):
        if size == 4:
            return data[:offset] + struct.pack(">I", value) + data[offset+4:]
        elif size == 8:
            return data[:offset] + struct.pack(">Q", value) + data[offset+8:]
        raise ValueError("Unsupported integer size")

    try:
        # 读取原始文件数据
        with open(input_file, "rb") as f:
            data = f.read()

        mvhd_offset = data.find(b"mvhd")
        if mvhd_offset == -1:
            raise ValueError("未找到 mvhd atom")

        version = data[mvhd_offset + 4]
        
        if version not in (0, 1):
            raise ValueError("Unsupported mvhd version")

        duration_offset = mvhd_offset + (20 if version == 0 else 28)
        time_scale_offset = mvhd_offset + (16 if version == 0 else 24)

        time_scale = read_int(data, time_scale_offset, 4)
        old_duration = read_int(data, duration_offset, 8 if version == 1 else 4)

        print(f"mvhd time_scale: {time_scale}, old duration: {old_duration}, time:{old_duration/time_scale} s")

        new_duration_value = int(time_scale * new_duration)
        modified_data = write_int(data, duration_offset, 8 if version == 1 else 4, new_duration_value)
        
        print(f"=>new duration: {new_duration_value}, modified time: {new_duration} s")
        print("----------")

        # 修改 mdhd boxes
        search_start = 0
        while True:
            mdhd_pos = data.find(b"mdhd", search_start)
            if mdhd_pos == -1:
                break

            mdhd_version = data[mdhd_pos + 4]
            time_scale_offset = mdhd_pos + (16 if mdhd_version == 0 else 24)
            duration_offset = mdhd_pos + (20 if mdhd_version == 0 else 28)

            track_time_scale = read_int(data, time_scale_offset, 4)
            track_old_duration = read_int(data, duration_offset, 8 if version == 1 else 4)
            print(f"mdhd time_scale: {track_time_scale}, old duration: {track_old_duration}, time:{track_old_duration/track_time_scale} s")

            track_new_duration = int(track_time_scale * new_duration)
            modified_data = write_int(modified_data, duration_offset, 8 if mdhd_version == 1 else 4, track_new_duration)
            print(f"=>new duration: {track_new_duration}, modified time: {new_duration} s")
            print("----------")

            search_start = mdhd_pos + 1


        # 保存修改后的数据
        with open(output_file, "wb") as f_out:
            f_out.write(modified_data)
        print()
        print(f"The modified file has been saved in: {output_file}")

    except (FileNotFoundError, ValueError, struct.error) as e:
        print(f"FileNotFoundError: {e}")
    except Exception as e:
        print(f"An unknown error occurred: {e}")

# analyze_mp4(input_file)
input_mp4 = "C:/Users/Administrator/Desktop/example.mp4"  # 替换为你的输入文件
output_mp4 = "C:/Users/Administrator/Desktop/output.mp4" # 替换为你的输出文件
new_duration = 60  # 替换为你的新时长 (秒)



def main():
    parser = argparse.ArgumentParser(description="Fake mp4 video duration")
    parser.add_argument("input_file", help="Input the MP4 file path")
    parser.add_argument("output_file", help="Output the MP4 file path")
    parser.add_argument("new_duration", type=float, help="New Video Length (seconds)")

    args = parser.parse_args()

    modify_mp4_duration(args.input_file, args.output_file, args.new_duration)

if __name__ == "__main__":
    main()




