import requests
import json

FIREBASE_URL = "https://snookerdatamanager-default-rtdb.firebaseio.com/"
METADATA_NODE_URL = FIREBASE_URL + "metadata.json"
NODE1_URL = FIREBASE_URL + "node1.json"
NODE2_URL = FIREBASE_URL + "node2.json"
NODE3_URL = FIREBASE_URL + "node3.json"
NUM_NODES = 3


def init_database():

# returns as follows:
# {"block1": "first part of file",
#  "block2": "second part of file",
#  "block3": "third part of file"}
def partition_file(file, num_pieces):


def get_firebase_file(firebase_path):


def put_firebase_file(file, firebase_path, num_pieces):


def get_partition_node_number(file_partition_num, file_name):
    # get hash of file_name, mod by number of nodes, and return the result


def check_file_exists(path):
    # check if this file already exists


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


def write_to_block(file_partitions, block_locations):





def mkdir():


def ls():


def cat():


def rm(path):
    if check_file_exists(path):
        # get block locations in nodes
        # get file name
        # go to the nodes, use the id to delete the file blocks
        # delete the xxx.json in this path
    else:
        # give error

def put(file, path, num_partitions):
    if check_file_exists(path):
        # give error
    else:
        file_partitions = partition_file(file, num_partitions)
        block_locations = update_meta_data(file, path, num_partitions)
        write_to_block(file_partitions, block_locations)


def get_partition_locations(path):
    if check_file_exists(path):
        # return the block_locations in the xxx.json file
    else:
        # give error


def read_partition(path, partitionNum):
    if check_file_exists(path):
        # use index to get block's name in blocks, then use block_locations to
        # get the nodes storing the block.
        # then go to the node and read the data
    else:
        # give error

def main():


if __name__ == "__main__":
    main()