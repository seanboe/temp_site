def find_letter(line):
  counter = 0
  if line[0] != "#":
    return 0
  
  for char in line:
    if char != "#":
      return counter
    else:
      counter += 1

with open("_posts/2018-01-12-tree-of-codes.md", "r") as post:
  with open("_data/post_toc/tree-of-codes.yaml", "w") as toc:
    toc.write("toc:\n")

    prev_header_level = 0
    prev_header_exists = False
    for line in post:
      yaml_output = ""
      header_level = find_letter(line)
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
