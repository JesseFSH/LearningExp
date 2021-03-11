from multiprocessing import Pool

def testfunc(vm_info_list):
        hostname = vm_info_list[0]
        ipaddr = vm_info_list[1]
        print 'hostname:%s and ip:%s' % (hostname, ipaddr)


if __name__ == '__main__':
    with open('test.txt', 'r') as file:
        vm_info_list = []
        for line in file.readlines():
            line = line.strip()
            vm_info = line.split(',')
            vm_info_list.append(vm_info)
    pool = Pool()
    results = pool.map(testfunc, vm_info_list)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()