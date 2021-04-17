#!/usr/bin/python3
import sys

def parsare_argumente():
    in_dir="input"
    out_dir="output"
    n=3
    timeout=10
    for arg in sys.argv[1:]:
        check = arg.split("=")
        if len(check) < 2:
            print("invalid")
            exit()
        if check[0] == "if":
            in_dir = ''.join(check[1:])
        elif check[0] == "of":
            out_dir = ''.join(check[1:])
        elif check[0] == 'n':
            try:
                n = int(''.join(check[1:]))
            except ValueError:
                print("nr invalid")
        elif check[0] == 't':
            try:
                timeout = int(''.join(check[1:]))
            except ValueError:
                print("nr invalid")

    return [in_dir, out_dir, n, timeout]

def main():
    # aici functia principala
    print("salutare lume!!");
    print("Nr argumente: ", len(sys.argv))
    print(parsare_argumente())

if( __name__ == "__main__"):
    main();
