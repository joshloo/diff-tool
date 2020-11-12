# FILE:
diff_tool.py

# How to run:
To diff pass log vs fail log of last n lines. in below case, n = 10

diff_tool.py pass.log fail.log -n 10

# DESCRIPTION:
This program shows the difference between two files.
It is scaled to enhance issue triage of different components in BIOS/Linux
    
From the blog post: [Create your own diff tool using python post](https://florian-dahlitz.de/blog/create-your-own-diff-tool-using-python)