import time


def main():

    print("Comienzo programa")
    while True:

        print("-> Vamos a mirar en que aplicaciones estoy")
        configMapFile = open("/etc/config/file.txt")

        lineas = configMapFile.readlines()
        for linea in lineas:
            print(linea)

        time.sleep(5)   # espera 5 segundos



if __name__ == '__main__':

    main()