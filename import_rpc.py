import odoorpc
import configparser
import os
import csv
import urllib.request
import sys

# Set the console encoding to UTF-8
#sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)



# Obtenez le chemin du répertoire du script
script_directory = os.path.dirname(os.path.realpath(__file__))

# Construisez le chemin complet du fichier config.json
config_file_path = os.path.join(script_directory, 'service.conf')

# Check if the file exists before attempting to read it
if os.path.exists(config_file_path):
    config = configparser.ConfigParser()
    config_file = config.read(config_file_path)

    # Print the result of reading the configuration file
    print(f"Config file read successfully: {config_file}")
    
    # Now you can access configuration values like this:
    host = config.get('DEFAULT', 'HOST', fallback='')
    port = config.get('DEFAULT', 'PORT', fallback='')
    protocol = config.get('DEFAULT', 'PROTOCOL', fallback='')
    user = config.get('DEFAULT', 'USER', fallback='')
    db = config.get('DEFAULT', 'DB', fallback='')
    key = config.get('DEFAULT', 'KEY', fallback='')

    # Print the extracted values
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Protocol: {protocol}")
    print(f"User: {user}")
    print(f"DB: {db}")
else:
    print(f"Le fichier {config_file_path} n'a pas été trouvé.")


# Vérifier si tous les paramètres nécessaires sont présents
if not all([host, port, protocol, user, db, key]):
    print("Please try to provide all the necessary parameters in the config file !")
else:
    # Tester la connexion avant d'initialiser odoorpc
    odoo_url = f"{protocol}://{host}:{port}"
    try:
        urllib.request.urlopen(odoo_url, timeout=10)
    except Exception as e:
        print(f"Unable to connect to {odoo_url} : {e}")
        exit()

    # Préparer la connexion au serveur Odoo
    try:
        odoo = odoorpc.ODOO(host, port=int(port))
        # Afficher les bases de données disponibles
        print(host, port, user, db, key)
        # Se connecter à la base de données
        odoo.login(db, user, key)
        # Vérifier si le modèle product.template existe
        if 'product.template' in odoo.env:
            ProductTemplate = odoo.env['product.template']

            # Rechercher tous les produits
            product_ids = ProductTemplate.search([('to_weight', '=', True)])
            
            # Fetch product names and barcodes in a single loop
            product_data = [('1',product.default_code,product.list_price,product.name, product.barcode) for product in ProductTemplate.browse(product_ids)]

            # Récupérer les noms des produits
            #product_names = [product.name for product in ProductTemplate.browse(product_ids)]
            # Récupérer les codes à barre des produits
            #product_barcodes = [product.barcode for product in ProductTemplate.browse(product_ids)]            
            # Afficher les noms des produits
            #for product in product_ids:
            #    print(product)

            # Écrire les noms des produits dans un fichier CSV
            csv_file_path = os.path.join(script_directory, 'plu.csv')
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';')
                csv_writer.writerow(['@UPDATE plu'])
                csv_writer.writerow(['1;0;1;0;0;Divers;2000000'])
                csv_writer.writerows(product_data)


            print(f"The product list have been written in {csv_file_path}")

        else:
            print("The model 'product.template' is not found in Odoo.")

    except Exception as e:

        print(f"An error occurred during the connection to Odoo : {e}")
