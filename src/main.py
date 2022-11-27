import csv
import sys
import hashlib
import requests
import json
from multiprocessing.dummy import Pool as ThreadPool

FIREBASE_URL = "https://snookerdatamanager-default-rtdb.firebaseio.com/"
METADATA_NODE_URL = FIREBASE_URL + "metadata"
METADATA_ROOT_URL = METADATA_NODE_URL + "/edfs/root"
NUM_NODES = 3

def error(error_code):
    """give error message"""
    if error_code == 404:
        print("Error: Path does not exist!")
    elif error_code == 1:
        print("Error: Having issue reading the file, please try again later!")
    #TODO
    sys.exit(1)

def init_database():
    metadata = {}
    metadata['nodes'] = {}
    for i in range(0, NUM_NODES):
        node = "node" + str(i + 1)
        node_url = FIREBASE_URL + node
        metadata['nodes'][node] = {}
        metadata['nodes'][node]['url'] = node_url

    metadata['edfs'] = {}
    metadata['edfs']['root'] = ""

    metadata_json_file = json.dumps(metadata, indent=4)
    response = requests.put(METADATA_NODE_URL + '.json', metadata_json_file)

    for i in range(0, NUM_NODES):
        node = "node" + str(i + 1)
        node_address = get_node_address(node)
        node_data = "" # init with empty node
        node_data_json_file = json.dumps(node_data, indent=4)
        response = requests.put(node_address + '.json', node_data_json_file)


def get_node_address(node_name):
    node_metadata = requests.get(f'{METADATA_NODE_URL}/nodes.json').json()
    return node_metadata[node_name]['url']


def get_hash(str):
    """returns the SHA-256 hash of the input"""
    return hashlib.sha256(bytes(str, encoding='utf-8')).hexdigest()


def format_output(list, num_pieces):
    piece_length = len(list) // num_pieces
    output = {}
    i = 0
    for i in range(0, num_pieces):
            if i == num_pieces - 1:
                output["block" + str(i + 1)] = list[i * piece_length:]
            else:
                output["block" + str(i + 1)] = list[i * piece_length: (i + 1) * piece_length]
    return output


# returns as follows:
# {"block1": "first part of file",
#  "block2": "second part of file",
#  "block3": "third part of file"}
def partition_file(file, num_pieces):
    if file[len(file) - 3:] == "csv":
        f = open(file, newline='')
        csvfile = csv.reader(f, delimiter=',', quotechar = '|')
        content = []
        for row in csvfile:
            while ("" in row):
                row.remove("")
            content.append(row)
    else:
        f = open(file)
        content = f.read()
    return format_output(content, num_pieces)


def get_firebase_file(firebase_path):
    pass


def put_firebase_file(file, firebase_path, num_pieces):
    pass


def assign_block_to_node(file_partition_num, file_name):
    # get hash of file_name, mod by number of nodes, and return the result
    return (hash(file_name) + file_partition_num) % NUM_NODES


def split_path(path):
    split = path.split('/')
    while "" in split:
        split.remove("")
    return split


def check_file_exists(path):
    """check if a path exists in metadata"""
    split = split_path(path)
    filename = split[-1]
    filename_hash = get_hash(filename)
    path = "/".join(split[:-1]) + "/" + str(filename_hash)
    response = requests.get(f'{METADATA_ROOT_URL}/{path}.json')
    if response.status_code == 200 and response.json() is not None:
        return True
    return False

def check_path_exists(path):
    """check if a path exists in metadata"""
    dir_metadata = requests.get(f'{METADATA_ROOT_URL}{path}.json')
    if dir_metadata.status_code == 200 and dir_metadata.json() is not None:
        return True
    return False

