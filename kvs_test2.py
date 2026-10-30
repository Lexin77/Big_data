import sys
import kvs


def main(argv):
    kvs_1 = kvs.KVS('localhost', 50001)
    kvs_2 = kvs.KVS('localhost', 50002)

    test_key = 'a'
    test_val = 'test_1'    
   
    i = 1
    while i <= 250:
        test_val = 'test_' + str(i);
        if i % 2 == 0:
            set_res = kvs_1.set(test_key, test_val)
        else:
            set_res = kvs_2.set(test_key, test_val)
        
        if set_res:
            print ('set_res = true')

            if i % 3 == 0:            
                is_success, value = kvs_1.get(test_key)
            else:
                is_success, value = kvs_2.get(test_key)
            
            print ('Read value = %s' %value)
            assert test_val == value,'Значения не совпадают'
        else:
            print ('set_res = false')
        i = i + 1


if __name__ == "__main__":
    main(sys.argv)

