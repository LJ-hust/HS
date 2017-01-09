import avltree
from draw import plot_tree
import pickle
import time
from Heap import Heap

if __name__ == '__main__':
    avl = avltree.AVLTree()
    n1 = avltree.AVLNode(143,12,time.time())
    n2 = avltree.AVLNode(18,4,time.time())
    n3 = avltree.AVLNode(1432,512,time.time())
    n4 = avltree.AVLNode(173,112,time.time())
    n5 = avltree.AVLNode(1,1,time.time())
    n6 = avltree.AVLNode(3,120,time.time())

    avl.insert_node(n1)
    avl.insert_node(n2)
    avl.insert_node(n3)
    avl.insert_node(n4)
    avl.insert_node(n5)
    avl.insert_node(n6)
    """
    avl.insert(143,12,time.time())
    avl.insert(18,4,time.time())
    avl.insert(1432,512,time.time())
    avl.insert(173,112,time.time())
    avl.insert(1,1,time.time())
    avl.insert(3,120,time.time())
    """
    pickle.dump(avl,open("lj.txt","w"))
    avl_read = pickle.load(open("lj.txt","r"))
    avl_read.delete(173)
    plot_tree(avl_read)
    heap = Heap()
    """
    avl_read.get_node(143).hotnessCount = 7
    avl_read.get_node(18).hotnessCount = 9
    avl_read.get_node(1432).hotnessCount = 688
    avl_read.get_node(1).hotnessCount = 1
    avl_read.get_node(3).hotnessCount = 277
    """
    n1.hotnessCount = 7
    n2.hotnessCount = 9
    n3.hotnessCount = 688
    n4.hotnessCount = 1
    n5.hotnessCount = 277
    """
    heap.add(avl_read.get_node(143))
    heap.add(avl_read.get_node(18))
    heap.add(avl_read.get_node(1432))
    heap.add(avl_read.get_node(1))
    heap.add(avl_read.get_node(3))
    """
    heap.add(n1)
    heap.add(n2)
    heap.add(n3)
    heap.add(n4)
    heap.add(n5)

    heap.heapsort()
    lis = heap.showArray()
    for l in lis:
        print "key = ", l.key, "  count = ",l.hotnessCount
    #print heap.pop().key
    #print heap.pop().key
    #print heap.pop().key
    #print heap.pop().key
    #print heap.pop().key