def update_meta_data(file, path, num_partitions):
    """for each file partition number, use get_partition_node_number to get the corresponding node
    insert a xxx.json directory in edfs/root/
    for each file to be stored, it needs to have the following structure:
    - blocks: ["block1", "block2", ...]
    - block_locations: { "block1": ["node1", "node3"], "block2": ["node2", "node3"] }
    returns the block_locations:
        { "block1": [
            "node1",
            "node3"
        ],
        "block2": [
            "node2",
            "node3"
        ],
        "block3": [
            "node1",
            "node3"
        ] }
    """
    # check if path exists
    if not check_path_exists(path):
        error(404)
    filename_hash = get_hash(file)
    metadata = requests.get(f'{METADATA_ROOT_URL}{path}.json').json()
    # check if it's an empty directory
    if not isinstance(metadata, dict):
        metadata = {}
    
    metadata[filename_hash] = {}
    current_dir = metadata[filename_hash]
    current_dir['filename'] = file
    current_dir['blocks'] = []
    current_dir['block_locations'] = {}
    for i in range(0, num_partitions):
        block_name = "block" + str(i + 1)
        current_dir['blocks'].append(block_name)
        block_location1 = assign_block_to_node(i, file)
        block_location2 = (assign_block_to_node(i, file) + 1) % NUM_NODES
        current_dir['block_locations'][block_name] = []
        current_dir['block_locations'][block_name].append("node" + str(block_location1 + 1))
        current_dir['block_locations'][block_name].append("node" + str(block_location2 + 1))

    metadata_json_file = json.dumps(metadata, indent=4)
    response = requests.put(f'{METADATA_ROOT_URL}{path}.json', metadata_json_file)
    return current_dir['block_locations']


def get_id(filename, block):
    return "id_" + get_hash(filename) + "_" + block

def get_node_data(node_address):
    return json.loads(requests.get(node_address).text)

def write_to_node(address, data):
    data = json.dumps(data, indent=4)
    response = requests.put(address, data)

def write_to_block(filename, file_partitions, block_locations):
    # file_partitions: {'block1': 'abc', 'block2': 'def', 'block3': 'ghi\n'}
    # block_locations: {'block1': ['node2', 'node0'], 'block2': ['node1', 'node2'], 'block3': ['node0', 'node1']}
    for block in file_partitions.keys():
        for node in block_locations[block]:
            node_address = get_node_address(node)
            block_id = get_id(filename, block)
            data_address =  node_address + "/" + block_id + ".json"
            write_to_node(data_address, file_partitions[block])


# APIs
def mkdir(path):
    """
    create a directory in metedata
    """
    # get the path of json file
    dir_path, new_dir = path.rsplit("/", 1)
    dir_metadata = requests.get(f'{METADATA_ROOT_URL}{dir_path}.json')
    if check_path_exists(dir_path):
        dir_metadata = requests.get(f'{METADATA_ROOT_URL}{dir_path}.json').json()
        if not isinstance(dir_metadata, dict):
            dir_metadata = {}
        if new_dir in dir_metadata:
            print("Directory already exists!")
        else:
            dir_metadata[new_dir] = ""
            requests.put(f'{METADATA_ROOT_URL}{dir_path}.json', json.dumps(dir_metadata))
    else:
        error(404)


def ls(path):
    """
    List all directories and files under the given path
    """
    if check_path_exists(path):
        dir_metadata = requests.get(f'{METADATA_ROOT_URL}{path}.json').json()
        for key in dir_metadata:
            # the case when the key is a file
            if 'filename' in dir_metadata[key]:
                print(dir_metadata[key]['filename'])
            else:
               print(key)
    else:
        error(404)


def cat(path):
    if check_file_exists(path):
        # get block locations in nodes
        # for each block, read the data from the nodes
        split = split_path(path)
        filename = split[-1]
        filename_hash = get_hash(filename)
        path = "/".join(split[:-1]) + "/" + str(filename_hash)
        file_metadata = requests.get(f'{METADATA_ROOT_URL}/{path}.json').json()
        filename = file_metadata['filename']
        for block in file_metadata['blocks']:
            nodes = file_metadata['block_locations'][block]
            read_success = False
            for node in nodes:
                node_address = get_node_address(node)
                file_id = get_id(filename, block)
                # read the data from the node
                # for each block, we only need to read from one node
                # try 3 times for a node, if failed, try the next node
                for _ in range(3):
                    try:
                        data = requests.get(f'{node_address}/{file_id}.json').json()
                        print(data, end='')
                        read_success = True
                        break
                    except: 
                        continue
                if read_success:
                    break
                else:
                    error(1)    
        print('')   
    else:
        error(404)


