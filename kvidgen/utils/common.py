import json
import subprocess


def split_text(text):
    # 如果文本长度小于280个汉字，直接返回
    if len(text) <= 280:
        return [text]

    # 定义切分符号的优先级，优先使用换行符，其次句号，再其次逗号等
    split_chars = ["\n\r", "\n", "。"]

    # 初始化结果列表
    result = []
    # 初始化当前段落
    current_paragraph = ""

    # 遍历文本中的每个字符
    for char in text:
        # 将字符添加到当前段落
        current_paragraph += char

        # 如果当前段落长度超过280个汉字
        if len(current_paragraph) > 280:
            # 从切分符号中找到当前段落中最后一个出现的符号
            last_split_char = None
            last_split_char_index = -1
            for split_char in split_chars:
                index = current_paragraph.rfind(split_char)
                if index != -1 and index > last_split_char_index:
                    last_split_char = split_char
                    last_split_char_index = index

            # 如果找到了切分符号
            if last_split_char is not None:
                # 将当前段落从切分符号处切分为两部分
                paragraph_part1 = current_paragraph[: last_split_char_index + 1]
                paragraph_part2 = current_paragraph[last_split_char_index + 1 :]

                # 将第一部分添加到结果列表
                result.append(paragraph_part1)

                # 将第二部分作为新的当前段落继续处理
                current_paragraph = paragraph_part2
            else:
                # 如果没有找到合适的切分符号，说明当前段落中没有合适的切分点
                # 可以考虑将当前段落截断，或者根据实际情况进行其他处理
                # 这里简单地将当前段落截断为前280个字符，剩余部分继续处理
                result.append(current_paragraph[:280])
                current_paragraph = current_paragraph[280:]

    # 将最后一段添加到结果列表
    if current_paragraph:
        result.append(current_paragraph)

    return result


def get_audio_duration(file_path):
    command = [
        "ffprobe",
        "-i",
        file_path,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-of",
        "json",
    ]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])
