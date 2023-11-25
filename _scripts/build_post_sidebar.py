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

        if abs(line_level - depth) > 1:
          # Dump if it doesn't follow on the hierarchy
          continue

        headers += depth * "  " + f"- title: {header_title}\n"
      
    print(headers)


    with open(f"_data/post_toc/{post_title}.yaml", "w") as toc:
      toc.write(headers)


    #     print(header_title)

    #     if len(all_headers) == 0:
    #       all_headers.append(header_title)
    #     elif line_level == depth:
          
    #       # Append based on depth
    #       if depth == 1:
    #         all_headers.append(header_title)
    #       elif depth == 2:
    #         all_headers[-1].append(header_title)
    #       elif depth == 3:
    #         all_headers[-1][-1].append(header_title)

    #     elif line_level < depth:
          
    #       # Append based on depth
    #       if depth == 2:
    #         all_headers.append(header_title)
    #       elif depth == 3:
    #         all_headers[-1].append(header_title)
          
    #       depth -= 1

    #     elif line_level - 1 == depth:

    #       # Append based on depth
    #       if depth == 2:
    #         all_headers.append([header_title])
    #       elif depth == 3:
    #         all_headers[-1].append([header_title])
          
    #       depth += 1
    
    # print(all_headers)





    # post.readline()
    # post.readline()
    # title_line = post.readline()
    # title = title_line[title_line.find('"') + 1:title_line.find('"', title_line.find('"') + 1)]
    # title = title.lower().replace(" ", "-")

    # with open(f"_data/post_toc/{title}.yaml", "w") as toc:
    #   toc.write("toc:\n")

    #   prev_header_level = 0
    #   prev_header_exists = False
    #   within_code = False
    #   for line in post:
    #     yaml_output = ""
    #     header_level = find_letter(line)
    #     if line[0:2] == "{%" or line[0:3] == "```":
    #       within_code = not within_code
    #       if "burning" in title:
    #         print("in code")
    #         print(line, within_code)

    #     if within_code:
    #       continue
    #     if header_level == 0:
    #       continue

        
    #     # The correct way to do this is to refer to the previous header level so that everything is relative;
    #     # I have not done this to force myself to use the headers in order (you should really be styling the headers)
    #     # Independently instead of switching to different header vlaues to satisfy what you want) and because I am lazy and dont
    #     # Want to implement it now. 
    #     heading = line.strip("#").strip(" ")
    #     if prev_header_level < header_level and prev_header_level != 0:
    #       yaml_output += "  " * header_level + f"subsections:\n"
    #     yaml_output += "  " * header_level + f"- title: { heading }"

    #     prev_header_level = header_level

    #     toc.write(yaml_output)