def rm(path):
    if check_file_exists(path):
        split = split_path(path)
        filename = split[len(split) - 1]
        split = split[:-1]
        filename_hash = get_hash(filename)

        partition_locations = get_partition_locations_helper(path)
        for block in partition_locations.keys():
            block_id = get_id(filename, block)
            for node in partition_locations[block]:
                node_address = get_node_address(node) + ".json"
                nodedata = get_node_data(node_address)
                nodedata[block_id] = {}
                write_to_node(node_address, nodedata)

        metadata = json.loads(requests.get(METADATA_NODE_URL + ".json").text)
        root = metadata['edfs']['root']
        prev_dir = root

        for i in range(0, len(split) - 1):
            name = split[i]
            prev_dir = prev_dir[name]
        current_dir = prev_dir[split[len(split) - 1]]

        current_dir[filename_hash] = {}


        current_dir_empty = True
        for key in current_dir:
            if current_dir[key] != {}:
                current_dir_empty = False

        if current_dir_empty:
            prev_dir[split[len(split) - 1]] = ""

        metadata_json_file = json.dumps(metadata, indent=4)
        response = requests.put(METADATA_NODE_URL + ".json", metadata_json_file)

    else:
        error(404)

def put(file, path, num_partitions):
    if check_file_exists(path):
        error(1)
    else:
        filename = split_path(file)
        filename = filename[len(filename) - 1]
        file_partitions = partition_file(file, num_partitions)
        block_locations = update_meta_data(filename, path, num_partitions)
        write_to_block(filename, file_partitions, block_locations)


def get_partition_locations(path):
    print(get_partition_locations_helper(path))


def get_partition_locations_helper(path):
    if check_file_exists(path):
        split = split_path(path)

        split[len(split) - 1] = get_hash(split[len(split) - 1])

        metadata = json.loads(requests.get(METADATA_NODE_URL + ".json").text)
        root = metadata['edfs']['root']
        current_dir = root

        for name in split:
            current_dir = current_dir[name]

        return current_dir['block_locations']

    else:
        error(404)


def read_partition(path, partitionNum):
    if check_file_exists(path):
        split = split_path(path)
        block_name = "block" + str(partitionNum)
        partition_locations = get_partition_locations_helper(path)
        partition_location = partition_locations[block_name]
        block_id = get_id(split[len(split) - 1], "block" + str(partitionNum))
        return get_node_data(get_node_address(partition_location[0])+ "/" + block_id + ".json")
    else:
        error(404)

def map_partition(path, partitionNum, mapFunc):
    data = read_partition(path, partitionNum)
    data = mapFunc(data)
    return data

def reduce(data_partitions, combineFunc):
    it = iter(data_partitions)
    value = next(it)
    for element in it:
        value = combineFunc(value, element)
    return value

def map_reduce(path, mapFunc, combineFunc, num_partitions):
    with ThreadPool(10) as pool:
        data_partitions = pool.starmap(map_partition, [(path, i + 1, mapFunc) for i in range(num_partitions)])
    return reduce(data_partitions, combineFunc)

def usage():
    print("Usage: ")

def main():
    arg_length = len(sys.argv)
    if arg_length <= 1:
        usage()
    elif arg_length == 2:
        if sys.argv[1] == "init":
            init_database()
        else:
            usage()
    elif arg_length == 3:
        cmd = sys.argv[1]
        arg = sys.argv[2]
        if cmd == "put" or cmd == "readPartition":
            usage()
        else:
            if cmd == "mkdir":
                mkdir(arg)
            elif cmd == "ls":
                ls(arg)
            elif cmd == "cat":
                cat(arg)
            elif cmd == "rm":
                rm(arg)
            elif cmd == "getPartitionLocations":
                get_partition_locations(arg)
            else:
                usage()
    elif arg_length == 4:
        if sys.argv[1] == "readPartition":
            path = sys.argv[2]
            partition_number = sys.argv[3]
            data = read_partition(path, partition_number)
            print(data)
        else:
            usage()
    elif arg_length == 5:
        if sys.argv[1] == "put":
            file = sys.argv[2]
            path = sys.argv[3]
            num_partitions = int(sys.argv[4])
            put(file, path, num_partitions)
        else:
            usage()
    else:
        usage()


if __name__ == "__main__":
    main()