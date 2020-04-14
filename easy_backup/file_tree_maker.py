import os
import argparse
import time


def sizeof_fmt(num, suffix='B'):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Unit suffix (optionnal) default = B
    :type suffix: str
    :rtype: str
    """
    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


#https://stackoverflow.com/questions/16953842/using-os-walk-to-recursively-traverse-directories-in-python@32656429
class FileTreeMaker(object):

    def _recurse(self, parent_path, file_list, prefix, output_buf, level):
        if len(file_list) == 0 \
            or (self.max_level != -1 and self.max_level <= level):
            return
        else:
            file_list.sort(key=lambda f: os.path.isfile(os.path.join(parent_path, f)))
            for idx, sub_path in enumerate(file_list):
                if any(exclude_name in sub_path for exclude_name in self.exn):
                    continue

                full_path = os.path.join(parent_path, sub_path)
                idc = "┣━"
                if idx == len(file_list) - 1:
                    idc = "┗━"

                if os.path.isdir(full_path) and sub_path not in self.exf:
                    output_buf.append("%s%s[%s]" % (prefix, idc, sub_path))
                    if len(file_list) > 1 and idx != len(file_list) - 1:
                        tmp_prefix = prefix + "┃  "
                    else:
                        tmp_prefix = prefix + "    "
                    self._recurse(full_path, os.listdir(full_path), tmp_prefix, output_buf, level + 1)
                elif os.path.isfile(full_path):
                    file_size = sizeof_fmt(os.path.getsize(full_path))
                    output_buf.append("%s%s%s (%s)" % (prefix, idc, sub_path, file_size))

    def make(self, root):
        self.root = root
        self.exf = []
        self.exn = []
        self.max_level = -1

        print("root:%s" % self.root)

        buf = []
        path_parts = self.root.rsplit(os.path.sep, 1)
        buf.append("[%s]" % (path_parts[-1],))
        self._recurse(self.root, os.listdir(self.root), "", buf, 0)

        return "\n".join(buf)

#         output_str = "\n".join(buf)
#         if len(args.output) != 0:
#             with open(args.output, 'w') as of:
#                 of.write(output_str)
#         return output_str

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-r", "--root", help="root of file tree", default=".")
#     parser.add_argument("-o", "--output", help="output file name", default="")
#     parser.add_argument("-xf", "--exclude_folder", nargs='*', help="exclude folder", default=[])
#     parser.add_argument("-xn", "--exclude_name", nargs='*', help="exclude name", default=[])
#     parser.add_argument("-m", "--max_level", help="max level",
#                         type=int, default=-1)
#     args = parser.parse_args()
#     print(FileTreeMaker().make(args))
# you will get this:

# root:.
# [.]
# ┣━[.idea]
# ┃  ┣━[scopes]
# ┃  ┃  ┗━scope_settings.xml
# ┃  ┣━.name
# ┃  ┣━Demo.iml
# ┃  ┣━encodings.xml
# ┃  ┣━misc.xml
# ┃  ┣━modules.xml
# ┃  ┣━vcs.xml
# ┃  ┗━workspace.xml
# ┣━[test1]
# ┃  ┗━test1.txt
# ┣━[test2]
# ┃  ┣━[test2-2]
# ┃  ┃  ┗━[test2-3]
# ┃  ┃      ┣━test2
# ┃  ┃      ┗━test2-3-1
# ┃  ┗━test2
# ┣━folder_tree_maker.py
# ┗━tree.py
# shareeditfollowflag
# edited Sep 19 '15 at 12:20
# answered Sep 18 '15 at 16:01

# legendmohe
# 51444 silver badges99 bronze badges

# Hi there, I really love your script, but its a bit too complicated for the project I am working on, is there any chance I could have it as one small function, with only the -r argument present? – jeff_h Jan 16 '17 at 12:11

# how to print it in a .txt? I tried print(FileTreeMaker().make(args),file=tree) but it gives me 'charmap' codec can't encode characters in position 17-21: character maps to <undefined> – Luis Felipe Mar 24 '17 at 14:28

# what is idc stand for – voices Nov 6 '19 at 14:16

# I wrote something similar with os.listdir() too. Yours is much better; I couldn't get the recursion right, it only worked 2 or 3 layers deep. In the end I decided to try again from scratch with os.walk() instead, which I thought would be far more suitable. I'm surprised you didn't use it at all here. – voices Nov 6 '19 at 14:32
# add a comment

