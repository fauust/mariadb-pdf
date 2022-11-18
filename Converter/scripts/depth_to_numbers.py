import csv
from os.path import join as path_join

def modify_csv(filepath):
    """modifies a csv file replacing each depth with a (idk)"""
    #read csv
    with open(filepath) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    #main loop
    depths = {} #depth: count
    last_depth = 0
    pool = [] # a list of resulting strings for each depth
    capture = []
    rows = [row for row in rows if row["Include"] not in ["", '0']]
    for index, row in enumerate(rows):
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
            for key in list(depths):
                if key > depth:
                    del depths[key]
            depths[depth] += 1
        
        last_depth = depth
        #keeping track of each depth (temporary)
        capture.append(depth)

        #adding next depth string
        add_to_pool(pool, depths, index)
    output_filepath = path_join("temp", f"m_{filepath}")
    with open(output_filepath, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames)
        writer.writeheader()
        for index, row in enumerate(rows):
            row["Header"] = "".join([i for i in row["Header"]])
            row["Depth"] = pool[index]
            writer.writerow(row)
        #writer.writerows(rows)
    
    return output_filepath

def add_to_pool(pool, depths, line):
    """converts the depths into a single string and adds it to the pool"""
    string = ""
    highest = max(list(depths))

    for i in range(1, highest+1):
        if i not in depths:
            print(f"error on line {line}")
            continue
        string += str(depths[i])
        string += "."
    string = string[:-1]
    pool.append(string)

if __name__ == "__main__":
    path = path_join("kb_urls.csv")
    modify_csv(path)