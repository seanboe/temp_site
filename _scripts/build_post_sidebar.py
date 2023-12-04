import os
import markdown
import re


def get_line_level(line):
  header = re.findall(r"<h\d>", line)

  if len(header) > 1:
    raise ValueError("More than one start header tag")

  if len(header) == 0:
    return 0
  else:
    header = header[0]
    return int(header[header.find("h") + 1])


for post_file in os.listdir(os.getcwd() + "/_posts/"):

  # post_file_string = post_file[post_file.find(next(filter(str.isalpha, post_file))):post_file.find(".")]
  if post_file == ".DS_Store" or post_file == "_site":
    continue

  with open(f"_posts/{post_file}", "r") as post:

    lines = post.readlines()

    post_start_index = 0
    post_title = ""
    for index, line in enumerate(lines):
      if index > 1:
        if line.find("title:") >= 0:
          post_title = line[line.find("title:") + len("title:") + 1:].strip().strip("\"")
          post_title = post_title.lower().replace(" ", "-")
        if line.find("---") >= 0:
          post_start_index = index + 1
          break

    all_headers = []
    depth = 1     # 1 indexed to match h1, h2, etc.
    headers = """toc:\n"""
    within_code = False

    for line in range(post_start_index, len(lines)):
      html = markdown.markdown(lines[line])

      line_level = get_line_level(html)
      if line_level == 0 or line_level > 3:
        if re.findall("```", html) or re.findall("{% highlight", html) or re.findall("{% endhighlight %}", html):
          within_code = not within_code
      elif not within_code:
        header_title = re.findall("<h\d>(.*?)<\/h\d>", html)[0]

        # if abs(2 * line_level - depth) > 1:
        #   # Dump if it doesn't follow on the hierarchy
        #   continue
      
        if line_level > depth:
            headers += (depth) * "    " + "subsections:\n"
            depth += 1
        elif line_level < depth:
          depth -= 1

        headers += (depth - 1) * "    " + f"  - title: \"{header_title}\"\n"


    with open(f"_data/post_toc/{post_title}.yaml", "w") as toc:
      toc.write(headers)

print("Finished building sidebars")
