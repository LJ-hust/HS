'''
Created on Oct 25, 2013

@author: pm429015
'''

class Heap(object):
    '''
    Min Heap
    '''

    def __init__(self):
        '''
        Constructor
        Using array to implement Heap sturcture
        '''
        self.__array = [None]

    def addcheck(self, parent, index, value):
        # maintain the rule of heap
        # add the new value first
        # then swap if the value is smaller than parent. recursive check
        if not (self.__array[parent] and self.__array[index]):
            return
            # swap
        if self.__array[parent].hotnessCount > self.__array[index].hotnessCount:
            # swap
            temp = self.__array[parent]
            self.__array[parent] = self.__array[index]
            self.__array[index] = temp
            self.addcheck(parent // 2, parent, value)

    def add(self, value):
        # Heap start from index 1
        index = len(self.__array)
        if index > 1:
            index = index
            parent = index // 2
            self.__array.append(value)
            self.addcheck(parent, index, value)

        else:
            self.__array.append(value)

    def showArray(self):
        # show the result of the sort list
        return self.__array

    def beheap(self, index):
        # recursive maintain the heap rules
        # which is children are bigger than parent
        length = len(self.__array)
        if index * 2 + 1 < length:
            if self.__array[index * 2].hotnessCount >= self.__array[index * 2 + 1].hotnessCount:
                if self.__array[index].hotnessCount > self.__array[index * 2 + 1].hotnessCount:
                    temp = self.__array[index]
                    self.__array[index] = self.__array[index * 2 + 1]
                    self.__array[index * 2 + 1 ] = temp
                    self.beheap(index*2+1)
            else:
                if self.__array[index].hotnessCount > self.__array[index * 2 ].hotnessCount:
                    temp = self.__array[index]
                    self.__array[index] = self.__array[index * 2 ]
                    self.__array[index * 2] = temp
                    self.beheap(index*2)
        elif index * 2 < length:
            if self.__array[index].hotnessCount > self.__array[index * 2].hotnessCount:
                    temp = self.__array[index]
                    self.__array[index] = self.__array[index * 2 ]
                    self.__array[index * 2  ] = temp
                    self.beheap(index*2)


    def heapsort(self):
        # easy. just pop out the heap tree
        # call method "beheap" to maintain the heap
        sort = []
        length = len(self.__array)
        while length > 1:
            sort.append(self.__array[1])
            self.__array[1] = self.__array[length-1]
            self.__array.pop()
            self.beheap(1)
            length = len(self.__array)
        # store back
        self.__array = sort
"""
if __name__=="__main__":
    heap = Heap()
    heap.add(7)
    heap.add(9)
    heap.add(688)
    heap.add(1)
    heap.add(277)

    heap.heapsort()
    heap.showArray()
"""
