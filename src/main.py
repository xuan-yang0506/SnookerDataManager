import sys
import hashlib
import requests
import json

FIREBASE_URL = "https://snookerdatamanager-default-rtdb.firebaseio.com/"
METADATA_NODE_URL = FIREBASE_URL + "metadata.json"
NUM_NODES = 3

def init_database():
    metadata = {}
    metadata['nodes'] = {}
    for i in range(0, NUM_NODES):
        node = "node" + str(i + 1)
        node_url = FIREBASE_URL + node + ".json"
        metadata['nodes'][node] = {}
        metadata['nodes'][node]['url'] = node_url

    metadata['edfs'] = {}
    metadata['edfs']['root'] = ""

    metadata_json_file = json.dumps(metadata, indent=4)
    response = requests.put(METADATA_NODE_URL, metadata_json_file)

    for i in range(0, NUM_NODES):
        node = "node" + str(i + 1)
        node_address = get_node_address(node)
        node_data = {}
        node_data_json_file = json.dumps(node_data, indent=4)
        response = requests.put(node_address, node_data_json_file)


def get_node_address(node_name):
    return FIREBASE_URL + node_name + ".json"


# returns as follows:
# {"block1": "first part of file",
#  "block2": "second part of file",
#  "block3": "third part of file"}
def partition_file(file, num_pieces):
    f = open(file)
    content = f.read()
    num_characters = len(content)
    piece_length = num_characters // num_pieces
    output = {}
    i = 0
    for i in range(0, num_pieces):
        if i == num_pieces - 1:
            output["block" + str(i + 1)] = content[i * piece_length:]
        else:
            output["block" + str(i + 1)] = content[i * piece_length: (i + 1) * piece_length]
    return output


def get_firebase_file(firebase_path):
    pass


def put_firebase_file(file, firebase_path, num_pieces):
    pass


def assign_block_to_node(file_partition_num, file_name):
    # get hash of file_name, mod by number of nodes, and return the result
    return hash(file_name) * (file_partition_num + 1) % NUM_NODES


def split_path(path):
    split = path.split('/')
    while "" in split:
        split.remove("")
    return split


def check_file_exists(path):
    split = split_path(path)

    metadata = json.loads(requests.get(METADATA_NODE_URL).text)
    root = metadata['edfs']['root']
    current_dir = root

    for name in split:
        if type(current_dir) is dict and name in current_dir.keys():
            current_dir = current_dir[name]
        else:
            return False
    return True


def update_meta_data(file, path, num_partitions):
    # for each file partition number, use get_partition_node_number to get the corresponding node
    # insert a xxx.json directory in edfs/root/
    # for each file to be stored, it needs to have the following structure:
    # - blocks: ["block1", "block2", ...]
    # - block_locations: { "block1": ["node1", "node3"], "block2": ["node2", "node3"] }
    # returns the block_locations:
    #     { "block1": [
    #         "node1",
    #         "node3"
    #     ],
    #     "block2": [
    #         "node2",
    #         "node3"
    #     ],
    #     "block3": [
    #         "node1",
    #         "node3"
    #     ] }
    filename_hash = hashlib.sha256(bytes(file, encoding='utf-8')).hexdigest()
    split = split_path(path)
    metadata = json.loads(requests.get(METADATA_NODE_URL).text)
    root = metadata['edfs']['root']
    if type(root) is not dict:
        metadata['edfs']['root'] = {}
        root = metadata['edfs']['root']
    current_dir = root
    for name in split:
        if name in current_dir.keys():
            current_dir = current_dir[name]
        if name not in current_dir.keys():
            current_dir[name] = {}
            current_dir = current_dir[name]
    current_dir[filename_hash] = {}
    current_dir = current_dir[filename_hash]
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
    response = requests.put(METADATA_NODE_URL, metadata_json_file)
    return current_dir['block_locations']


def get_id(filename, block):
    return "id_" + filename + "_" + block


def get_node_data(node_address):
    return json.loads(requests.get(node_address).text)


def write_to_node(node_address, nodedata):
    metadata_json_file = json.dumps(nodedata, indent=4)
    response = requests.put(node_address, metadata_json_file)

def write_to_block(filename, file_partitions, block_locations):
    # file_partitions: {'block1': 'abc', 'block2': 'def', 'block3': 'ghi\n'}
    # block_locations: {'block1': ['node2', 'node0'], 'block2': ['node1', 'node2'], 'block3': ['node0', 'node1']}
    for block in file_partitions.keys():
        for node in block_locations[block]:
            node_address = get_node_address(node)
            block_id = get_id(filename, block)
            nodedata = get_node_data(node_address)
            if type(nodedata) is not dict:
                nodedata = {}
            nodedata[block_id] = file_partitions[block]
            write_to_node(node_address, nodedata)



def mkdir(path):
    print("mkdir " + path)


def ls(path):
    print("ls " + path)


def cat(path):
    print("cat " + path)


def rm(path):
    print("rm " + path)
    if check_file_exists(path):
        # get block locations in nodes
        # get file name
        # go to the nodes, use the id to delete the file blocks
        # delete the xxx.json in this path
        pass
    else:
        # give error
        pass


def put(file, path, num_partitions):
    # if check_file_exists(path):
    #     print("File already exists!")
    # else:
    file_partitions = partition_file(file, num_partitions)
    block_locations = update_meta_data(file, path, num_partitions)
    write_to_block(file, file_partitions, block_locations)


def get_partition_locations(path):
    # if check_file_exists(path):
    split = split_path(path)

    split[len(split) - 1] = hashlib.sha256(b'test.txt').hexdigest()

    metadata = json.loads(requests.get(METADATA_NODE_URL).text)
    root = metadata['edfs']['root']
    current_dir = root

    for name in split:
        current_dir = current_dir[name]

    print(current_dir['block_locations'])

    # else:
    #     # give error
    #     pass


def read_partition(path, partitionNum):
    print("read_partition" + path + " " + partitionNum)
    # if check_file_exists(path):
        # use index to get block's name in blocks, then use block_locations to
        # get the nodes storing the block.
        # then go to the node and read the data
        # pass
    # else:
    #     # give error
    #     pass


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
            read_partition(path, partition_number)
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