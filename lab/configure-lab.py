from pathlib import Path
import yaml, secrets

ROOT = Path('/opt/openg2p-lab')
ROOT.mkdir(exist_ok=True)
DOMAIN = 'openg2p.localhost'
password = secrets.token_urlsafe(24)
credential_file = ROOT / 'credentials.yaml'
if credential_file.exists():
    password = yaml.safe_load(credential_file.read_text())['admin_password']
else:
    credential_file.write_text(yaml.safe_dump({'admin_username': 'admin', 'admin_password': password}))
    credential_file.chmod(0o600)

base = {
    'global': {'baseDomain': DOMAIN, 'defaultStorageClass': 'local-path', 'storageClass': 'local-path', 'sysAdminEmail': 'admin@nigeria.openg2p.localhost'},
    'postgresql': {'auth': {'postgresPassword': password}, 'primary': {'persistence': {'size': '20Gi'}}},
    'keycloak': {'auth': {'adminPassword': password}},
    'keycloak-init': {'staffAdminEmail': 'admin@nigeria.openg2p.localhost', 'realms': {'staff': {'users': [{'username': 'admin', 'password': password, 'firstName': 'Nigeria', 'lastName': 'UX Admin', 'email': 'admin@nigeria.openg2p.localhost', 'clientRoleMappings': {'openg2p-kafka': ['Admin'], 'openg2p-minio': ['consoleAdmin']}}]}}},
    'minio': {'auth': {'rootPassword': password}, 'persistence': {'size': '10Gi'}},
    'kafka': {'controller': {'persistence': {'size': '8Gi'}}},
}
(ROOT / 'commons-base.yaml').write_text(yaml.safe_dump(base))
(ROOT / 'commons-base.yaml').chmod(0o600)
print('Local commons configuration saved; credentials retained in Linux with mode 0600.')

common_global = {'baseDomain': DOMAIN, 'defaultStorageClass': 'local-path', 'storageClass': 'local-path', 'keycloakBaseUrl': f'https://keycloak.{DOMAIN}', 'keycloakInternalUrl': 'http://commons-keycloak:80', 'keycloakIssuerUrl': 'http://commons-keycloak/realms/staff', 'keycloakExternalIssuerUrl': f'https://keycloak.{DOMAIN}/realms/staff', 'sysAdminEmail': 'admin@nigeria.openg2p.localhost'}
services = {'global': common_global, 'keycloak-init': {'staffAdminEmail': 'admin@nigeria.openg2p.localhost'}}
(ROOT / 'commons-services.yaml').write_text(yaml.safe_dump(services))

registry = {'global': {**common_global, 'srAdminHostname': f'registry.{DOMAIN}', 'srLandingPageHostname': f'socialregistry.{DOMAIN}', 'srOdooOidcClientId': 'openg2p-sr-nigeria', 'srMinioHostname': f'minio.{DOMAIN}'}, 'odoo': {'odooEmail': 'admin@nigeria.openg2p.localhost', 'odooPassword': password, 'loadDemoData': False, 'postgresql': {'auth': {'postgresPassword': password}, 'primary': {'persistence': {'size': '10Gi'}}}}, 'openg2p-registry-bg-tasks': {'enabled': True}}
for component in ['mail', 'odk-central', 'odk-central-enketo-redis-main', 'odk-central-enketo-redis-cache', 'minio', 'opensearch', 'kafka', 'kafkaUi', 'reporting', 'reporting-init', 'loggingFlow', 'artifactory', 'softhsm', 'keymanager', 'idgenerator', 'mosipKernelPostgresInit', 'superset', 'esignet', 'mock-identity-system', 'landing']:
    registry[component] = {'enabled': False}
(ROOT / 'registry.yaml').write_text(yaml.safe_dump(registry))
(ROOT / 'registry.yaml').chmod(0o600)
pbms = {'global': {**common_global, 'keymanagerBaseUrl': 'http://commons-services-keymanager', 'g2pPbmsBgTaskHostname': f'pbms-api.{DOMAIN}', 'registryInstallationName': 'registry', 'pbmsInstallationName': 'pbms'}, 'hostname': f'pbms.{DOMAIN}', 'odoo': {'odooEmail': 'admin@nigeria.openg2p.localhost', 'odooPassword': password, 'loadDemoData': False, 'postgresql': {'auth': {'postgresPassword': password}, 'primary': {'persistence': {'size': '10Gi'}}}}, 'minio': {'enabled': False}}
(ROOT / 'pbms.yaml').write_text(yaml.safe_dump(pbms))
(ROOT / 'pbms.yaml').chmod(0o600)
