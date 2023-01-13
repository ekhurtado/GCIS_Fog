from jproperties import Properties
import time

def main():

    print("Comienzo programa")
    while True:

        print("-> Vamos a mirar en que aplicaciones estoy")

        configs = Properties()
        with open('/etc/config/component-data.properties', 'rb') as read_prop:
            configs.load(read_prop)

        prop_view = configs.items()
        # print(type(prop_view))

        for item in prop_view:
            # print(item)
            # print(item[0], '=', item[1].data)

            print("      Application name: " + item[0])
            print("      Related topic: " + item[1].data)
            print("      ---")

        time.sleep(5)   # espera 5 segundos



if __name__ == '__main__':

    main()