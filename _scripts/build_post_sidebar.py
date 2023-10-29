import os

def find_letter(line):
  counter = 0
  if line[0] != "#":
    return 0
  
  for char in line:
    if char != "#":
      return counter
    else:
      counter += 1

for post_file in os.listdir(os.getcwd() + "/_posts/"):

  # post_file_string = post_file[post_file.find(next(filter(str.isalpha, post_file))):post_file.find(".")]

  with open(f"_posts/{post_file}", "r") as post:
    post.readline()
    post.readline()
    title_line = post.readline()
    title = title_line[title_line.find('"') + 1:title_line.find('"', title_line.find('"') + 1)]
    title = title.lower().replace(" ", "-")

    with open(f"_data/post_toc/{title}.yaml", "w") as toc:
      toc.write("toc:\n")

      prev_header_level = 0
      prev_header_exists = False
      within_code = False
      for line in post:
        yaml_output = ""
        header_level = find_letter(line)
        if line[0] == "`" or line[0:2] == "{%":
          within_code = not within_code
        if within_code:
          continue
        if header_level == 0:
          continue

        
        # The correct way to do this is to refer to the previous header level so that everything is relative;
        # I have not done this to force myself to use the headers in order (you should really be styling the headers)
        # Independently instead of switching to different header vlaues to satisfy what you want) and because I am lazy and dont
        # Want to implement it now. 
        heading = line.strip("#").strip(" ")
        if prev_header_level < header_level and prev_header_level != 0:
          yaml_output += "  " * header_level + f"subsections:\n"
        yaml_output += "  " * header_level + f"- title: { heading }"

        prev_header_level = header_level

        toc.write(yaml_output)
