import sys
import kvs


def main(argv):
    kvs_1 = kvs.KVS('localhost', 50001)
    kvs_2 = kvs.KVS('localhost', 50002)

    test_key = 'a'
    test_val = 'test_1'
    set_res = kvs_1.set(test_key, test_val)

    if set_res:
        is_success, value = kvs_2.get(test_key)
        assert (test_val == value)


if __name__ == "__main__":
    main(sys.argv)

