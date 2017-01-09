from avltree import AVLTree
from draw import plot_tree
import pickle
import time
from Heap import Heap

if __name__ == '__main__':
    tr = AVLTree().load_tree()
    plot_tree(tr)
