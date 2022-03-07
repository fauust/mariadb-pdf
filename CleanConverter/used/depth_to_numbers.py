import csv
from os.path import join as path_join

#this script needs a better name please


def modify_csv(filepath):
    """modifies a csv file replacing each depth with a (idk)"""
    #read csv
    with open(filepath) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    
    #main loop
    depths = {} #depth: count
    last_depth = 0
    pool = [] # a list of resulting strings for each depth
    capture = []
    for row in rows:
        depth = row["Depth"]
        if depth == "":
            capture.append("")
            pool.append("")
            continue
        depth = int(depth)

        if depth == last_depth:
            depths[depth] += 1
        elif depth > last_depth:
            depths[depth] = 1
        else: #depth < last_depth:
            del depths[last_depth]
            depths[depth] += 1
        
        last_depth = depth
        #keeping track of each depth (temporary)
        capture.append(depth)

        #adding next depth string
        add_to_pool(pool, depths)

        # mapping capture and pool together and combining their elements into {capture_index}, {pool_index}
    #   list_contents = map((lambda x, y: f"{x}, {y}"), capture, pool)
        #making a single string containing each depth seperated with a newline
    #   content = "\n".join(list_contents)

    #   with open("test.txt", 'w') as file:
    #       file.write(content)

    output_filepath = path_join("tmp", f"m_{filepath}")
    with open(output_filepath, "w", newline="") as file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(file, fieldnames)
        writer.writeheader()
        for index, row in enumerate(rows):
            #row["Header"].strip(".")
            row["Header"] = "".join([i for i in row["Header"] if not i.isdigit() and i != "."])
            row["Depth"] = pool[index]
            writer.writerow(row)
        #writer.writerows(rows)
    
    return output_filepath

def add_to_pool(pool, depths):
    """converts the depths into a single string and adds it to the pool"""
    string = ""
    highest = max(list(depths))
    for i in range(1, highest+1):
        string += str(depths[i])
        string += "."
    string = string[:-1]
    pool.append(string)