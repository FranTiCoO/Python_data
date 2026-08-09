import logging
import os
import re
import ssl
import subprocess
import tempfile

try:
    import rpyc
    from rpyc.utils.server import ThreadedServer
except ImportError:  # pragma: no cover - exercised in minimal test environments
    rpyc = None
    ThreadedServer = None

from logger_setup import logger


SHARED_SECRET = os.environ.get("RPC_SHARED_SECRET")
TLS_DIR = os.path.join(os.path.dirname(__file__), "certs")
TLS_CERT_PATH = os.environ.get("RPC_TLS_CERT", os.path.join(TLS_DIR, "rpc-cert.pem"))
TLS_KEY_PATH = os.environ.get("RPC_TLS_KEY", os.path.join(TLS_DIR, "rpc-key.pem"))
TLS_CA_CERT_PATH = os.environ.get("RPC_TLS_CA_CERT", os.path.join(TLS_DIR, "ca-cert.pem"))
TLS_CA_KEY_PATH = os.environ.get("RPC_TLS_CA_KEY", os.path.join(TLS_DIR, "ca-key.pem"))


def _ca_cert_is_valid(ca_cert_path):
    try:
        result = subprocess.run(
            ["openssl", "x509", "-in", ca_cert_path, "-noout", "-text"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

    text = result.stdout
    return (
        "CA:TRUE" in text
        and "Certificate Sign" in text
        and "CRL Sign" in text
    )


def ensure_tls_material(base_dir=None):
    if base_dir is None:
        base_dir = TLS_DIR

    cert_path = os.environ.get("RPC_TLS_CERT") or os.path.join(base_dir, "rpc-cert.pem")
    key_path = os.environ.get("RPC_TLS_KEY") or os.path.join(base_dir, "rpc-key.pem")
    ca_cert_path = os.environ.get("RPC_TLS_CA_CERT") or os.path.join(base_dir, "ca-cert.pem")
    ca_key_path = os.environ.get("RPC_TLS_CA_KEY") or os.path.join(base_dir, "ca-key.pem")

    if (
        os.path.exists(cert_path)
        and os.path.exists(key_path)
        and os.path.exists(ca_cert_path)
        and os.path.exists(ca_key_path)
        and _ca_cert_is_valid(ca_cert_path)
    ):
        return cert_path, key_path, ca_cert_path

    os.makedirs(os.path.dirname(cert_path), exist_ok=True)
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    os.makedirs(os.path.dirname(ca_cert_path), exist_ok=True)
    os.makedirs(os.path.dirname(ca_key_path), exist_ok=True)

    if not _ca_cert_is_valid(ca_cert_path):
        for path in (ca_cert_path, ca_key_path, cert_path, key_path):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

        ca_ext_path = None
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as ca_ext_file:
            ca_ext_file.write("basicConstraints=critical,CA:TRUE\n")
            ca_ext_file.write("keyUsage=critical,keyCertSign,cRLSign\n")
            ca_ext_file.write("subjectKeyIdentifier=hash\n")
            ca_ext_file.write("authorityKeyIdentifier=keyid:always,issuer\n")
            ca_ext_path = ca_ext_file.name

        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-days",
                "3650",
                "-subj",
                "/CN=OrchideenPi RPC CA",
                "-sha256",
                "-extensions",
                "v3_ca",
                "-config",
                "/etc/ssl/openssl.cnf",
                "-keyout",
                ca_key_path,
                "-out",
                ca_cert_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Re-sign with explicit extension file for environments where openssl.cnf lacks v3_ca defaults.
        subprocess.run(
            [
                "openssl",
                "x509",
                "-in",
                ca_cert_path,
                "-signkey",
                ca_key_path,
                "-days",
                "3650",
                "-sha256",
                "-extfile",
                ca_ext_path,
                "-out",
                ca_cert_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.remove(ca_ext_path)

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as ext_file:
            ext_file.write("basicConstraints=CA:FALSE\n")
            ext_file.write("keyUsage=digitalSignature,keyEncipherment\n")
            ext_file.write("extendedKeyUsage=serverAuth\n")
            ext_file.write("subjectAltName=DNS:localhost,IP:127.0.0.1\n")
            ext_path = ext_file.name

        subprocess.run(
            [
                "openssl",
                "req",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-subj",
                "/CN=localhost",
                "-keyout",
                key_path,
                "-out",
                "/tmp/rpc-csr.pem",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "openssl",
                "x509",
                "-req",
                "-in",
                "/tmp/rpc-csr.pem",
                "-CA",
                ca_cert_path,
                "-CAkey",
                ca_key_path,
                "-CAcreateserial",
                "-out",
                cert_path,
                "-days",
                "825",
                "-sha256",
                "-extfile",
                ext_path,
                "-copy_extensions",
                "copy",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.remove("/tmp/rpc-csr.pem")
        os.remove(ext_path)

    return cert_path, key_path, ca_cert_path


class TlsThreadedServer(ThreadedServer):
    def __init__(self, service, hostname=None, ipv6=False, port=0, backlog=4096, reuse_addr=True,
                 authenticator=None, registrar=None, auto_register=None, protocol_config=None,
                 logger=None, listener_timeout=0.5, socket_path=None, certfile=None, keyfile=None):
        super().__init__(
            service,
            hostname=hostname,
            ipv6=ipv6,
            port=port,
            backlog=backlog,
            reuse_addr=reuse_addr,
            authenticator=authenticator,
            registrar=registrar,
            auto_register=auto_register,
            protocol_config=protocol_config,
            logger=logger,
            listener_timeout=listener_timeout,
            socket_path=socket_path,
        )
        self.certfile = certfile or TLS_CERT_PATH
        self.keyfile = keyfile or TLS_KEY_PATH

    def _accept_method(self, sock):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        try:
            tls_sock = context.wrap_socket(sock, server_side=True)
        except ssl.SSLError as exc:
            # Keep the server alive if a non-TLS client hits the TLS port.
            logger.warning("TLS handshake failed: %s", exc)
            try:
                sock.close()
            except OSError:
                pass
            return
        super()._accept_method(tls_sock)


def update_config_file(updates, config_path="config.py"):
    if not updates:
        return False

    config_path = os.path.abspath(config_path)
    with open(config_path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    updated = False
    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=")
    new_lines = []

    for line in lines:
        match = pattern.match(line.strip())
        if match and match.group(1) in updates:
            new_lines.append(f"{match.group(1)} = {updates[match.group(1)]}\n")
            updated = True
        else:
            new_lines.append(line)

    if updated:
        with open(config_path, "w", encoding="utf-8") as handle:
            handle.writelines(new_lines)

    return updated


if rpyc is not None:
    @rpyc.service
    class Server(rpyc.Service):

        def __init__(self):
            self.authenticated = False

        @rpyc.exposed
        def handshake(self, token):
            if token == SHARED_SECRET:
                self.authenticated = True
                logger.info("RPC client authenticated")
                return True

            logger.warning("RPC authentication failed")
            return False

        @rpyc.exposed
        def write_config(self, data):
            if not self.authenticated:
                logger.warning("Rejected config update without authentication")
                return "authentication required"

            logger.debug("Updating configuration via RPC")
            normalized = {key: data[key] for key in data}
            updated = update_config_file(normalized)
            if updated:
                logger.info("config.py was modified")
                return "config.py was modified!"

            logger.warning("No matching config values were updated")
            return "No matching config values were updated"
else:
    class Server:  # pragma: no cover - fallback for environments without rpyc
        pass

def start_server():
    if rpyc is None or ThreadedServer is None:
        raise RuntimeError("RPyC is not installed; cannot start the RPC server")

    cert_path, key_path, _ = ensure_tls_material()
    server = TlsThreadedServer(
        Server,
        reuse_addr=True,
        port=18711,
        protocol_config={'allow_public_attrs': True},
        logger=logger,
        certfile=cert_path,
        keyfile=key_path,
    )
    logging.debug("start")
    server.start()
    logging.debug("started")


