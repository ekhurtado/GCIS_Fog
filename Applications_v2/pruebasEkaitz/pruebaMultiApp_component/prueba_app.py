import time

print_all = lambda s: print(repr(s))

def main():

    print("Comienzo programa")
    while True:

        print("-> Vamos a mirar en que aplicaciones estoy")
        configMapFile = open("/etc/config/configmap_data.txt")

        lineas = configMapFile.read().splitlines()
        for linea in lineas:
            # print_all(linea)
            # print_all(linea.split(": ")[1])
            print("      Application name: " + linea.split(": ")[0])
            print("      Related topic: " + linea.split(": ")[1])
            print("      ---")

        time.sleep(5)   # espera 5 segundos



if __name__ == '__main__':

    main()