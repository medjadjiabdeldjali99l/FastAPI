import xmlrpc.client
from tools.Credentials import OdooCredentials
from xmlrpc.client import ServerProxy


odooCredentials = OdooCredentials()

class OdooDatabase:

    def __init__(self):
        self.url = odooCredentials.url
        self.db = odooCredentials.db
        self.username = odooCredentials.username
        self.password = odooCredentials.password
        self.uid = None
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        if uid:
            self.uid = uid
            print("Authentification réussie : ", uid)
        else:
            self.uid = None
            print("Authentification échouée")
        base_url = self.execute_kw('ir.config_parameter', 'get_param',['web.base.url'])
        self.base_url = base_url

    def execute_kw(self, *args):
        return self.models.execute_kw(self.db, self.uid, self.password, *args)

    def get_partner_by_phone(self, phone_number):
        # Recherche du partenaire avec le numéro de téléphone spécifié
        partner_ids = self.execute_kw('res.partner', 'search', [[('phone', '=', phone_number)]])  # Filtre par téléphone
        
        if partner_ids:
            # Récupérer les informations détaillées du partenaire trouvé
            partner = self.execute_kw('res.partner', 'read', [partner_ids, ['name', 'email', 'phone']])
            return partner[0]  # Retourne les informations du premier partenaire trouvé
        else:
            return "Aucun partenaire trouvé avec ce numéro de téléphone."



